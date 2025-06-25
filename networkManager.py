import socket
import logging
import threading
from cryptoEngine import CryptoEngine

PORT = 50505
DISCOVERY_MSG = b"STEALTHCLIP_DISCOVERY_V1"
BROADCAST_ADDR = "255.255.255.255"


class NetworkManager:
    """Manages peer discovery and clipboard data transmission."""

    def __init__(self, crypto_engine: CryptoEngine, on_data_received):
        self.crypto_engine = crypto_engine
        self.on_data_received = on_data_received
        self.peers = set()
        self.sock = self._create_socket()
        self.is_running = True

    def _create_socket(self):
        """Creates and configures the UDP socket."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind(("", PORT))
        return sock

    def start_listener(self):
        """Listens for incoming broadcast and unicast messages."""
        logging.info(f"Network listener started on port {PORT}")
        while self.is_running:
            try:
                data, addr = self.sock.recvfrom(4096)  # Buffer size

                # Ignore our own messages
                if addr[0] == socket.gethostbyname(socket.gethostname()):
                    continue

                if data == DISCOVERY_MSG:
                    logging.info(f"Discovered peer at {addr[0]}")
                    self.peers.add(addr[0])
                else:
                    # This is potentially clipboard data, try to decrypt it
                    decrypted_data = self.crypto_engine.decrypt(data)
                    if decrypted_data:
                        # If decryption is successful, it's for our group
                        self.on_data_received(decrypted_data.decode("utf-8"))

            except Exception as e:
                if self.is_running:
                    logging.error(f"Error in network listener: {e}")

    def start_discovery(self):
        """Sends a discovery broadcast to find other peers."""
        logging.info("Sending discovery broadcast...")
        self.sock.sendto(DISCOVERY_MSG, (BROADCAST_ADDR, PORT))

    def broadcast_clipboard(self, encrypted_data: bytes):
        """Sends encrypted clipboard data to all known peers via unicast."""
        if not self.peers:
            logging.warning("No peers found yet. Sending broadcast as fallback.")
            self.sock.sendto(encrypted_data, (BROADCAST_ADDR, PORT))
            return

        for peer_ip in list(self.peers):
            try:
                self.sock.sendto(encrypted_data, (peer_ip, PORT))
            except Exception as e:
                logging.error(f"Failed to send to peer {peer_ip}: {e}")
                # Optional: remove peer if sending fails consistently
                # self.peers.remove(peer_ip)

    def stop(self):
        """Stops the network listener and closes the socket."""
        self.is_running = False
        self.sock.close()
        logging.info("Network manager stopped.")
