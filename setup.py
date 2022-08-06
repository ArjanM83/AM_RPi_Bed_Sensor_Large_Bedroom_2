import os
import subprocess
import sys


# parameters ###########################################################################################################


CURRENT_CWD = "AM_RPi_Bed_Sensor_Large_Bedroom_2"
TIMEZONE = "Europe/Amsterdam"
SAMBA_FILE_SHARE_PASSWORD = "raspberry"

LINUX_PACKAGES_TO_BE_INSTALLED = [
    "samba samba-common-bin"  # required for creating a samba file share
]

PYTHON_LIBRARIES_TO_BE_INSTALLED = [
    "RPi.GPIO==0.7.0"  # library for utilizing the Raspberry Pi GPIO pins
]


# functions ############################################################################################################


def exec_cmd_visible(shell_cmd_list):
    return subprocess.call(shell_cmd_list)


def exec_cmd_and_wait_for_completion(shell_cmd, path_working_folder=None):
    process = subprocess.Popen(shell_cmd, shell=True, stdout=subprocess.PIPE, cwd=path_working_folder)
    return process.communicate()


def script_is_root():
    user_id = subprocess.Popen("id -u", shell=True, stdout=subprocess.PIPE).communicate()[0]

    if user_id.strip() == "0":
        return True
    else:
        return False


def install_python_module(module_name, module_index, libraries_list):
    print "\n{0}/{1} installing python module: {2}...".format(
        module_index + 1, len(libraries_list), module_name)

    exec_cmd_visible(["sudo", "pip", "install", "{0}".format(module_name)])


def install_linux_package(package_index, package_name):
    print "\n{0}/{1} installing linux package: {2}...".format(
        package_index + 1, len(LINUX_PACKAGES_TO_BE_INSTALLED), package_name)

    if " " in package_name:
        exec_cmd_visible(
            ["sudo", "apt-get", "--assume-yes", "install", package_name.split(" ")[0], package_name.split(" ")[1]])
    else:
        exec_cmd_visible(["sudo", "apt-get", "--assume-yes", "install", package_name])


def create_and_enable_service(service_name, executable_file):
    service_file = "{0}.service".format(service_name)

    print "\nMaking script executable: {0}".format(executable_file)
    exec_cmd_and_wait_for_completion("chmod +x {0}".format(executable_file))

    print "Create service file: {0}".format(service_file)
    service_file_contents = """
    [Unit]
    Description={0}

    [Service]
    ExecStart={1}

    [Install]
    WantedBy=multi-user.target
    """.format(service_name, executable_file)
    exec_cmd_and_wait_for_completion("printf '{0}' > {1}".format(service_file_contents, service_file))

    print "Move service file to /etc/systemd/system/"
    exec_cmd_and_wait_for_completion("sudo mv {0} /etc/systemd/system/".format(service_file))

    print "Enabling service: {0}".format(service_file)
    exec_cmd_and_wait_for_completion("sudo systemctl enable {0}".format(service_file))


def show_end_notes():
    print "\n\nSetup is now complete! Please reboot the system and the door sensor script will start automatically."


# check if script is running with root level permissions ###############################################################


print "\nChecking if script is running with root level permissions..."
if script_is_root():
    print "Root level permissions: OK!"
else:
    print "Root level permissions: Failed!"
    print "Setup aborted! Please restart script using: sudo python setup.py\n"
    sys.exit()


# update raspberry pi image ############################################################################################


check_for_system_updates = raw_input("\nDo you want to check for system updates? (y/n): ")
if check_for_system_updates == "y":
    print "\nChecking if the system needs updates..."
    exec_cmd_visible(["sudo", "apt-get", "update"])
    print "\nUpgrading system components..."
    exec_cmd_visible(["sudo", "apt-get", "upgrade", "-y"])


# check current working directory ######################################################################################


required_cwd = CURRENT_CWD
if os.getcwd().split("/")[-1] != required_cwd:
    print "Setup aborted! Current folder is not: {0}".format(required_cwd)
    sys.exit()


# install packages and libraries #######################################################################################


create_samba_share = raw_input(
    "\nDo you want to create a samba share for sharing the file system with other network devices? (y/n): ")
if create_samba_share == "y":
    # setting an answer to the question of the samba installation
    exec_cmd_and_wait_for_completion(
        "echo 'samba-common samba-common/workgroup string WORKGROUP' | sudo debconf-set-selections")
    exec_cmd_and_wait_for_completion(
        "echo 'samba-common samba-common/dhcp boolean true' | sudo debconf-set-selections")
    exec_cmd_and_wait_for_completion(
        "echo 'samba-common samba-common/do_debconf boolean true' | sudo debconf-set-selections")

# install linux packages
for index, linux_package in enumerate(LINUX_PACKAGES_TO_BE_INSTALLED):
    if linux_package == "samba samba-common-bin":
        if create_samba_share == "y":
            install_linux_package(index, linux_package)
        else:
            print "\n{0}/{1} skipping linux package: {2}...".format(
                index + 1, len(LINUX_PACKAGES_TO_BE_INSTALLED), linux_package)
    else:
        install_linux_package(index, linux_package)

# install python libraries
for index, python_library in enumerate(PYTHON_LIBRARIES_TO_BE_INSTALLED):
    install_python_module(python_library, index, PYTHON_LIBRARIES_TO_BE_INSTALLED)


# set timezone #########################################################################################################


corrent_timezone = raw_input("\nDo you want to set the system's timezeone to {0}? (y/n): ".format(TIMEZONE))
if corrent_timezone == "y":
    print "\nSetting timezone to {0}...".format(TIMEZONE)
    exec_cmd_and_wait_for_completion("sudo ln -fs /usr/share/zoneinfo/{0} /etc/localtime".format(TIMEZONE))
    exec_cmd_and_wait_for_completion("sudo dpkg-reconfigure -f noninteractive tzdata")


# create and enable services to start modules automatically ############################################################


create_and_enable_service(
    "am_rpi_bed_sensor_large_bedroom_2",
    "/home/pi/AM_RPi_Bed_Sensor_Large_Bedroom_2/run_AM_RPi_Bed_Sensor_Large_Bedroom_2_redirect_stderr.sh")


# create samba file share ##############################################################################################


if create_samba_share == "y":
    path_samba_configuration_file = "/etc/samba/smb.conf"

    with open(path_samba_configuration_file) as f:
        content = f.readlines()

    if "[PiShare]" not in str(content):
        exec_cmd_and_wait_for_completion("echo '{0}' >> {1}".format(
            "\n\n"
            "[PiShare]\n"
            "comment=Raspberry Pi Share\n"
            "path=/\n"
            "browseable=Yes\n"
            "writeable=Yes\n"
            "only guest=no\n"
            "create mask=0777\n"
            "directory mask=0777\n"
            "public=no\n",
            path_samba_configuration_file))

    # set password for user: pi
    exec_cmd_and_wait_for_completion("(echo {0}; echo {0}) | sudo smbpasswd -s -a pi".format(SAMBA_FILE_SHARE_PASSWORD))


# end notes ############################################################################################################


show_end_notes()


# reboot ###############################################################################################################


reboot = raw_input("\nDo you want to reboot the system now? (y/n): ")
if reboot == "y":
    exec_cmd_visible(["sudo", "reboot"])
