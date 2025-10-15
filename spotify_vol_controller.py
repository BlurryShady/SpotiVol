import sys
import threading
import requests
import traceback
import webbrowser
import json
import os
from urllib.parse import urlencode
from http.server import HTTPServer, BaseHTTPRequestHandler

from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, QSlider,
                             QVBoxLayout, QHBoxLayout, QComboBox, QTabWidget, QGroupBox, QMessageBox, QDialog)
from PyQt5.QtCore import Qt, QEvent, pyqtSignal, QObject

"""
importing sys lets us use the runtime environment of Python.
importing threading lets us use multiple threads.
importing requests lets us make HTTP requests for API usage.
importing traceback is for error debugging.
importing webbrowser opens URL in your default browser.
importing json helps us on read/write structured data that is on json format.
importing os lets us interact with operating system to check files existance.
urllib.parse and http.server parts lets us create local server. For this app it helps us to get Spotify credentials.
PyQt5 and things I import from there are essential for the GUI I am creating. They let me use the buttons and create all
the design of the GUI.
"""


class SettingsDialog(QDialog):
    """Dialog for entering Spotify API credentials"""

    def __init__(self, parent=None, current_id="", current_secret=""):
        super().__init__(parent)
        self.setWindowTitle("Spotify API Settings")
        self.setModal(True)
        self.setFixedWidth(500)

        layout = QVBoxLayout()
#The part above creates the GUI of Spotify API setting part.
        # Instructions
        instructions = QLabel(
            "To use Spotify Web API mode, you need to create a Spotify app:\n\n"
            "1. Go to: https://developer.spotify.com/dashboard\n"
            "2. Click 'Create an App'\n"
            "3. In Settings, add Redirect URI: http://localhost:8888/callback\n"
            "4. Copy your Client ID and Client Secret below:"
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # Client ID
        layout.addWidget(QLabel("Client ID:"))
        self.client_id_input = QLineEdit()
        self.client_id_input.setText(current_id)
        self.client_id_input.setPlaceholderText("Paste your Client ID here")
        layout.addWidget(self.client_id_input)

        # Client Secret
        layout.addWidget(QLabel("Client Secret:"))
        self.client_secret_input = QLineEdit()
        self.client_secret_input.setText(current_secret)
        self.client_secret_input.setPlaceholderText("Paste your Client Secret here")
        self.client_secret_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.client_secret_input)
        #The code above allows the user to enter and save their Client ID and Client Secret.
        # Buttons
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def get_credentials(self):
        """Return entered credentials"""
        return self.client_id_input.text().strip(), self.client_secret_input.text().strip()


# Spotify OAuth Configuration
REDIRECT_URI = "http://localhost:8888/callback"
SCOPE = "user-modify-playback-state user-read-playback-state"
TOKEN_FILE = "spotify_tokens.json"
SETTINGS_FILE = "spotify_settings.json"
#Part above is essential for Spotify API usage. That's how we use the things we gain from API.

class SpotifyAuth:
    """Handles Spotify OAuth authentication and token management"""

    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.client_id = None
        self.client_secret = None
        self.load_settings()
        self.load_tokens()

    def load_settings(self):
        """This part loads Client ID and Secret from file"""
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    data = json.load(f)
                    self.client_id = data.get('client_id')
                    self.client_secret = data.get('client_secret')
            except Exception as e:
                print(f"Failed to load settings: {e}")

    def save_settings(self):
        """Save Client ID and Secret to file"""
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump({
                    'client_id': self.client_id,
                    'client_secret': self.client_secret
                }, f)
        except Exception as e:
            print(f"Failed to save settings: {e}")

    def load_tokens(self):
        """Load saved tokens from file"""
        if os.path.exists(TOKEN_FILE):
            try:
                with open(TOKEN_FILE, 'r') as f:
                    data = json.load(f)
                    self.access_token = data.get('access_token')
                    self.refresh_token = data.get('refresh_token')
            except Exception as e:
                print(f"Failed to load tokens: {e}")

    def save_tokens(self):
        """Save tokens to file"""
        try:
            with open(TOKEN_FILE, 'w') as f:
                json.dump({
                    'access_token': self.access_token,
                    'refresh_token': self.refresh_token
                }, f)
        except Exception as e:
            print(f"Failed to save tokens: {e}")

    def get_auth_url(self):
        """Generate Spotify authorization URL"""
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': REDIRECT_URI,
            'scope': SCOPE,
        }
        return f"https://accounts.spotify.com/authorize?{urlencode(params)}"
        #part above gives the specific link (spotify API source) to user so they can get Client ID and Client Secret.

    def exchange_code(self, code):
        #This part gets access_tokens and refresh_Tokens. With access_tokens app serves the user and with refresh_tokens
        #app gets fresh access_tokens. Access_tokens are active for an hour so it's a necessary part for app to work.
        try:
            data = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': REDIRECT_URI,
                'client_id': self.client_id,
                'client_secret': self.client_secret,
            }
            r = requests.post('https://accounts.spotify.com/api/token', data=data)
            if r.status_code == 200:
                tokens = r.json()
                self.access_token = tokens['access_token']
                self.refresh_token = tokens.get('refresh_token')
                self.save_tokens()
                return True, "Successfully authenticated!"
            else:
                return False, f"Token exchange failed: {r.status_code} - {r.text}"
        except Exception as e:
            return False, f"Error exchanging code: {e}"

    def refresh_access_token(self):
        """Refresh the access token using refresh token"""
        if not self.refresh_token:
            return False, "No refresh token available"

        try:
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token,
                'client_id': self.client_id,
                'client_secret': self.client_secret,
            }
            r = requests.post('https://accounts.spotify.com/api/token', data=data)
            if r.status_code == 200:
                tokens = r.json()
                self.access_token = tokens['access_token']
                # Refresh token might be updated
                if 'refresh_token' in tokens:
                    self.refresh_token = tokens['refresh_token']
                self.save_tokens()
                return True, "Token refreshed successfully"
            else:
                return False, f"Token refresh failed: {r.status_code}"
        except Exception as e:
            return False, f"Error refreshing token: {e}"
        #Part above refreshes token that user gave and gives feedback about situation of the token since it's essential


class CallbackHandler(BaseHTTPRequestHandler):
    """HTTP server to handle OAuth callback"""
    auth_code = None

    def do_GET(self):
        if '/callback' in self.path:
            # Extracts code from query parameters
            if '?code=' in self.path:
                code = self.path.split('?code=')[1].split('&')[0]
                CallbackHandler.auth_code = code

                # Sends success response
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"""
                    <html>
                    <body>
                        <h1>Success!</h1>
                        <p>You can close this window and return to the application.</p>
                    </body>
                    </html>
                """)
            else:
                # Send error response
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<h1>Error: No code received</h1>')
        else:
            self.send_response(404)
            self.end_headers()
        #Those functions create mini web server so Spotify can send it's data to there.

    def log_message(self, format, *args):
        pass  # Suppress server logs


class AuthSignals(QObject):
    """Signals for OAuth callbacks"""
    auth_complete = pyqtSignal(bool, str)


class ProfileWidget(QGroupBox):
    #Widget for a single profile (slider, hotkey, bind/unbind/apply)

    def __init__(self, title: str, set_volume_callback):
        super().__init__(title)
        self.set_volume_callback = set_volume_callback
        self.bound_hotkey_id = None

        # volume slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(50)
        self.slider.setTickInterval(5)
        self.slider.valueChanged.connect(self.on_slider_change)
        self.value_label = QLabel("50%")

        # hotkey input
        self.hotkey_input = QLineEdit()
        self.hotkey_input.setPlaceholderText("e.g. F9 or ctrl+alt+v")

        # buttons
        self.bind_btn = QPushButton("Bind")
        self.unbind_btn = QPushButton("Unbind")
        self.apply_btn = QPushButton("Apply")

        self.bind_btn.clicked.connect(self.bind_hotkey)
        self.unbind_btn.clicked.connect(self.unbind_hotkey)
        self.apply_btn.clicked.connect(self.apply_now)

        # layout
        layout = QVBoxLayout()
        s_layout = QHBoxLayout()
        s_layout.addWidget(QLabel("Volume:"))
        s_layout.addWidget(self.slider)
        s_layout.addWidget(self.value_label)
        layout.addLayout(s_layout)

        hk_layout = QHBoxLayout()
        hk_layout.addWidget(QLabel("Hotkey:"))
        hk_layout.addWidget(self.hotkey_input)
        layout.addLayout(hk_layout)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.bind_btn)
        btn_layout.addWidget(self.unbind_btn)
        btn_layout.addWidget(self.apply_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
    #all codes in this function used to create buttons and layouts for profile part

    def on_slider_change(self, v):
        self.value_label.setText(f"{v}%")

    def get_config(self):
        return {
            "volume": int(self.slider.value()),
            "hotkey": self.hotkey_input.text().strip()
        }

    def apply_now(self):
        cfg = self.get_config()
        threading.Thread(target=self.set_volume_callback, args=(cfg["volume"],), daemon=True).start()

    def bind_hotkey(self):
        try:
            import keyboard
        except ImportError:
            QMessageBox.warning(self, "keyboard not available",
                                "Install the 'keyboard' package to use global hotkeys.")
            return

        cfg = self.get_config()
        key = cfg["hotkey"]
        if not key:
            QMessageBox.information(self, "No hotkey", "Enter a hotkey to bind (e.g. F9).")
            return
        if self.bound_hotkey_id is not None:
            QMessageBox.information(self, "Already bound", f"Already bound to {key}. Unbind first.")
            return

        try:
            import keyboard
            handler = keyboard.add_hotkey(
                key,
                lambda: threading.Thread(
                    target=self.set_volume_callback,
                    args=(cfg["volume"],),
                    daemon=True
                    #daemon is used for background running. It makes background threads stop automatically.
                    #we do it here instead of main so entire GUI won't freeze. It makes critical callbacks run in
                    #background so app can work with flow

                ).start()
            )
            self.bound_hotkey_id = handler
            self.bind_btn.setEnabled(False)
            self.unbind_btn.setEnabled(True)
        except Exception as e:
            QMessageBox.warning(self, "Bind failed",
                                f"Could not bind hotkey: {e}\n\n{traceback.format_exc()}")

    def unbind_hotkey(self):
        try:
            import keyboard
        except ImportError:
            return

        if self.bound_hotkey_id is None:
            QMessageBox.information(self, "Not bound", "No hotkey is currently bound.")
            return
        try:
            keyboard.remove_hotkey(self.bound_hotkey_id)
        except Exception:
            key = self.hotkey_input.text().strip()
            if key:
                try:
                    keyboard.remove_hotkey(key)
                except Exception:
                    pass
        self.bound_hotkey_id = None
        self.bind_btn.setEnabled(True)
        self.unbind_btn.setEnabled(False)
        #The function above unbinds the hotkey and disables the ‘Unbind’ button if no key is currently bound.


class MainWindow(QWidget):
    #Main class. It has all the details of design and bindings of buttons.
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spotify Volume Controller — Profiles")
        self.setGeometry(400, 200, 600, 400)

        # Initialize Spotify auth
        self.spotify_auth = SpotifyAuth()
        self.auth_signals = AuthSignals()
        self.auth_signals.auth_complete.connect(self.on_auth_complete)

        # Check for optional libraries
        self.check_dependencies()

        # Top controls
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Local (Windows, pycaw)", "Spotify Web API"])
        self.mode_combo.currentIndexChanged.connect(self.on_mode_change)

        # Login button for Spotify API
        self.login_btn = QPushButton("Login to Spotify")
        self.login_btn.clicked.connect(self.start_spotify_login)

        self.settings_btn = QPushButton("API Settings")
        self.settings_btn.clicked.connect(self.open_settings)

        self.logout_btn = QPushButton("Logout")
        self.logout_btn.clicked.connect(self.logout_spotify)
        self.logout_btn.setEnabled(False)

        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Mode:"))
        top_layout.addWidget(self.mode_combo)
        top_layout.addWidget(self.login_btn)
        top_layout.addWidget(self.settings_btn)
        top_layout.addWidget(self.logout_btn)

        # Tabs for profiles
        self.tabs = QTabWidget()
        self.profile1 = ProfileWidget("Profile 1", self.apply_volume)
        self.profile2 = ProfileWidget("Profile 2", self.apply_volume)
        self.tabs.addTab(self.profile1, "Profile 1")
        self.tabs.addTab(self.profile2, "Profile 2")

        # Status label
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addWidget(self.tabs)
        layout.addWidget(self.status_label)
        self.setLayout(layout)

        # Update UI based on current auth state
        self.update_auth_ui()

        # initial state
        self.on_mode_change(0)

    def check_dependencies(self):
        #this function checks are optional dependencies are available or not.
        self.LOCAL_AVAILABLE = False
        self.KEYBOARD_AVAILABLE = False

        try:
            from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
            from comtypes import CLSCTX_ALL
            self.LOCAL_AVAILABLE = True
        except Exception:
            pass

        try:
            import keyboard
            self.KEYBOARD_AVAILABLE = True
        except Exception:
            pass

    def update_auth_ui(self):
        #Updates buttons, labels based on whether used logged into Spotify API.
        if self.spotify_auth.access_token:
            self.login_btn.setEnabled(False)
            self.logout_btn.setEnabled(True)
            self.status_label.setText("✓ Logged in to Spotify API")
        else:
            self.login_btn.setEnabled(True)
            self.logout_btn.setEnabled(False)

    def open_settings(self):
        #dialog settings when setting is opened by user
        dialog = SettingsDialog(
            self,
            self.spotify_auth.client_id or "",
            self.spotify_auth.client_secret or ""
        )

        if dialog.exec_() == QDialog.Accepted:
            client_id, client_secret = dialog.get_credentials()

            if client_id and client_secret:
                self.spotify_auth.client_id = client_id
                self.spotify_auth.client_secret = client_secret
                self.spotify_auth.save_settings()
                QMessageBox.information(self, "Settings Saved",
                                        "API credentials saved! You can now login to Spotify.")
            else:
                QMessageBox.warning(self, "Invalid Input",
                                    "Please enter both Client ID and Client Secret.")

    def start_spotify_login(self):
        #messages to send when user wants to use API but didn't put API credentials
        if not self.spotify_auth.client_id or not self.spotify_auth.client_secret:
            reply = QMessageBox.question(
                self,
                "API Settings Required",
                "You need to configure your Spotify API credentials first.\n\n"
                "Would you like to open the settings now?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.open_settings()
            return

        self.status_label.setText("Opening browser for Spotify login...")

        # Start callback server in background thread
        def run_server():
            server = HTTPServer(('localhost', 8888), CallbackHandler)
            server.timeout = 120  # 2 minute timeout to make it safe
            CallbackHandler.auth_code = None

            # Open browser
            webbrowser.open(self.spotify_auth.get_auth_url())

            # Wait for callback
            server.handle_request()

            # Process the code
            if CallbackHandler.auth_code:
                success, message = self.spotify_auth.exchange_code(CallbackHandler.auth_code)
                self.auth_signals.auth_complete.emit(success, message)
            else:
                self.auth_signals.auth_complete.emit(False, "No authorization code received")

        threading.Thread(target=run_server, daemon=True).start()

    def on_auth_complete(self, success, message): #Messages to send when everything goes smooth
        if success:
            self.update_auth_ui()
            QMessageBox.information(self, "Success", "Successfully logged in to Spotify!")
        else:
            QMessageBox.warning(self, "Login Failed", f"Failed to login: {message}")
        self.status_label.setText(message)

    def logout_spotify(self):
        #Removes all credentials when logging out.
        self.spotify_auth.access_token = None
        self.spotify_auth.refresh_token = None
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)
        self.update_auth_ui()
        self.status_label.setText("Logged out from Spotify")

    def on_mode_change(self, index):
        #With this code macOS-Linux users will get error on local mode since I've used pycaw.
        mode_text = self.mode_combo.currentText()
        if "Local" in mode_text:
            self.login_btn.setVisible(False)
            self.settings_btn.setVisible(False)
            self.logout_btn.setVisible(False)
            if not self.LOCAL_AVAILABLE:
                self.status_label.setText(
                    "Local mode not available: pycaw/comtypes not installed or not running on Windows.")
            else:
                self.status_label.setText("Local mode selected. Hotkeys will change the Spotify desktop app volume.")
        else:
            self.login_btn.setVisible(True)
            self.settings_btn.setVisible(True)
            self.logout_btn.setVisible(True)
            if self.spotify_auth.access_token:
                self.status_label.setText("Spotify Web API mode. You're logged in!")
            else:
                self.status_label.setText("Spotify Web API mode. Configure API settings and login to authenticate.")

    def apply_volume(self, volume: int):
        #Codes to apply volume that is chosen and messages to give as feedback when tokens run out
        mode_text = self.mode_combo.currentText()
        try:
            if "Local" in mode_text:
                ok, msg = self._set_local_spotify_volume(volume)
                self._set_status(ok, msg)
            else:
                if not self.spotify_auth.access_token:
                    self._set_status(False, "Not logged in. Click 'Login to Spotify' first.")
                else:
                    ok, msg = self._set_spotify_api_volume(volume)
                    # If token expired, try to refresh
                    if not ok and "401" in msg:
                        refresh_ok, refresh_msg = self.spotify_auth.refresh_access_token()
                        if refresh_ok:
                            # Retry with new token that is given
                            ok, msg = self._set_spotify_api_volume(volume)
                        else:
                            msg = f"Token expired. Please login again. ({refresh_msg})"
                    self._set_status(ok, msg)
        except Exception as e:
            self._set_status(False, f"Unexpected error: {e}\n{traceback.format_exc()}")

    def _set_status(self, ok: bool, message: str):

        def updater():
            if ok:
                self.status_label.setText(f"✓ {message}")
            else:
                self.status_label.setText(f"✗ {message}")

        QApplication.instance().postEvent(self, _CallableEvent(updater))

    def _set_local_spotify_volume(self, percent: int):
        if not self.LOCAL_AVAILABLE:
            return False, "pycaw not available (Local mode is supported only on Windows)."

        try:
            import comtypes
            from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume

            # Initialize COM for this thread
            comtypes.CoInitialize()
            #The code above must be used for pycaw to communicate with Windows audio system. Without this code it simply
            #won't work because of lack of connection.

            try:
                sessions = AudioUtilities.GetAllSessions()
                spotify_found = False

                for session in sessions:
                    proc = session.Process
                    if proc and proc.name():
                        name = proc.name().lower()
                        if "spotify" in name:
                            spotify_found = True
                            try:
                                vol = session._ctl.QueryInterface(ISimpleAudioVolume)
                                vol.SetMasterVolume(max(0.0, min(1.0, percent / 100.0)), None)
                            except Exception as e:
                                return False, f"Failed to set session volume: {e}"

                if not spotify_found:
                    return False, "Spotify process not found. Make sure Spotify Desktop is running."
                return True, f"Local Spotify volume set to {percent}%"
            finally:
                comtypes.CoUninitialize()

        except Exception as e:
            return False, f"pycaw error: {e}"

    def _set_spotify_api_volume(self, percent: int):
        """Set volume using Spotify Web API"""
        try:
            endpoint = "https://api.spotify.com/v1/me/player/volume"
            headers = {"Authorization": f"Bearer {self.spotify_auth.access_token}"}
            params = {"volume_percent": percent}
            r = requests.put(endpoint, headers=headers, params=params, timeout=8)

            if r.status_code in (204, 202):
                return True, f"Spotify API volume set to {percent}%"
            else:
                try:
                    j = r.json()
                    return False, f"API error {r.status_code}: {j.get('error', {}).get('message', j)}"
                except Exception:
                    return False, f"API error {r.status_code}: {r.text}"
        except Exception as e:
            return False, f"Request error: {e}"

    def event(self, ev):
        #Override event to handle all called functions safely
        if isinstance(ev, _CallableEvent):
            ev.callable()
            return True
        return super().event(ev)


class _CallableEvent(QEvent):
    #It safely runs the UI update so UI won't crash and won't be bugged.
    TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, callable_):
        super().__init__(_CallableEvent.TYPE)
        self.callable = callable_


def main():
    # Check dependencies at startup
    try:
        import keyboard
        print("✓ keyboard package available")
    except ImportError:
        print("⚠ Warning: 'keyboard' package not available. Hotkeys will be disabled.")

    try:
        from pycaw.pycaw import AudioUtilities
        print("✓ pycaw package available")
    except ImportError:
        print("⚠ Warning: 'pycaw' not available. Local mode will be disabled.")

    app = QApplication(sys.argv)
    wnd = MainWindow()
    wnd.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()