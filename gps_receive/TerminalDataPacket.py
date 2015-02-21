__author__ = 'blues'
'''
Packet form example:
GPSDataPacket:
    start_id: 6868
    packet_length: 25
    LAC: 266A
    IMEI: 0358688000000158
    sequence_id: 0001
    protocol_id: 10
    date_time: 0A0C1E0A2E05
    latitude: 027AC839
    longitude: 0C4657C5
    speed: 00
    direction: 01
    MNC: DF
    cell_id: 100000
    phone_status: 006
    end_id: 0D0A
'''


class TerminalDataPacket():
    data_type = -1


class GPSDataPacket(TerminalDataPacket):

    def __init__(self, data_type, start_id, packet_length, LAC, IMEI, sequence_id, protocol_id,
                 date_time, latitude, longitude, speed, direction, MNC, cell_id, phone_status):
        self.data_type = data_type
        self.start_id = start_id
        self.packet_length = packet_length
        self.LAC = LAC
        self.IMEI = IMEI
        self.sequence_id = sequence_id
        self.protocol_id = protocol_id
        self.date_time = date_time
        self.latitude = latitude
        self.longitude = longitude
        self.speed = speed
        self.direction = direction
        self.MNC = MNC
        self.cell_id = cell_id
        self.phone_status = phone_status


class HeartBreakPacket(TerminalDataPacket):
    data_type = 1


class ExceptionPacket(TerminalDataPacket):
    pass
