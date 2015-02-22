#! -*- coding:utf-8 -*-
import os
import sys
import struct
import urllib
import time
from gps_settings import *

sys.path.append(PROJECT_DIR_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = 'zq_bus.settings'

from bus.models import *
from SocketServer import StreamRequestHandler
from TerminalDataPacket import *


class BusStreamRequestHandler(StreamRequestHandler):

    packed_data = TerminalDataPacket()
    unpacked_data = ()
    data_type = -1

    '''
    测试后台输入控制函数
    '''
    @staticmethod
    def debug_log(debug_info):
        now = unicode(time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime(time.time())))
        if GPS_DEBUG:
            if debug_info is not None:
                print now + u":" + debug_info
            else:
                print now + u":sorry,no debug info..."
        else:
            return

    @staticmethod
    def temp_save(data):
        test_coordinate = TestCoordinate(latitude=data['latitude'], longitude=data['longitude'])
        test_coordinate.save()
        print 'time:', test_coordinate.time, '; lat:', test_coordinate.latitude, '; lont:', test_coordinate.longitude

    '''
    更新车辆坐标
    '''
    @staticmethod
    def update_bus_coordinate(data, bus):
        coordinate = Coordinate(longitude=data['longitude'],
                                latitude=data['latitude'], bus_number=data['bus_number'])
        coordinate.save()
        bus.coordinate = coordinate
        bus.save()

    @staticmethod
    def register_new_bus(data):

        '''
        if SpecialCoordinate.objects.filter(route_name='TEST'):
            special_coordinate = SpecialCoordinate.objects.get(route_name='TEST')
        else:
            special_coordinate = SpecialCoordinate(longitude=114.332141, latitude=30.520142, route_name='TEST')
            special_coordinate.save()

        if Route.objects.filter(final_stop="TEST2"):
            route = Route.objects.get(departure_stop='TEST1', final_stop='TEST2',special_coordinate = special_coordinate)
        else:
            route = Route.objects.get(final_stop='TEST2')
            route.save()

        if Stop.objects.filter(name='TEST'):
            stop = Stop.objects.get(name='TEST')
        else:
            stop = Stop(name='TEST', route=route, longitude=114.233333, latitude=30.520212)
            stop.save()
        '''

        try:
            coordinate = Coordinate.objects.all()[0]
        except:
            coordinate = Coordinate(longitude=114.233333, latitude=30.5312333)
            coordinate.save()
        route = Route.objects.all()[0]
        stop = Stop.objects.filter(route=route)[0]
        bus = Bus(route=route, stop=stop, coordinate=coordinate, number=data['bus_number'])
        bus.save()
        return bus

    '''
    更新车站
    '''
    @staticmethod
    def update_bus_stop(data, bus):
        stops = Stop.objects.filter(route=bus.route)
        distance = MAX_LENGTH
        for stop in stops:
            temp_distance = ((bus.coordinate.latitude - stop.latitude)**2 +
                             (bus.coordinate.longitude - stop.longitude)**2)
            if distance < temp_distance:
                bus.stop = stop
        bus.save()

    '''
    更新车辆路线
    '''
    @staticmethod
    def update_bus_route(data, bus):

        routes = Route.objects.all()
        for r in routes:
            if (abs(r.special_coordinate.latitude - data['latitude']) < ERROR_VALUE) \
                    and (abs(r.special_coordinate.longitude - data['longitude'] < ERROR_VALUE)):

                bus.route = r
        bus.save()

    '''
    数据流处理主调用函数
    '''
    def handle(self):
        while True:
            try:
                raw_data = self.request.recv(1024).strip()
                if len(raw_data) == 0:
                    self.debug_log(u"the data is empty!")
                else:
                    self.debug_log(u"the length of data is " + str(len(raw_data)))
                    self.judge_and_pack(raw_data)
            except Exception as ex:
                self.debug_log(u"Exception in receiving:" + str(ex))
                break

    '''
    判断包类型与数据包封装
    '''
    def judge_and_pack(self, raw_data):
        global unpacked_data
        global packed_data

        #类型判断句柄字典
        data_type_handler = {
            'gps': (0x6868, 0x10),
            'heartbreak': (0x6868, 0x1A),
            'ip': (0x6868, 0x1B),
            'command': (0x6868, 0x1C)
        }

        #分割成以字节为单位的元组
        form_string = 'B' * len(raw_data)
        try:
            unpacked_data = struct.unpack(form_string, raw_data)
        except Exception as ex:
            self.debug_log(u"Exception during Unpacking data:" + str(ex))

        #获取数据包类型判断句柄
        self.debug_log(str(unpacked_data[0:2]))
        start_id = hex(unpacked_data[0:2])
        protocol_id = hex(unpacked_data[15:16])
        judge_handler = (start_id, protocol_id)

        #获取IMEI号（车辆标识）
        IMEI = str()
        for i in range(5, 13):
            temp_str = str(unpacked_data[i]/16)+str(unpacked_data[i] % 16)
            IMEI += str(temp_str)

        #数据包为GPS数据
        if judge_handler == data_type_handler['gps']:
            self.debug_log(u"the packet is GPS Data")
            end_id = hex(unpacked_data[40:42])
            if end_id == 0x0D0A:
                #坐标转换
                latitude = (unpacked_data[22] * (256 ** 3) + unpacked_data[23] * (256 ** 2) +
                            unpacked_data[24] * 256 + unpacked_data[25])
                latitude = (latitude + 0.0) / (30000*60)
                longitude = (unpacked_data[26] * (256 ** 3) + unpacked_data[27] * (256 ** 2) +
                             unpacked_data[28] * 256 + unpacked_data[29])
                longitude = (longitude + 0.0) / (30000*60)

                #百度地图API
                transform_url = "http://api.map.baidu.com/geoconv/v1/?coords=" + str(longitude) + \
                                "," + str(latitude) + "&from=1&to=5&ak=7yTvUeESUHB7GTw9Pb9BRv1U"

                transform_data = urllib.urlopen(transform_url).read()
                try:
                    transform_data = eval(transform_data)['result'][0]
                    latitude = transform_data['y']
                    longitude = transform_data['x']
                except Exception as ex:
                    self.debug_log(u"Exception after calling API to unpack:" + str(ex))

                latitude = float(latitude)
                longitude = float(longitude)

                packed_data = GPSDataPacket(0, unpacked_data[2:3], hex(unpacked_data[3:5]),
                                            IMEI, unpacked_data[13:15], protocol_id, unpacked_data[16:22], latitude,
                                            longitude, unpacked_data[30:31], unpacked_data[31:33], unpacked_data[33:34],
                                            hex(unpacked_data[34:36]), unpacked_data[36:40])
                self.debug_log(u"have packed the GPSData!")

                #调用数据存储
                data_for_app = {
                    'bus_number': packed_data.IMEI,
                    'latitude': packed_data.latitude,
                    'longitude': packed_data.longitude,
                }
                self.save(data_for_app)
                self.debug_log(u"have packed the GPSData for app!")
            else:
                self.debug_log(u"the GPSData packet is not complete,and it will be discarded")

        #数据包为心跳包
        elif judge_handler == data_type_handler['heartbreak']:
            self.debug_log(u"the packet is heartbreak Data")
            content_length = unpacked_data[2:3]
            if content_length >= 20:
                packet_length = content_length + 3 + 2
                end_id = unpacked_data[packet_length - 3:packet_length - 1]
                if end_id == 0x0D0A:
                    numberof_satellite = unpacked_data[17:18]
                    signal_to_noise_ratio = unpacked_data[18:18+numberof_satellite]
                    packed_data = HeartBreakPacket(1, content_length, unpacked_data[3:4],
                                                   unpacked_data[4:5], IMEI, unpacked_data[13:15],
                                                   protocol_id, unpacked_data[16:17], numberof_satellite,
                                                   signal_to_noise_ratio)
                    self.debug_log(u"have packed the HeartBreakData, and ready to send back")

                    #心跳包应答
                    values = (0x54, 0x68, 0x1A, 0x0D, 0x0A)
                    s = struct.Struct('BBBBB')
                    return_data = s.pack(*values)
                    self.debug_log(u"the return data is" + str(values))

                    self.request.send(return_data)
                    self.debug_log(u"heartbreak data has been send back successfully!")
                else:
                    self.debug_log(u"the heartbreak packet is not complete, and it will be"
                                   u"discarded")
            else:
                self.debug_log(u"the heartbreak packet is too short!")

        #数据包为IP请求包
        elif judge_handler == data_type_handler['ip']:
            self.debug_log(u"the packet is ip Data")
            pass

        #数据包为指令包
        elif judge_handler == data_type_handler['command']:
            self.debug_log(u"the packet is command Data")
            pass
        else:
            self.debug_log(u"Unknown data type!")

    '''
    数据库存储
    '''
    def save(self, data):
        try:
            if Bus.objects.filter(number=data['bus_number']):
                bus = Bus.objects.get(number=data['bus_number'])
            else:
                bus = self.register_new_bus(data)
                self.update_bus_coordinate(data, bus)
                self.update_bus_route(data, bus)
            if bus.route:
                self.update_bus_stop(data, bus)
        except Exception as ex:
            self.debug_log(u"Exception during save GPSData into DB:" + str(ex))