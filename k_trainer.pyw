

import os, sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import time
import random
import math
import locale

def format_time(value):
    mins = value // 60
    secs = value - mins*60
    ceil = math.ceil
    if mins:
        return "{:02}:{:02}".format(int(mins), int(secs))
    else:
        return "0:{}".format(int(secs) if int(secs) else '')

class QMyWidget(QWidget):

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)


        wrong_key_delta = time.time() - self.wrong_key
        if wrong_key_delta < 1.0:
            t = max(.5 - wrong_key_delta, 0.0)
            value = int(160*t)
            color = QColor(value, 0, 0)
        else:
            color = Qt.black


        painter.fillRect(self.rect(), color)

        if self.started:

            painter.setPen(QPen(Qt.white))

            _time_passed = time.time() - self.started_time
            time_passed = format_time(_time_passed)
            chars_typed = len(self.typed_text_line) + len(self.mistyped_text_line)
            minutes = int(_time_passed//60)
            if minutes == 0:
                chars_per_minute = "~"
            else:
                chars_per_minute = int( chars_typed / (minutes))
            if chars_typed > 0:
                accuracy = 100 * len(self.typed_text_line)/chars_typed
                accuracy = f'{accuracy:.2f}'
            else:
                accuracy = 100
            status_line = f'Прошло {time_passed}; знаков набрано {chars_typed}; скорость {chars_per_minute} зн/мин; точность {accuracy}%'
            self.status_line = status_line
            painter.drawText(QPoint(100, 20), status_line)

            font = painter.font()
            font_size = 100
            font.setPixelSize(font_size)
            font.setWeight(1900)
            font.setFamily('Consolas')
            painter.setFont(font)

            painter.setRenderHint(QPainter.Antialiasing, True)
            Y_OFFSET = self.rect().height()//2-font_size//2

            # очередь символов для печати
            pen = QPen(QColor(200, 200, 200), 3)
            painter.setPen(pen)
            X_OFFSET = self.rect().width()//2
            pos = QPoint(X_OFFSET, 50+Y_OFFSET)
            pos3 = QPoint(self.rect().width(), pos.y()+font_size*2)
            rect = QRect(pos +QPoint(0, -font_size), pos3)
            painter.drawText(rect, Qt.AlignLeft, self.text_line)

            rect = painter.drawText(rect, Qt.AlignLeft, self.get_current_char())
            painter.drawRect(rect)

            # отпечатанные символы
            gray = QColor(100, 100, 100)
            pen = QPen(gray, 3)
            painter.setPen(pen)
            pos2 = QPoint(0, pos.y()-font_size)
            rect = QRect(pos2, pos)
            text = self.typed_text_line
            painter.drawText(rect, Qt.AlignRight, text)

            # ошибки
            pen = QPen(Qt.red, 3)
            painter.setPen(pen)
            offset = QPoint(0, -font_size)
            pos2 += offset
            pos += offset
            rect = QRect(pos2, pos)
            text = self.mistyped_text_line
            painter.drawText(rect, Qt.AlignRight, text)

            # progressbar
            progress = len(self.text_line) / self.overall_count

            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(Qt.red))
            rect = QRect(0, 0, int(self.rect().width()*(1.0-progress)), 5)
            painter.drawRect(rect)


        else:

            font = painter.font()
            font.setPointSize(20)
            painter.setFont(font)
            menu = ""
            for n, menu_value in enumerate(self.symbols_arrays.values()):
                if self.choose_index == n:
                    arrow = "➜"
                else:
                    arrow = " "
                menu += f"{arrow} {menu_value}\n"
            text = f"{menu}\n{self.status_line}\nНажмите Enter для старта\nTab для выбора набора символов"
            painter.setPen(QPen(Qt.white))
            painter.drawText(self.rect(), Qt.AlignCenter, text)

        painter.end()

    def get_current_char(self):
        try:
            return self.text_line[0]
        except:
            self.started = False
            return " "

    def update(self):
        if isinstance(self.text_line, str) and len(self.text_line) < 1 and self.started:
            self.started = False
            self.write_statistics()
        super().update()

    def write_statistics(self):
        locale.setlocale(locale.LC_ALL, "russian")
        datetime_string = time.strftime("%d %B %Y %X").capitalize()
        path = os.path.join(
            os.path.dirname(__file__),
            'statistics_history.txt'
        )
        data = self.status_line
        with open(path, "a+", encoding="utf8") as stat_log:
            stat_log.write(f'{datetime_string}: {data}\n')

    def mousePressEvent(self, event):
        pass

    def keyReleaseEvent(self, event):
        if not self.started:
            if event.key() in [Qt.Key_Return, Qt.Key_Enter]:
                self.init_session()
            elif event.key() == Qt.Key_Tab:
                self.choose_index += 1
                if self.choose_index > len(self.symbols_arrays)-1:
                    self.choose_index = 0
        else:
            key_text = event.text()
            if event.key() == Qt.Key_Escape:
                self.started = False
            elif event.key() == Qt.Key_F3:
                self.write_statistics()
            else:
                if self.get_current_char() == key_text:
                    self.text_line = self.text_line[1:]
                    self.typed_text_line += key_text
                else:
                    self.wrong_key = time.time()
                    self.mistyped_text_line += key_text
        self.update()

    def keyPressEvent(self, event):
        pass

    symbols_arrays = {
        "symbols_digits_all": '0123456789-=',
        "symbols_digits":   '0123456789',
        "symbols_en":       "!@#$%^&*()-_+=",
        "symbols_ru_only":  "!\"№;%:?*()_-+=",
    }

    def __init__(self, ):
        super().__init__()
        self.started = False
        self.choose_index = 0
        self.status_line = ""
        self.text_line = None
        self.wrong_key = time.time() - 2.0
        self.timer = QTimer()
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.update)
        self.setWindowTitle(f"Keyboard trainer")
        self.timer.start()

    def init_session(self):

        symbols = list(self.symbols_arrays.values())[self.choose_index]

        num = 200
        numbers = []
        for n in range(num):
            a = lambda: random.choice(symbols)
            number = f'{a()}{a()}'
            numbers.append(number)

        self.text_line = " ".join(numbers)
        self.typed_text_line = ""
        self.mistyped_text_line = ""
        self.started = True
        self.started_time = time.time()
        self.status_line = "test"

        self.overall_count = len(self.text_line)

if __name__ == '__main__':

    app = QApplication(sys.argv)
    widget = QMyWidget()
    widget.resize(1500, 900)
    widget.show()
    app.exec()
    sys.exit()
