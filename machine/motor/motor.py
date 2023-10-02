#!/usr/bin/python3
import os
import sys
from threading import Thread
from time import sleep

import roslibpy
from squaternion import Quaternion

import dcmotor

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from log import Level, Logger
from message import Header

client = roslibpy.Ros(host='localhost', port=9090, is_secure=True)
client.run()

motor1 = dcmotor.DCMotor(6, 5, 12)
motor2 = dcmotor.DCMotor(27, 17, 13)

listener = roslibpy.Topic(client, '/command', 'geometry_msgs/Twist')
publisher = roslibpy.Topic(client, '/pose', 'geometry_msgs/PoseStamped')
logger = Logger(roslibpy.Topic(client, '/log_motors', 'rosgraph_msgs/Log'))

# Pose in termini relativi
pose = {"pose": {"position": {"x": 0, "y": 0, "z": 0},
                 "orientation": {"x": 0, "y": 0, "z": 0, "w": 0}}}
header = Header(frame_id="motor")

linear_unit = 1


def get_distance(power):
    return linear_unit * power


angular_unit = 1


def get_angle(power):
    quat = (Quaternion.from_euler(0, 0, power * angular_unit)).to_dict()
    return quat


def move(direction: int):

    if -100 <= direction <= 100:
        if direction > 0:
            Thread(target=motor1.forward(direction)).start()
            Thread(target=motor2.forward(direction)).start()

        elif direction < 0:
            direction = -direction
            Thread(target=motor1.backwards(direction)).start()
            Thread(target=motor2.backwards(direction)).start()
            direction = -direction

        else:
            logger.write_log(Level.WARN, "Null speed", "Speed set to null, expected not null value", ["/command"])

        pose["pose"]["position"]["x"] += get_distance(direction)

        sleep(1)

        Thread(target=motor1.stop()).start()
        Thread(target=motor2.stop()).start()

        publisher.publish(header.stamp(pose))

    else:
        logger.write_log(Level.ERROR, "Speed out of range",
                         f"Expected speed between 0 and 100, given {direction}. Device di not move.",
                         ["/command"])


def rotate(direction: int):
    global pose

    quat = get_angle(direction)

    if -100 <= direction <= 100:
        if direction > 0:
            Thread(target=motor1.forward(direction)).start()
            Thread(target=motor2.backwards(direction)).start()

        elif direction < 0:
            direction = -direction
            Thread(target=motor1.backwards(direction)).start()
            Thread(target=motor2.forward(direction)).start()

        else:
            logger.write_log(Level.WARN, "Null speed", "Speed set to null, expected not null value", ["/command"])

        pose['pose']['orientation'] = quat

        sleep(1)

        Thread(target=motor1.stop()).start()
        Thread(target=motor2.stop()).start()

        publisher.publish(header.stamp(pose))

    else:
        logger.write_log(Level.ERROR, "Speed out of range",
                         f"Expected speed between 0 and 100, given {direction}. Device di not rotate.",
                         ["/command"])


def movement(message):
    linear = message["linear"]["x"]
    angular = message["angular"]["z"]

    if linear != 0:
        move(linear)

    if angular != 0:
        rotate(angular)


publisher.advertise()
logger.write_log(Level.INFO, "Start", "Session started, motors activated", ["/command", "/pose"])
listener.subscribe(movement)

try:
    while client.is_connected:
        pass

    motor1.stop()
    motor2.stop()
    logger.write_log(Level.INFO, "End", "Session terminated, motors deactivated", ["/command", "/pose"])
    publisher.unadvertise()
    logger.terminate()
    client.terminate()
except KeyboardInterrupt:
    motor1.stop()
    motor2.stop()
    logger.write_log(Level.INFO, "End", "Session terminated, motors deactivated", ["/command", "/pose"])
    publisher.unadvertise()
    logger.terminate()
    client.terminate()
