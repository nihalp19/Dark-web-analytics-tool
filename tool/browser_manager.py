import subprocess
import time
import requests

BROWSER_CONFIG = {
    'tor': {
        'command': r"C:\Users\NIHAL\Downloads\tor-expert-bundle-windows-x86_64-14.5.6\tor\tor.exe",
        'check_cmd': r"C:\Users\NIHAL\Downloads\tor-expert-bundle-windows-x86_64-14.5.6\tor\tor.exe --version",
        'socks_port': 9050
    }
}

class BrowserManager:
    def __init__(self):
        self.current_browser = None
        self.process = None
        self.socks_port = None

    def connect(self, browser_type):
        browser_type = browser_type.lower()
        if browser_type not in BROWSER_CONFIG:
            print(f"[-] Unsupported browser: {browser_type}")
            return False

        browser_config = BROWSER_CONFIG[browser_type]
        print(f"[+] Connecting to {browser_type.upper()}...")

        try:
            # Check if Tor exists
            check_cmd = browser_config['check_cmd'].split()
            result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                print(f"[-] {browser_type.upper()} is not installed or not in PATH")
                return False

            # Start Tor process and capture stdout
            cmd = browser_config['command'].split()
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

            # Wait for Tor to fully bootstrap
            if browser_type == 'tor':
                if not self.wait_for_tor_bootstrap():
                    print("[-] Tor did not bootstrap in time")
                    return False
                self.socks_port = browser_config['socks_port']

            # Verify connection via Tor
            if self.verify_connection(browser_type):
                self.current_browser = browser_type
                print(f"[+] Connected to {browser_type.upper()} successfully")
                return True
            else:
                print(f"[-] Failed to verify {browser_type.upper()} connection")
                return False

        except Exception as e:
            print(f"[-] Error connecting to {browser_type.upper()}: {str(e)}")
            return False

    def wait_for_tor_bootstrap(self, timeout=300):
        """Wait until Tor reports 100% bootstrapped."""
        start_time = time.time()
        print("[*] Waiting for Tor to bootstrap...")
        while True:
            if time.time() - start_time > timeout:
                return False
            line = self.process.stdout.readline()
            if not line:
                time.sleep(1)
                continue
            line = line.strip()
            print("[Tor]", line)  # Optional: show Tor logs
            if "Bootstrapped 100%" in line:
                return True

    def verify_connection(self, browser_type):
        """Check if Tor proxy is working by fetching external IP."""
        try:
            session = requests.session()
            if browser_type == 'tor':
                session.proxies = {
                    'http': f"socks5h://127.0.0.1:{self.socks_port}",
                    'https': f"socks5h://127.0.0.1:{self.socks_port}"
                }
                response = session.get("https://httpbin.org/ip", timeout=10)
                if response.status_code == 200:
                    print(f"[Tor] External IP via Tor: {response.text}")
                    return True
            return True
        except Exception as e:
            print(f"[-] Tor verification error: {e}")
            return False


    def get_proxy_settings(self):
        """Get the current proxy settings for the connected browser."""
        if not self.current_browser:
            return None

        if self.current_browser == 'tor':
            return {
                'http': f"socks5h://127.0.0.1:{self.socks_port}",
                'https': f"socks5h://127.0.0.1:{self.socks_port}"
            }
        # Add more browsers if needed
        return None


    def disconnect(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.current_browser = None
            self.socks_port = None
            print("[+] Browser disconnected")
