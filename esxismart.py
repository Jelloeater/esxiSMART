import argparse
import getpass
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


def get_smart_status():
    ip = 'server ip'
    port = 22
    username = 'root'
    password = 'password'

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, port, username, password)

    stdin, stdout, stderr = ssh.exec_command('./usr/lib/vmware/vm-support/bin/smartinfo.sh')
    outlines = stdout.readlines()
    resp = ''.join(outlines)
    logging.debug(resp)


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

if __name__ == "__main__":
    main()
