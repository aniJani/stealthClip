# StealthClip 📋

<p align="center">
  A secure, peer-to-peer clipboard synchronization tool for local networks.
  <br>
  Share your clipboard between multiple computers securely and invisibly.
</p>

---

## ✨ Features

- **Secure by Design:** Uses strong **AES-256 encryption**. Your clipboard data is end-to-end encrypted and never exposed on the network.
- **Truly Peer-to-Peer:** No central server or internet connection required. Devices communicate directly on your local network.
- **Private Groups:** Use a shared password to create a private clipboard group. Multiple groups can coexist on the same network without interfering with each other.
- **Stealthy Operation:** Runs silently in the background with only a system tray icon. No annoying console windows.
- **Lightweight & Fast:** Has a minimal footprint on CPU, RAM, and network resources. Updates are nearly instantaneous.
- **Cross-Platform:** Works on Windows, macOS, and Linux. Sync your clipboard between different operating systems seamlessly.
- **Standalone Executable:** Packaged into a single file for each OS. No installation or dependencies required for end-users.

## 🚀 How to Use (For Users)

Getting started is simple. No installation is needed.

1.  Go to the [**Releases Page**].
2.  Download the latest executable file for your operating system (`.exe` for Windows, `.app` for macOS, binary for Linux).
3.  Run the application on your first computer.
4.  When prompted, enter a strong, secret password. This password defines your private sync group.
5.  Run the application on your other computers and enter the **exact same password**.

That's it! Your clipboards are now synchronized. Any text you copy on one machine will be available on the others.

## 🛠️ How to Build from Source
If you prefer to build the application yourself:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/aniJani/stealthClip
    cd stealthClip
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows:
    # venv\Scripts\activate
    # On macOS/Linux:
    # source venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run the script:**
    ```bash
    python main.py
    ```
5.  **To package the executable for your OS:**
    ```bash
    pyinstaller main.py --noconsole --onefile --name StealthClip --add-data "icon.png:."
    ```
    The final application will be in the `dist/` folder.

## ⚙️ How It Works

StealthClip operates on a simple but robust principle:

1.  **Key Generation:** A secure AES key is derived from your shared password using `PBKDF2HMAC`. The same password always generates the same key.
2.  **Peer Discovery:** On startup, each client sends a UDP broadcast packet to the local network to announce its presence.
3.  **Direct Communication:** When other clients receive a discovery packet, they add the new peer's IP to a list and communicate directly via **unicast** from then on. This is efficient and stealthy.
4.  **Syncing:** When your clipboard changes, the new content is encrypted with the AES key and sent directly to all known peers.
5.  **Decryption:** Peers receiving data attempt to decrypt it. If successful (meaning they share the same password/key), they update their local clipboard. If not, the packet is silently ignored.

## 🏗️ Technology Stack

| Purpose                     | Tool / Library                |
| --------------------------- | ----------------------------- |
| Programming Language        | **Python 3.10+**              |
| Clipboard Access            | `pyperclip`                   |
| GUI (System Tray)           | `pystray` + `Pillow`          |
| Networking                  | `socket` (UDP Broadcast/Unicast) |
| Encryption                  | `cryptography` (Fernet)       |
| Packaging                   | `pyinstaller`                 |

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.