import AM_Logging_Lib as Logging_Lib
import json
import os

logger = Logging_Lib.get_logger(__name__)


def get_file_list(path_dir, exclude_hidden_files=False):
    return get_file_list_with_ext(
        path_dir=path_dir, requested_ext=None, exclude_hidden_files=exclude_hidden_files, include_ext=False)


def get_file_list_with_ext(path_dir, requested_ext=None, exclude_hidden_files=False, include_ext=True):
    if path_dir:
        file_list = []

        for dir_item in os.listdir(path_dir):
            if os.path.isfile(os.path.join(path_dir, dir_item)):
                append_dir_item = True

                # exclude hidden files if requested
                if exclude_hidden_files:
                    if dir_item.startswith("."):
                        append_dir_item = False

                # include only specific extensions if requested
                if requested_ext:
                    if not dir_item.upper().endswith(requested_ext.upper()):
                        append_dir_item = False

                if append_dir_item:
                    file_name, file_extension = os.path.splitext(dir_item)

                    # extension included
                    if include_ext:
                        file_list.append(dir_item)

                    # extension excluded
                    else:
                        file_list.append(file_name)

        return sorted(file_list)
    else:
        logger.error("Unable to retrieve file list because no path was specified.")
        return []


def get_folder_list(path_dir):
    folder_list = []

    for dir_item in os.listdir(path_dir):
        if os.path.isdir(os.path.join(path_dir, dir_item)):
            folder_list.append(dir_item)

    return sorted(folder_list)


def get_dict_from_file(path_file, errors_enabled=True):
    if os.path.isfile(path_file):
        output_dict = {}
        with open(path_file, "r") as json_file:
            try:
                file_dict = json.loads(json_file.read())
                output_dict = file_dict
            except ValueError:
                if errors_enabled:
                    logger.error("AM Lib: Retrieving dictionary from file failed for file: {0}".format(path_file))
        return output_dict
    else:
        if errors_enabled:
            logger.error(
                "AM Lib: Retrieving dictionary from file failed because file could not be found: {0}".format(path_file))
        return {}


def get_list_from_dict_from_file(dict_key, path_file):
    # returns a list from a dict from a file, returns an empty list if an error occurs
    dict_from_file = get_dict_from_file(path_file)

    if dict_key in dict_from_file:
        if isinstance(dict_from_file[dict_key], list):
            return dict_from_file[dict_key]
        else:
            logger.error("AM Lib: List '{0}' could not be retrieved from dictionary from file: {1} because the "
                         "dictionary key is not a list.".format(dict_key, path_file))
            return []
    else:
        logger.error("AM Lib: List '{0}' could not be retrieved from dictionary from file: {1} because the dictionary "
                     "key is missing.".format(dict_key, path_file))
        return []


def get_dict_list_from_file(path_file, number_of_lines=1):
    dict_list = []

    lines = read_last_lines_from_file(path_file, number_of_lines)

    for line in lines[-number_of_lines:]:
        try:
            dict_list.append(json.loads(line))
        except ValueError:
            logger.exception("AM Lib: Retrieving dictionary list from file failed for file: {0}".format(path_file))

    if len(dict_list) == 0:
        dict_list.append({})

    return dict_list


def get_last_dict_from_file(path_file):
    return get_dict_list_from_file(path_file, 1)[0]


def save_dict_to_file(input_dict, path_file):
    try:
        with open(path_file, "w") as json_file:
            json_file.write(json.dumps(input_dict))
    except OSError:
        logger.exception("AM Lib: Saving dictionary to file failed: {0}".format(path_file))


def add_dict_to_file(input_dict, path_file):
    try:
        with open(path_file, "a") as json_file:
            json_file.write(json.dumps(input_dict) + "\n")
    except OSError:
        logger.exception("AM Lib: Adding dictionary to file failed: {0}".format(path_file))


def remove_file(path_file, logging_enabled=True):
    try:
        os.remove(path_file)
        if logging_enabled:
            logger.info("AM Lib: Removed file: {0}".format(path_file))
    except OSError:
        logger.exception("AM Lib: Removing file failed: {0}".format(path_file))


def remove_folder(path_folder):
    try:
        for root, dirs, files in os.walk(path_folder, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

        os.rmdir(path_folder)
        logger.info("AM Lib: Removing folder and contents: {0}".format(path_folder))
    except OSError:
        logger.exception("AM Lib: Removing folder and contents failed: {0}".format(path_folder))


def read_last_lines_from_file(path_file, number_of_lines):
    if os.path.isfile(path_file):
        with open(path_file, "rb") as json_file:
            json_file.seek(0, 2)
            bytes_in_file = json_file.tell()
            lines_found, total_bytes_scanned = 0, 0

            while number_of_lines + 1 > lines_found and bytes_in_file > total_bytes_scanned:
                byte_block = min(1024, bytes_in_file - total_bytes_scanned)
                json_file.seek(-(byte_block + total_bytes_scanned), 2)
                total_bytes_scanned += byte_block
                lines_found += json_file.read(1024).count("\n")

            json_file.seek(-total_bytes_scanned, 2)
            log_lines_list = list(json_file.readlines())

        return log_lines_list[-number_of_lines:]
    else:
        logger.error("AM Lib: Reading last {0} lines of: {1} failed because file could not be found.".format(
            number_of_lines, path_file))
        return []


def get_safe_file_system_entity(file_system_entity, maximum_entity_length=260):
    if file_system_entity:
        unsafe_file_characters_list = ["<", ">", ":", "\"", "/", "\\", "|", "?", "*", "&", "%"]

        for unsafe_character in unsafe_file_characters_list:
            file_system_entity = file_system_entity.replace(unsafe_character, "_")

        file_system_entity = file_system_entity[:maximum_entity_length]
        return file_system_entity
    else:
        return ""


def create_folder(path_folder):
    if not os.path.exists(path_folder):
        os.makedirs(path_folder)
    else:
        logger.error("Creating folder failed because folder already exists: {0}".format(path_folder))


def get_path_application_folder_and_executable(input_folder_list, input_sub_folder, input_executable):
    path_folder = ""
    path_executable = ""

    # search in each folder for sub folder
    for folder in input_folder_list:
        if os.path.isdir(folder):
            for sub_folder in get_folder_list(folder):
                if sub_folder.lower() == input_sub_folder:
                    path_folder = os.path.join(folder, sub_folder)
                    break

    # search for executable
    if path_folder:
        for executable_file in get_file_list_with_ext(path_folder):
            if executable_file.lower() == input_executable:
                path_executable = os.path.join(path_folder, executable_file)
                break

    if not path_folder or not path_executable:
        logger.error("Working folder and executable could not be found using folder list: {0}, "
                     "subfolder: {1} and executable: {2}".format(input_folder_list, input_sub_folder, input_executable))

    return path_folder, path_executable
