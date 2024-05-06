import time

from PySide2.QtCore import Qt, QThread, Signal, QObject, QTimer

class WorkerThread(QThread):
    changed_signal = Signal(int)

    def __init__(self):
        super().__init__()
        self.data = 0
        print('hhhh')
    def run(self):
        print('hhhh')
        while True:
            if data==10:
                break
        print('hhhh')

# class MainWindow:
#     def __init__(self):
#         super().__init__()
#         loadUi('TimeShow.ui', self)
#         self.initUI()
#     def initUI(self):
#         # 创建线程
#         self.backend = BackendThread()
#         #self.backend.setPath("")
#         # 连接信号
#         self.backend.update_date.connect(self.handleDisplay)
#         self.backend.path="./test.jpg"#也可以将子线程中的成员变量直接赋值
#         self.backend.setPath("./test.jpg")#通过成员变量的方法赋值
#         # 开始线程
#         self.backend.start()
#     def handleDisplay(self, data,number):#参数位置和signal位置一样，信号内的变量自动给到函数，相对位置也不变
#         self.label.setText(data)



if __name__ == "__main__":
    # from PySide2.QtWidgets import QApplication
    # import sys
    #
    # app = QApplication(sys.argv)
    #
    # main_window = MainWindow()
    # main_window.start_thread()
    #
    # sys.exit(app.exec_())
    data = 0
    worker = WorkerThread()
    worker.data = data
    worker.start()
    for i in range(15):
        data += 1
    time.sleep(2)

