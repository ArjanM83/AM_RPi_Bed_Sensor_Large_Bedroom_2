import RPi.GPIO as GPIO
import Libraries.AM_Home_Server_Lib as Home_Server_Lib
import Libraries.AM_Logging_Lib as Logging_Lib
import Libraries.AM_Network_Lib as Network_Lib
import threading
import time


logger = Logging_Lib.get_logger(__name__)


# first wait for working internet connection
Network_Lib.wait_for_working_internet_connection()

# set gpio parameters
pin_dt = 27
pin_sck = 17
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_sck, GPIO.OUT)

# set input parameters
debug_mode = True
value_kg = 20400
send_trigger_for_kg_min = 10
send_trigger_for_kg_max = 200
reset_total_weight_count_after_x_seconds = 1800
reset_cumulative_weight_kg = 10
bed_sensor_name = "bed sensor large bedroom 2"
total_weight_log_object_name = "{0} {1}".format(bed_sensor_name, "Weight")


def trigger(trigger_name):
    Home_Server_Lib.am_tcp_client_external("trigger", {"action_type": "trigger", "trigger_name": trigger_name})


def sensor(name, value, unit=""):
    Home_Server_Lib.am_tcp_client_external("sensor", {"name": name, "value": value, "unit": unit})


def send_alive_message():
    while True:
        trigger("alive notification RPi {0}".format(bed_sensor_name))

        # sleep for a while
        time.sleep(300)


def reset_cumulative_stable_value_difference():
    cumulative_stable_value_kg = 0
    sensor(total_weight_log_object_name, cumulative_stable_value_kg, "kg")
    return cumulative_stable_value_kg


def read_bed_sensor_value():
    temp = 0
    count = 0
    GPIO.setup(pin_dt, GPIO.OUT)
    GPIO.output(pin_dt, 1)
    GPIO.output(pin_sck, 0)
    GPIO.setup(pin_dt, GPIO.IN)

    while GPIO.input(pin_dt) == 1:
        temp = 0
        
    for i in range(24):
        GPIO.output(pin_sck, 1)
        count = count << 1

        GPIO.output(pin_sck, 0)
        if GPIO.input(pin_dt) == 0:
            count = count + 1

    GPIO.output(pin_sck, 1)
    count = count ^ 0x800000
    time.sleep(0.001)
    GPIO.output(pin_sck, 0)
    return count, temp


def monitor_bed_sensor():
    # setup
    value_current = read_bed_sensor_value()[0]
    stable_value_current = 0
    stable_value_previous = 0
    stable_values_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    stable_true_counter = 0
    cumulative_stable_value_kg = reset_cumulative_stable_value_difference()

    while True:
        # init
        value_previous = value_current

        # retrieve current value
        value_current, unused_value_2 = read_bed_sensor_value()
        value_difference = abs(value_current - value_previous)

        # determine if situation is stable: 10 last values that are close to each other
        stable_values_list.append(value_current)
        stable_values_list = stable_values_list[-10:]
        stable = True
        for index in range(0, 9):
            # not stable if any of the last 10 values are missing
            if stable_values_list[index] == 0:
                stable = False
                stable_true_counter = 0
                break
            # not stable if any value is not close enough to the others
            else:
                if abs(stable_values_list[index] - stable_values_list[index + 1]) > (value_kg / 4):
                    stable = False
                    stable_true_counter = 0
                    break

        if stable:
            # increase stable true counter
            if stable_true_counter < 2:
                # counter is 0: not stable
                # counter is 1: stable since 1 measurement
                # counter is 2: stable since 2 measurements
                stable_true_counter += 1
            # update stable values, but only when the change is small, to compensate for drifting,
            # or when a new stable period has been reached
            if value_difference < (value_kg / 10) or stable_true_counter == 1:
                stable_value_previous = stable_value_current
                stable_value_current = value_current

        # new stable situation
        stable_value_difference = 0
        stable_value_difference_kg = 0
        if stable_true_counter == 1 and stable_value_previous:
            stable_value_difference = stable_value_current - stable_value_previous
            # ignore changes smaller than one kilogram
            if abs(stable_value_difference) < value_kg:
                stable_value_difference = 0

        # apply actions
        if stable_true_counter == 1:
            stable_value_difference_kg = float(stable_value_difference)/value_kg
            # stable_value_difference_kg_reporting = int(round(stable_value_difference_kg))

            cumulative_stable_value_kg += stable_value_difference_kg
            # if cumulative weight becomes small or negative: reset to 0
            if cumulative_stable_value_kg < reset_cumulative_weight_kg:
                cumulative_stable_value_kg = 0

            if stable_true_counter == 1:
                # take action when change is within specified boundaries
                if send_trigger_for_kg_min <= abs(stable_value_difference_kg) <= send_trigger_for_kg_max:
                    # send total weight to sensor operator
                    sensor(total_weight_log_object_name, int(round(cumulative_stable_value_kg)), "kg")

                    # send current weight to sensor operator
                    # sensor("{0} Weight Current".format(bed_sensor_name), stable_value_difference_kg_reporting, "kg")

        # debug output formatting
        if debug_mode:
            value_current_str = "{0}{1}".format("          ", value_current)[-10:]
            value_difference_str = "{0}{1}".format("          ", value_difference)[-10:]
            stable_value_current_str = "{0}{1}".format("          ", stable_value_current)[-10:]
            stable_value_difference_str = "{0}{1}".format("          ", stable_value_difference)[-10:]

            if stable_value_difference != 0:
                stable_value_difference_kg_str = "{0} kg".format(stable_value_difference_kg)
            else:
                stable_value_difference_kg_str = "0 kg"

            logger.info("curr: {0}  -  diff: {1}  -  stable: {2} ({3})  -  change: {4} ({5})".format(
                value_current_str, value_difference_str, stable, stable_value_current_str,
                stable_value_difference_str, stable_value_difference_kg_str))

        time.sleep(0.1)


# send alive message to server
# thread_send_alive_message = threading.Thread(target=send_alive_message)
# thread_send_alive_message.setDaemon = True
# thread_send_alive_message.start()


# monitor bed sensor
# thread_monitor_bed_sensor = threading.Thread(target=monitor_bed_sensor)
# thread_monitor_bed_sensor.setDaemon = True
# thread_monitor_bed_sensor.start()
monitor_bed_sensor()