#!/usr/bin/python3
import os
import sys

import roslibpy

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from log import Logger, Level
from message import Header

client = roslibpy.Ros(host='localhost', port=9090, is_secure=True)
client.run()

poses = roslibpy.Topic(client, '/pose', 'geometry_msgs/PoseStamped')
transform = roslibpy.Topic(client, '/tf', 'tf2_msgs/TFMessage')
logger = Logger(roslibpy.Topic(client, "/log_transform", "rosgraph_msgs/Log"))

tf = {"translation": {}, "rotation": {}}
header = Header(frame_id="map")


def get_transform(pose_stamped_msg):
    tf["translation"] = pose_stamped_msg["pose"]["position"]
    tf["rotation"] = pose_stamped_msg["pose"]["orientation"]

    message = header.stamp({"child_frame_id": pose_stamped_msg["header"]["frame_id"], "transform": tf})

    transform.publish(roslibpy.Message({"transforms": [dict(message)]}))


transform.advertise()
poses.subscribe(get_transform)
logger.write_log(Level.INFO, "Start", "Session started", ["/tf", "/pose"])

try:
    while client.is_connected:
        pass

    logger.write_log(Level.INFO, "End", "Session terminated", ["/tf", "/pose"])
    transform.unadvertise()
    logger.terminate()
    client.terminate()
except KeyboardInterrupt:
    logger.write_log(Level.INFO, "End", "Session terminated", ["/tf", "/pose"])
    transform.unadvertise()
    logger.terminate()
    client.terminate()
