from sys import exit, argv
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import QObject, pyqtSignal, QRect, Qt
from PyQt5.QtGui import QIcon, QPainter, QPen, QCursor
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QFileDialog, QMessageBox
from PyQt5.QtWidgets import QWidget, QSystemTrayIcon, QMenu
from system_hotkey import SystemHotkey


class MyWindow(QWidget, QObject):
    # 定义一个热键信号
    sig_keyhot = pyqtSignal(str)

    def __init__(self):
        # 创建窗口并且隐藏
        super().__init__()
        self.msgBox = None
        self.show_tips()
        self.pixmap = None
        self.setWindowTitle('工具')
        self.setWindowIcon(QIcon("exit.ico"))
        self.sys_icon()
        # 记录鼠标的初始坐标和结束坐标
        self.start_x, self.x, self.start_y, self.y = 0, 0, 0, 0
        # 记录松开鼠标时开始截图时候的位置
        self.width, self.height, self.res_x, self.res_y = 0, 0, 0, 0
        # 鼠标是否松开
        self.flag = False
        self.background = QLabel(self)

        # 全局热键，电脑任何地方开始截图
        self.sig_keyhot.connect(self.MKey_pressEvent)
        self.hk_shot = SystemHotkey()
        self.hk_shot.register(('control', 'q'), callback=lambda x: self.send_key_event("start"))

        # 局部热键，只能在窗口范围内使用
        QtWidgets.QShortcut(QtGui.QKeySequence('Esc', ), self, self.stop_painting)
        # 复制图像的按钮
        self.button_copy = QPushButton('复制', self)
        self.button_copy.setGeometry(10, 10, 50, 30)
        self.button_copy.setStyleSheet('''
                    QPushButton {
                        background-color: #FFFFFF;
                        color: black;
                    }
                    QPushButton:hover {
                        background-color: #ADD8E6;
                    }
                    QPushButton:pressed {
                        background-color: #2e6b2e;
                    }
                ''')
        self.button_copy.hide()

        # 保存图像的按钮
        self.button_save = QPushButton('保存', self)
        self.button_save.setGeometry(10, 10, 50, 30)
        self.button_save.setStyleSheet('''
                    QPushButton {
                        background-color: #FFFFFF;
                        color: black;
                    }
                    QPushButton:hover {
                        background-color: #ADD8E6;
                    }
                    QPushButton:pressed {
                        background-color: #2e6b2e;
                    }
                ''')
        self.button_save.hide()
        self.rect = None
        self.button_copy.clicked.connect(lambda: self.copy2clipboard(self.pixmap.copy(self.rect)))
        self.button_save.clicked.connect(lambda: self.save_img(self.pixmap, self.rect))

    def show_tips(self):
        # 提示窗弹出
        QMessageBox.information(self, "提示", "截图工具已经启动\n使用全局快捷键Ctrl+q开始截图")

    def stop_painting(self):
        self.hide()

    def send_key_event(self, i_str):
        self.sig_keyhot.emit(i_str)

    def MKey_pressEvent(self):
        self.button_copy.hide()
        self.button_save.hide()

        screen = QApplication.primaryScreen()
        if screen is not None:
            print("Starting get Screenshot...")
            self.pixmap = screen.grabWindow(QApplication.desktop().winId())
            self.background.setPixmap(self.pixmap)
            self.background.setScaledContents(True)
            self.showFullScreen()
            cursor = QCursor(Qt.CrossCursor)
            self.setCursor(cursor)

    def mousePressEvent(self, event):
        self.flag = True
        self.start_x = event.x()
        self.start_y = event.y()

    def mouseReleaseEvent(self, event):
        self.flag = False
        self.button_copy.move(event.pos())
        self.button_copy.show()

        self.button_save.move(event.x(), event.y() - 35)
        self.button_save.show()

    def mouseMoveEvent(self, event):
        if self.flag:
            self.x = event.x()
            self.y = event.y()
            self.update()

    def paintEvent(self, event):

        try:
            super().paintEvent(event)

            width = abs(self.x - self.start_x)
            height = abs(self.y - self.start_y)

            self.res_x = min(self.x, self.start_x)
            self.res_y = min(self.y, self.start_y)
            self.rect = QRect(self.res_x, self.res_y, width, height)
            if self.flag:

                tmp = self.pixmap.copy()
                painter = QPainter(tmp)
                painter.setPen(QPen(Qt.blue, 2, style=Qt.SolidLine, cap=Qt.SquareCap, join=Qt.BevelJoin))

                painter.drawRect(self.rect)
                painter.end()
                self.background.setPixmap(tmp)
            else:
                return

        except Exception as e:
            print("Error:", e)

    def sys_icon(self):
        # 系统托盘
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(QIcon("exit.ico"))
        tray_menu = QMenu()
        exit_action = tray_menu.addAction("退出")
        exit_action.triggered.connect(self.exit)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.setToolTip('Ctrl+Q截屏')
        self.tray_icon.setVisible(True)

    @staticmethod
    def exit(self):
        # 点击关闭按钮或者点击退出事件会出现图标无法消失的bug，需要手动将图标内存清除
        # self.tray_icon = None
        exit(app.exec())

    def copy2clipboard(self, img):
        print("进来了copy img")
        clipboard = QApplication.clipboard()
        clipboard.setPixmap(img)
        self.stop_painting()

    def save_img(self, img, rect):
        print("进来了save img")
        file_path, _ = QFileDialog.getSaveFileName(None, "保存图片", "", "Images (*.png *.xpm *.jpg)")
        if file_path:
            img_copy = img.copy(rect)
            img_copy.save(file_path)
        self.stop_painting()


if __name__ == "__main__":
    app = QApplication(argv)

    window = MyWindow()

    app.exec_()
    # exit(app.exec())
