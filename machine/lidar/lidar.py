#!/usr/bin/python3
import os
import sys
from math import pi
from time import time

import roslibpy
from adafruit_rplidar import RPLidar

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from log import Logger, Level
from message import Header


# Functions and constants

def to_radians(angle: float):
    return pi / 180 * angle


distance_idx = 3
angle_idx = 2
quality_idx = 1

# Initialising ROS-bridge client
client = roslibpy.Ros(host='localhost', port=9090, is_secure=True)
client.run()
# Initialising topics
publisher = roslibpy.Topic(client, '/lidar', 'sensor_msgs/LaserScan')
logger = Logger(roslibpy.Topic(client, '/log_lidar', 'rosgraph_msgs/Log'))
# Setting up LaserScan message
message = {"angle_min": 0, "angle_max": 0, "angle_increment": 0, "time_increment": 0, "scan_time": 0, "range_min": 0,
           "range_max": 0, "ranges": [], "intensities": []}
header = Header("lidar")

# Connecting to lidar
PORT_NAME = '/dev/ttyAMA0'
lidar = RPLidar(None, PORT_NAME, timeout=3)

logger.write_log(Level.INFO, "Start", "Beginning scanning", ["/lidar"])

start = time()

for scan in lidar.iter_measurements():
    end = time()
    scan_time = start - end

    message["angle_min"] = to_radians(min(scan, key=lambda x: x[angle_idx]))
    message["angle_max"] = to_radians(max(scan, key=lambda x: x[angle_idx]))
    message["angle_increment"] = (message["angle_max"] - message["angle_min"]) / len(scan)
    message["scan_time"] = scan_time
    message["time_increment"] = (scan_time / len(scan))
    message["range_min"] = (min(scan, key=lambda x: x[distance_idx]))
    message["range_min"] = (max(scan, key=lambda x: x[distance_idx]))
    message["ranges"] = [measure[distance_idx] / 1000 for measure in scan if
                         message["range_min"] <= measure[distance_idx] <= message["range_max"]]
    message["intensities"] = [measure[quality_idx] for measure in scan]

    publisher.publish(header.stamp(message))

    scan = []
    start = time()

    if not client.is_connected:
        break

logger.write_log(Level.INFO, "End", "Scanning stopped", ["/lidar"])

# Lidar shutdown
lidar.stop()
lidar.disconnect()
# ROS topics shutdown
publisher.unadvertise()
logger.terminate()
# ROS shutdown
client.terminate()
