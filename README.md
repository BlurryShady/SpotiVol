# SpotiVol 🎧

SpotiVol is a lightweight application that lets you control Spotify's volume with custom, global hotkeys. It offers 2 options, local and using Spotify's API.

---

## ## Features
- **Profile-Based Control:** Create multiple profiles with specific volume percentages.
- **Global Hotkeys:** Bind profiles to a single key press (e.g., `F9`, `ctrl+alt+1`) that works even when the app is minimized.
- **Dual Operation Modes:** Choose the method that works best for you.

| Feature | Local Mode | API Mode |
| :--- | :--- | :--- |
| **Setup** | No setup required | Requires Spotify API credentials |
| **Platform** | **Windows Only** | Works on any OS |
| **Control Method**| Changes Spotify's volume in the Windows Mixer | Changes volume within the Spotify app itself |
| **Best For** | Quick, simple use on Windows | Controlling volume on other devices; more stable |

---

## ## Setup and Usage

### ### API Mode Setup
To use the more flexible API mode, you need to get credentials from Spotify:

1.  **Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).**
2.  Click **"Create an App"** and give it a name and description.
3.  Go into your new app's **Settings**.
4.  Add the following Redirect URI: `http://localhost:8888/callback`
5.  Copy your **Client ID** and **Client Secret** into SpotiVol's API Settings.
6.  Click **"Login to Spotify"** in the app. This will open a browser window to authorize the connection. After this you're set to go!
<details>
  <summary>How the API Authentication Works</summary>
  
  - SpotiVol runs a temporary local webserver to handle the Spotify authentication callback.
  - It retrieves your Access Token and Refresh Token, saving them securely in a local `spotify_tokens.json` file.
  - The Access Token expires after 1 hour, but SpotiVol automatically uses the Refresh Token to get a new one in the background.
</details>

---

## ## ⚠️ Important Notes

> **Local Mode is Windows Only**
> This mode relies on the `pycaw` library to function, which is specific to the Windows audio system. If you are on macOS or Linux, you must use the API Mode.

> **Gaming Requires Administrator Privileges**
> For your hotkeys to be detected while a game is running, **you must run SpotiVol as an administrator**. You can right-click the `.exe` and choose "Run as administrator," or set it to always run as admin in the file's Properties -> Compatibility tab.

---

## ## Feedback and Questions
If you have any ideas or feedback, feel free to reach out!
- **Discord:** blurryshady

**I hope you will enjoy and use this project as much as I do, take care and enjoy your life!**