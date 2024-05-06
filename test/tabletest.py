from PySide2.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from PySide2.QtCore import Qt

class EditableTableWidget(QWidget):
    def __init__(self):
        super().__init__()

        # 创建表格
        self.tableWidget = QTableWidget(self)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(["数据名称", "数据值"])

        # 连接 cellChanged 信号
        self.tableWidget.cellChanged.connect(self.handle_cell_changed)

        # 添加数据
        self.populate_table()

        # 创建布局
        layout = QVBoxLayout(self)
        layout.addWidget(self.tableWidget)

    def populate_table(self):
        # 填充表格数据
        data = [
            ["名称1", "值1"],
            ["名称2", "值2"],
            ["名称3", "值3"],
            ["名称4", "值4"],
            ["名称5", "值5"]
        ]

        self.tableWidget.setRowCount(len(data))

        for row, rowData in enumerate(data):
            for col, item in enumerate(rowData):
                newItem = QTableWidgetItem(str(item))
                newItem.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(row, col, newItem)

    def handle_cell_changed(self, row, col):
        # 在这里处理单元格内容变化事件
        item = self.tableWidget.item(row, col)
        if item is not None:
            print(f"Cell at row {row}, column {col} changed to: {item.text()}")

if __name__ == "__main__":
    app = QApplication([])

    widget = EditableTableWidget()
    widget.show()

    app.exec_()
