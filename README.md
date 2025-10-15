# 🎧 SpotiVol  

SpotiVol is a lightweight desktop app that lets you control **Spotify’s volume with custom global hotkeys**.  
It supports two modes, **Local** and **Spotify Web API**, so you can use it anywhere.

---

## Features

- **Profile-Based Control:** Create multiple profiles with specific volume percentages (e.g., 100%, 40%).  
- **Global Hotkeys:** Bind keys like `F9` or `Ctrl + Alt + 1` to instantly switch volume profiles even while gaming.  
- **Dual Operation Modes:** Choose between **Local (Windows Mixer)** and **API (Spotify Web)** control.

| Feature | Local Mode | API Mode                                   |
| :--- | :--- |:-------------------------------------------|
| **Setup** | No setup required | Requires Spotify API credentials           |
| **Platform** |  **Windows Only** | Works on any OS                            |
| **Control Method** | Changes Spotify’s volume in Windows Mixer | Changes volume directly in the Spotify app |
| **Best For** | Quick, simple use on Windows | Using while gaming, stable performance   |

---

## ⚙️ Setup & Usage

### 🎵 API Mode Setup

To use the Spotify Web API mode:

1. Go to the **[Spotify Developer Dashboard](https://developer.spotify.com/dashboard)**.  
2. Click **"Create an App"**, and give it a name + description.  
3. Open your new app’s **Settings**.  
4. Add this Redirect URI → `http://127.0.0.1:8888/callback`  
5. Copy your **Client ID** and **Client Secret** into SpotiVol’s **API Settings** tab.  
6. Click **“Login to Spotify”** in the app your browser will open to authorize the connection.  
7. Done! You can now control Spotify remotely.


  - SpotiVol runs a temporary local webserver to capture the Spotify callback.  
  - It retrieves your **Access Token** and **Refresh Token**, storing them safely in `spotify_tokens.json`.  
  - The Access Token lasts 1 hour so SpotiVol auto-refreshes it using your Refresh Token.  
</details>

---

## ⚠️ Important Notes

> **Local Mode is Windows Only**  
> This feature relies on the `pycaw` library, which interacts with Windows’ audio system.  
> macOS and Linux users must use **API Mode** instead.

> **Run as Administrator for Gaming**  
> To detect global hotkeys while gaming, **run SpotiVol as administrator**.  
> Right-click → “Run as administrator” or enable it permanently under **Properties → Compatibility**.
> You have to do this otherwise your hotkeys won't go through because of game that you are playing. Running as administrator gives permission for it.

---

## Contact
 If you want to ask something or suggest anything reach out to me via discord!
 
- **Discord:** [blurryshady](#)



Built with **Python + PyQt5 + Spotify Web API**

