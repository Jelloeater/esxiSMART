import argparse
import getpass
import json
import logging

from keyring.errors import PasswordDeleteError
import paramiko
import keyring

__author__ = 'Jesse'


class Password:
    KEYRING_APP_ID = 'esxiSMART'
    USER_ID = 'root'

    def set_password(self):
        print("Enter ESXi root pass")
        password = getpass.getpass(prompt='>')  # To stop shoulder surfing
        keyring.set_password(self.KEYRING_APP_ID, self.USER_ID, password)

    def get_password(self):
        return keyring.get_password(self.KEYRING_APP_ID, self.USER_ID)

    def clear_password(self):
        try:
            keyring.delete_password(self.KEYRING_APP_ID, self.USER_ID)
            print("Password removed from Keyring")
        except PasswordDeleteError:
            logging.error("Password cannot be deleted or already has been removed")


def get_smart_status(host_ip):
    port = 22
    username = Password.USER_ID
    password = Password().get_password()

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host_ip, port, username, password)

    stdin, stdout, stderr = ssh.exec_command('./usr/lib/vmware/vm-support/bin/smartinfo.sh')
    outlines = stdout.readlines()
    resp = ''.join(outlines)
    return resp


def parse_smart_status_to_JSON(raw_input):
    raw_device_list = raw_input.split('Device:  ')

    device_list = []
    for device in raw_device_list[1:]:
        device_list.append(device.split('\n'))
        # For each item in the list, we will split it into a sub list, then add that sub list to the master list

    logging.debug(raw_input)
    big_list = []
    for device in device_list:
        device_info = []
        for line in device[3:]:  # Skips header and separator line
            if line != '':  # Ignores empty lines
                device_info.append({"Parameter": line[:30].strip(), "Value": line[30:37].strip(),
                                    "Threshold": line[37:48].strip(), "Worst": line[48:].strip()})
        big_list.append({'Device': device[0], 'Info': device_info})
    return json.dumps(big_list, indent=4, sort_keys=True)


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
    if args.clear_password:
        Password().clear_password()

    stats = get_smart_status('192.168.1.150')
    out = parse_smart_status_to_JSON(stats)
    print(out)


def start_web_server():
    from flask import Flask
    app = Flask(__name__)

    @app.route('/')
    def hello_world():
        return 'Hello, World!'

    app.run()


if __name__ == "__main__":
    main()
    start_web_server()
