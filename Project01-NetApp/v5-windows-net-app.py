import sys
import platform
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QWidget, QLineEdit, QTextEdit, QTabWidget, QFileDialog, QComboBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal


# Worker Thread to Run Commands (Ping/Traceroute/Whois/NSLookup)
class CommandWorker(QThread):
    output_signal = pyqtSignal(str)  # Signal to send output back to GUI

    def __init__(self, command):
        super().__init__()
        self.command = command
        self.process = None

    def run(self):
        try:
            self.process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in iter(self.process.stdout.readline, ''):
                self.output_signal.emit(line)
            self.process.stdout.close()
            self.process.wait()
        except Exception as e:
            self.output_signal.emit(f"Error: {str(e)}")

    def stop(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()


# Helper Functions to Adjust Commands Based on OS
def get_ping_command(target, mode):
    """Get the ping command based on the operating system."""
    if platform.system() == "Windows":
        if mode == "Standard Ping":
            return ["ping", "-n", "4", target]
        elif mode == "Continuous Ping":
            return ["ping", "-t", target]  # Continuous ping on Windows
    else:  # macOS/Linux
        if mode == "Standard Ping":
            return ["ping", "-c", "4", target]
        elif mode == "Continuous Ping":
            return ["ping", target]  # Continuous ping by default on macOS/Linux


# Main GUI Class
class NetworkUtility(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Network Utility - Ping, Traceroute, Whois, NSLookup")
        self.setGeometry(300, 100, 800, 600)
        self.setStyleSheet("background-color: #0d1117; color: #00FF00;")

        # Main Layout
        main_layout = QVBoxLayout()

        # Tab Widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("QTabBar::tab { background: #003300; color: #00FF00; padding: 10px; }")

        # Add Tabs
        self.ping_tab = self.create_ping_tab()
        self.traceroute_tab = self.create_traceroute_tab()
        self.whois_tab = self.create_whois_tab()
        self.nslookup_tab = self.create_nslookup_tab()

        self.tab_widget.addTab(self.ping_tab, "Ping")
        self.tab_widget.addTab(self.traceroute_tab, "Traceroute")
        self.tab_widget.addTab(self.whois_tab, "Whois")
        self.tab_widget.addTab(self.nslookup_tab, "NSLookup")

        main_layout.addWidget(self.tab_widget)

        # Status Bar
        self.status_label = QLabel("Status: Ready")
        self.status_label.setFont(QFont("Consolas", 10))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #00FFFF; margin-top: 5px;")
        main_layout.addWidget(self.status_label)

        # Set Central Widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Initialize Worker
        self.worker = None

    def create_ping_tab(self):
        """Create the Ping tool tab."""
        layout = QVBoxLayout()

        input_layout = QHBoxLayout()
        self.ping_input = QLineEdit()
        self.ping_input.setPlaceholderText("Enter IP address or hostname")
        self.ping_input.setFont(QFont("Consolas", 11))
        self.ping_input.setStyleSheet("padding: 5px; color: #00FF00; background-color: #111; border: 1px solid #00FF00;")
        input_layout.addWidget(self.ping_input)

        self.ping_mode_dropdown = QComboBox()
        self.ping_mode_dropdown.addItems(["Standard Ping", "Continuous Ping"])
        self.ping_mode_dropdown.setFont(QFont("Consolas", 11))
        self.ping_mode_dropdown.setStyleSheet("background-color: #003300; color: #00FF00; padding: 5px;")
        input_layout.addWidget(self.ping_mode_dropdown)

        button_layout = QHBoxLayout()
        self.ping_button = QPushButton("Ping")
        self.ping_button.setFont(QFont("Consolas", 11))
        self.ping_button.setFixedSize(100, 40)
        self.ping_button.setStyleSheet("background-color: #003300; color: #00FF00;")
        self.ping_button.clicked.connect(self.run_ping)
        button_layout.addWidget(self.ping_button)

        self.stop_ping_button = QPushButton("Stop")
        self.stop_ping_button.setFont(QFont("Consolas", 11))
        self.stop_ping_button.setFixedSize(100, 40)
        self.stop_ping_button.setStyleSheet("background-color: #550000; color: #FF0000;")
        self.stop_ping_button.clicked.connect(self.stop_command)
        button_layout.addWidget(self.stop_ping_button)

        self.save_ping_button = QPushButton("Save Output")
        self.save_ping_button.setFont(QFont("Consolas", 11))
        self.save_ping_button.setFixedSize(100, 40)
        self.save_ping_button.setStyleSheet("background-color: #003300; color: #00FF00;")
        self.save_ping_button.clicked.connect(lambda: self.save_output(self.ping_output))
        button_layout.addWidget(self.save_ping_button)

        # Center buttons
        input_layout.addStretch()
        input_layout.addLayout(button_layout)
        input_layout.addStretch()

        layout.addLayout(input_layout)

        self.ping_output = QTextEdit()
        self.ping_output.setReadOnly(True)
        self.ping_output.setFont(QFont("Courier", 10))
        self.ping_output.setStyleSheet(
            "background-color: #111; color: #00FF00; border: 1px solid #00FF00; padding: 10px;"
        )
        layout.addWidget(self.ping_output)

        tab = QWidget()
        tab.setLayout(layout)
        return tab

    def create_traceroute_tab(self):
        """Create the Traceroute tool tab."""
        layout = QVBoxLayout()

        input_layout = QHBoxLayout()
        self.traceroute_input = QLineEdit()
        self.traceroute_input.setPlaceholderText("Enter IP address or hostname")
        self.traceroute_input.setFont(QFont("Consolas", 11))
        self.traceroute_input.setStyleSheet("padding: 5px; color: #00FF00; background-color: #111; border: 1px solid #00FF00;")
        input_layout.addWidget(self.traceroute_input)

        button_layout = QHBoxLayout()
        self.traceroute_button = QPushButton("Traceroute")
        self.traceroute_button.setFont(QFont("Consolas", 11))
        self.traceroute_button.setFixedSize(120, 40)
        self.traceroute_button.setStyleSheet("background-color: #003300; color: #00FF00;")
        self.traceroute_button.clicked.connect(self.run_traceroute)
        button_layout.addWidget(self.traceroute_button)

        self.stop_traceroute_button = QPushButton("Stop")
        self.stop_traceroute_button.setFont(QFont("Consolas", 11))
        self.stop_traceroute_button.setFixedSize(100, 40)
        self.stop_traceroute_button.setStyleSheet("background-color: #550000; color: #FF0000;")
        self.stop_traceroute_button.clicked.connect(self.stop_command)
        button_layout.addWidget(self.stop_traceroute_button)

        self.save_traceroute_button = QPushButton("Save Output")
        self.save_traceroute_button.setFont(QFont("Consolas", 11))
        self.save_traceroute_button.setFixedSize(100, 40)
        self.save_traceroute_button.setStyleSheet("background-color: #003300; color: #00FF00;")
        self.save_traceroute_button.clicked.connect(lambda: self.save_output(self.traceroute_output))
        button_layout.addWidget(self.save_traceroute_button)

        input_layout.addStretch()
        input_layout.addLayout(button_layout)
        input_layout.addStretch()

        layout.addLayout(input_layout)

        self.traceroute_output = QTextEdit()
        self.traceroute_output.setReadOnly(True)
        self.traceroute_output.setFont(QFont("Courier", 10))
        self.traceroute_output.setStyleSheet(
            "background-color: #111; color: #00FF00; border: 1px solid #00FF00; padding: 10px;"
        )
        layout.addWidget(self.traceroute_output)

        tab = QWidget()
        tab.setLayout(layout)
        return tab

    # The Whois and NSLookup tabs can be updated similarly to ensure consistency

    # Add the other methods for whois, nslookup, and command handling as needed...


# Run the App
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Consolas", 11))  # Global font setting
    window = NetworkUtility()
    window.show()
    sys.exit(app.exec_())