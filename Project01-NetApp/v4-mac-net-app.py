
import sys
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

        self.ping_button = QPushButton("Ping")
        self.ping_button.setFont(QFont("Consolas", 11))
        self.ping_button.setStyleSheet("background-color: #003300; color: #00FF00;")
        self.ping_button.clicked.connect(self.run_ping)
        input_layout.addWidget(self.ping_button)

        self.stop_ping_button = QPushButton("Stop")
        self.stop_ping_button.setFont(QFont("Consolas", 11))
        self.stop_ping_button.setStyleSheet("background-color: #550000; color: #FF0000;")
        self.stop_ping_button.clicked.connect(self.stop_command)
        input_layout.addWidget(self.stop_ping_button)

        self.save_ping_button = QPushButton("Save Output")
        self.save_ping_button.setFont(QFont("Consolas", 11))
        self.save_ping_button.setStyleSheet("background-color: #003300; color: #00FF00;")
        self.save_ping_button.clicked.connect(lambda: self.save_output(self.ping_output))
        input_layout.addWidget(self.save_ping_button)

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

        self.traceroute_button = QPushButton("Traceroute")
        self.traceroute_button.setFont(QFont("Consolas", 11))
        self.traceroute_button.setStyleSheet("background-color: #003300; color: #00FF00;")
        self.traceroute_button.clicked.connect(self.run_traceroute)
        input_layout.addWidget(self.traceroute_button)

        self.stop_traceroute_button = QPushButton("Stop")
        self.stop_traceroute_button.setFont(QFont("Consolas", 11))
        self.stop_traceroute_button.setStyleSheet("background-color: #550000; color: #FF0000;")
        self.stop_traceroute_button.clicked.connect(self.stop_command)
        input_layout.addWidget(self.stop_traceroute_button)

        self.save_traceroute_button = QPushButton("Save Output")
        self.save_traceroute_button.setFont(QFont("Consolas", 11))
        self.save_traceroute_button.setStyleSheet("background-color: #003300; color: #00FF00;")
        self.save_traceroute_button.clicked.connect(lambda: self.save_output(self.traceroute_output))
        input_layout.addWidget(self.save_traceroute_button)

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

    def create_whois_tab(self):
        """Create the Whois tool tab."""
        layout = QVBoxLayout()

        input_layout = QHBoxLayout()
        self.whois_input = QLineEdit()
        self.whois_input.setPlaceholderText("Enter domain name or IP address")
        self.whois_input.setFont(QFont("Consolas", 11))
        self.whois_input.setStyleSheet("padding: 5px; color: #00FF00; background-color: #111; border: 1px solid #00FF00;")
        input_layout.addWidget(self.whois_input)

        self.whois_button = QPushButton("Run Whois")
        self.whois_button.setFont(QFont("Consolas", 11))
        self.whois_button.setStyleSheet("background-color: #003300; color: #00FF00;")
        self.whois_button.clicked.connect(self.run_whois)
        input_layout.addWidget(self.whois_button)

        self.stop_whois_button = QPushButton("Stop")
        self.stop_whois_button.setFont(QFont("Consolas", 11))
        self.stop_whois_button.setStyleSheet("background-color: #550000; color: #FF0000;")
        self.stop_whois_button.clicked.connect(self.stop_command)
        input_layout.addWidget(self.stop_whois_button)

        self.save_whois_button = QPushButton("Save Output")
        self.save_whois_button.setFont(QFont("Consolas", 11))
        self.save_whois_button.setStyleSheet("background-color: #003300; color: #00FF00;")
        self.save_whois_button.clicked.connect(lambda: self.save_output(self.whois_output))
        input_layout.addWidget(self.save_whois_button)

        layout.addLayout(input_layout)

        self.whois_output = QTextEdit()
        self.whois_output.setReadOnly(True)
        self.whois_output.setFont(QFont("Courier", 10))
        self.whois_output.setStyleSheet(
            "background-color: #111; color: #00FF00; border: 1px solid #00FF00; padding: 10px;"
        )
        layout.addWidget(self.whois_output)

        tab = QWidget()
        tab.setLayout(layout)
        return tab

    def create_nslookup_tab(self):
        """Create the NSLookup tool tab."""
        layout = QVBoxLayout()

        input_layout = QHBoxLayout()
        self.nslookup_input = QLineEdit()
        self.nslookup_input.setPlaceholderText("Enter domain name or IP address")
        self.nslookup_input.setFont(QFont("Consolas", 11))
        self.nslookup_input.setStyleSheet("padding: 5px; color: #00FF00; background-color: #111; border: 1px solid #00FF00;")
        input_layout.addWidget(self.nslookup_input)

        self.nslookup_button = QPushButton("Run NSLookup")
        self.nslookup_button.setFont(QFont("Consolas", 11))
        self.nslookup_button.setStyleSheet("background-color: #003300; color: #00FF00;")
        self.nslookup_button.clicked.connect(self.run_nslookup)
        input_layout.addWidget(self.nslookup_button)

        self.stop_nslookup_button = QPushButton("Stop")
        self.stop_nslookup_button.setFont(QFont("Consolas", 11))
        self.stop_nslookup_button.setStyleSheet("background-color: #550000; color: #FF0000;")
        self.stop_nslookup_button.clicked.connect(self.stop_command)
        input_layout.addWidget(self.stop_nslookup_button)

        self.save_nslookup_button = QPushButton("Save Output")
        self.save_nslookup_button.setFont(QFont("Consolas", 11))
        self.save_nslookup_button.setStyleSheet("background-color: #003300; color: #00FF00;")
        self.save_nslookup_button.clicked.connect(lambda: self.save_output(self.nslookup_output))
        input_layout.addWidget(self.save_nslookup_button)

        layout.addLayout(input_layout)

        self.nslookup_output = QTextEdit()
        self.nslookup_output.setReadOnly(True)
        self.nslookup_output.setFont(QFont("Courier", 10))
        self.nslookup_output.setStyleSheet(
            "background-color: #111; color: #00FF00; border: 1px solid #00FF00; padding: 10px;"
        )
        layout.addWidget(self.nslookup_output)

        tab = QWidget()
        tab.setLayout(layout)
        return tab

    def run_ping(self):
        """Run the Ping command."""
        target = self.ping_input.text()
        if not target:
            self.ping_output.setText("Please enter a valid IP address or hostname.")
            return

        # Clear output area for fresh output
        self.ping_output.clear()

        mode = self.ping_mode_dropdown.currentText()
        command = ["ping", "-c", "4", target] if mode == "Standard Ping" else ["ping", target]
        self.start_command(command, self.ping_output)

    def run_traceroute(self):
        """Run the Traceroute command."""
        target = self.traceroute_input.text()
        if not target:
            self.traceroute_output.setText("Please enter a valid IP address or hostname.")
            return

        # Clear output area for fresh output
        self.traceroute_output.clear()

        command = ["traceroute", target]
        self.start_command(command, self.traceroute_output)

    def run_whois(self):
        """Run the Whois command."""
        target = self.whois_input.text()
        if not target:
            self.whois_output.setText("Please enter a valid domain name or IP address.")
            return

        # Clear output area for fresh output
        self.whois_output.clear()

        command = ["whois", target]
        self.start_command(command, self.whois_output)

    def run_nslookup(self):
        """Run the NSLookup command."""
        target = self.nslookup_input.text()
        if not target:
            self.nslookup_output.setText("Please enter a valid domain name or IP address.")
            return

        # Clear output area for fresh output
        self.nslookup_output.clear()

        command = ["nslookup", target]
        self.start_command(command, self.nslookup_output)

    def start_command(self, command, output_widget):
        """Start a command in a separate thread."""
        if self.worker and self.worker.isRunning():
            output_widget.setText("A command is already running. Please stop it first.")
            return

        self.worker = CommandWorker(command)
        self.worker.output_signal.connect(lambda text: output_widget.append(text))
        self.worker.finished.connect(self.command_finished)
        self.worker.start()

    def stop_command(self):
        """Stop the running command."""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
            self.status_label.setText("Status: Stopped")
        else:
            self.status_label.setText("Status: No command running")

    def save_output(self, output_widget):
        """Save the output to a text file."""
        filename, _ = QFileDialog.getSaveFileName(self, "Save Output", "", "Text Files (*.txt)")
        if filename:
            with open(filename, "w") as file:
                file.write(output_widget.toPlainText())
            self.status_label.setText("Output saved successfully.")

    def command_finished(self):
        """Handle command completion."""
        self.status_label.setText("Status: Ready")


# Run the App
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NetworkUtility()
    window.show()
    sys.exit(app.exec_())