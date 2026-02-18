#!/usr/bin/env python3
"""
Geolocation Module - IP to Location Mapping
Supports multiple APIs with fallback + Premium APIs
"""

import json
import urllib.request
import urllib.error
import socket
from datetime import datetime

class GeoTracker:
    def __init__(self):
        self.cache = {}
        
        # Free APIs (fallback)
        self.apis = [
            'http://ip-api.com/json/{}',
            'https://geolocation-db.com/json/{}',
            'http://ipwhois.app/json/{}'
        ]
        self.api_index = 0
        
        # Premium APIs dengan API key lo
        self.premium_apis = [
            {
                'name': 'IP2Location',
                'url': 'https://api.ip2location.io/?key=9346B9052E2AFBB20D4203CC6A188273&ip={}',
                'priority': 1  # Prioritas tertinggi
            },
            {
                'name': 'IPinfo',
                'url': 'https://ipinfo.io/{}?token=f2372f5524eceb',
                'priority': 2
            }
        ]

    def locate(self, ip):
        """Get geolocation data for IP address (Premium first, then fallback)"""
        # Skip local IPs
        if self._is_private_ip(ip):
            return self._get_local_geo()

        # Check cache
        if ip in self.cache:
            return self.cache[ip]

        # 1. COBA PREMIUM APIS DULU (lebih akurat)
        for premium in sorted(self.premium_apis, key=lambda x: x['priority']):
            try:
                data = self._query_premium_api(ip, premium)
                if data:
                    self.cache[ip] = data
                    data['source'] = premium['name']  # Tandai sumber
                    return data
            except Exception as e:
                continue

        # 2. FALLBACK KE FREE APIS kalo premium gagal
        for i in range(len(self.apis)):
            try:
                data = self._query_api(ip)
                if data and data.get('status') != 'fail':
                    self.cache[ip] = data
                    data['source'] = 'Free API'
                    return data
            except:
                continue

        # 3. Kalo semua gagal
        return self._get_fallback_geo()

    def _query_premium_api(self, ip, premium_config):
        """Query premium IP geolocation API"""
        url = premium_config['url'].format(ip)
        
        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                
                # STANDARDISASI FORMAT berdasarkan API
                if premium_config['name'] == 'IP2Location':
                    return {
                        'country': data.get('country_name', 'Unknown'),
                        'region': data.get('region_name', 'Unknown'),
                        'city': data.get('city_name', 'Unknown'),
                        'isp': data.get('as', 'Unknown'),
                        'lat': data.get('latitude', 0),
                        'lon': data.get('longitude', 0),
                        'timezone': data.get('time_zone', 'Unknown'),
                        'org': data.get('as', 'Unknown'),
                        'as': data.get('asn', 'Unknown'),
                        'zip': data.get('zip_code', 'Unknown'),
                        'proxy': data.get('is_proxy', False)
                    }
                    
                elif premium_config['name'] == 'IPinfo':
                    # Parse location dari field 'loc' (format: "lat,lon")
                    lat_lon = data.get('loc', '0,0').split(',')
                    return {
                        'country': data.get('country', 'Unknown'),
                        'region': data.get('region', 'Unknown'),
                        'city': data.get('city', 'Unknown'),
                        'isp': data.get('org', 'Unknown'),
                        'lat': float(lat_lon[0]) if len(lat_lon) > 0 else 0,
                        'lon': float(lat_lon[1]) if len(lat_lon) > 1 else 0,
                        'timezone': data.get('timezone', 'Unknown'),
                        'org': data.get('org', 'Unknown'),
                        'as': data.get('asn', {}).get('asn', 'Unknown') if isinstance(data.get('asn'), dict) else 'Unknown',
                        'hostname': data.get('hostname', 'Unknown'),
                        'anycast': data.get('anycast', False)
                    }
                    
        except Exception as e:
            return None
        
        return None

    def _query_api(self, ip):
        """Query free IP geolocation API (original method)"""
        url = self.apis[self.api_index].format(ip)
        self.api_index = (self.api_index + 1) % len(self.apis)

        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req, timeout=3) as response:
                data = json.loads(response.read().decode())
                return self._standardize_format(data, self.api_index)
        except:
            return None

    def _standardize_format(self, data, api_idx):
        """Standardize different API formats (original method)"""
        if api_idx == 0:  # ip-api.com
            return {
                'country': data.get('country', 'Unknown'),
                'region': data.get('regionName', 'Unknown'),
                'city': data.get('city', 'Unknown'),
                'isp': data.get('isp', 'Unknown'),
                'lat': data.get('lat', 0),
                'lon': data.get('lon', 0),
                'timezone': data.get('timezone', 'Unknown'),
                'org': data.get('org', 'Unknown'),
                'as': data.get('as', 'Unknown')
            }
        elif api_idx == 1:  # geolocation-db.com
            return {
                'country': data.get('country_name', 'Unknown'),
                'region': data.get('state', 'Unknown'),
                'city': data.get('city', 'Unknown'),
                'isp': data.get('isp', 'Unknown'),
                'lat': data.get('latitude', 0),
                'lon': data.get('longitude', 0),
                'timezone': data.get('timezone', 'Unknown'),
                'org': 'N/A',
                'as': 'N/A'
            }
        else:  # ipwhois.app
            return {
                'country': data.get('country', 'Unknown'),
                'region': data.get('region', 'Unknown'),
                'city': data.get('city', 'Unknown'),
                'isp': data.get('isp', 'Unknown'),
                'lat': data.get('latitude', 0),
                'lon': data.get('longitude', 0),
                'timezone': data.get('timezone', 'Unknown'),
                'org': data.get('org', 'Unknown'),
                'as': data.get('asn', 'Unknown')
            }

    def _is_private_ip(self, ip):
        """Check if IP is private/local"""
        try:
            socket.inet_aton(ip)
            if ip.startswith(('10.', '172.16.', '172.17.', '172.18.', '172.19.',
                            '172.20.', '172.21.', '172.22.', '172.23.', '172.24.',
                            '172.25.', '172.26.', '172.27.', '172.28.', '172.29.',
                            '172.30.', '172.31.', '192.168.', '127.')):
                return True
            return False
        except:
            return True

    def _get_local_geo(self):
        """Return data for local IPs"""
        return {
            'country': 'Local Network',
            'region': 'Local',
            'city': 'Local',
            'isp': 'Local ISP',
            'lat': 0,
            'lon': 0,
            'timezone': 'Local',
            'org': 'Local Network',
            'as': 'Private'
        }

    def _get_fallback_geo(self):
        """Return fallback data when all APIs fail"""
        return {
            'country': 'Unknown',
            'region': 'Unknown',
            'city': 'Unknown',
            'isp': 'Unknown',
            'lat': 0,
            'lon': 0,
            'timezone': 'Unknown',
            'org': 'Unknown',
            'as': 'Unknown'
        }


