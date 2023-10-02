import roslibpy
from roslibpy import Message, Time


class Header:
    def __init__(self, frame_id: str, sequence_start: int = 0) -> None:
        self.frame_id = frame_id
        self.seq = sequence_start
        self.mem = {}

    def stamp(self, message: dict, timestamp=None) -> Message:
        if timestamp is None:
            timestamp = Time.now()
        stamp = {"header": roslibpy.Header(seq=self.seq, stamp=timestamp, frame_id=self.frame_id)}

        self.seq += 1

        stamp.update(message)

        return Message(stamp)

    def set_frame(self, frame_id: str, sequence_start: int = 0):
        if frame_id in self.mem:
            self.frame_id = frame_id
            self.seq = self.mem
        else:
            self.mem[self.frame_id] = self.seq
            self.frame_id = frame_id
            self.seq = sequence_start

    def reset(self, sequence_start: int = 0):
        self.seq = sequence_start
