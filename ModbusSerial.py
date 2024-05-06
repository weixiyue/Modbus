from Modbus import ModbusMaster, Query, DataBank, ModbusServer
from exceptions import *
import utils

# import serial
import struct
from typing import Any
import time

class RtuQuery(Query):
    def __init__(self):
        """Constructor"""
        super(RtuQuery, self).__init__()
        self._request_address = 0
        self._response_address = 0

    def build_request(self, pdu, slave):
        """Add the Modbus RTU part to the request"""
        self._request_address = slave
        if (self._request_address < 0) or (self._request_address > 255):
            raise InvalidArgumentError("Invalid address {0}".format(self._request_address))
        data = struct.pack(">B", self._request_address) + pdu
        crc = struct.pack(">H", utils.calculate_crc(data))
        return data + crc

    def parse_response(self, response):
        """Extract the pdu from the Modbus RTU response"""
        if len(response) < 3:
            raise ModbusInvalidResponseError("Response length is invalid {0}".format(len(response)))

        (self._response_address, ) = struct.unpack(">B", response[0:1])
        if self._request_address != self._response_address:
            raise ModbusInvalidResponseError(
                "Response address {0} is different from request address {1}".format(
                    self._response_address, self._request_address
                )
            )
        (crc, ) = struct.unpack(">H", response[-2:])
        if crc != utils.calculate_crc(response[:-2]):
            raise ModbusInvalidResponseError("Invalid CRC in response")

        return response[1:-2]

    def parse_request(self, request):
        """Extract the pdu from the Modbus RTU request"""
        if len(request) < 3:
            raise ModbusInvalidRequestError("Request length is invalid {0}".format(len(request)))

        (self._request_address, ) = struct.unpack(">B", request[0:1])

        (crc, ) = struct.unpack(">H", request[-2:])
        if crc != utils.calculate_crc(request[:-2]):
            raise ModbusInvalidRequestError("Invalid CRC in request")

        return self._request_address, request[1:-2]

    def build_response(self, response_pdu):
        """Build the response"""
        self._response_address = self._request_address
        data = struct.pack(">B", self._response_address) + response_pdu
        crc = struct.pack(">H", utils.calculate_crc(data))
        return data + crc


class RtuMaster(ModbusMaster):
    """Subclass of ModbusMaster. Implements the Modbus RTU MAC layer"""

    def __init__(self, serial,  delay=0.05, **kwargs: Any):
        # self._serial = serial.Serial(port=serial_port,
        #                              baudrate=baud_rate,
        #                              bytesize=byte_size,
        #                              parity=parity,
        #                              stopbits=stop_bits,
        #                              xonxoff=0)  # 创建串口对象
        self._serial = serial
        self.use_sw_timeout = False
        super(RtuMaster, self).__init__(response_timeout=self._serial.timeout, delay=delay)


        interchar_multiplier = 1.5
        interframe_multiplier = 3.5
        self._t0 = utils.calculate_rtu_inter_char(self._serial.baudrate)
        self._serial.inter_byte_timeout = interchar_multiplier * self._t0
        self.set_timeout(interframe_multiplier * self._t0)

        # self._bandrate = band_rate
        # self._bytesize = byte_size
        # self._parity = parity
        # self.stopbits = stop_bits

    def _do_connect(self):
        """Open the given serial port if not already opened"""
        if not self._serial.is_open:
            self._serial.open()

    def _do_disconnect(self):
        """Close the serial port if still opened"""
        if self._serial.is_open:
            self._serial.close()
            # call_hooks("modbus_rtu.RtuMaster.after_close", (self,))
            return True

    def set_timeout(self, timeout_in_sec, use_sw_timeout=False):
        """Change the timeout value"""
        ModbusMaster.set_timeout(self, timeout_in_sec)
        self._serial.timeout = timeout_in_sec
        # Use software based timeout in case the timeout functionality provided by the serial port is unreliable
        self.use_sw_timeout = use_sw_timeout

    def _send(self, request):
        """Send request to the slave"""
        self._serial.reset_input_buffer()
        self._serial.reset_output_buffer()

        self._serial.write(request)
        self._serial.flush()


    def _recv(self, expected_length=-1):
        """Receive the response from the slave"""
        response = utils.to_data("")
        start_time = time.time() if self.use_sw_timeout else 0
        readed_len = 0
        while True:
            if self._serial.timeout:
                read_bytes = self._serial.read(expected_length - readed_len
                                               if (expected_length - readed_len) > 0 else 1)
            else:
                read_bytes = self._serial.read(expected_length if expected_length > 0 else 1)
            if self.use_sw_timeout:
                read_duration = time.time() - start_time
            else:
                read_duration = 0
            if (not read_bytes) or (read_duration > self._serial.timeout):
                break
            response += read_bytes

            if 0 <= expected_length <= len(response):
                break
            readed_len += len(read_bytes)
        return response


    def _make_query(self):
        """Returns an instance of a Query subclass implementing the modbus RTU protocol"""
        return RtuQuery()


class RtuServer(ModbusServer):
    """ RTU通信方式下的ModbusServer子类 """
    _timeout = 0
    def __init__(self, serial, databank=None, error_on_missing_slave=True, **kwargs):
        interframe_multiplier = kwargs.pop('interframe_multiplier', 3.5)
        interchar_multiplier = kwargs.pop('interchar_multiplier', 1.5)

        databank = databank if databank else DataBank(error_on_missing_slave=error_on_missing_slave)
        super(RtuServer, self).__init__(databank)

        self._serial = serial

        self._t0 = utils.calculate_rtu_inter_char(self._serial.baudrate)
        self._serial.inter_byte_timeout = interchar_multiplier * self._t0
        self.set_timeout(interframe_multiplier * self._t0)

        self._block_on_first_byte = False

    def close(self):
        """close the serial communication"""
        if self._serial.is_open:
            # call_hooks("modbus_rtu.RtuServer.before_close", (self, ))
            self._serial.close()
            # call_hooks("modbus_rtu.RtuServer.after_close", (self, ))

    def set_timeout(self, timeout):
        self._timeout = timeout
        self._serial.timeout = timeout

    def get_timeout(self):
        return self._timeout

    def __del__(self):
        """Destructor"""
        self.close()

    def _make_query(self):
        """Returns an instance of a Query subclass implementing the modbus RTU protocol"""
        return RtuQuery()

    def start(self):
        """Allow the server thread to block on first byte"""
        self._block_on_first_byte = True
        super(RtuServer, self).start()

    def stop(self):
        """Force the server thread to exit"""
        self._block_on_first_byte = False
        if self._serial.is_open:
            # 阻塞停止读取报文帧
            self._serial.cancel_read()
        super(RtuServer, self).stop()

    def _do_init(self):
        """initialize the serial connection"""
        if not self._serial.is_open:
            # call_hooks("modbus_rtu.RtuServer.before_open", (self, ))
            self._serial.open()
            # call_hooks("modbus_rtu.RtuServer.after_open", (self, ))

    def _do_exit(self):
        """close the serial connection"""
        self.close()

    def _do_run(self):
        """main function of the server"""
        try:
            # check the status of every socket
            request = utils.to_data('')
            if self._block_on_first_byte:
                # do a blocking read for first byte
                self._serial.timeout = None
                try:
                    read_bytes = self._serial.read(1)
                    request += read_bytes
                except Exception as e:
                    self._serial.close()
                    self._serial.open()
                self._serial.timeout = self._timeout

            # Read rest of the request
            while True:
                try:
                    read_bytes = self._serial.read(128)
                    if not read_bytes:
                        break
                except Exception as e:
                    self._serial.close()
                    self._serial.open()
                    break
                request += read_bytes

            # parse the request
            if request:
                response = self._handle(request)

                if response:
                    if self._serial.in_waiting > 0:
                        pass
                    else:
                        self._serial.write(response)
                        self._serial.flush()
                        time.sleep(self.get_timeout())

        except Exception as excpt:
            pass



if __name__ == '__main__':
    pass
