import datetime
from enum import Enum


class StatusMessage(Enum):
    SENDED = 0
    FORBIDDEN = 1
    BADREQUEST = 2
    FLOOD = 3
    NOTSENDED = 4


class Message:
    text = ""
    sending_date = datetime.datetime
    status = StatusMessage(0)
    channel = ""

    def set_message(self, text, sending_date, status, channel):
        self.text = text
        self.sending_date = sending_date
        self.status = status
        self.channel = channel
