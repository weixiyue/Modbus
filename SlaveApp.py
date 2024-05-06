from PySide6.QtWidgets import QApplication

from ModbusGui import SlaveGui

if __name__ == '__main__':
    SlaveApp = QApplication([])
    slave = SlaveGui()
    slave.ui.show()
    SlaveApp.aboutToQuit.connect(slave.stop)
    SlaveApp.exec_()