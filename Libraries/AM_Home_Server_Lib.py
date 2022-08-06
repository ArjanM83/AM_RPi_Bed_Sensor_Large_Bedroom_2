import AM_File_System_Lib as F_S_Lib
import AM_Logging_Lib as Logging_Lib
import AM_Server_Config_Lib as Server_Config_Lib
import AM_Server_Path_Lib as Server_Path_Lib
import json
import multiprocessing
import multiprocessing.pool
import os
import SocketServer
import socket
import sys

logger = Logging_Lib.get_logger(__name__)


def am_tcp_server_retrieve_settings(operator_name, external=False):
    return Server_Config_Lib.am_tcp_server_retrieve_settings(operator_name, external)


class AMTCPServer(multiprocessing.Process):
    def __init__(self, module_name, operator_queue):
        multiprocessing.Process.__init__(self)

        self.module_name = module_name
        self.operator_queue = operator_queue
        self.server = None

    def run(self):
        tcp_ip, tcp_port = am_tcp_server_retrieve_settings(self.module_name)

        if not tcp_ip or not tcp_port:
            logger.error("Server could not be started for '{0}' operator.".format(self.module_name))
            return

        try:
            self.server = SocketServer.ThreadingTCPServer((tcp_ip, int(tcp_port),), AMTCPServerRequestHandler)
            logger.info("Starting {0} operator: {1}:{2}".format(self.module_name, tcp_ip, tcp_port))
        except (socket.error, TypeError):
            logger.exception("Unable to start a server for {0} operator at address: {1}:{2}".format(
                self.module_name, tcp_ip, tcp_port))
            sys.exit()

        self.server.operator_queue = self.operator_queue
        self.server.serve_forever()


class AMTCPServerRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        received = self.request.recv(1024)
        try:
            self.server.operator_queue.put(json.loads(received))
        except ValueError:
            logger.error("AM TCP Server Request Handler error: {0}".format(received[:500]))


def am_tcp_client_external(operator_name, input_dict, attempt=1):
    return am_tcp_client(operator_name, input_dict, attempt, True)


def am_tcp_client(operator_name, input_dict, attempt=1, external=False):
    tcp_ip, tcp_port = am_tcp_server_retrieve_settings(operator_name, external)

    if not tcp_ip or not tcp_port:
        logger.error("Request for {0} operator could not be performed.".format(operator_name))
        return

    new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        new_socket.connect((tcp_ip, int(tcp_port)))
        new_socket.send(json.dumps(input_dict))
    except socket.error:
        if operator_name not in ["error", "entertainment pc server", "game pc server"] and \
                not input_dict == {"update_meta_data": ""}:
            logger.exception("Unable to connect to {0} operator with input: {1}".format(operator_name, input_dict))
        return
    except (TypeError, UnicodeDecodeError):
        if operator_name not in ["error", "entertainment pc server", "game pc server"] and \
                not input_dict == {"update_meta_data": ""}:
            logger.exception("Unable to connect to {0} operator".format(operator_name))
        return

    # receive answer from log operator if status is requested
    # or receive answer from entertainment pc ping request
    if (operator_name == "log" and input_dict.get("action_type", "") == "get_state") or \
            (operator_name in ["entertainment pc server", "game pc server"] and
             input_dict.get("value_2", "") == "ping"):
        try:
            received_data = new_socket.recv(1024)

            if received_data:
                try:
                    output_dict = json.loads(received_data)
                    return output_dict
                except ValueError:
                    logger.exception("Corrupt data received from module: {0}".format(operator_name))
            else:
                logger.error("No data was received from module '{0}' with input: {1}".format(
                    operator_name, input_dict))
        except (socket.error, TypeError):
            if attempt < 3:
                return am_tcp_client(operator_name, input_dict, attempt + 1)
            else:
                logger.exception("Error occurred requesting data from module: '{0}', no more retry.".format(
                    operator_name))
                return

    new_socket.close()


def update_meta_data_all_operators():
    am_tcp_client("metadata", {"update_meta_data": ""})


def is_operator_enabled(operator_name):
    path_settings_server = Server_Path_Lib.get_path(["Settings", "Server"])
    if path_settings_server:
        path_operator_settings_dict = os.path.join(path_settings_server, "Operator Settings.json")
        operator_setttings_dict = F_S_Lib.get_dict_from_file(path_operator_settings_dict)
        if operator_setttings_dict.get(operator_name, "").lower() == "enabled":
            return True
        else:
            return False
    else:
        return False
