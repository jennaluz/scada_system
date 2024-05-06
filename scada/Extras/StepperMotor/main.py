from enum import IntEnum
from pymodbus.client import ModbusTcpClient
import json
import time


# An ENUM to describe whether to read or write to a Modbus address
class AddressType(IntEnum):
    read = 0
    write = 1


# Group together info about a Modbus address, relating to a PLC input/output
class PLCTag:
    def __init__(self, name: str, address: int, address_type: AddressType, value):
        self.name = name
        self.address = address
        self.address_type = type
        self.value = value


# Initialize and interact with a ClickPLC
class ClickPLC:
    def __init__(self, ip_address: str, port: int):
        self.ip_address = ip_address
        self.port = port
        self.client = ModbusTcpClient(ip_address, port)

        self.e_stop = PLCTag('Emergency Stop Button', 16385, AddressType.read, None);
        self.in_hand = PLCTag('Selector in Hand', 16386, AddressType.read, None)
        self.in_auto = PLCTag('Selector in Auto', 16387, AddressType.read, None)

        self.motor_pulse = PLCTag('Stepper Motor Pulse', 16388, AddressType.write, None)
        self.motor_dir = PLCTag('Stepper Motor Direction', 16389, AddressType.write, None)
        self.motor_ena = PLCTag('Stepper Motor Enable', 16390, AddressType.write, None)

        self.hmi_dir_cw = PLCTag('HMI Stepper Motor Clockwise', 16488, AddressType.read, None)
        self.hmi_dir_ccw = PLCTag('HMI Stepper Motor Counterclockwise', 16489, AddressType.read, None)

        self.hmi_e_stop_lamp = PLCTag('HMI Emergency Stop Bit Lamp', 16485, AddressType.write, None)
        self.hmi_in_hand_lamp = PLCTag('HMI In Hand Bit Lamp', 16486, AddressType.write, None)
        self.hmi_in_auto_lamp = PLCTag('HMI In Auto Bit Lamp', 16487, AddressType.write, None)

        self.hmi_dir_cw_lamp = PLCTag('HMI Stepper Motor Clockwise Bit Lamp', 16490, AddressType.write, None)
        self.hmi_dir_ccw_lamp = PLCTag('HMI Stepper Motor Counterclockwise Bit Lamp', 16491, AddressType.write, None)

    # Attempt to connect to the ClickPLC
    def connect(self):
        print('Connecting to Click PLC...')
        self.connected = self.client.connect()

        if self.connected:
            print('Connected to Click PLC.')

    # Disconnect from the ClickPLC
    def disconnect(self):
        if self.connected:
            print('Disconnecting to Click PLC...')
            self.client.close()

        print('Disconnected from Click PLC.')
        self.connected = False

    # Attempt to read from Modbus address(es)
    def read_coils(self, start_coil_addr: int, num_of_coils: int = 1):
        read_result = []
        result_list = []

        print('Reading {0} coils starting at Modbus address {1}'
              .format(num_of_coils, start_coil_addr))

        # There is an offset between the ClickPLC and PyModbus
        # PyModbus starts at 0 while ClickPLC starts at 1
        # Subtract 1 from the Modbus address
        start_coil_addr = start_coil_addr - 1

        read_result = self.client.read_coils(start_coil_addr, num_of_coils)

        # Slice the import results
        result_list = read_result.bits[0:num_of_coils]

        return result_list

    def write_coil(self, coil_addr: int, value):
        print('Writing {0} to Modbus address {1}'.format(value, coil_addr))

        # There is an offset between the ClickPLC and PyModbus
        # PyModbus starts at 0 while ClickPLC starts at 1
        # Subtract 1 from the Modbus address
        coil_addr = coil_addr - 1

        self.client.write_coil(coil_addr, value)

    def loop(self):
        while True:
            (self.e_stop.value, self.in_hand.value, self.in_auto.value) = self.read_coils(self.e_stop.address, 3)

            # The EStop and Motor Enable are active low
            if (self.e_stop.value is False):
                # The EStop button is pressed
                # Stop the stepper motor from running
                self.write_coil(self.motor_pulse.address, True)
                self.write_coil(self.motor_ena.address, True)

                self.write_coil(self.hmi_in_hand_lamp.address, False)
                self.write_coil(self.hmi_in_auto_lamp.address, False)
            else:
                # The EStop button is not pressed
                self.write_coil(self.motor_ena.address, False)
                self.write_coil(self.hmi_in_hand_lamp.address, self.in_hand.value)
                self.write_coil(self.hmi_in_auto_lamp.address, self.in_auto.value)

            # Turn the stepper motor clockwise
            if self.in_auto.value is True:
                self.write_coil(motor_dir.address, False)

                self.write_coil(self.motor_pulse.address, True)
                time.sleep(0.001)
                self.write_coil(self.motor_pulse.address, False)
                time.sleep(0.005)

            # Listen for HMI input
            if self.in_hand.value is True:
                (self.hmi_dir_cw.value, self.hmi_dir_ccw.value) = self.read_coils(self.hmi_dir_cw.address, 2)

                if self.hmi_dir_cw.value is True:
                    self.write_coil(self.motor_dir.address, False)

                    self.write_coil(self.motor_pulse.address, True)
                    time.sleep(0.001)
                    self.write_coil(self.motor_pulse.address, False)
                    time.sleep(0.005)

                    # Write the value if the EStop button is not pressed
                    if self.e_stop.value is True:
                        self.write_coil(self.hmi_dir_cw_lamp.address, True)
                else:
                    self.write_coil(self.hmi_dir_cw_lamp.address, False)

                if self.hmi_dir_ccw.value is True:
                    self.write_coil(self.motor_dir.address, True)

                    self.write_coil(self.motor_pulse.address, True)
                    time.sleep(0.001)
                    self.write_coil(self.motor_pulse.address, False)
                    time.sleep(0.005)

                    # Write the value if the EStop button is not pressed
                    if self.e_stop.value is True:
                        self.write_coil(self.hmi_dir_ccw_lamp.address, True)
                else:
                    self.write_coil(self.hmi_dir_ccw_lamp.address, False)

        self.disconnect()


def main():
    click_plc = ClickPLC('192.168.3.10', 502)
    click_plc.connect()
    click_plc.loop()


if __name__ == '__main__':
    main()
