#!/usr/bin/env python3
"""
Termux Notification Module
Send notifications to Termux when visitors arrive
"""

import subprocess
import os

class TermuxNotifier:
    def __init__(self, enabled=True):
        self.enabled = enabled
        self.check_termux()
    
    def check_termux(self):
        """Check if running in Termux"""
        try:
            result = subprocess.run(['uname', '-o'], capture_output=True, text=True)
            self.is_termux = 'Android' in result.stdout
        except:
            self.is_termux = False
        
        if not self.is_termux:
            self.enabled = False
    
    def send_notification(self, visitor_data):
        """Send Termux notification"""
        if not self.enabled or not self.is_termux:
            return
        
        try:
            # Create notification title and content
            title = f"Visitor #{visitor_data['id']}"
            content = f"IP: {visitor_data['ip_address']} | {visitor_data['device']['os']}"
            
            # Send notification using termux-notification
            cmd = [
                'termux-notification',
                '--title', title,
                '--content', content,
                '--button1', 'View Details',
                '--button1-action', f'echo "{visitor_data}"'
            ]
            
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Also vibrate briefly
            subprocess.Popen(['termux-vibrate', '-d', '100'], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
        except:
            pass  # Silently fail if notification fails
    
    def send_alert(self, message, level='INFO'):
        """Send custom alert"""
        if not self.enabled:
            return
        
        try:
            colors = {
                'INFO': 'green',
                'WARN': 'yellow',
                'ERROR': 'red'
            }
            
            cmd = [
                'termux-notification',
                '--title', f'[{level}] Tracker Alert',
                '--content', message,
                '--led-color', colors.get(level, 'blue')
            ]
            
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass
