from pymodbus.client import ModbusTcpClient
import time
import json
from datetime import datetime


class PLCTag:
    def __init__(self, name, address: int, value):
        self.name = name
        self.address = address
        self.value = value


class BRXPLC:
    def __init__(self, ip_address: str, port: int):
        self.ip_address = ip_address
        self.port = port
        self.client = ModbusTcpClient(ip_address, port)

        self.white_valve = PLCTag('White Valve', 1, False)
        self.red_valve = PLCTag('Red Valve', 2, False)
        self.blue_valve = PLCTag('Blue Valve', 3, False)

        self.conveyor_belt = PLCTag('Conveyor Belt', 4, False)

        self.detect_blue = PLCTag('Detected Blue', 5, False)
        self.detect_red = PLCTag('Detected Red', 6, False)
        self.detect_white = PLCTag('Detected White', 7, False)

        self.color_sensor = PLCTag('Color Sensor', 8, 0)

    def connect(self):
        self.connected = self.client.connect()

        if self.connected:
            print('Connected to BRX PLC.')
        else:
            print('Unable to connect to BRX PLC.')

    def disconnect(self):
        if self.connected:
            print('Disconnecting from BRX PLC...')
            self.client.close()

        print('Disconnected from BRX PLC.')
        self.connected = False

    def read_coils(self, start_coil_addr: int, num_of_coils: int = 1):
        read_result = []
        read_list = []

        #print('Reading {0} coils starting at Modbus address {1}'
        #      .format(num_of_coils, start_coil_addr))

        # There is an offset between the BRXPLC and PyModbus
        # PyModbus starts at 0 while BRXPLC starts at 1
        # Subtract 1 from the Modbus address
        start_coil_addr = start_coil_addr - 1

        read_result = self.client.read_coils(start_coil_addr, num_of_coils)

        # Slice the import results
        result_list = read_result.bits[0:num_of_coils]

        return result_list

    def read_holding_registers(self, start_register_addr: int, num_of_registers: int = 1):
        read_result = []
        read_list = []

        #print('Reading {0} holding registers starting at Modbus address {1}'
        #      .format(num_of_registers, start_register_addr))

        # There is an offset between the BRXPLC and PyModbus
        # PyModbus starts at 0 while BRXPLC starts at 1
        # Subtract 1 from the Modbus address
        start_register_addr = start_register_addr - 1

        read_result = self.client.read_holding_registers(start_register_addr, num_of_registers)

        # Slice the import results
        result_list = read_result.registers[0:num_of_registers]

        return result_list

    def cache_state(self):
        filename = 'data.json'
        state = {}

        state[self.white_valve.name] = self.white_valve.value
        state[self.red_valve.name] = self.red_valve.value
        state[self.blue_valve.name] = self.blue_valve.value

        state[self.conveyor_belt.name] = self.conveyor_belt.value
        state[self.color_sensor.name] = self.color_sensor.value

        state["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        state[self.detect_blue.name] = self.detect_blue.value
        state[self.detect_red.name] = self.detect_red.value
        state[self.detect_white.name] = self.detect_white.value

        with open(filename, 'w') as file:
            json.dump(state, file)

    def loop(self):
        self.connect()

        while True:
            (self.white_valve.value, self.red_valve.value, self.blue_valve.value) = self.read_coils(self.white_valve.address, 3)

            self.conveyor_belt.value = self.read_coils(self.conveyor_belt.address)[0]

            self.color_sensor.value = self.read_holding_registers(self.color_sensor.address)[0]


            (self.detect_blue.value, self.detect_red.value, self.detect_white.value) = self.read_coils(self.detect_blue.address, 3)

            print(self.detect_blue.value, self.detect_red.value, self.detect_white.value)

            self.cache_state()
            time.sleep(1)

        self.disconnect()


def main():
    brx_plc = BRXPLC('192.168.3.6', 502)
    brx_plc.loop()


if __name__ == '__main__':
    main()
