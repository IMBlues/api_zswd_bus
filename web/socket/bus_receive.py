# -*-coding:utf-8 -*-
from streamhandler import BusStreamRequestHandler
from SocketServer import ThreadingTCPServer


'''
HOST = '0.0.0.0'
PORT = 8080
BUFSIZ = 1024

address = (HOST, PORT)
tcpSerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpSerSock.bind(address)
tcpSerSock.listen(5)
'''


class DataStruct:

    data_type = ''

    def __init__(self, temp_type):
        data_type = temp_type

    @staticmethod
    def update_bus_coordinate(data, bus):
        coordinate = Coordinate(longitude=data['longitude'],
        latitude=data['latitude'], bus_number=data['bus_number'])
        coordinate.save()
        bus.coordinate = coordinate
        bus.save()

    @staticmethod
    def update_bus_stop(data, bus):

        MAX_LENGTH = 21000000

        stops = Stop.objects.filter(route=bus.route)
        distance = MAX_LENGTH
        for stop in stops:
            temp_distance = ((bus.coordinate.latitude - stop.latitude)**2 +
                             (bus.coordinate.longitude - stop.longitude)**2)
            if distance < temp_distance:
                bus.stop = stop
        bus.save()

    @staticmethod
    def update_bus_route(data, bus):
        ERROR_VALUE =0.000006

        routes = Route.objects.all()
        for r in routes:
            if (abs(r.special_coordinate.latitude - data['latitude'])<ERROR_VALUE)\
                and (abs(r.special_coordinate.longitude -
                data['longitude']<ERROR_VALUE)):

                bus.route = r
        bus.save()

    @staticmethod
    def datasave(data):
        try:
            try:
                bus = Bus.objects.get(number= data['bus_number'])
            except:
                route = Route.objects.get(id=1)
                bus = Bus(number = data['bus_number'], route=route)
            DataStruct.update_bus_coordinate(data, bus)
            DataStruct.update_bus_route(data, bus)
            DataStruct.update_bus_stop(data, bus)
            print 'update success'
        except:
            pass

if __name__ == '__main__':
    HOST = '0.0.0.0'
    PORT = 12333 
    BUFSIZ = 1024
    ADDR = (HOST, PORT)
    ThreadingTCPServer.allow_reuse_address = True
    server = ThreadingTCPServer(ADDR, BusStreamRequestHandler)
    server.serve_forever()
