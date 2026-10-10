# clay-roku 🎬

CLI tool to control Roku devices on your local network.

## What It Does

- Turn TV on/off (via power key)
- Launch apps (Netflix, YouTube, Disney+, etc.)
- Control playback (play, pause, rewind, fast forward)
- Navigate menus (arrow keys, select, back, home)
- Volume control

## Why It Matters

This expands Clay's entertainment control beyond just audio (clay-media) to video streaming. Now Clay can:
- Launch Netflix for movie night
- Switch to YouTube for kids' videos
- Control playback without needing the remote

## Requirements

- Python 3.7+
- `requests` library
- Roku device on local network
- Port 8060 accessible

## Installation

```bash
pip install requests
```

## Usage

```bash
# Set executable
chmod +x clay_roku.py

# Find your Roku IP (check router or TV network settings)
# Common IPs: 192.168.1.50, 192.168.1.100, etc.

# Get device info
python3 clay_roku.py 192.168.1.X info

# List installed apps
python3 clay_roku.py 192.168.1.X apps

# Launch an app
python3 clay_roku.py 192.168.1.X launch Netflix
python3 clay_roku.py 192.168.1.X launch "YouTube"
python3 clay_roku.py 192.168.1.X launch "Disney+"

# Send key commands
python3 clay_roku.py 192.168.1.X key Home
python3 clay_roku.py 192.168.1.X key Back
python3 clay_roku.py 192.168.1.X keysend Select

# Volume control
python3 clay_roku.py 192.168.1.X volume-up
python3 clay_roku.py 192.168.1.X volume-down
python3 clay_roku.py 192.168.1.X mute

# Power off
python3 clay_roku.py 192.168.1.X power-off
```

## Commands

| Command | Description |
|---------|-------------|
| `info` | Get device info (model, serial, IP) |
| `apps` | List all installed apps |
| `launch <name>` | Launch app by name |
| `key <key>` | Press and hold a key |
| `keysend <key>` | Press and release a key |
| `volume-up` | Volume up |
| `volume-down` | Volume down |
| `mute` | Toggle mute |
| `power-off` | Turn off TV |

## Keys

Available keys: `Home`, `Back`, `Left`, `Right`, `Up`, `Down`, `Select`, `Play`, `Pause`, `Rev` (rewind), `Fwd` (fast forward), `Replay` (instant replay), `Info`, `Search`, `VolumeMute`, `VolumeUp`, `VolumeDown`, `PowerOff`

## Config File (Optional)

Create `config.yaml` for persistent settings:

```yaml
default_ip: "192.168.1.50"
```

## Examples

```bash
# Netflix night!
python3 clay_roku.py 192.168.1.50 launch Netflix

# Play YouTube video
python3 clay_roku.py 192.168.1.50 launch YouTube

# Navigate to settings
python3 clay_roku.py 192.168.1.50 home
python3 clay_roku.py 192.168.1.50 keysend Right
python3 clay_roku.py 192.168.1.50 keysend Right
python3 clay_roku.py 192.168.1.50 keysend Down
python3 clay_roku.py 192.168.1.50 keysend Select
```

## Related Tools

- [clay-media](https://github.com/robb99/clay-media) - Play music through HA speakers
- [clay-voice](https://github.com/robb99/clay-voice) - TTS announcements
- [clay-tesla](https://github.com/robb99/clay-tesla) - Tesla vehicle control
