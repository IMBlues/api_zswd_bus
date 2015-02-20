#! -*- coding:utf-8 -*-
import os
import sys
import struct
import urllib
import time
from gps_settings import *

sys.path.append(PROJECT_DIR_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = 'zq_bus.settings'

from lib.hexadecimal_deal import DataStruct
from bus.models import *
from SocketServer import StreamRequestHandler


class BusStreamRequestHandler(StreamRequestHandler):

    packed_data = str()

    '''
    测试后台输入控制函数
    '''
    @staticmethod
    def debug_log(debug_info):
        now = unicode(time.strftime('%Y-%m-%d-%h-%m-%s', time.localtime(time.time())))
        if GPS_DEBUG:
            if debug_info is not None:
                print now + u":" + debug_info
            else:
                print now + u":no debug info"
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
    判断包类型
    '''
    def judge_data_type(self, raw_data):
        data_type = {
            'ip': 0,
            'gps': 1,
            'heartbreak': 2,
            'heartbreak_return': 3,
            's2c_info_cn': 4,
            's2c_info_en': 5,
            'c2s_info': 6,
            's2c_command': 7,
            'c2s_command': 8,
        }

        form_string = 'B' * len(raw_data)
        try:
            unpacked_data = struct.unpack(form_string, raw_data)
        except Exception as ex:
            self.debug_log(u"Exception during Unpacking data:" + str(ex))



    '''
    数据包封装
    '''
    def repack_data(self, unpacked_data):
        return unpacked_data

    def pack_data(self, data):
        start = DataStruct('bb')
        length = DataStruct('b')
        LAC = DataStruct('h')
        terminal_id = DataStruct('bbbbbbbb')
        info_code = DataStruct('h')
        agreement_code = DataStruct('b')
        datetime = DataStruct('bbbbbb')
        latitude = DataStruct('bbbb')
        longitude = DataStruct('bbbb')
        speed = DataStruct('b')
        direction = DataStruct('bb')
        MNC = DataStruct('b')
        cell_id = DataStruct('h')
        status = DataStruct('bbbb')
        end = DataStruct('bb')
        if len(data) == 0:
            return 0, 0
        if data[0] == 'h' and data[1] == 'h':
            print 'ok'
        else:
            return 0, 0
        if data[2] == '%':
            print 'position_update'
        else:
            print 'live_confirm'
            return 0, 0

        form_string = 'B' * len(data)
        try:
            packed_data = struct.unpack(form_string, data)
        except Exception as ex:
            print "Exception during Unpacking data:", ex
            return 0, 0

        bus_number = str()
        for i in range(5, 13):
            temp_str = str(packed_data[i]/16)+str(packed_data[i]%16)
            bus_number += str(temp_str)

        latitude = packed_data[22] * (256 ** 3) + packed_data[23] * (256 ** 2) + packed_data[24] * 256 + packed_data[25]
        latitude = (latitude + 0.0) / (30000*60)
        longitude = packed_data[26] * (256 ** 3) + packed_data[27] * (256 ** 2) + packed_data[28] * 256 + packed_data[29]
        longitude = (longitude + 0.0) / (30000*60)

#       百度地图API
        transform_url = "http://api.map.baidu.com/geoconv/v1/?coords=" + str(longitude) + \
                        "," + str(latitude) + "&from=1&to=5&ak=7yTvUeESUHB7GTw9Pb9BRv1U"

        print transform_url
        transform_data = urllib.urlopen(transform_url).read()
#        print transform_data
        try:
            transform_data = eval(transform_data)['result'][0]
            latitude = transform_data['y']
            longitude = transform_data['x']
        except Exception as ex:
            print 'Exception after calling API to unpack:', ex
        latitude = float(latitude)
        longitude = float(longitude)

        data = {
            'bus_number': bus_number,
            'latitude': latitude,
            'longitude': longitude,
        }
        print data

        #存储更新坐标数据
        self.save(data)

        #测试坐标数据
        #self.temp_save(data)

        return packed_data

    '''
    数据库存储
    '''
    def save(self, data):
        bus = str()
        try:
            if Bus.objects.filter(number=data['bus_number']):
                bus = Bus.objects.get(number=data['bus_number'])
            else:
                bus = self.register_new_bus(data)
                self.update_bus_coordinate(data, bus)
                self.update_bus_route(data, bus)
            if bus.route:
                self.update_bus_stop(data, bus)
        except:
            pass

    def handle(self):
        while True:
            try:
                raw_data = self.request.recv(1024).strip()
                if len(raw_data) == 0:
                    self.debug_log(u"the data is empty!")
                else:
                    self.debug_log(u"the length of data is %d" + str(len(raw_data)))
                    self.judge_data_type(raw_data)
                    self.packed_data = self.repack_data(raw_data)
            except Exception as ex:
                self.debug_log(u"Exception in receiving:" + str(ex))
                break
