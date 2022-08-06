import AM_File_System_Lib as F_S_Lib
import os


def get_root_path():
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    folder_list = F_S_Lib.get_folder_list(root_path)
    if "Logging" in folder_list or "Settings" in folder_list:
        return root_path
    else:
        return os.path.dirname(root_path)


def get_path(folder_list):
    server_path = get_root_path()

    if server_path:
        if folder_list[0] in F_S_Lib.get_folder_list(server_path):
            output_path = os.path.join(server_path, folder_list[0])

            if len(folder_list) == 1:
                return output_path
            else:
                for folder in folder_list[1:]:
                    if folder in F_S_Lib.get_folder_list(output_path):
                        output_path = os.path.join(output_path, folder)
                    else:
                        return
                return output_path
