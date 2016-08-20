# Summary
Parses ESXI SMART status and displays JSON

# Requires
paramiko
keyring
flask

# Usage
Enter device password first
python esxismart.py --set_password

To clear password
python esxismart.py --clear_password

Server Device Listing
http://ip_of_webserver/server_ip

Device SMART Info
http://ip_of_webserver/server_ip:device_ID