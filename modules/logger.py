#!/usr/bin/env python3
"""
Multi-format Logger Module
Logs visitor data in multiple formats simultaneously
"""

import json
import sqlite3
import os
from datetime import datetime

class LoggerSystem:
    def __init__(self, log_dir='logs'):
        self.log_dir = log_dir
        self._ensure_log_directory()
        self._init_database()
        self.latest_visitor = {}
    
    def _ensure_log_directory(self):
        """Create log directory if it doesn't exist"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def _init_database(self):
        """Initialize SQLite database"""
        db_path = os.path.join(self.log_dir, 'visitors.db')
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS visitors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                ip_address TEXT,
                path TEXT,
                method TEXT,
                browser TEXT,
                os TEXT,
                device TEXT,
                country TEXT,
                city TEXT,
                isp TEXT,
                latitude REAL,
                longitude REAL,
                language TEXT,
                referrer TEXT,
                user_agent TEXT,
                raw_data TEXT
            )
        ''')
        
        # Create index for faster queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON visitors(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ip ON visitors(ip_address)')
        
        self.conn.commit()
    
    def log_all(self, visitor_data):
        """Log visitor data in all formats"""
        self.latest_visitor = visitor_data
        
        # Log to Apache-style access log
        self._log_access(visitor_data)
        
        # Log to JSON file
        self._log_json(visitor_data)
        
        # Log to SQLite database
        self._log_sqlite(visitor_data)
    
    def _log_access(self, data):
        """Apache-style access log"""
        log_path = os.path.join(self.log_dir, 'access.log')
        
        # Format: IP - - [timestamp] "METHOD path" 200 - "referrer" "user_agent"
        log_entry = f'{data["ip_address"]} - - [{data["timestamp"]}] "{data["method"]} {data["path"]} HTTP/1.1" 200 - "{data["referrer"]}" "{data["user_agent"]}"\n'
        
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    
    def _log_json(self, data):
        """JSON format logging (append)"""
        log_path = os.path.join(self.log_dir, 'detailed.json')
        
        # Create entry with timestamp for JSONL format
        entry = {
            'timestamp': data['timestamp'],
            'ip': data['ip_address'],
            'path': data['path'],
            'method': data['method'],
            'device': data['device'],
            'geolocation': data['geolocation'],
            'language': data['language'],
            'referrer': data['referrer']
        }
        
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')
    
    def _log_sqlite(self, data):
        """SQLite database logging"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT INTO visitors (
                timestamp, ip_address, path, method,
                browser, os, device, country, city,
                isp, latitude, longitude, language,
                referrer, user_agent, raw_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['timestamp'],
            data['ip_address'],
            data['path'],
            data['method'],
            data['device']['browser'],
            data['device']['os'],
            data['device']['device'],
            data['geolocation']['country'],
            data['geolocation']['city'],
            data['geolocation']['isp'],
            data['geolocation']['lat'],
            data['geolocation']['lon'],
            data['language'],
            data['referrer'],
            data['user_agent'],
            json.dumps(data['headers'])
        ))
        
        self.conn.commit()
    
    def get_latest(self):
        """Get latest visitor data"""
        return self.latest_visitor
    
    def get_statistics(self):
        """Get visitor statistics from database"""
        cursor = self.conn.cursor()
        
        stats = {}
        
        # Total visitors
        cursor.execute('SELECT COUNT(*) FROM visitors')
        stats['total'] = cursor.fetchone()[0]
        
        # Unique IPs
        cursor.execute('SELECT COUNT(DISTINCT ip_address) FROM visitors')
        stats['unique_ips'] = cursor.fetchone()[0]
        
        # Visitors by country
        cursor.execute('SELECT country, COUNT(*) FROM visitors GROUP BY country ORDER BY COUNT(*) DESC LIMIT 5')
        stats['top_countries'] = cursor.fetchall()
        
        # Visitors by device
        cursor.execute('SELECT device, COUNT(*) FROM visitors GROUP BY device')
        stats['devices'] = dict(cursor.fetchall())
        
        return stats
