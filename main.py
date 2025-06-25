import sys
import logging
import threading
from tkinter import simpledialog, Tk

from cryptoEngine import CryptoEngine
from networkManager import NetworkManager
from clipboardMonitor import ClipboardMonitor
from uiManager import UIManager

# Setup basic logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(threadName)s - %(message)s"
)


class MainApp:
    def __init__(self):
        self.crypto_engine = None
        self.network_manager = None
        self.clipboard_monitor = None
        self.ui_manager = None

    def get_password(self):
        """Shows a password dialog to get the shared secret."""
        root = Tk()
        root.withdraw()  # Hide the main tkinter window
        password = simpledialog.askstring(
            "Password", "Enter network password:", show="*"
        )
        root.destroy()

        if not password:
            logging.warning("No password entered. Exiting.")
            sys.exit(0)

        return password.encode("utf-8")

    def start(self):
        """Initializes and starts all application components."""
        logging.info("Starting StealthClip application...")

        password = self.get_password()
        self.crypto_engine = CryptoEngine(password)
        logging.info("Encryption key generated successfully.")

        self.clipboard_monitor = ClipboardMonitor(
            on_clipboard_change=self.handle_local_clipboard_change
        )

        self.network_manager = NetworkManager(
            crypto_engine=self.crypto_engine,
            on_data_received=self.clipboard_monitor.update_clipboard_from_network,
        )

        self.ui_manager = UIManager(on_exit=self.shutdown)

        # Start background threads
        self._start_thread(self.network_manager.start_listener, "NetworkListener")
        self._start_thread(self.clipboard_monitor.start_monitoring, "ClipboardMonitor")

        # Start peer discovery
        self.network_manager.start_discovery()

        # Start the UI (this blocks the main thread)
        logging.info("Application is running. Control via system tray icon.")
        self.ui_manager.run()

    def _start_thread(self, target, name):
        """Helper to start a daemon thread."""
        thread = threading.Thread(target=target, name=name, daemon=True)
        thread.start()

    def handle_local_clipboard_change(self, data: str):
        """Encrypts local changes and tells the network manager to send them."""
        encrypted_data = self.crypto_engine.encrypt(data.encode("utf-8"))
        self.network_manager.broadcast_clipboard(encrypted_data)

    def shutdown(self):
        """Gracefully shuts down the application."""
        logging.info("Shutdown requested. Cleaning up...")
        if self.clipboard_monitor:
            self.clipboard_monitor.stop()
        if self.network_manager:
            self.network_manager.stop()
        logging.info("StealthClip has exited.")
        sys.exit(0)


if __name__ == "__main__":
    app = MainApp()
    try:
        app.start()
    except (KeyboardInterrupt, SystemExit):
        app.shutdown()
    except Exception as e:
        logging.critical(f"A critical error occurred: {e}", exc_info=True)
