import AM_File_System_Lib as F_S_Lib
import AM_Logging_Lib as Logging_Lib
import AM_Server_Path_Lib as Server_Path_Lib
import os

logger = Logging_Lib.get_logger(__name__)


def get_network_ip_names_dict():
    path_network_ip_names_settings = \
        os.path.join(Server_Path_Lib.get_path(["Settings", "Network"]), "Network IP Addresses Names.json")
    return F_S_Lib.get_dict_from_file(path_network_ip_names_settings)


def get_name_network_ip_dict():
    name_network_ip_dict = {}
    network_ip_names_dict = get_network_ip_names_dict()

    for network_ip in network_ip_names_dict:
        name_network_ip_dict[network_ip_names_dict[network_ip]] = network_ip

    return name_network_ip_dict


def get_ip_address_for_name(network_name):
    ip_address_found_counter = 0
    name_network_ip_dict = get_name_network_ip_dict()
    ip_address = ""

    for name in name_network_ip_dict:
        if network_name.lower() in name.lower():
            ip_address = name_network_ip_dict[name]
            ip_address_found_counter += 1

    if ip_address_found_counter == 0:
        logger.error("AM Server Lib: No network name including: '{0}' was found in the network IP addresses settings.".
                     format(network_name))
    elif ip_address_found_counter == 1:
        return ip_address
    else:
        logger.error("AM Server Lib: Multiple network names including: '{0}' were found in the network IP addresses "
                     "settings.".format(network_name))


def get_names_mac_addresses_dict():
    path_names_mac_addresses_settings = \
        os.path.join(Server_Path_Lib.get_path(["Settings", "Network"]), "Names Mac Addresses.json")
    return F_S_Lib.get_dict_from_file(path_names_mac_addresses_settings)


def get_names_list_for_mac_addresses():
    return sorted(get_names_mac_addresses_dict().keys())


def get_wake_on_lan_names_list_for_mac_addresses():
    w_o_l_names_list = []
    names_list = get_names_list_for_mac_addresses()

    for name in names_list:
        if "amazon dash button" not in name.lower():
            w_o_l_names_list.append(name)

    return sorted(w_o_l_names_list)


def get_mac_address_for_name(network_name):
    name_found_counter = 0
    names_mac_addresses_dict = get_names_mac_addresses_dict()
    mac_address = ""

    for name in names_mac_addresses_dict:
        if network_name.lower() in name.lower():
            mac_address = names_mac_addresses_dict[name]
            name_found_counter += 1

    if name_found_counter == 0:
        logger.error("AM Server Lib: No network name including: '{0}' was found in the 'names mac addresses' network "
                     "settings.".format(network_name))
    elif name_found_counter == 1:
        return mac_address
    else:
        logger.error("AM Server Lib: Multiple network names including: '{0}' were found in the 'names mac addresses' "
                     "network settings.".format(network_name))


def get_name_for_mac_address(mac_address):
    mac_address_found_counter = 0
    names_mac_addresses_dict = get_names_mac_addresses_dict()
    output_name = ""

    for name in names_mac_addresses_dict:
        if mac_address.lower() in names_mac_addresses_dict[name].lower():
            output_name = name
            mac_address_found_counter += 1

    if mac_address_found_counter == 0:
        logger.error("AM Server Lib: No mac address including: '{0}' was found in the 'names mac addresses' "
                     "network settings.".format(mac_address))
    elif mac_address_found_counter == 1:
        return output_name
    else:
        logger.error("AM Server Lib: Multiple mac addresses including: '{0}' were found in the 'names mac addresses' "
                     "network settings.".format(mac_address))
