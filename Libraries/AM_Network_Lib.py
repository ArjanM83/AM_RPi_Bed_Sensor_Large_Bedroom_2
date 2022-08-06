import socket
import subprocess as sp
import time


def get_local_ip_address(logger=None):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        s.connect(("8.8.8.8", 80))
    except socket.error:
        if logger:
            logger.error("Could not trace local IP.")

    ip_address = s.getsockname()[0]
    s.close()

    return ip_address


def wait_for_network_init_and_get_local_ip_address(logger=None):
    local_ip_address = get_local_ip_address(logger)

    time_counter = 0
    while local_ip_address == "0.0.0.0" and time_counter < 60:
        time.sleep(1)
        time_counter += 1
        local_ip_address = get_local_ip_address(logger)

    return local_ip_address


def ping(ip_address):
    # windows OS
    network_ping = sp.Popen(
        ["ping", "-n", "1", ip_address], stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
    network_ping_output, network_ping_error = network_ping.communicate()

    if "destination host unreachable" in network_ping_output.lower() or \
        "request timed out" in network_ping_output.lower() or \
        "no resources" in network_ping_output.lower() or \
        "general failure" in network_ping_output.lower() or \
            "100% loss" in network_ping_output.lower():
        return False
    # linux OS
    elif len(network_ping_output) == 0:
        network_ping = sp.Popen(
            ["sudo", "ping", "-c", "1", ip_address, "-W", "1"], stdout=sp.PIPE, stderr=sp.PIPE)
        network_ping_output, network_ping_error = network_ping.communicate()

        if "0 received" in network_ping_output.lower():
            return False
        else:
            return True
    else:
        return True


def wait_for_working_internet_connection(logger=None):
    if wait_for_network_init_and_get_local_ip_address(logger):
        ping_reply = ping("8.8.8.8")

        time_counter = 0
        while not ping_reply and time_counter < 60:
            time.sleep(1)
            time_counter += 1
            ping_reply = ping("8.8.8.8")
            
        return ping_reply
