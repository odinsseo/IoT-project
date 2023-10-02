#!/usr/bin/python3
import os
import sys
from math import tan, pi
from time import sleep

import cv2
import numpy as np
import roslibpy

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from message import Header
from log import Logger, Level

image_width = 640
image_height = 480
cx = image_width / 2.0
cy = image_height / 2.0
fx = image_width / (
        2.0 * tan(70.0 * pi / 360.0))
fy = fx

client = roslibpy.Ros(host='localhost', port=9090, is_secure=True)
client.run()

images = roslibpy.Topic(client, '/camera', 'sensor_msgs/CompressedImage')
info = roslibpy.Topic(client, '/camera_info', 'sensor_msgs/CameraInfo')
logger = Logger(roslibpy.Topic(client, "/log_camera", "rosgraph_msgs/Log"))

message = {"format": "jpeg", "data": []}
camera_info = {"width": image_width,
               "height": image_height,
               "distortion_model": '',
               "K": [fx, 0, cx, 0, fy, cy, 0, 0, 1],
               "D": [],
               "R": [1.0, 0, 0, 0, 1.0, 0, 0, 0, 1.0],
               "P": [fx, 0, cx, 0, 0, fy, cy, 0, 0, 0, 1.0, 0],
               "binning_x": 0,
               "binning_y": 0,
               "roi": {
                   "x_offset": 0,
                   "y_offset": 0,
                   "height": image_height,
                   "width": image_width,
                   "do_rectify": False
               }}
header_image = Header("camera")
header_info = Header("camera")

vs = cv2.VideoCapture('/dev/video0', cv2.CAP_V4L)
vs.set(cv2.CAP_PROP_FRAME_WIDTH, image_width)
vs.set(cv2.CAP_PROP_FRAME_HEIGHT, image_height)
logger.write_log(Level.INFO, "Start", "Camera recording started", ["/camera", "/camera_info"])

info.publish(header_info.stamp(camera_info))

while client.is_connected:
    frame = vs.read()[1]
    now = roslibpy.Time.now()
    serialized = np.array(cv2.imencode('.jpg', frame)[1])
    serialized = (serialized.flatten()).tolist()
    message["data"] = serialized
    images.publish(header_image.stamp(message, now))
    info.publish(header_info.stamp(camera_info, now))
    logger.write_log(Level.INFO, "Image sent", f"Image of shape {frame.shape} has been sent",
                     ["/camera", "/camera_info"])
    sleep(0.042)

vs.release()
logger.write_log(Level.INFO, "Stop", "Recording has stopped", ["/camera", "/camera_info"])
images.unadvertise()
logger.terminate()
client.terminate()
