import sys
import os
import threading
import math
import psutil
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QTextEdit, QVBoxLayout, QHBoxLayout, QGridLayout
)
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QPixmap
from PyQt6.QtCore import Qt, QTimer

import jarvis as main


# ========================================================
# REVOLVING ARC REACTOR COMPONENT (IMAGE-BASED)
# ========================================================
class ArcReactor(QWidget):
    def __init__(self, size=260):
        super().__init__()
        self.angle = 0
        self.pulse = 0
        self.pulse_dir = 1
        self.target_size = size
        self.setFixedSize(size, size)

        # Load Arc Reactor Image
        img_path = os.path.join(os.path.dirname(__file__), "arc_reactor_circle.png")
        if not os.path.exists(img_path):
            img_path = os.path.join(os.path.dirname(__file__), "arc_reactor.jpg")

        if os.path.exists(img_path):
            raw_pixmap = QPixmap(img_path)
            self.pixmap = raw_pixmap.scaled(
                size - 24, size - 24,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        else:
            self.pixmap = None

        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(25)  # 40 FPS smooth rotation

    def animate(self):
        # Continuous smooth revolving
        self.angle = (self.angle + 1.2) % 360
        self.pulse += 0.04 * self.pulse_dir
        if self.pulse > 1.0 or self.pulse < 0.0:
            self.pulse_dir *= -1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        center = self.rect().center()

        # 1. Outer Hologram HUD Ring with subtle breathing pulse
        glow_alpha = int(70 + 80 * self.pulse)
        glow_pen = QPen(QColor(0, 255, 255, glow_alpha), 2)
        painter.setPen(glow_pen)
        painter.drawEllipse(center, self.target_size // 2 - 5, self.target_size // 2 - 5)

        # 2. Draw Revolving Arc Reactor
        if self.pixmap:
            painter.save()
            painter.translate(center)
            painter.rotate(self.angle)
            painter.drawPixmap(
                -self.pixmap.width() // 2,
                -self.pixmap.height() // 2,
                self.pixmap
            )
            painter.restore()
        else:
            # Fallback if image missing
            pen = QPen(QColor(0, 255, 255), 3)
            painter.setPen(pen)
            painter.drawEllipse(center, 60, 60)


# ========================================================
# AUDIO REACTIVE VOICE WAVE COMPONENT
# ========================================================
class VoiceWave(QWidget):
    def __init__(self, color_hex="#00ffff"):
        super().__init__()
        self.phase = 0
        self.color = QColor(color_hex)
        self.amplitude = 18
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_wave)
        self.timer.start(35)
        self.setFixedHeight(75)

    def set_color(self, hex_code):
        self.color = QColor(hex_code)
        self.update()

    def update_wave(self):
        self.phase += 0.25
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(self.color, 2))

        w = self.width()
        h = self.height() // 2

        last_x, last_y = 0, h

        for x in range(0, w, 2):
            y = h + (math.sin(x * 0.035 + self.phase) * self.amplitude) + (math.sin(x * 0.08 - self.phase) * (self.amplitude * 0.4))
            painter.drawLine(last_x, int(last_y), x, int(y))
            last_x, last_y = x, int(y)


# ========================================================
# MAIN JARVIS HUD WINDOW
# ========================================================
class JarvisHUD(QWidget):
    THEMES = [
        {"name": "MARK 85 CYAN", "primary": "#00ffff", "accent": "#00ffaa", "bg": "#020b12"},
        {"name": "STARK CRIMSON", "primary": "#ff2244", "accent": "#ffd700", "bg": "#120205"},
        {"name": "TACTICAL GREEN", "primary": "#00ff66", "accent": "#aaff00", "bg": "#021206"},
    ]

    def __init__(self):
        super().__init__()
        self.theme_idx = 0
        self.current_theme = self.THEMES[self.theme_idx]

        self.setWindowTitle("J.A.R.V.I.S – STARK INDUSTRIES INTERFACE")
        self.setFixedSize(1080, 720)
        self.apply_theme()

        self.init_ui()
        self.boot_sequence()
        self.start_telemetry()

    def init_ui(self):
        # 1. Header & Title
        self.title = QLabel("J.A.R.V.I.S")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setFont(QFont("Orbitron", 34, QFont.Weight.Bold))

        self.status = QLabel("BOOTING SYSTEM...")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setFont(QFont("Consolas", 12))

        # Real-time Hardware Telemetry Bar
        self.telemetry = QLabel("CPU LOAD: 0%  |  RAM USAGE: 0%  |  BATTERY: SCANNING...")
        self.telemetry.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.telemetry.setFont(QFont("Consolas", 10))

        # 2. Main Terminal Console
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFont(QFont("Consolas", 11))

        # 3. Visualizer Widgets: Revolving Arc Reactor & Harmonic Audio Wave
        self.arc = ArcReactor(size=270)
        self.wave = VoiceWave(self.current_theme["primary"])

        # 4. Interactive Action Buttons
        self.activate_btn = QPushButton("🎙️ ACTIVATE JARVIS")
        self.activate_btn.clicked.connect(self.start_jarvis)
        self.activate_btn.setFixedHeight(48)
        self.activate_btn.setFont(QFont("Orbitron", 11, QFont.Weight.Bold))

        self.stats_btn = QPushButton("📊 SYSTEM DIAGNOSTICS")
        self.stats_btn.clicked.connect(self.trigger_stats)
        self.stats_btn.setFixedHeight(36)

        self.weather_btn = QPushButton("⛅ WEATHER FORECAST")
        self.weather_btn.clicked.connect(self.trigger_weather)
        self.weather_btn.setFixedHeight(36)

        self.notes_btn = QPushButton("📝 READ MY NOTES")
        self.notes_btn.clicked.connect(self.trigger_notes)
        self.notes_btn.setFixedHeight(36)

        self.theme_btn = QPushButton("🎨 THEME: " + self.current_theme["name"])
        self.theme_btn.clicked.connect(self.cycle_theme)
        self.theme_btn.setFixedHeight(36)

        self.clear_btn = QPushButton("🧹 CLEAR CONSOLE")
        self.clear_btn.clicked.connect(self.console.clear)
        self.clear_btn.setFixedHeight(36)

        # Layout Assembly
        top_layout = QVBoxLayout()
        top_layout.addWidget(self.title)
        top_layout.addWidget(self.status)
        top_layout.addWidget(self.telemetry)

        # Side Control Panel with Revolving Arc Reactor
        side_layout = QVBoxLayout()
        side_layout.addWidget(self.arc, alignment=Qt.AlignmentFlag.AlignCenter)
        side_layout.addWidget(self.wave)
        side_layout.addWidget(self.activate_btn)

        grid = QGridLayout()
        grid.addWidget(self.stats_btn, 0, 0)
        grid.addWidget(self.weather_btn, 0, 1)
        grid.addWidget(self.notes_btn, 1, 0)
        grid.addWidget(self.theme_btn, 1, 1)
        grid.addWidget(self.clear_btn, 2, 0, 1, 2)
        side_layout.addLayout(grid)

        # Center Body
        mid_layout = QHBoxLayout()
        mid_layout.addWidget(self.console, 6)
        mid_layout.addLayout(side_layout, 4)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addLayout(mid_layout)
        self.setLayout(main_layout)

    def boot_sequence(self):
        self.console.append(">> INITIALIZING STARK AI CORE...")
        self.console.append(">> AUDIO ENGINES: NEURAL TTS & RECOGNITION ACTIVE")
        self.console.append(">> ARC REACTOR CORE: ONLINE & STABLE")
        self.console.append(">> ALL PROTOCOLS VERIFIED. WELCOME BACK, SIR.")
        self.status.setText("SYSTEM STATUS : STANDBY (SAY 'HEY JARVIS')")

    def start_telemetry(self):
        self.telemetry_timer = QTimer()
        self.telemetry_timer.timeout.connect(self.update_telemetry)
        self.telemetry_timer.start(2000)
        self.update_telemetry()

    def update_telemetry(self):
        try:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            battery = psutil.sensors_battery()
            bat_str = f"{battery.percent}%" if battery else "N/A"
            charging = " [AC]" if (battery and battery.power_plugged) else ""
            self.telemetry.setText(f"CPU LOAD: {int(cpu)}%  |  RAM USAGE: {int(ram)}%  |  BATTERY: {bat_str}{charging}")
        except Exception:
            pass

    def log(self, text):
        self.console.append(text)

    def start_jarvis(self):
        self.status.setText("SYSTEM STATUS : LISTENING...")
        self.console.append(">> VOICE PROTOCOL ENGAGED")
        main.play_hud_sound("activate")
        t = threading.Thread(target=main.run_jarvis, args=(self.log,), daemon=True)
        t.start()

    def trigger_stats(self):
        threading.Thread(target=main.get_system_stats, daemon=True).start()

    def trigger_weather(self):
        threading.Thread(target=main.get_weather, daemon=True).start()

    def trigger_notes(self):
        threading.Thread(target=main.read_notes, daemon=True).start()

    def cycle_theme(self):
        self.theme_idx = (self.theme_idx + 1) % len(self.THEMES)
        self.current_theme = self.THEMES[self.theme_idx]
        self.theme_btn.setText("🎨 THEME: " + self.current_theme["name"])
        self.wave.set_color(self.current_theme["primary"])
        self.apply_theme()

    def apply_theme(self):
        p = self.current_theme["primary"]
        a = self.current_theme["accent"]
        bg = self.current_theme["bg"]
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg};
            }}
            QLabel {{
                color: {p};
            }}
            QTextEdit {{
                background-color: rgba(0, 10, 20, 220);
                color: {p};
                border: 2px solid {p};
                border-radius: 12px;
                padding: 10px;
            }}
            QPushButton {{
                color: {p};
                border: 2px solid {p};
                border-radius: 18px;
                background-color: rgba(0, 0, 0, 110);
                font-family: Consolas;
                font-size: 11px;
                font-weight: bold;
                padding: 4px;
            }}
            QPushButton:hover {{
                background-color: {p};
                color: #000000;
            }}
        """)
        if hasattr(self, "title"):
            self.title.setStyleSheet(f"color: {p};")
            self.status.setStyleSheet(f"color: {a};")
            self.telemetry.setStyleSheet(f"color: {a};")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    hud = JarvisHUD()
    hud.show()
    sys.exit(app.exec())
