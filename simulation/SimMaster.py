
""" simulate the Modbus Master """

import sys
import serial

from defines import READ_HOLDING_REGISTERS, WRITE_SINGLE_COIL, READ_COILS
import ModbusSerial
import Modbus
from exceptions import ModbusError

PORT = 'COM1'


def main():
    """main"""
    try:
        #Connect to the slave
        serial_ = serial.Serial(port=PORT, baudrate=9600, bytesize=8, stopbits=1, parity='E')
        master = ModbusSerial.RtuMaster(serial=serial_)
        master.set_timeout(5.0)

        slave = None
        starting_address = None
        quantity = None
        output_value = None
        function_code = None

        print('example: read_coils, read_holding_registers, write_single_coil...\n'
              'read_coils slave_id starting_address quantity\n'
              'read_holding_registers slave_id starting_address quantity\n'
              'write_single_coil slave_id starting_address output_value\n'
              '')

        while True:
            cmd = sys.stdin.readline()
            args = cmd.split(' ')

            if cmd.find('quit') == 0:
                sys.stdout.write('bye-bye\r\n')
                break
            elif args[0].lower() == 'READ_COILS'.lower():
                function_code = READ_COILS
                slave = int(args[1])
                starting_address = int(args[2])
                quantity = int(args[3])
            elif args[0].lower() == 'READ_HOLDING_REGISTERS'.lower():
                function_code = READ_HOLDING_REGISTERS
                slave = int(args[1])
                starting_address = int(args[2])
                quantity = int(args[3])
            elif args[0].lower() == 'WRITE_SINGLE_COIL'.lower():
                function_code = WRITE_SINGLE_COIL
                slave = int(args[1])
                starting_address = int(args[2])
                output_value = int(args[3])

            else:
                sys.stdout.write("unknown command %s\r\n" % (args[0]))
                continue

            response = master.execute(slave_id=slave, function_code=function_code,
                                      starting_address=starting_address, quantity=quantity,
                                      output_value=output_value)
            print(response)

    except ModbusError as exc:
        pass

if __name__ == "__main__":
    main()
