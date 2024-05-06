# Modbus Implementation
import struct
import time
import threading

from exceptions import *
from defines import *

class Query(object):
    """ 构建封装报文帧和解析报文帧 """
    def __init__(self):
        """Constructor"""
        pass

    def build_request(self, pdu, slave):
        """ 构建封装主站请求报文帧 """
        raise NotImplementedError()

    def parse_response(self, response):
        """ 解析从站响应报文帧 """
        raise NotImplementedError()

    def parse_request(self, request):
        """ 解析主站请求报文帧 """
        raise NotImplementedError()

    def build_response(self, response_pdu):
        """ 构建封装从站响应报文帧 """
        raise NotImplementedError()


class ModbusMaster(object):
    def __init__(self, response_timeout, delay):
        self._timeout = response_timeout
        self.delay = delay
        self.is_connect = False

    def __del__(self):
        """调用对应函数断开连接"""
        self.disconnect()

    def set_timeout(self, timeout_in_sec):
        """设定超时时间"""
        self._timeout = timeout_in_sec

    def get_timeout(self):
        """获取超时时间设定"""
        return self._timeout

    def connect(self):
        if not self.is_connect:
            self._do_connect()
            self.is_connect = True
            print('Modbus master connected!')
            return True

    def disconnect(self):
        if self.is_connect:
            ret = self._do_disconnect()
            if ret:
                self.is_connect = False

    def _do_connect(self):
        """Open the MAC layer(connect)"""
        raise NotImplementedError()

    def _do_disconnect(self):
        """Close the MAC layer"""
        raise NotImplementedError()

    def _send(self, buffer):
        """Send data to a slave on the MAC layer"""
        raise NotImplementedError()

    def _recv(self, expected_length):
        """Receive data from a slave on the MAC layer"""
        raise NotImplementedError()

    def _make_query(self):
        """
        Returns an instance of a Query subclass implementing
        the MAC layer protocol
        """
        raise NotImplementedError()

    def execute(self, slave_id, function_code, starting_address=0,
                quantity=0, output_value=0, data_format='',
                expected_length=-1, pdu="", returns_raw=False):
        is_read_function = False
        nb_of_digits = 0
        # 打开串口连接
        self.connect()
        # 判断功能码类型
        if function_code == READ_HOLDING_REGISTERS: # 功能码03H读保持寄存器
            print('Reading holding registers...')
            is_read_function = True
            pdu = struct.pack(">BHH", function_code, starting_address, quantity)

            if not data_format:
                data_format = ">" + (quantity * "H")
            if expected_length < 0:
                # 计算响应数据帧的字节数
                # slave + function_code + data_bytes + quantity x 2 + crc1 + crc2
                expected_length = 2 * quantity + 5

        elif function_code == READ_COILS: # 功能码01H读线圈寄存器
            print('reading coils..')
            is_read_function = True
            pdu = struct.pack(">BHH", function_code, starting_address, quantity)
            byte_count = quantity // 8
            if (quantity % 8) > 0:
                byte_count += 1
            nb_of_digits = quantity
            if not data_format:
                data_format = ">" + (byte_count * "B")
            if expected_length < 0:
                # 计算响应数据帧的字节数
                # slave + function_code + data_bytes + byte_count + crc1 + crc2
                expected_length = byte_count + 5
            

        elif function_code == WRITE_SINGLE_COIL: # 功能码05H写单个线圈寄存器
            print('writing single coil...')
            if output_value != 0:
                output_value = 0xff00
            fmt = ">BHH"

            pdu = struct.pack(fmt, function_code, starting_address, output_value)
            if not data_format:
                data_format = ">HH"
            if expected_length < 0:
                # 计算响应数据帧的字节数
                # slave + func + address1 + address2 + value1+value2 + crc1 + crc2
                expected_length = 8

        # make query
        query = self._make_query() # 创建Query对象
        # 根据PDU和从站地址构建得到请求数据帧
        request = query.build_request(pdu, slave_id)
        print('Request: ', request)
        self._send(request) # 发送请求报文帧
        time.sleep(self.delay)

        if slave_id != 0:
            # receive the data from the slave
            response = self._recv(expected_length)
            print('response: ', bytes(response))
            # extract the pdu part of the response
            response_pdu = query.parse_response(response)
            # analyze the received data
            (return_code, byte_2) = struct.unpack(">BB", response_pdu[0:2])

            if return_code > 0x80:
                # the slave has returned an error
                exception_code = byte_2 # 返回功能码出错
                raise ModbusError(exception_code)
            else:
                if is_read_function:
                    # get the values returned by the reading function
                    byte_count = byte_2
                    data = response_pdu[2:]
                    if byte_count != len(data):
                        # the byte count in the pdu is invalid
                        raise ModbusInvalidResponseError("Byte count is {0} "
                         "while actual number of bytes is {1}. ".format(byte_count, len(data))
                        )
                else:
                    # returns what is returned by the slave after a writing function
                    data = response_pdu[1:]
                if returns_raw:
                    return data
                # returns the data as a tuple according to the data_format
                result = struct.unpack(data_format, data)
                if nb_of_digits > 0:
                    digits = []
                    for byte_val in result:
                        for i in range(8):
                            if len(digits) >= nb_of_digits:
                                break
                            digits.append(byte_val % 2)
                            byte_val = byte_val >> 1
                    result = tuple(digits)

                return result


class ModbusBlock(object):
    """This class represents the values for a range of addresses"""
    def __init__(self, starting_address, size, name=''):
        """ Constructor: defines the address range and creates the array of values """
        self.starting_address = starting_address
        self._data = [0] * size
        self.size = len(self._data)

    def is_in(self, starting_address, size):
        """ 判断数据块是否在给定的地址范围内 """
        if starting_address > self.starting_address:
            return (self.starting_address + self.size) > starting_address
        elif starting_address < self.starting_address:
            return (starting_address + size) > self.starting_address
        return True

    def __getitem__(self, item):
        """"""
        return self._data.__getitem__(item)

    def __setitem__(self, item, value):
        """"""
        return self._data.__setitem__(item, value)


class ModbusSlave(object):
    def __init__(self, slave_id, unsigned=True, memory=None):
        """Constructor"""
        self._id = slave_id
        self.request_received = None
        # 数据都视为无符号数处理
        self.unsigned = unsigned
        # the map registering all blocks of the slave
        self._blocks = {}
        # 寄存器映射
        if memory is None:
            self._memory = {
                COILS: [],
                DISCRETE_INPUTS: [],
                HOLDING_REGISTERS: [],
                ANALOG_INPUTS: [],
            }
        else:
            self._memory = memory
        # 线程锁
        self._data_lock = threading.RLock()
        # 函数功能码映射
        self._fn_code_map = {
            READ_COILS: self._read_coils,
            READ_HOLDING_REGISTERS: self._read_holding_registers,
            WRITE_SINGLE_COIL: self._write_single_coil
        }

    def _get_block_and_offset(self, block_type, address, length):
        """returns the block and offset corresponding to the given address"""
        for block in self._memory[block_type]:
            if address >= block.starting_address:
                offset = address - block.starting_address
                if block.size >= offset + length:
                    return block, offset
        raise ModbusError(ILLEGAL_DATA_ADDRESS)


    def _read_digital(self, block_type, request_pdu):
        """read the value of coils """
        (starting_address, quantity_of_x) = struct.unpack(">HH", request_pdu[1:5])
        if (quantity_of_x <= 0) or (quantity_of_x > 2000):
            # maximum allowed size is 2000 bits in one reading
            raise ModbusError(ILLEGAL_DATA_VALUE)
        block, offset = self._get_block_and_offset(block_type, starting_address, quantity_of_x)
        values = block[offset:offset + quantity_of_x]
        # pack bits in bytes
        byte_count = quantity_of_x // 8
        if (quantity_of_x % 8) > 0:
            byte_count += 1
        # write the response header
        response = struct.pack(">B", byte_count)

        i, byte_value = 0, 0
        for coil in values:
            if coil:
                byte_value += (1 << i)
            if i >= 7:
                # write the values of 8 bits in a byte
                response += struct.pack(">B", byte_value)
                # reset the counters
                i, byte_value = 0, 0
            else:
                i += 1
        if i > 0:
            fmt = "B" if self.unsigned else "b"
            response += struct.pack(">" + fmt, byte_value)
        return response

    def _read_coils(self, request_pdu):
        self.request_received = READ_COILS
        """handle read coils modbus function"""
        return self._read_digital(COILS, request_pdu)


    def _read_registers(self, block_type, request_pdu):
        """read the value of holding  registers"""
        (starting_address, quantity_of_x) = struct.unpack(">HH", request_pdu[1:5])
        if (quantity_of_x <= 0) or (quantity_of_x > 125):
            # maximum allowed size is 125 registers in one reading
            raise ModbusError(ILLEGAL_DATA_VALUE)
        # get the block corresponding to the request
        block, offset = self._get_block_and_offset(block_type, starting_address, quantity_of_x)
        # get the values
        values = block[offset:offset+quantity_of_x]
        # write the response header
        response = struct.pack(">B", 2 * quantity_of_x)
        # add the values of every register on 2 bytes
        for reg in values:
            fmt = "H" if self.unsigned else "h"
            response += struct.pack(">"+fmt, reg)
        return response

    def _read_holding_registers(self, request_pdu):
        self.request_received = READ_HOLDING_REGISTERS
        """handle read coils modbus function"""
        return self._read_registers(HOLDING_REGISTERS, request_pdu)


    def _write_single_coil(self, request_pdu):
        self.request_received = WRITE_SINGLE_COIL
        """execute modbus function 5"""
        (data_address, value) = struct.unpack(">HH", request_pdu[1:5])
        block, offset = self._get_block_and_offset(COILS, data_address, 1)
        self.changed_data_address = data_address
        self.changed_data = value
        if value == 0:
            block[offset] = 0
        elif value == 0xff00:
            block[offset] = 1
        else:
            raise ModbusError(ILLEGAL_DATA_VALUE)
        # returns echo of the command
        return request_pdu[1:]


    def handle_request(self, request_pdu, broadcast=False):
        """ 解析请求PDU并做出相应处理，然后返回响应报文帧 """
        # thread-safe
        with self._data_lock:
            try:
                # get the function code
                (function_code, ) = struct.unpack(">B", request_pdu[0:1])
                # 判断功能码是否合法
                if function_code not in self._fn_code_map:
                    raise ModbusError(ILLEGAL_FUNCTION)
                # if read query is broadcasted raises an error
                cant_be_broadcasted = (
                    READ_COILS,
                    READ_HOLDING_REGISTERS ) # 读数据功能码不能被广播
                if broadcast and (function_code in cant_be_broadcasted):
                    raise ModbusInvalidRequestError("Function %d can not be broadcasted" % function_code)
                # execute the corresponding function
                response_pdu = self._fn_code_map[function_code](request_pdu)
                if response_pdu:
                    if broadcast:
                        # call_hooks("modbus.Slave.on_handle_broadcast", (self, response_pdu))
                        # LOGGER.debug("broadcast: %s", get_log_buffer("!!", response_pdu))
                        return ""
                    else:
                        return struct.pack(">B", function_code) + response_pdu
                raise Exception("No response for function %d" % function_code)

            except ModbusError as excpt:
                return struct.pack(">BB", function_code+128, excpt.get_exception_code())


    def add_block(self, block_name, block_type, starting_address, size):
        """ 在从站中添加新的数据块 """
        # thread-safe
        with self._data_lock:
            if size <= 0:
                raise InvalidArgumentError("size must be a positive number")

            if starting_address < 0:
                raise InvalidArgumentError("starting address must be zero or positive number")

            if block_name in self._blocks:
                raise DuplicatedKeyError("Block {0} already exists. ".format(block_name))

            if block_type not in self._memory:
                raise InvalidModbusBlockError("Invalid block type {0}".format(block_type))

            # check that the new block doesn't overlap an existing block
            # it means that only 1 block per type must correspond to a given address
            # for example: it must not have 2 holding registers at address 100
            index = 0
            for i in range(len(self._memory[block_type])):
                block = self._memory[block_type][i]
                if block.is_in(starting_address, size):
                    raise OverlapModbusBlockError(
                        "Overlap block at {0} size {1}".format(block.starting_address, block.size)
                    )
                if block.starting_address > starting_address:
                    index = i
                    break

            # if the block is ok: register it
            self._blocks[block_name] = (block_type, starting_address)
            # add it in the 'per type' shortcut
            self._memory[block_type].insert(index, ModbusBlock(starting_address, size, block_name))

    def remove_block(self, block_name):
        """ 移除从站中指定的数据块 """
        # thread safe
        with self._data_lock:
            block = self._get_block(block_name)

            # the block has been found: remove it from the shortcut
            block_type = self._blocks.pop(block_name)[0]
            self._memory[block_type].remove(block)

    def remove_all_blocks(self):
        """
        Remove all the blocks
        """
        # thread safe
        with self._data_lock:
            self._blocks.clear()
            for key in self._memory:
                self._memory[key] = []

    def _get_block(self, block_name):
        """Find a block by its name and raise and exception if not found"""
        if block_name not in self._blocks:
            raise MissingKeyError("block {0} not found".format(block_name))
        (block_type, starting_address) = self._blocks[block_name]
        for block in self._memory[block_type]:
            if block.starting_address == starting_address:
                return block
        raise Exception("Bug?: the block {0} is not registered properly in memory".format(block_name))

    def set_values(self, block_name, address, values):
        """ 设置寄存器中的数据值, 这是外部设定 """
        # thread safe
        with self._data_lock:
            block = self._get_block(block_name)
            offset = address-block.starting_address
            size = 1
            if isinstance(values, list) or isinstance(values, tuple):
                size = len(values)
            # 确认写入的地址是否合法
            if (offset < 0) or ((offset + size) > block.size):
                raise OutOfModbusBlockError(
                    "address {0} size {1} is out of block {2}".format(address, size, block_name)
                )
            # if Ok: write the values
            if isinstance(values, list) or isinstance(values, tuple):
                block[offset:offset+len(values)] = values
            else:
                block[offset] = values

    def get_values(self, block_name, address, size=1):
        """ 获取指定地址数据块中的数据 """
        # thread safe
        with self._data_lock:
            block = self._get_block(block_name)

            # the block has been found
            # check that it doesn't write out of the block
            offset = address - block.starting_address

            if (offset < 0) or ((offset + size) > block.size):
                raise OutOfModbusBlockError(
                    "address {0} size {1} is out of block {2}".format(address, size, block_name)
                )

            # returns the values
            if size == 1:
                return tuple([block[offset], ])
            else:
                return tuple(block[offset:offset+size])


class DataBank(object):
    """A databank is a shared place containing the data of all slaves"""
    def __init__(self, error_on_missing_slave=True):
        """Constructor"""
        # the map of slaves by ids
        self._slaves = {}
        # protect access to the map of slaves
        self._lock = threading.RLock()
        self.error_on_missing_slave = error_on_missing_slave

    def add_slave(self, slave_id, unsigned=True, memory=None):
        """Add a new slave with the given id"""
        with self._lock:
            if (slave_id <= 0) or (slave_id > 255):
                raise Exception("Invalid slave id {0}".format(slave_id))
            if slave_id not in self._slaves:
                self._slaves[slave_id] = ModbusSlave(slave_id, unsigned, memory)
                return self._slaves[slave_id]
            else:
                raise DuplicatedKeyError("Slave {0} already exists".format(slave_id))

    def get_slave(self, slave_id):
        """Get the slave with the given id"""
        with self._lock:
            if slave_id in self._slaves:
                return self._slaves[slave_id]
            else:
                raise MissingKeyError("Slave {0} doesn't exist".format(slave_id))

    def remove_slave(self, slave_id):
        """Remove the slave with the given id"""
        with self._lock:
            if slave_id in self._slaves:
                self._slaves.pop(slave_id)
            else:
                raise MissingKeyError("Slave {0} already exists".format(slave_id))

    def remove_all_slaves(self):
        """clean the list of slaves"""
        with self._lock:
            self._slaves.clear()

    def handle_request(self, query, request):
        """ when a request is received, handle it and returns the response pdu """
        request_pdu = ""
        try:
            # extract the pdu and the slave id
            (slave_id, request_pdu) = query.parse_request(request)

            # 让slave_id对应的从站执行相应的操作
            if slave_id == 0:
                # broadcast
                for key in self._slaves:
                    self._slaves[key].handle_request(request_pdu, broadcast=True)
                return
            else:
                try:
                    slave = self.get_slave(slave_id)
                except MissingKeyError:
                    if self.error_on_missing_slave:
                        raise
                    else:
                        return ""

                response_pdu = slave.handle_request(request_pdu)
                # make the full response
                response = query.build_response(response_pdu)
                return response
        except ModbusInvalidRequestError as excpt:
            # Request is invalid, do not send any response
            return ""
        except MissingKeyError as excpt:
            # No slave with this ID in server, do not send any response
            return ""
        except Exception as excpt:
            pass

        # If the request was not handled correctly, return a server error response
        func_code = 1
        if len(request_pdu) > 0:
            (func_code, ) = struct.unpack(">B", request_pdu[0:1])

        return struct.pack(">BB", func_code + 0x80, SLAVE_DEVICE_FAILURE)


class ModbusServer(object):
    """ Modbus中有多个从站, Server用于管理从站"""
    def __init__(self, databank=None):
        """Constructor"""
        self._databank = databank if databank else DataBank()
        self._verbose = False
        self._thread = None
        self._go = None
        self._make_thread()

    def _do_init(self):
        """executed before the server starts: to be overridden"""
        pass

    def _do_exit(self):
        """executed after the server stops: to be overridden"""
        pass

    def _do_run(self):
        """main function of the server: to be overridden"""
        pass

    def _make_thread(self):
        """create the main thread of the server"""
        self._thread = threading.Thread(target=ModbusServer._run_server, args=(self,))
        self._go = threading.Event()

    def set_verbose(self, verbose):
        """if verbose is true the sent and received packets will be logged"""
        self._verbose = verbose

    def get_db(self):
        """returns the databank"""
        return self._databank

    def add_slave(self, slave_id, unsigned=True, memory=None):
        """add slave to the server"""
        return self._databank.add_slave(slave_id, unsigned, memory)

    def get_slave(self, slave_id):
        """get the slave with the given id"""
        return self._databank.get_slave(slave_id)

    def remove_slave(self, slave_id):
        """remove the slave with the given id"""
        self._databank.remove_slave(slave_id)

    def remove_all_slaves(self):
        """remove the slave with the given id"""
        self._databank.remove_all_slaves()

    def _make_query(self):
        """
        Returns an instance of a Query subclass implementing
        the MAC layer protocol
        """
        raise NotImplementedError()

    def start(self):
        """Start the server. It will handle request"""
        self._go.set()
        self._thread.start()

    def stop(self):
        """stop the server. It doesn't handle request anymore"""
        if self._thread.is_alive():
            self._go.clear()
            self._thread.join()

    def _run_server(self):
        """main function of the main thread"""
        try:
            self._do_init()
            while self._go.isSet():
                self._do_run()
            self._do_exit()
        except Exception as excpt:
            pass
        self._make_thread()

    def _handle(self, request):
        """handle a received message"""
        if self._verbose:
            pass
        # gets a query for analyzing the request
        query = self._make_query()
        response = self._databank.handle_request(query, request)

        if response and self._verbose:
            pass
        return response