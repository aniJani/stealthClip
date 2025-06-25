import pyperclip
import time
import logging
import threading


class ClipboardMonitor:
    """Monitors the clipboard for changes and triggers updates."""

    def __init__(self, on_clipboard_change):
        self.on_clipboard_change = on_clipboard_change
        self.last_sent_content = ""
        self.last_received_content = ""
        self.is_running = True
        self.lock = (
            threading.Lock()
        )  # To safely access state variables from different threads

    def start_monitoring(self):
        """Starts the clipboard polling loop."""
        logging.info("Clipboard monitor started.")
        # Initialize last_sent_content with current clipboard to avoid initial broadcast
        try:
            self.last_sent_content = pyperclip.paste()
        except pyperclip.PyperclipException:
            self.last_sent_content = ""

        while self.is_running:
            try:
                current_content = pyperclip.paste()

                with self.lock:
                    # This is the crucial logic to prevent echo loops.
                    # Only broadcast if the change is new and wasn't set by us from the network.
                    if (
                        current_content
                        and current_content != self.last_sent_content
                        and current_content != self.last_received_content
                    ):
                        logging.info("New local clipboard change detected.")
                        self.last_sent_content = current_content
                        self.on_clipboard_change(current_content)

            except pyperclip.PyperclipException as e:
                # This can happen on some systems when the clipboard is empty or being used.
                # It's usually safe to ignore.
                pass

            time.sleep(0.5)  # Poll every 500ms

    def update_clipboard_from_network(self, data: str):
        """Updates the clipboard with data received from a peer."""
        with self.lock:
            # Set the last_received_content *before* changing the clipboard
            # to prevent our own monitor from re-broadcasting it.
            self.last_received_content = data

        try:
            pyperclip.copy(data)
            logging.info("Clipboard updated from network.")
        except pyperclip.PyperclipException as e:
            logging.error(f"Failed to update clipboard: {e}")

    def stop(self):
        self.is_running = False
