from PySide2.QtWidgets import QApplication, QMessageBox
from PySide2.QtUiTools import QUiLoader

class MasterGui:
    def __init__(self):
        self.function_code = None
        self.serial_port = None
        # 从文件中加载UI定义

        # 从 UI 定义中动态 创建一个相应的窗口对象
        # 注意：里面的控件对象也成为窗口对象的属性了
        # 比如 self.ui.button , self.ui.textEdit
        self.ui = QUiLoader().load('../ModbusMaster.ui')
        #! connect 函数不要加()
        self.ui.slave_id_input.returnPressed.connect(self.set_slave_id)
        self.ui.serial_port_input.returnPressed.connect(self.set_serial_port)
        self.ui.quantity_input.returnPressed.connect(self.set_quantity)

        self.ui.function_code.addItem('01 Read Coils')
        self.ui.function_code.addItem('03 Read Holding Registers')
        self.ui.function_code.addItem('05 Write Single Coil')
        self.ui.function_code.currentIndexChanged.connect(self.change_function_code)

        # self.ui.button.clicked.connect(self.handleCalc)
        self.ui.send_button.clicked.connect(self.send)

    def set_slave_id(self):
        slave = self.ui.slave_id_input.text()
        print('slave_id: ', slave)
        QMessageBox.about(self.ui, 'Slave', slave)
        # print(slave)

    def set_serial_port(self):
        serial_port = self.ui.serial_port_input.text()
        print('serial port: ', serial_port)
        QMessageBox.about(self.ui, 'Serial Port', serial_port)
        # print(serial_port)

    def set_quantity(self):
        quantity = self.ui.quantity_input.text()
        print('serial port: ', quantity)
        QMessageBox.about(self.ui, 'Quantity', quantity)


    def change_function_code(self, index):
        # 在这里更新你的变量
        if index == 0:
            self.function_code = 1
        elif index == 1:
            self.function_code = 3
        elif index == 2:
            self.function_code = 5

        # 打印变量的值
        print(f"Variable value: {self.function_code}")

    def send(self):
        info = self.ui.function_code.currentText()
        print(info)
        QMessageBox.about(self.ui, 'Function', info)
        print(self.function_code)




    # def handleCalc(self):
    #     info = self.ui.textEdit.toPlainText()
    #
    #     salary_above_20k = ''
    #     salary_below_20k = ''
    #     for line in info.splitlines():
    #         if not line.strip():
    #             continue
    #         parts = line.split(' ')
    #
    #         parts = [p for p in parts if p]
    #         name, salary, age = parts
    #         if int(salary) >= 20000:
    #             salary_above_20k += name + '\n'
    #         else:
    #             salary_below_20k += name + '\n'
    #
    #     QMessageBox.about(self.ui,
    #                       '统计结果',
    #                       f'''薪资20000 以上的有：\n{salary_above_20k}
    #                     \n薪资20000 以下的有：\n{salary_below_20k}'''
    #                       )


app = QApplication([])
master = MasterGui()
master.ui.show()
app.exec_()