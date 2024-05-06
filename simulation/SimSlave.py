
""" simulate the Modbus Slave """

import sys
import serial

from defines import COILS, HOLDING_REGISTERS
import ModbusSerial
import Modbus


PORT = 'COM2'   # slave port


def main():
    """main"""
    # Create the server
    server = ModbusSerial.RtuServer(serial.Serial(PORT))
    try:
        server.start()
        # add modbus slave
        slave = server.add_slave(1)
        # add coils and holding registers
        slave.add_block('1', COILS, 0, 10)
        slave.add_block('3', HOLDING_REGISTERS, 10, 10)

        print('example: set_values to change the data in coils and registers, get_values to ...\n'
              'set_values slave block_type starting_address values...\n'
              'get_values slave block_type starting_address quantity\n'
              'enter quit to exit!\n')

        while True:
            cmd = sys.stdin.readline()
            args = cmd.split(' ')

            if cmd.find('quit') == 0:
                sys.stdout.write('bye-bye\r\n')
                break

            elif args[0] == 'add_slave':
                slave_id = int(args[1])
                server.add_slave(slave_id)
                sys.stdout.write('done: slave %d added\r\n' % slave_id)

            elif args[0] == 'add_block':
                slave_id = int(args[1])
                name = args[2]
                block_type = int(args[3])
                starting_address = int(args[4])
                length = int(args[5])
                slave = server.get_slave(slave_id)
                slave.add_block(name, block_type, starting_address, length)
                sys.stdout.write('done: block %s added\r\n' % (name))

            elif args[0] == 'set_values':
                slave_id = int(args[1])
                name = args[2]
                address = int(args[3])
                values = []
                for val in args[4:]:
                    values.append(int(val))
                slave = server.get_slave(slave_id)
                slave.set_values(name, address, values)
                values = slave.get_values(name, address, len(values))
                sys.stdout.write('done: values written: %s\r\n' % (str(values)))

            elif args[0] == 'get_values':
                slave_id = int(args[1])
                name = args[2]
                address = int(args[3])
                length = int(args[4])
                slave = server.get_slave(slave_id)
                values = slave.get_values(name, address, length)
                sys.stdout.write('done: values read: %s\r\n' % (str(values)))

            else:
                sys.stdout.write("unknown command %s\r\n" % (args[0]))
    finally:
        server.stop()

if __name__ == "__main__":
    main()