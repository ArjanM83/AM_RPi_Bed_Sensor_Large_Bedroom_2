import AM_Network_Lib as Network_Lib
import logging
import logging.config
import logging.handlers
import os
import sys


def setup(logger_name="", logging_level="INFO", path_logging="Logging", s_h_host="", s_h_port=""):
    # path log files
    if path_logging:
        folder_one_up = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).split("/")[-1]

        if logger_name:
            path_logging_all = os.path.join(path_logging, "{0}_{1}.log".format(folder_one_up, logger_name))
            path_logging_error = os.path.join(path_logging, "{0}_{1}.error.log".format(folder_one_up, logger_name))
        else:
            path_logging_all = os.path.join(path_logging, "{0}_all.log".format(folder_one_up))
            path_logging_error = os.path.join(path_logging, "{0}_all.error.log".format(folder_one_up))
    else:
        path_logging_all = ""
        path_logging_error = ""

    # socket handler
    if not s_h_host:
        s_h_host = Network_Lib.get_local_ip_address()
    if not s_h_port:
        s_h_port = "5001"

    formatter_string = "%(asctime)s [%(levelname)s] %(module)s %(funcName)s: %(message)s"
    f_h_max_bytes = 10485760
    f_h_backup_count = 20

    if logger_name:
        new_logger = logging.getLogger(logger_name)
        formatter = logging.Formatter(formatter_string)

        c_h = logging.StreamHandler(sys.stdout)
        c_h.setFormatter(formatter)
        c_h.setLevel("INFO")

        new_logger.setLevel(logging_level)
        new_logger.addHandler(c_h)

        if s_h_host and s_h_port:
            s_h = logging.handlers.SocketHandler(s_h_host, int(s_h_port))
            s_h.setFormatter(formatter)
            s_h.setLevel("ERROR")
            new_logger.addHandler(s_h)

        if path_logging:
            f_h_all = logging.handlers.RotatingFileHandler(
                path_logging_all,
                mode="a", maxBytes=f_h_max_bytes, backupCount=f_h_backup_count, encoding="utf8")
            f_h_all.setFormatter(formatter)
            f_h_all.setLevel(logging_level)

            f_h_error = logging.handlers.RotatingFileHandler(
                path_logging_error,
                mode="a", maxBytes=f_h_max_bytes, backupCount=f_h_backup_count, encoding="utf8")
            f_h_error.setFormatter(formatter)
            f_h_error.setLevel("ERROR")

            new_logger.addHandler(f_h_all)
            new_logger.addHandler(f_h_error)

        return logger_name
    else:
        logging_dict = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {"standard": {"format": formatter_string}, },
            "handlers": {
                "console": {"class": "logging.StreamHandler", "level": "INFO", "formatter": "standard",
                            "stream": "ext://sys.stdout"}},
            "root": {"level": logging_level, "handlers": ["console"]}}

        if s_h_host and s_h_port:
            logging_dict["handlers"]["error_operator"] = {
                "class": "logging.handlers.SocketHandler", "level": "ERROR",
                "formatter": "standard", "host": s_h_host, "port": int(s_h_port)}
            logging_dict["root"]["handlers"] += ["error_operator"]

        if path_logging:
            logging_dict["handlers"]["file_handler"] = {
                "class": "logging.handlers.RotatingFileHandler", "level": logging_level,
                "formatter": "standard", "filename": path_logging_all, "maxBytes": f_h_max_bytes,
                "backupCount": f_h_backup_count, "encoding": "utf8"}
            logging_dict["handlers"]["error_file_handler"] = {
                "class": "logging.handlers.RotatingFileHandler", "level": "ERROR",
                "formatter": "standard", "filename": path_logging_error,
                "maxBytes": f_h_max_bytes, "backupCount": f_h_backup_count, "encoding": "utf8"}
            logging_dict["root"]["handlers"] += ["file_handler"]
            logging_dict["root"]["handlers"] += ["error_file_handler"]

        logging.config.dictConfig(logging_dict)


def get_logger(name, logging_level="INFO", path_logging="Logging", s_h_host="", s_h_port=""):
    if not os.path.isdir(path_logging):
        path_logging = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), path_logging)

    if os.path.isdir(path_logging):
        return logging.getLogger(setup(name, logging_level, path_logging, s_h_host, s_h_port))
    else:
        # try to create logging folder
        try:
            os.mkdir(path_logging)
            logger = logging.getLogger(setup(name, logging_level, path_logging, s_h_host, s_h_port))
            logger.info("Folder for log files was missing but has been automatically created: {0}".format(path_logging))
        except OSError:
            logger = logging.getLogger(setup(name, logging_level, "", s_h_host, s_h_port))
            logger.error("Folder for log files is missing and could not be automatically created: {0}".format(
                path_logging))
        return logger
