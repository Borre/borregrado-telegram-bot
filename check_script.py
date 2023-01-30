import socket

import requests


# Check for internet connectivity


def check_internet():
    try:
        # Connect to Google DNS server
        socket.gethostbyname('www.google.com')
        return "Connected"
    except:
        return "Not Connected"

# Check if the DNS ip 10.10.10.1 is resolving


def check_dns():
    try:
        # Resolve IP address
        socket.gethostbyname('10.10.10.1')
        return "Resolving"
    except:
        return "Not Resolving"

# Check if the firewall ip 10.10.10.1 is responding


def check_firewall():
    try:
        # Connect to firewall
        socket.create_connection(('10.10.10.1', 80), timeout=1)
        return "Responding"
    except:
        return "Not Responding"

# Check if the NAS 10.10.30.1 is responding


def check_nas():
    try:
        # Connect to IP
        socket.create_connection(('10.10.30.1', 80), timeout=1)
        return "Responding"
    except:
        return "Not Responding"

# Check ifconfig.me


def get_ifconfig_me_all():
    try:
        response = requests.get("http://ifconfig.me/all")
        if response.status_code == 200:
            return response.text
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(e)
        return None
