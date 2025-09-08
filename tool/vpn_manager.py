import subprocess
import time
import os
from config import VPN_CONFIG


class VPNManager:
    def __init__(self):
        self.process = None
        self.connected = False

    def _connect_single(self, openvpn_path, config_path, auth_path):
        """Connect to a single VPN config"""
        print(f"[+] Connecting to VPN using {config_path}")

        if not os.path.exists(openvpn_path):
            print(f"[-] OpenVPN not found at {openvpn_path}")
            return False

        if not os.path.exists(config_path):
            print(f"[-] Config file not found: {config_path}")
            return False

        # Build command
        cmd = [
            openvpn_path,
            "--config", config_path,
            "--auth-user-pass", auth_path
        ]

        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Check connection status
            timeout = 25  # seconds
            start_time = time.time()
            while time.time() - start_time < timeout:
                output = self.process.stdout.readline()
                if output:
                    print(output.strip())
                    if "Initialization Sequence Completed" in output:
                        print(f"[+] Connected with {config_path}")
                        self.connected = True
                        return True
                if self.process.poll() is not None:
                    stdout, stderr = self.process.communicate()
                    print(f"[-] VPN exited early:\n{stdout}\n{stderr}")
                    return False

            print("[-] VPN connection timed out.")
            return False

        except Exception as e:
            print(f"[-] VPN connection error: {str(e)}")
            return False

    def disconnect(self):
        """Disconnect VPN"""
        if self.process:
            self.process.terminate()
            self.process.wait()
        self.process = None
        self.connected = False
        print("[+] VPN disconnected")

    def is_connected(self):
        return self.connected and self.process and self.process.poll() is None

    def rotate_connections(self, interval=600):
        """Rotate VPN servers every X seconds (default = 10 minutes)"""
        configs = VPN_CONFIG.get("configs", [])

        if not configs:
            print("[-] No VPN configs found in VPN_CONFIG")
            return

        idx = 0
        while True:
            cfg = configs[idx]
            print(f"\n[=] Switching to config: {cfg['config_path']}")
            
            success = self._connect_single(
                VPN_CONFIG["openvpn_path"],
                cfg["config_path"],
                cfg["auth_path"]
            )

            if not success:
                print("[-] Failed to connect, skipping to next...")
            else:
                time.sleep(interval)  # stay connected for 10 min
                self.disconnect()

            # Rotate to next config
            idx = (idx + 1) % len(configs)
