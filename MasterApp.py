from PySide6.QtWidgets import QApplication

from ModbusGui import MasterGui

if __name__ == '__main__':
    MasterApp = QApplication([])
    master = MasterGui()
    master.ui.show()
    MasterApp.exec_()