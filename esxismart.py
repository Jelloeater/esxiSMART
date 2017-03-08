import argparse
import getpass
import json
import logging
import sys

from flask import Flask
from keyring.errors import PasswordDeleteError
import paramiko
import keyring

__author__ = 'Jesse'


class Password:
    KEYRING_APP_ID = 'esxiSMART'
    USER_ID = 'root'

    def set_password(self):
        print("Enter ESXi ip address")
        ip = getpass.getpass(prompt='>')  # To stop shoulder surfing
        print("Enter ESXi root pass")
        password = getpass.getpass(prompt='>')  # To stop shoulder surfing
        keyring.set_password(str(self.KEYRING_APP_ID + ':' + ip), self.USER_ID, password)

    def get_password(self, ip):
        return keyring.get_password(str(self.KEYRING_APP_ID + ':' + ip), self.USER_ID)

    def clear_password(self):
        try:
            print("Enter ESXi ip address to clear")
            ip = getpass.getpass(prompt='>')  # To stop shoulder surfing
            keyring.delete_password(str(self.KEYRING_APP_ID + ':' + ip), self.USER_ID)
            print("Password removed from Keyring")
        except PasswordDeleteError:
            logging.error("Password cannot be deleted or already has been removed")


def get_smart_status(host_ip):
    port = 22
    username = Password.USER_ID
    password = Password().get_password(host_ip)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host_ip, port, username, password)
    except paramiko.ssh_exception.SSHException:
        return False

    stdin, stdout, stderr = ssh.exec_command('./usr/lib/vmware/vm-support/bin/smartinfo.sh')
    outlines = stdout.readlines()
    resp = ''.join(outlines)
    return resp


def parse_smart_status_to_list(raw_input):
    raw_device_list = raw_input.split('Device:  ')

    device_list = []
    for device in raw_device_list[1:]:
        device_list.append(device.split('\n'))
        # For each item in the list, we will split it into a sub list, then add that sub list to the master list

    # logging.debug(raw_input)
    big_list = []
    for device in device_list:
        device_info = []
        for line in device[3:]:  # Skips header and separator line
            if line != '':  # Ignores empty lines
                device_info.append({"Parameter": line[:30].strip(), "Value": line[30:37].strip(),
                                    "Threshold": line[37:48].strip(), "Worst": line[48:].strip()})
        big_list.append({'Device': device[0], 'Info': device_info})
    return big_list


def get_devices_from_server(ip):
    raw_data = get_smart_status(ip)
    if raw_data is False:
        return 'No password / Bad Password for ' + str(ip)

    server_list = parse_smart_status_to_list(raw_data)
    device_list = []
    for i in server_list:
        device_list.append(i['Device'])
    return json.dumps(device_list, indent=4, sort_keys=True)


def get_devices_stats(ip, device_name):
    raw_dat = get_smart_status(ip)
    server_list = parse_smart_status_to_list(raw_dat)
    for i in server_list:
        print(i['Device'])
        if i['Device'] == device_name:
            return json.dumps(i['Info'], indent=4, sort_keys=True)
        break


def main():
    logging.basicConfig(format="[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)",
                        level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument("--set_password",
                        action="store_true")
    parser.add_argument("--clear_password",
                        action="store_true")
    args = parser.parse_args()
    if args.set_password:
        Password().set_password()
        sys.exit()
    elif args.clear_password:
        Password().clear_password()
        sys.exit()
    else:
        start_web_server()


def start_web_server():
    app = Flask(__name__)

    @app.route('/')
    def index():
        return str('Enter IP of server to check (ex /127.0.0.1)<br>'
                   'Enter the device you wish to parse (/127.0.0.1:Device_ID)')

    @app.route('/<x>')
    def get_server(x):
        return get_devices_from_server(x)

    @app.route('/<x>:<y>')
    def get_device_from_server(x, y):
        return get_devices_stats(x, y)

    app.run(host="0.0.0.0", port=80, debug=True)


if __name__ == "__main__":
    main()
