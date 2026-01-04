import sys
import threading
import math
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QTextEdit, QVBoxLayout, QHBoxLayout
)
from PyQt6.QtGui import QFont, QPainter, QColor, QPen
from PyQt6.QtCore import Qt, QTimer

import jarvis as main



class ArcReactor(QWidget):
    def __init__(self):
        super().__init__()
        self.angle = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)
        self.setFixedSize(160, 160)

    def animate(self):
        self.angle += 2
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center = self.rect().center()

        pen = QPen(QColor(0, 255, 255))
        pen.setWidth(4)
        painter.setPen(pen)

        painter.drawEllipse(center, 60, 60)

        painter.save()
        painter.translate(center)
        painter.rotate(self.angle)

        for i in range(6):
            painter.drawLine(0, -60, 0, -90)
            painter.rotate(60)

        painter.restore()


class VoiceWave(QWidget):
    def __init__(self):
        super().__init__()
        self.phase = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_wave)
        self.timer.start(50)
        self.setFixedHeight(80)

    def update_wave(self):
        self.phase += 0.3
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(QColor(0, 255, 255), 2))

        w = self.width()
        h = self.height() // 2

        last_x, last_y = 0, h

        for x in range(w):
            y = h + math.sin(x * 0.04 + self.phase) * 20
            painter.drawLine(last_x, last_y, x, int(y))
            last_x, last_y = x, int(y)


class JarvisHUD(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("J.A.R.V.I.S")
        self.setFixedSize(1000, 650)
        self.setStyleSheet(self.style())

        self.init_ui()
        self.boot_sequence()

    def init_ui(self):
        self.title = QLabel("J.A.R.V.I.S")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setFont(QFont("Orbitron", 32))
        self.title.setStyleSheet("color:#00ffff")

        self.status = QLabel("BOOTING SYSTEM...")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setFont(QFont("Consolas", 12))
        self.status.setStyleSheet("color:#00ffaa")

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFont(QFont("Consolas", 11))
        self.console.setStyleSheet("""
            background-color: rgba(0,20,30,200);
            color: #00ffff;
            border: 2px solid #00ffff;
            border-radius: 12px;
        """)

        self.arc = ArcReactor()
        self.wave = VoiceWave()

        self.activate_btn = QPushButton("ACTIVATE")
        self.activate_btn.clicked.connect(self.start_jarvis)

        self.activate_btn.setFont(QFont("Orbitron", 12))
        self.activate_btn.setFixedHeight(45)

        top = QVBoxLayout()
        top.addWidget(self.title)
        top.addWidget(self.status)

        mid = QHBoxLayout()
        mid.addWidget(self.console, 2)

        side = QVBoxLayout()
        side.addWidget(self.arc, alignment=Qt.AlignmentFlag.AlignCenter)
        side.addWidget(self.wave)
        side.addWidget(self.activate_btn)

        mid.addLayout(side, 1)

        layout = QVBoxLayout()
        layout.addLayout(top)
        layout.addLayout(mid)

        self.setLayout(layout)

    def boot_sequence(self):
        self.console.append(">> INITIALIZING AI CORE")
        self.console.append(">> LOADING NEURAL NETWORKS")
        self.console.append(">> SYNCHRONIZING AUDIO MODULE")
        self.console.append(">> SYSTEM ONLINE")
        self.status.setText("SYSTEM STATUS : STANDBY")

    def log(self, text):
        self.console.append(text)

    def start_jarvis(self):
        self.status.setText("SYSTEM STATUS : LISTENING")
        self.console.append(">> VOICE INTERFACE ACTIVATED")

        t = threading.Thread(
            target=main.run_jarvis,
            args=(self.log,),
            daemon=True
        )
        t.start()

    def style(self):
        return """
        QWidget { background-color:#020b12; }

        QPushButton {
            color:#00ffff;
            border:2px solid #00ffff;
            border-radius:22px;
            background:transparent;
        }

        QPushButton:hover {
            background:rgba(0,255,255,40);
        }
        """


if __name__ == "__main__":
    app = QApplication(sys.argv)
    hud = JarvisHUD()
    hud.show()
    sys.exit(app.exec())
