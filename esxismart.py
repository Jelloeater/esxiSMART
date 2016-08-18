import logging
import paramiko

__author__ = 'Jesse'


def get_smart_status():
    ip = 'server ip'
    port = 22
    username = 'username'
    password = 'password'

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, port, username, password)

    stdin, stdout, stderr = ssh.exec_command('some really useful command')
    outlines = stdout.readlines()
    resp = ''.join(outlines)
    logging.debug(resp)


def main():
    logging.basicConfig(format="[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)",
                        level=logging.DEBUG)


if __name__ == "__main__":
    main()
