import sys
import os
import threading
import math
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QProgressBar,
    QVBoxLayout, QHBoxLayout, QStackedWidget
)
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QPixmap, QCursor
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

import jarvis as main


# ========================================================
# 1. PURE REVOLVING ARC REACTOR (CENTERPIECE)
# ========================================================
class PureArcReactor(QWidget):
    clicked = pyqtSignal()

    def __init__(self, size=440):
        super().__init__()
        self.size = size
        self.angle = 0
        self.pulse = 0
        self.pulse_dir = 1
        self.is_active = False

        self.setFixedSize(size, size)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        # Load Arc Reactor Image (AI-generated Stark Industries Arc Reactor)
        img_path = os.path.join(os.path.dirname(__file__), "ai_arc_reactor_circle.png")
        if not os.path.exists(img_path):
            img_path = os.path.join(os.path.dirname(__file__), "ai_arc_reactor.jpg")
        if not os.path.exists(img_path):
            img_path = os.path.join(os.path.dirname(__file__), "arc_reactor_circle.png")

        if os.path.exists(img_path):
            raw = QPixmap(img_path)
            self.pixmap = raw.scaled(
                size - 40, size - 40,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        else:
            self.pixmap = None

        # 50 FPS Smooth Revolving Timer (20ms interval)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(20)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

    def animate(self):
        # Continuous revolving (faster if actively listening/speaking)
        step = 2.2 if self.is_active else 1.2
        self.angle = (self.angle + step) % 360

        # Breathing hologram pulse
        self.pulse += 0.03 * self.pulse_dir
        if self.pulse > 1.0 or self.pulse < 0.0:
            self.pulse_dir *= -1
        self.update()

    def set_active_state(self, active: bool):
        self.is_active = active
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        center = self.rect().center()
        radius = (self.size - 40) // 2

        # 1. Subtle Outer Hologram Reticle Rings
        glow_alpha = int(70 + 80 * self.pulse)
        pen1 = QPen(QColor(0, 255, 255, glow_alpha), 2)
        painter.setPen(pen1)
        painter.drawEllipse(center, radius + 10, radius + 10)

        pen2 = QPen(QColor(0, 255, 255, int(glow_alpha * 0.4)), 1, Qt.PenStyle.DashLine)
        painter.setPen(pen2)
        painter.drawEllipse(center, radius + 18, radius + 18)

        # 2. Draw Smoothly Revolving Arc Reactor Image
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
            # Fallback procedural ring if image not loaded
            painter.setPen(QPen(QColor(0, 255, 255), 4))
            painter.drawEllipse(center, 80, 80)


# ========================================================
# 2. STARK LOADING / BOOT SEQUENCE SCREEN
# ========================================================
class LoadingScreen(QWidget):
    loading_complete = pyqtSignal()

    BOOT_STEPS = [
        ("INITIALIZING QUANTUM CORE...", 15),
        ("CONNECTING SATELLITE UPLINK...", 35),
        ("DEPLOYING NEURAL REASONING MATRIX...", 60),
        ("CALIBRATING AUDIO & HOLOGRAPHIC HUD...", 85),
        ("ARC REACTOR STABILIZED. WELCOME, SIR.", 100),
    ]

    def __init__(self):
        super().__init__()
        self.step_idx = 0
        self.current_progress = 0

        self.init_ui()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.advance_loading)
        self.timer.start(35)  # Updates progress smoothly

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        # 1. Stark Industries Branding
        self.brand = QLabel("S T A R K   I N D U S T R I E S")
        self.brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.brand.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        self.brand.setStyleSheet("color: rgba(0, 255, 255, 180); letter-spacing: 6px;")

        self.title = QLabel("J . A . R . V . I . S")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setFont(QFont("Orbitron", 42, QFont.Weight.Bold))
        self.title.setStyleSheet("color: #00ffff; text-shadow: 0 0 20px #00ffff;")

        self.version = QLabel("SYSTEM BOOT PROTOCOL V8.5")
        self.version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.version.setFont(QFont("Consolas", 10))
        self.version.setStyleSheet("color: #5599bb;")

        # 2. Minimalist Holographic Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedSize(450, 4)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: rgba(0, 30, 45, 180);
                border: none;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #005577, stop:0.8 #00ffff, stop:1 #ffffff);
                border-radius: 2px;
            }
        """)

        # 3. Dynamic Status Label
        self.status = QLabel("INITIALIZING...")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setFont(QFont("Consolas", 11))
        self.status.setStyleSheet("color: #00ffaa;")

        layout.addStretch()
        layout.addWidget(self.brand)
        layout.addWidget(self.title)
        layout.addWidget(self.version)
        layout.addSpacing(25)
        layout.addWidget(self.progress_bar, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status)
        layout.addStretch()

        self.setLayout(layout)

    def advance_loading(self):
        target_text, target_val = self.BOOT_STEPS[self.step_idx]

        if self.current_progress < target_val:
            self.current_progress += 1
            self.progress_bar.setValue(self.current_progress)
            self.status.setText(target_text)
        else:
            if self.step_idx < len(self.BOOT_STEPS) - 1:
                self.step_idx += 1
            else:
                # 100% Boot Complete
                self.timer.stop()
                QTimer.singleShot(400, self.loading_complete.emit)


# ========================================================
# 3. MAIN PURE ARC REACTOR SCREEN (NOTHING ELSE)
# ========================================================
class PureArcReactorScreen(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)

        # The Revolving Arc Reactor - Alone in the center
        self.reactor = PureArcReactor(size=460)
        self.reactor.clicked.connect(self.on_reactor_click)
        layout.addWidget(self.reactor, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def on_reactor_click(self):
        # Clicking the reactor activates voice interface
        main.play_hud_sound("activate")


# ========================================================
# 4. TOP-LEVEL WINDOW (STACKED: LOADING -> REVOLVING REACTOR)
# ========================================================
class JarvisMainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("J.A.R.V.I.S – ARC REACTOR")
        self.resize(900, 750)
        self.setStyleSheet("background-color: #000000;")

        self.is_widget_mode = False
        self.drag_position = None

        # Window Controls: Stack for Loading -> Reactor
        self.stack = QStackedWidget(self)
        self.loading_screen = LoadingScreen()
        self.reactor_screen = PureArcReactorScreen()

        self.stack.addWidget(self.loading_screen)
        self.stack.addWidget(self.reactor_screen)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stack)
        self.setLayout(layout)

        # Switch to reactor screen once boot sequence finishes
        self.loading_screen.loading_complete.connect(self.on_boot_complete)

    def on_boot_complete(self):
        # Play activation chime
        main.play_hud_sound("activate")

        # Smoothly switch to pure revolving reactor
        self.stack.setCurrentWidget(self.reactor_screen)

        # Launch Jarvis background voice listener
        t = threading.Thread(target=main.run_jarvis, daemon=True)
        t.start()

    def toggle_widget_mode(self):
        self.is_widget_mode = not self.is_widget_mode

        if self.is_widget_mode:
            # Floating transparent on-top desktop hologram widget
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.WindowStaysOnTopHint |
                Qt.WindowType.SubWindow
            )
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
            self.setStyleSheet("background-color: transparent;")

            screen = QApplication.primaryScreen().geometry()
            self.resize(260, 260)
            self.move(screen.width() - 290, screen.height() - 320)
            self.show()
        else:
            # Return to normal window
            self.setWindowFlags(Qt.WindowType.Window)
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
            self.setStyleSheet("background-color: #000000;")
            self.resize(900, 750)
            screen = QApplication.primaryScreen().geometry()
            self.move((screen.width() - 900) // 2, (screen.height() - 750) // 2)
            self.show()

    def mousePressEvent(self, event):
        if self.is_widget_mode and event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.is_widget_mode and event.buttons() == Qt.MouseButton.LeftButton and self.drag_position is not None:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseDoubleClickEvent(self, event):
        # Double clicking the reactor toggles between floating widget and normal window
        if self.stack.currentWidget() == self.reactor_screen:
            self.toggle_widget_mode()

    def keyPressEvent(self, event):
        # F10: Toggle Floating Desktop Hologram Widget Mode
        if event.key() == Qt.Key.Key_F10:
            self.toggle_widget_mode()
        # F11: Fullscreen mode
        elif event.key() == Qt.Key.Key_F11:
            if not self.is_widget_mode:
                if self.isFullScreen():
                    self.showNormal()
                else:
                    self.showFullScreen()
        # Escape: Exit
        elif event.key() == Qt.Key.Key_Escape:
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JarvisMainWindow()
    window.show()
    sys.exit(app.exec())
