__author__ = 'blues'


class TerminalDataPacket():
    data_type = -1


class GPSDataPacket(TerminalDataPacket):
    data_type = 0


class HeartBreakPacket(TerminalDataPacket):
    data_type = 1


class ExceptionPacket(TerminalDataPacket):
    pass
