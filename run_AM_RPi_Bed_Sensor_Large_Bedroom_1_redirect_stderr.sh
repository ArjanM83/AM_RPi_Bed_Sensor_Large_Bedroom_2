#!/bin/bash
# shellcheck disable=SC2164
cd "$(dirname "$0")"

mkdir -p Logging
python /home/pi/AM_RPi_Bed_Sensor_Large_Bedroom_1/AM_RPi_Bed_Sensor_Large_Bedroom_1.py 2>> Logging/stderr_am_rpi_bed_sensor_large_bedroom_1.log