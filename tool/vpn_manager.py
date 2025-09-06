import subprocess
import time
import os
from config import VPN_CONFIG

class VPNManager:
    def __init__(self):
        self.process = None
        self.connected = False

    def connect(self):
        """Connect to VPN using OpenVPN CLI"""
        print("[+] Connecting to VPN...")

        openvpn_path = r"C:\Program Files\OpenVPN\bin\openvpn.exe"

        # Check if OpenVPN exists
        if not os.path.exists(openvpn_path):
            print(f"[-] OpenVPN not found at {openvpn_path}")
            return False

        # Build command
        cmd = [
            openvpn_path,
            "--config", VPN_CONFIG["config_path"],
            "--auth-user-pass", VPN_CONFIG["auth_path"]
        ]

        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Check connection status
            timeout = 15  # seconds
            start_time = time.time()
            while time.time() - start_time < timeout:
                output = self.process.stdout.readline()
                if output:
                    print(output.strip())
                    # Detect successful connection message
                    if "Initialization Sequence Completed" in output:
                        self.connected = True
                        print("[+] VPN connected successfully!")
                        return True
                if self.process.poll() is not None:
                    # Process exited unexpectedly
                    stdout, stderr = self.process.communicate()
                    print(f"[-] VPN process exited. Logs:\n{stdout}\n{stderr}")
                    return False

            # Timeout reached without success
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
            self.connected = False
            print("[+] VPN disconnected")

    def is_connected(self):
        """Check VPN status"""
        # Also check if process is still running
        if self.process and self.process.poll() is None:
            return self.connected
        return False
