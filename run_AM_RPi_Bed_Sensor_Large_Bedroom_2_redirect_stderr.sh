#!/bin/bash
# shellcheck disable=SC2164
cd "$(dirname "$0")"

mkdir -p Logging
python2 /home/pi/AM_RPi_Bed_Sensor_Large_Bedroom_2/AM_RPi_Bed_Sensor_Large_Bedroom_2.py 2>> Logging/stderr_am_rpi_bed_sensor_large_bedroom_2.log