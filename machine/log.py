#!/usr/bin/env python3
import inspect
import os
from enum import Enum

from message import Header


class Level(Enum):
    DEBUG = 1
    INFO = 2
    WARN = 4
    ERROR = 8
    FATAL = 16


class Logger:
    def __init__(self, topic: "roslibpy.Topic"):
        self.logger = topic
        self.header = Header(topic.name + "_log")

    def write_log(self, level: Level, name: str, msg: str, topics: list):
        caller = inspect.stack()[1]
        function = caller.function
        file = os.path.splitext(os.path.basename(caller.filename))[0]
        line = caller.lineno

        log = {"level": level.value, "name": name, "msg": msg, "file": file, "function": function, "line": line,
               "topics": topics}

        self.logger.publish(self.header.stamp(log))

    def terminate(self):
        self.logger.unadvertise()
