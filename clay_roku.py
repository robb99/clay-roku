#!/usr/bin/env python3
"""
clay-roku - CLI tool to control Roku devices

Usage:
    python3 clay_roku.py <ip> <command> [args]
    
Commands:
    info           - Get device info
    apps           - List installed apps
    launch <app>  - Launch an app by name
    key <key>     - Send a key press (Home, Back, Up, Down, Left, Right, Select, Play, Rev, Fwd, *)
    keysend <key>  - Press and release a key
    volume-up     - Volume up
    volume-down   - Volume down
    mute          - Toggle mute
    power-off     - Turn off TV
    
Examples:
    python3 clay_roku.py 192.168.1.50 info
    python3 clay_roku.py 192.168.1.50 apps
    python3 clay_roku.py 192.168.1.50 launch "Netflix"
    python3 clay_roku.py 192.168.1.50 key Home
"""

import sys
import argparse
import requests
import xml.etree.ElementTree as ET
from typing import Optional, Dict, List

# Common key mappings
KEY_MAP = {
    'home': 'Home',
    'back': 'Back',
    'left': 'Left',
    'right': 'Right',
    'up': 'Up',
    'down': 'Down',
    'select': 'Select',
    'play': 'Play',
    'pause': 'Pause',
    'rev': 'Reverse',
    'fwd': 'Forward',
    'replay': 'InstantReplay',
    'info': 'Info',
    'search': 'Search',
    'mute': 'VolumeMute',
    'volup': 'VolumeUp',
    'voldown': 'VolumeDown',
    'power': 'PowerOff',
    '*': '*'
}

# App name to ID mapping (common apps)
APP_IDS = {
    'netflix': '12',
    'youtube': '13',
    'hulu': '2285',
    'disney': '47137',
    'disney+': '47137',
    'prime': '13',  # Amazon Prime is often channel 13
    'amazon': '13',
    'hbo': '34376',
    'hbo max': '34376',
    'spotify': '19977',
    'plex': '13535',
    'roku channel': '14507',
    'the roku channel': '14507',
    'apple tv': '105957',
    'espn': '140030',
    'disney plus': '47137',
    'paramount': '44401',
    'peacock': '45300',
    'google play': '632',
    'vimeo': '25866',
    'twitch': '2283',
    'sling': '24465',
    'youtube tv': '385116'
}


class RokuController:
    def __init__(self, ip: str, port: int = 8060):
        self.base_url = f"http://{ip}:{port}"
    
    def _request(self, method: str, path: str, **kwargs) -> Optional[requests.Response]:
        """Make a request to the Roku API"""
        url = f"{self.base_url}{path}"
        try:
            response = requests.request(method, url, timeout=5, **kwargs)
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to Roku at {self.base_url}: {e}", file=sys.stderr)
            return None
    
    def get_info(self) -> Optional[Dict]:
        """Get device information"""
        response = self._request('GET', '/query/device-info')
        if not response:
            return None
        
        try:
            root = ET.fromstring(response.text)
            info = {}
            for child in root:
                info[child.tag] = child.text
            return info
        except ET.ParseError:
            print("Failed to parse device info response", file=sys.stderr)
            return None
    
    def get_apps(self) -> Optional[List[Dict]]:
        """Get list of installed apps"""
        response = self._request('GET', '/query/apps')
        if not response:
            return None
        
        try:
            root = ET.fromstring(response.text)
            apps = []
            for app in root.findall('.//app'):
                apps.append({
                    'id': app.get('id'),
                    'name': app.text
                })
            return apps
        except ET.ParseError:
            print("Failed to parse apps response", file=sys.stderr)
            return None
    
    def launch_app(self, app_id: str) -> bool:
        """Launch an app by ID"""
        response = self._request('POST', f'/launch/{app_id}')
        return response is not None and response.status_code == 200
    
    def launch_app_by_name(self, name: str) -> bool:
        """Launch an app by name (fuzzy match)"""
        apps = self.get_apps()
        if not apps:
            print("Failed to get app list", file=sys.stderr)
            return False
        
        name_lower = name.lower().strip()
        
        # First try exact match
        for app in apps:
            if app['name'].lower() == name_lower:
                print(f"Launching '{app['name']}' (ID: {app['id']})")
                return self.launch_app(app['id'])
        
        # Then try partial match
        for app in apps:
            if name_lower in app['name'].lower():
                print(f"Launching '{app['name']}' (ID: {app['id']})")
                return self.launch_app(app['id'])
        
        # Try known app IDs
        if name_lower in APP_IDS:
            app_id = APP_IDS[name_lower]
            print(f"Launching '{name}' (known ID: {app_id})")
            return self.launch_app(app_id)
        
        print(f"App '{name}' not found", file=sys.stderr)
        print("Use 'apps' command to see available apps", file=sys.stderr)
        return False
    
    def send_key(self, key: str, action: str = 'press') -> bool:
        """Send a key press"""
        key = KEY_MAP.get(key.lower(), key)
        
        if action == 'press':
            response = self._request('POST', f'/keydown/{key}')
        elif action == 'release':
            response = self._request('POST', f'/keyup/{key}')
        else:  # press and release
            down = self._request('POST', f'/keydown/{key}')
            import time
            time.sleep(0.1)
            up = self._request('POST', f'/keyup/{key}')
            return down is not None and up is not None
        
        return response is not None and response.status_code == 200
    
    def home(self) -> bool:
        """Go to home screen"""
        return self.send_key('home', 'press')
    
    def volume_up(self) -> bool:
        """Volume up"""
        return self.send_key('volup', 'press')
    
    def volume_down(self) -> bool:
        """Volume down"""
        return self.send_key('voldown', 'press')
    
    def mute(self) -> bool:
        """Toggle mute"""
        return self.send_key('mute', 'press')
    
    def power_off(self) -> bool:
        """Power off"""
        return self.send_key('power', 'press')


def main():
    parser = argparse.ArgumentParser(
        description='Control Roku devices from command line',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('ip', help='Roku device IP address')
    parser.add_argument('command', help='Command to execute',
                        choices=['info', 'apps', 'launch', 'key', 'keysend', 
                                'volume-up', 'volume-down', 'mute', 'power-off'])
    parser.add_argument('args', nargs='*', help='Command arguments')
    
    args = parser.parse_args()
    
    roku = RokuController(args.ip)
    
    if args.command == 'info':
        info = roku.get_info()
        if info:
            print(f"Device: {info.get('friendly-device-name', 'Unknown')}")
            print(f"Model: {info.get('model-name', 'Unknown')}")
            print(f"Serial: {info.get('serial-number', 'Unknown')}")
            print(f"Version: {info.get('software-version', 'Unknown')}")
            print(f"IP: {info.get('external-ip', args.ip)}")
    
    elif args.command == 'apps':
        apps = roku.get_apps()
        if apps:
            print(f"{'ID':<10} {'App Name'}")
            print("-" * 40)
            for app in apps:
                print(f"{app['id']:<10} {app['name']}")
    
    elif args.command == 'launch':
        if not args.args:
            print("Error: app name required", file=sys.stderr)
            sys.exit(1)
        app_name = ' '.join(args.args)
        success = roku.launch_app_by_name(app_name)
        sys.exit(0 if success else 1)
    
    elif args.command == 'key':
        if not args.args:
            print("Error: key name required", file=sys.stderr)
            sys.exit(1)
        key = args.args[0]
        success = roku.send_key(key, 'press')
        sys.exit(0 if success else 1)
    
    elif args.command == 'keysend':
        if not args.args:
            print("Error: key name required", file=sys.stderr)
            sys.exit(1)
        key = args.args[0]
        success = roku.send_key(key, 'send')
        sys.exit(0 if success else 1)
    
    elif args.command == 'volume-up':
        success = roku.volume_up()
        sys.exit(0 if success else 1)
    
    elif args.command == 'volume-down':
        success = roku.volume_down()
        sys.exit(0 if success else 1)
    
    elif args.command == 'mute':
        success = roku.mute()
        sys.exit(0 if success else 1)
    
    elif args.command == 'power-off':
        success = roku.power_off()
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
