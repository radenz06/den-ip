#!/usr/bin/env python3
"""
Device Fingerprinting Module
Parse User-Agent strings into detailed device information
"""

import re

class DeviceParser:
    def __init__(self):
        # Browser patterns
        self.browsers = {
            'Chrome': r'Chrome/(\d+)',
            'Firefox': r'Firefox/(\d+)',
            'Safari': r'Safari/(\d+)',
            'Edge': r'Edg/(\d+)',
            'Opera': r'OPR/(\d+)',
            'IE': r'MSIE (\d+)|Trident.*rv:(\d+)'
        }
        
        # OS patterns
        self.os_patterns = {
            'Windows': r'Windows NT (\d+\.\d+)',
            'macOS': r'Mac OS X (\d+[._]\d+)',
            'iOS': r'iPhone OS (\d+[._]\d+)|iPad; CPU OS (\d+[._]\d+)',
            'Android': r'Android (\d+\.\d+)',
            'Linux': r'Linux (?!Android)',
            'Chrome OS': r'CrOS'
        }
        
        # Device patterns
        self.devices = {
            'Mobile': r'Mobile|iPhone|iPad|Android.*Mobile',
            'Tablet': r'Tablet|iPad|Android(?!.*Mobile)',
            'Desktop': r'Windows|Macintosh|Linux(?!.*Mobile)',
            'Bot': r'bot|crawler|spider|scraper|curl|wget|python|java'
        }
    
    def parse(self, user_agent):
        """Parse User-Agent string"""
        user_agent = user_agent.lower()
        
        # Detect bot first
        is_bot = bool(re.search(self.devices['Bot'], user_agent, re.I))
        
        # Detect browser
        browser = self._detect_browser(user_agent)
        
        # Detect OS
        os_info = self._detect_os(user_agent)
        
        # Detect device type
        device_type = self._detect_device_type(user_agent)
        
        return {
            'browser': browser,
            'os': os_info,
            'device': device_type,
            'is_bot': is_bot,
            'raw_ua': user_agent[:200]  # Truncate for storage
        }
    
    def _detect_browser(self, ua):
        """Detect browser and version"""
        for browser, pattern in self.browsers.items():
            match = re.search(pattern, ua, re.I)
            if match:
                version = match.group(1) if match.group(1) else match.group(2)
                return f"{browser} {version}"
        return "Unknown Browser"
    
    def _detect_os(self, ua):
        """Detect operating system"""
        for os_name, pattern in self.os_patterns.items():
            match = re.search(pattern, ua, re.I)
            if match:
                if os_name == 'Windows':
                    version = self._get_windows_version(match.group(1))
                    return f"Windows {version}"
                elif os_name == 'macOS':
                    version = match.group(1).replace('_', '.')
                    return f"macOS {version}"
                elif os_name == 'iOS':
                    ver = match.group(1) or match.group(2)
                    return f"iOS {ver.replace('_', '.')}"
                elif os_name == 'Android':
                    return f"Android {match.group(1)}"
                elif os_name == 'Linux':
                    return "Linux"
                elif os_name == 'Chrome OS':
                    return "Chrome OS"
        return "Unknown OS"
    
    def _get_windows_version(self, nt_version):
        """Convert Windows NT version to friendly name"""
        versions = {
            '5.0': '2000',
            '5.1': 'XP',
            '5.2': 'Server 2003',
            '6.0': 'Vista',
            '6.1': '7',
            '6.2': '8',
            '6.3': '8.1',
            '10.0': '10/11'
        }
        return versions.get(nt_version, nt_version)
    
    def _detect_device_type(self, ua):
        """Detect device type"""
        if re.search(self.devices['Bot'], ua, re.I):
            return 'Bot/Crawler'
        elif re.search(self.devices['Tablet'], ua, re.I):
            return 'Tablet'
        elif re.search(self.devices['Mobile'], ua, re.I):
            return 'Mobile'
        elif re.search(self.devices['Desktop'], ua, re.I):
            return 'Desktop'
        return 'Unknown'
