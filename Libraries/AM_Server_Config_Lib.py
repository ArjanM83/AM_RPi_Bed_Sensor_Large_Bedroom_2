import AM_File_System_Lib as F_S_Lib
import AM_Network_Lib as Network_Lib
import AM_Logging_Lib as Logging_Lib
import AM_Server_Path_Lib as Server_Path_Lib
import os

logger = Logging_Lib.get_logger(__name__)


def am_tcp_server_retrieve_settings(operator_name, external=False):
    local_operator_port_dict = {
        # reachable from other machines
        "error": 5001,
        "trigger": 5002,
        "ble server": 5003,
        "sensor": 5004,
        "sensor http": 5050,  # used in Domoticz http push

        # important
        "action": 5010,
        "condition": 5011,
        "graphviz": 5012,
        "internet data": 5013,
        "log": 5014,
        "matplotlib": 5015,
        "metadata": 5016,
        "network": 5017,
        "rule": 5018,
        "schedule": 5019,

        # other
        "av receiver denon": 5060,
        "domoticz": 5061,
        "email": 5062,
        "entertainment pc client": 5063,
        "fibaro home center": 5064,
        "ifttt": 5065,
        "irtrans": 5066,
        "knmi": 5067,
        "netatmo weather station": 5068,
        "notification alexa": 5069,
        "philips hue": 5070,
        "philips hue emulator": 5071,
        "thermostat toon": 5072,
        "wake on lan": 5073,

        # not running on server
        "workstation server": 5101,
        "entertainment pc server": 5201
    }

    external_operator_port_dict = {
        # running on server
        "error": {"ip": "", "port": local_operator_port_dict["error"]},
        "trigger": {"ip": "", "port": local_operator_port_dict["trigger"]},
        "ble server": {"ip": "", "port": local_operator_port_dict["ble server"]},
        "sensor": {"ip": "", "port": local_operator_port_dict["sensor"]},

        # not running on server
        "workstation server": {"ip": "Workstation Wi-Fi", "port": local_operator_port_dict["workstation server"]},
        "entertainment pc server": {
            "ip": "Entertainment PC LAN", "port": local_operator_port_dict["entertainment pc server"]}
    }

    # internal
    if not external and operator_name in local_operator_port_dict:
        tcp_ip = Network_Lib.get_local_ip_address()
        tcp_port = local_operator_port_dict[operator_name]
    # external
    elif external and operator_name in external_operator_port_dict:
        # tcp ip
        if external_operator_port_dict[operator_name]["ip"]:
            import AM_Server_Network_Lib as Server_Network_Lib
            tcp_ip = Server_Network_Lib.get_ip_address_for_name(external_operator_port_dict[operator_name]["ip"])
        else:
            server_settings_path = Server_Path_Lib.get_path(["Settings", "Server"])
            if server_settings_path:
                server_settings_file_path = \
                    os.path.join(Server_Path_Lib.get_path(["Settings", "Server"]), "Server IP.json")
                if os.path.isfile(server_settings_file_path):
                    server_settings_dict = F_S_Lib.get_dict_from_file(server_settings_file_path)
                    tcp_ip = server_settings_dict["ip"]
                else:
                    tcp_ip = Network_Lib.get_local_ip_address()
                    logger.error("File not found for retrieving external server IP: '{0}', now using local IP address: "
                                 "{1}".format(server_settings_file_path, tcp_ip))
            else:
                tcp_ip = Network_Lib.get_local_ip_address()
                logger.error(
                    "Path not found for retrieving external server IP, now using local IP address: {0}".format(tcp_ip))
        # tcp port
        tcp_port = external_operator_port_dict[operator_name]["port"]
    # not found
    else:
        logger.error("tcp_ip and tcp_port not found for name: '{0}' and external: {1}".format(operator_name, external))
        tcp_ip = None
        tcp_port = None

    return tcp_ip, tcp_port
