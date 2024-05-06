import time

from PySide6.QtWidgets import QApplication, QMessageBox, QTableWidgetItem, QVBoxLayout, QWidget, QLCDNumber
from PySide6.QtCore import Qt, QThread, Signal, QObject
from PySide6.QtUiTools import QUiLoader
import serial
from threading import Thread

import Modbus
import ModbusSerial
from defines import *


class MasterGui:
    def __init__(self):
        self._serial = None
        self.master = None
        self.serial_port = 'COM1'
        self.function_code = 1
        self.slave_id = 1
        self.starting_address = 0
        self.quantity = 1
        self.output_value = None
        self.slave_running = False
        self.slave_start_count = 0
        self.slave_register_address = 10
        self.slave_indicator_address = 25

        # self._serial = serial.Serial(port=self.serial_port, baudrate=9600, bytesize=8, stopbits=1, parity='E')

        # ui
        self.ui = QUiLoader().load('ModbusMaster.ui')
        # self.ui.StartCount.setDigitCount(2)
        self.ui.StartCountLCD.display(self.slave_start_count)

        # init data buffer
        buffer_data = [["0", '0'], ["1", '0'], ["2", '0'], ["3", '0'], ["4", '0'],
                                 ["5", '0'], ["6", '0'], ["7", '0'], ["8", '0'], ["9", '0']]
        self.ui.DataBuffer.setColumnCount(2)
        self.ui.DataBuffer.setHorizontalHeaderLabels(["Address", "Value"])
        self.ui.DataBuffer.setRowCount(len(buffer_data))

        for row, rowData in enumerate(buffer_data):
            for col, item in enumerate(rowData):
                newItem = QTableWidgetItem(item)
                newItem.setTextAlignment(Qt.AlignCenter)
                if col == 0:
                    newItem.setFlags(newItem.flags() & ~Qt.ItemIsEditable)
                self.ui.DataBuffer.setItem(row, col, newItem)

        # init data buffer
        received_data = [["0", '0'], ["1", '0'], ["2", '0'], ["3", '0'], ["4", '0'],
                       ["5", '0'], ["6", '0'], ["7", '0'], ["8", '0'], ["9", '0']]
        self.ui.DataReceived.setColumnCount(2)
        self.ui.DataReceived.setHorizontalHeaderLabels(["Address", "Value"])
        self.ui.DataReceived.setRowCount(len(received_data))

        for row, rowData in enumerate(received_data):
            for col, item in enumerate(rowData):
                newItem = QTableWidgetItem(item)
                newItem.setTextAlignment(Qt.AlignCenter)
                if col == 0:
                    newItem.setFlags(newItem.flags() & ~Qt.ItemIsEditable)
                self.ui.DataReceived.setItem(row, col, newItem)
        # self.ui.CoilsBlock.cellChanged.connect(self.handle_data_buffer_changed)

        #
        self.ui.slave_id_input.returnPressed.connect(self.set_slave_id)
        self.ui.serial_port_input.returnPressed.connect(self.set_serial_port)
        self.ui.starting_address_input.returnPressed.connect(self.set_starting_address)
        self.ui.quantity_input.returnPressed.connect(self.set_quantity)

        self.ui.function_code.addItem('01 Read Coils')
        self.ui.function_code.addItem('03 Read Holding Registers')
        self.ui.function_code.addItem('05 Write Single Coil')
        self.ui.function_code.currentIndexChanged.connect(self.change_function_code)
        # button
        self.ui.send_button.clicked.connect(self.send)
        self.ui.connect_button.clicked.connect(self.connect)
        self.ui.disconnect_button.clicked.connect(self.disconnect)
        self.ui.start_button.clicked.connect(self.start_slave)
        self.ui.stop_button.clicked.connect(self.stop_slave)
        self.ui.reset_button.clicked.connect(self.reset)

    def set_serial_port(self):
        self.serial_port = self.ui.serial_port_input.text()
        print('serial port: ', self.serial_port)
        # QMessageBox.about(self.ui, 'Serial Port', self.serial_port)
        # print(serial_port)
        self._serial = serial.Serial(port=self.serial_port, baudrate=9600, bytesize=8, stopbits=1, parity='E')

    def connect(self):
        if self._serial is not None:
            self.master = ModbusSerial.RtuMaster(serial=self._serial)
            self.master.connect()
            QMessageBox.about(self.ui, 'OK', 'Master connected!')
        else:
            QMessageBox.about(self.ui, 'Error', 'Please set serial port first!')

    def disconnect(self):
        if self.master.is_connect:
            self.master.diconect()
            QMessageBox.about(self.ui, 'OK', 'Master disconnected!')

    def set_slave_id(self):
        self.slave_id = int(self.ui.slave_id_input.text())
        print('slave_id: ', self.slave_id)
        # QMessageBox.about(self.ui, 'Slave', self.slave_id)
        # print(slave)

    def set_starting_address(self):
        self.starting_address = int(self.ui.starting_address_input.text())
        print('starting address: ', self.starting_address)

    def set_quantity(self):
        self.quantity = int(self.ui.quantity_input.text())
        print('quantity: ', self.quantity)
        # QMessageBox.about(self.ui, 'Quantity', quantity)

    def change_function_code(self, index):
        # 在这里更新变量
        if index == 0:
            self.function_code = READ_COILS
        elif index == 1:
            self.function_code = READ_HOLDING_REGISTERS
        elif index == 2:
            self.function_code = WRITE_SINGLE_COIL
        # 打印变量的值
        print(f"function code: {self.function_code}")

    def send(self):
        info = self.ui.function_code.currentText()
        # print(info)
        QMessageBox.about(self.ui, 'Function', info)
        # print(self.function_code)
        if self.master.is_connect:
            if self.function_code == WRITE_SINGLE_COIL:
                item = self.ui.DataBuffer.item(self.starting_address, 1)
                self.output_value = int(item.text())
                response = self.master.execute(slave_id=self.slave_id, function_code=self.function_code,
                                           starting_address=self.starting_address, quantity=self.quantity,
                                           output_value=self.output_value)
                row, data = response
                item = self.ui.DataReceived.item(row, 1)
                if data == 0:
                    item.setText(str(data))
                else:
                    item.setText('1')
            # if self.function_code == WRITE_SINGLE_COIL:

                # item = QTableWidgetItem(data)
                # self.ui.DataReceived.setItem(row, 1, item)
            else:
                response = self.master.execute(slave_id=self.slave_id, function_code=self.function_code,
                                               starting_address=self.starting_address, quantity=self.quantity,
                                               output_value=self.output_value)
                for i, data in enumerate(response):
                    item = self.ui.DataReceived.item(self.starting_address+i-self.slave_register_address, 1)
                    item.setText(str(data))
                    # self.ui.DataReceived.setItem(self.starting_address+i, 1, item)

            print('response: ', response)
            QMessageBox.about(self.ui, 'Response', str(response))

    def start_slave(self):
        if self.master.is_connect:
            # if self.function_code == WRITE_SINGLE_COIL:
            #     item = self.ui.DataBuffer.item(self.starting_address, 1)
            #     self.output_value = int(item.text())
            response = self.master.execute(slave_id=self.slave_id, function_code=WRITE_SINGLE_COIL,
                                       starting_address=self.slave_indicator_address, output_value=1)
            row, data = response
            # item = self.ui.DataReceived.item(row, 1)
            if data == 0:
                # item.setText(str(data))
                QMessageBox.about(self.ui, 'Error', 'Start failed!')
            else:
                # item.setText('1')
                if self.slave_running:
                    QMessageBox.about(self.ui, 'Warning', 'Slave is running!')
                else:
                    QMessageBox.about(self.ui, 'OK', 'Slave started!')
                    self.slave_running = True
                    self.slave_start_count += 1
                    self.ui.StartCountLCD.display(self.slave_start_count)


    def stop_slave(self):
        if self.master.is_connect:
            # if self.function_code == WRITE_SINGLE_COIL:
            #     item = self.ui.DataBuffer.item(self.starting_address, 1)
            #     self.output_value = int(item.text())
            response = self.master.execute(slave_id=self.slave_id, function_code=WRITE_SINGLE_COIL,
                                       starting_address=self.slave_indicator_address, output_value=0)
            row, data = response
            # item = self.ui.DataReceived.item(row, 1)
            if data == 0:
                # item.setText(str(data))
                if self.slave_running:
                    self.slave_running = False
                    QMessageBox.about(self.ui, 'OK', 'Slave stopped!')
                else:
                    QMessageBox.about(self.ui, 'Warning', 'Slave is not running!')
            else:
                # item.setText('1')
                QMessageBox.about(self.ui, 'Error', 'Stop failed!')

    def reset(self):
        self.slave_start_count = 0
        self.ui.StartCountLCD.display(self.slave_start_count)
# class Worker(QObject):
#     finished = Signal()  # 用于通知主线程工作线程已完成的信号
#     change_signal = Signal(int)  # 用于传递自定义参数的信号
#
#     def __init__(self, parent=None):
#         super().__init__(parent)
#
#     def do_work(self, request):
#         # 模拟一些工作
#         if request == WRITE_SINGLE_COIL:  # 当参数等于某个特定值时发送信号给主线程
#             self.custom_signal.emit(WRITE_SINGLE_COIL)
#         else:
#             print(f"work thread is processing: {request}")
#
#         # 工作完成后发送finished信号
#         self.finished.emit()


class SlaveGui:
    # request_changed_signal = Signal(int)
    def __init__(self):
        self._serial = None
        self.server = None
        self.slave = None
        self.block_type = COILS
        self.slave_id = 1
        self.coils_address = 0
        self.register_address = 10
        self.coils_quantity = 10
        self.register_quantity = 10
        self.indicator_address = 25
        self.running = False
        self.loop_thread = None

        # self.worker_thread = QThread()
        # self.worker = Worker()

        self.ui = QUiLoader().load('ModbusSlave.ui')

        self.ui.slave_id_input.returnPressed.connect(self.set_slave_id)
        self.ui.serial_port_input.returnPressed.connect(self.set_serial_port)
        self.ui.coils_address_input.returnPressed.connect(self.set_coils_address)
        self.ui.coils_quantity_input.returnPressed.connect(self.set_coils_quantity)
        self.ui.register_address_input.returnPressed.connect(self.set_register_address)
        self.ui.register_quantity_input.returnPressed.connect(self.set_register_quantity)

        self.ui.function_code.addItem('01 Coils')
        self.ui.function_code.addItem('03 Holding Registers')
        # self.ui.function_code.addItem('05 Write Single Coil')
        self.ui.function_code.currentIndexChanged.connect(self.change_function_code)

        self.ui.connect_button.clicked.connect(self.connect)
        self.ui.run_button.clicked.connect(self.run)
        self.ui.stop_button.clicked.connect(self.stop)

        self.ui.isRunning.display(0)

        # self.ui.

        # init coils data
        coils_data = [ ["0", '0'], ["1", '0'], ["2", '0'], ["3", '0'], ["4", '0'],
                       ["5", '0'], ["6", '0'], ["7", '0'], ["8", '0'], ["9", '0'] ]
        self.ui.CoilsBlock.setColumnCount(2)
        self.ui.CoilsBlock.setHorizontalHeaderLabels(["Address", "Value"])
        self.ui.CoilsBlock.setRowCount(len(coils_data))

        for row, rowData in enumerate(coils_data):
            for col, item in enumerate(rowData):
                newItem = QTableWidgetItem(item)
                newItem.setTextAlignment(Qt.AlignCenter)
                if col == 0:
                    newItem.setFlags(newItem.flags() & ~Qt.ItemIsEditable)
                self.ui.CoilsBlock.setItem(row, col, newItem)
        self.ui.CoilsBlock.cellChanged.connect(self.handle_coils_changed)

        # init holding register data
        holding_register_data = [ ["0", '0'], ["1", '0'], ["2", '0'], ["3", '0'], ["4", '0'],
                                  ["5", '0'], ["6", '0'], ["7", '0'], ["8", '0'], ["9", '0'] ]
        self.ui.HoldingRegister.setColumnCount(2)
        self.ui.HoldingRegister.setHorizontalHeaderLabels(["Address", "Value"])
        self.ui.HoldingRegister.setRowCount(len(holding_register_data))

        for row, rowData in enumerate(holding_register_data):
            for col, item in enumerate(rowData):
                newItem = QTableWidgetItem(item)
                newItem.setTextAlignment(Qt.AlignCenter)
                if col == 0:
                    newItem.setFlags(newItem.flags() & ~Qt.ItemIsEditable)
                self.ui.HoldingRegister.setItem(row, col, newItem)
        self.ui.HoldingRegister.cellChanged.connect(self.handle_holding_register_changed)

        # self.request_changed_signal.connect(self.update_coils_data)

    def set_serial_port(self):
        serial_port = self.ui.serial_port_input.text()
        print('serial port: ', serial_port)
        # QMessageBox.about(self.ui, 'Serial Port', self.serial_port)
        # print(serial_port)
        self._serial = serial.Serial(port=serial_port, baudrate=9600, bytesize=8, stopbits=1, parity='E')

    def connect(self):
        if self._serial is not None:
            self.server = ModbusSerial.RtuServer(serial=self._serial)
            # self.master.connect()
            QMessageBox.about(self.ui, 'OK', 'Server connected!')
        else:
            QMessageBox.about(self.ui, 'Error', 'Please set serial port first!')

    def set_slave_id(self):
        self.slave_id = int(self.ui.slave_id_input.text())
        print('slave_id: ', self.slave_id)
        # QMessageBox.about(self.ui, 'Slave', self.slave_id)
        # print(slave)

    def set_coils_address(self):
        self.coils_address = int(self.ui.coils_address_input.text())
        print('coils starting address: ', self.coils_address)

    def set_coils_quantity(self):
        self.coils_quantity = int(self.ui.coils_quantity_input.text())
        print('coils_quantity: ', self.coils_quantity)
        # QMessageBox.about(self.ui, 'Coils Quantity', coils_quantity)

    def set_register_address(self):
        self.register_address = int(self.ui.register_address_input.text())
        print('register starting address: ', self.register_address)

    def set_register_quantity(self):
        self.register_quantity = int(self.ui.register_quantity_input.text())
        print('register_quantity: ', self.register_quantity)

    def change_function_code(self, index):
        # 在这里更新变量
        if index == 0:
            self.function_code = COILS
        elif index == 1:
            self.function_code = HOLDING_REGISTERS
        # 打印变量的值
        print(f"function code: {self.function_code}")

    # @property
    # def data(self):
    #     return self.slave.request_received
    #
    # @data.setter
    # def data(self, new_value):
    #     if new_value != self.slave.request_received:
    #         self.slave.request_received = new_value
    #         # 发射自定义信号，通知表格更新数据
    #         self.request_changed_signal.emit(new_value)

    def update_coils_data(self):
        if self.slave.request_received == WRITE_SINGLE_COIL:
            row = self.slave.changed_data_addres - self.coils_address
            value = self.slave.changed_data
            item = self.ui.CoilsBlock.item(row, 1)
            if value == 0:
                item.setText('0')
            else:
                item.setText('1')

    def run(self):
        if self.server is not None and not self.running:
            self.running = True
            QMessageBox.about(self.ui, 'OK', 'Server is running!')
            self.server.start()
            self.slave = self.server.add_slave(self.slave_id)

            self.slave.add_block('1', COILS, self.coils_address, self.coils_quantity)
            self.slave.add_block('3', HOLDING_REGISTERS, self.register_address, self.register_quantity)
            self.slave.add_block('indicator', COILS, self.indicator_address, 1)

            self.loop_thread = Thread(target=self.loop)
            self.loop_thread.start()

    def loop(self):
        while self.running:
            if self.slave.request_received == WRITE_SINGLE_COIL:
                row = self.slave.changed_data_address - self.coils_address
                value = self.slave.changed_data
                item = self.ui.CoilsBlock.item(row, 1)
                if value==0:
                    if row < 10:
                        item.setText('0')
                    else:
                        self.ui.isRunning.display(0)
                else:
                    if row < 10:
                        item.setText('1')
                    else:
                        self.ui.isRunning.display(1)
            time.sleep(0.1)


    def handle_coils_changed(self, row, col):
        if self.running:
            item = self.ui.CoilsBlock.item(row, col)
            if item is not None:
                print(f"Cell at row {row}, column {col} changed to: {item.text()}")
                self.slave.set_values('1', self.coils_address+row, int(item.text()))
        else:
            # item = QTableWidgetItem('0')
            # self.ui.CoilsBlock.setItem(row, col, item)
            QMessageBox.about(self.ui, 'Error', 'Please run server first!')
    def handle_holding_register_changed(self, row, col):
        if self.running:
            item = self.ui.HoldingRegister.item(row, col)
            if item is not None:
                print(f"Cell at row {row}, column {col} changed to: {item.text()}")
                self.slave.set_values('3', self.register_address+row, int(item.text()))
        else:
            QMessageBox.about(self.ui, 'Error', 'Please run server first!')


    def stop(self):
        self.running = False
        self.loop_thread.join()
        self.server.stop()
        print('stopped')


if __name__ == '__main__':
    # MasterApp = QApplication([])
    # master = MasterGui()
    # master.ui.show()
    # MasterApp.exec_()

    SlaveApp = QApplication([])
    slave = SlaveGui()
    slave.ui.show()
    SlaveApp.aboutToQuit.connect(slave.stop)
    SlaveApp.exec_()