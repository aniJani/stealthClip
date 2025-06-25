import pystray
from PIL import Image, ImageDraw


class UIManager:
    """Manages the system tray icon and its menu."""

    def __init__(self, on_exit):
        self.on_exit = on_exit
        self.icon = self._create_icon()

    def _create_icon(self):
        """Creates the pystray Icon object with a menu."""
        try:
            image = Image.open("icon.png")
        except FileNotFoundError:
            # Create a simple fallback image if icon.png is not found
            image = Image.new("RGB", (64, 64), "black")
            dc = ImageDraw.Draw(image)
            dc.rectangle([10, 10, 54, 54], fill="white")

        menu = pystray.Menu(pystray.MenuItem("Exit", self._on_exit_clicked))

        return pystray.Icon("StealthClip", image, "StealthClip", menu)

    def _on_exit_clicked(self):
        """Stops the icon and calls the main application's shutdown logic."""
        self.icon.stop()
        self.on_exit()

    def run(self):
        """Runs the system tray icon. This is a blocking call."""
        self.icon.run()
