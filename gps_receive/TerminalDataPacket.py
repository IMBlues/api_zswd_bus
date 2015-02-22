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

    def __init__(self, data_type, packet_length, LAC, IMEI, sequence_id, protocol_id,
                 date_time, latitude, longitude, speed, direction, MNC, cell_id, phone_status):
        self.data_type = data_type
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

    def __init__(self, data_type, content_length, voltage_strength, GSM_signal_strength,
                 IMEI, sequence_id, protocol_id, locator_status, numberof_satellite,
                 signal_to_noise_ratio):
        self.data_type = data_type
        self.content_length = content_length
        self.voltage_strength = voltage_strength
        self.GSM_signal_strength = GSM_signal_strength
        self.IMEI = IMEI
        self.sequence_id = sequence_id
        self.protocol_id = protocol_id
        self.locator_status = locator_status
        self.numberof_satellite = numberof_satellite
        self.signal_to_noise_ratio = signal_to_noise_ratio


class ExceptionPacket(TerminalDataPacket):
    pass
