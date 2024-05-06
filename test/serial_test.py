import serial
import time
import sys

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

def to_data(string_data):
    if PY2:
        return string_data
    else:
        return bytearray(string_data, 'ascii')


def serial_read(expected_length = 1):
    use_sw_timeout = False
    start_time = time.time()
    readed_len = 0
    response = to_data("")
    while True:
        if COM1.timeout:
            # serial.read() says if a timeout is set it may return less characters as requested
            # we should update expected_length by readed_len
            read_bytes = COM1.read(expected_length - readed_len if (expected_length - readed_len) > 0 else 1)
        else:
            read_bytes = COM1.read(expected_length if expected_length > 0 else 1)
        if use_sw_timeout:
            read_duration = time.time() - start_time
        else:
            read_duration = 0
        if (not read_bytes) or (read_duration > COM1.timeout):
            break
        response += read_bytes
        if expected_length >= 0 and len(response) >= expected_length:
            # if the expected number of byte is received consider that the response is done
            # improve performance by avoiding end-of-response detection by timeout
            break
        readed_len += len(read_bytes)
    return response

"""connection test"""
PORT = None
COM1 = serial.Serial(port=PORT, baudrate=9600, bytesize=8, parity='N', stopbits=1, xonxoff=0)
# COM1.open()
print(COM1.isOpen())
if not COM1.isOpen():
    COM1.open()
print(COM1.isOpen())

cmd =0x01030000000AC5CD
cmd_bytes = cmd.to_bytes(8, byteorder='big', signed=False)
print(cmd_bytes)
COM1.write(cmd_bytes)
read_bytes = COM1.read(25)
print('received data: ', read_bytes)

"""read data test"""
# Bytes = 8
# read_bytes = serial_read(Bytes)
# print('received data: ', read_bytes)
# if read_bytes:
#     print('received data: ', read_bytes)


