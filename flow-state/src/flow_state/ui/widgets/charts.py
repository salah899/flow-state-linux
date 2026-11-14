from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

from flow_state.ui.theme import ACCENTS


class StatCard(QFrame):
    def __init__(self, title, color):
        super().__init__()
        self.setObjectName("card")
        lay = QVBoxLayout(self)
        cap = QLabel(title)
        cap.setObjectName("muted")
        self.value = QLabel("0")
        self.value.setObjectName("statValue")
        self.value.setStyleSheet(f"color:{color};")
        lay.addWidget(cap)
        lay.addWidget(self.value)


class WeeklyChart(QWidget):
    def __init__(self):
        super().__init__()
        self.values = [0] * 7
        self.labels = [""] * 7
        self.unit = ""
        self.color = ACCENTS["primary"]
        self.setMinimumHeight(250)

    def set_data(self, values, labels, unit="", color=None):
        self.values, self.labels, self.unit = list(values), list(labels), unit
        self.color = color or ACCENTS["primary"]
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        text = self.palette().color(self.foregroundRole())
        grid = self.palette().color(self.backgroundRole()).lighter(125)
        w, h = self.width(), self.height()
        base = h - 45
        maximum = max(self.values + [1])
        gap = w / max(1, len(self.values))
        p.setPen(QPen(grid, 1))
        p.drawLine(18, base, w - 18, base)
        for i, value in enumerate(self.values):
            bh = (base - 38) * (value / maximum)
            rect = QRectF(i * gap + gap * .27, base - bh, gap * .46, bh)
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(self.color))
            p.drawRoundedRect(rect, 6, 6)
            p.setPen(text)
            shown = f"{value:g}{self.unit}" if value else "0"
            p.drawText(QRectF(i * gap, base - bh - 24, gap, 20), Qt.AlignCenter, shown)
            p.drawText(QRectF(i * gap, base + 8, gap, 24), Qt.AlignCenter, self.labels[i])


class DonutChart(QWidget):
    def __init__(self):
        super().__init__()
        self.rate = 0
        self.caption = "إنجاز"
        self.color = ACCENTS["green"]
        self.setMinimumHeight(230)

    def set_data(self, rate, caption, color):
        self.rate = max(0, min(100, float(rate)))
        self.caption, self.color = caption, color
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        side = max(30, min(self.width(), self.height()) - 58)
        rect = QRectF((self.width() - side) / 2, (self.height() - side) / 2, side, side)
        track = self.palette().color(self.backgroundRole()).lighter(130)
        text = self.palette().color(self.foregroundRole())
        p.setPen(QPen(track, 18, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(rect, 0, 360 * 16)
        p.setPen(QPen(QColor(self.color), 18, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(rect, 90 * 16, -int(360 * 16 * self.rate / 100))
        p.setPen(text)
        p.drawText(rect, Qt.AlignCenter, f"{round(self.rate)}%\n{self.caption}")
