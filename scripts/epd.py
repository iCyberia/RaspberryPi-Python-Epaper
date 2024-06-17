#!/usr/bin/python
# -*- coding:utf-8 -*-

#####################################################################
# Copyright (c) [2024] Hiroshi Thomas. 
#
# License: [GNU General Public License]
# You should have received a copy of the GNU General Public License
#
# Purpose: Displays Wifi netowrk name, CPU uptime, Shower Thought from reddit, and current time.
#
# Further documentation:
# - https://github.com/iCyberia/RaspberryPi-Python-Epaper
#
# Usage examples:
# - Runs on Rapsberry Pi Zero W with Waveshare 3.7in E-Ink Display
#####################################################################

# Imports
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import subprocess
import logging
from waveshare_epd import epd3in7
import time
from PIL import Image,ImageDraw,ImageFont
import psutil # type: ignore
import datetime
import socket
import requests
import random
import textwrap

# Debug logging
logging.basicConfig(level=logging.DEBUG)

# Declaring fonts
font48 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 48)
font36 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 36)
font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)

# User agent for the request
headers = {'User-Agent': 'shower_thoughts_fetcher/0.1 by iCyberia'}

# URL for the Reddit API endpoint
url = 'https://www.reddit.com/r/showerthoughts/top.json?sort=top&t=week&limit=100'

# Initialize with a default value
shower_thought = "Error: Unable to fetch data from Reddit."  


# Gets host name
def get_hostname():
    try:
        hostname = socket.gethostname()
        return hostname
    except Exception as e:
        logging.error(f"An error occurred while getting the hostname: {e}")
        return None    
    

# Gets wifi name
def get_wifi_name():
    try:
        # Run the nmcli command to get the Wi-Fi name
        result = subprocess.run(["nmcli", "-t", "-f", "active,ssid", "dev", "wifi"], capture_output=True, text=True)
        output = result.stdout

        # Parse the output to find the SSID of the active connection
        for line in output.split('\n'):
            if line.startswith("yes"):
                wifi_name = line.split(":")[1].strip()
                return wifi_name
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return None


# Gets system uptime
def get_system_uptime():
    boot_time_timestamp = psutil.boot_time()
    boot_time = datetime.datetime.fromtimestamp(boot_time_timestamp)
    uptime = datetime.datetime.now() - boot_time
    days, remainder = divmod(uptime.total_seconds(), 86400)  # 86400 seconds in a day
    hours, remainder = divmod(remainder, 3600)  # 3600 seconds in an hour
    minutes, _ = divmod(remainder, 60)  # 60 seconds in a minute
    return f"{int(days)} days, {int(hours)} hrs, {int(minutes)} min"


# Process Shower Thoughts from Reddit
try:
    response = requests.get(url, headers=headers, timeout=5)
    if response.status_code == 200:
        data = response.json()
        # Get the list of posts
        posts = data['data']['children']
        # Select a random post
        random_post = random.choice(posts)['data']
        shower_thought = f'{random_post["title"]} -{random_post["author"]}'
# Error handling
except requests.ConnectionError as e:
    logging.error(f"Connection error: {e}")
    shower_thought = "Error: Network connection issue."
except requests.Timeout as e:
    logging.error(f"Timeout error: {e}")
    shower_thought = "Error: Network timeout."
except requests.RequestException as e:
    logging.error(f"Request error: {e}")


# Wifi Name
wifi_name = get_wifi_name()
if wifi_name:
    networkName = f"Connected to Wi-Fi: \n{wifi_name}"
else:
    networkName = "Could not determine the Wi-Fi name."

# Sets the hostname
hostname = get_hostname()
if hostname:
    print(f"Hostname: {hostname}")
else:
    print("Could not determine the hostname.")

# Sets uptime variable
uptime = get_system_uptime()


# Display write
try:
    logging.info("Init and Clear")
    epd = epd3in7.EPD()  # get the display
    epd.init(0)
    epd.Clear(0xFF, 0)  # clear the display

    # write to display buffer
    def print_to_display(network_name, uptime_info, shower_thought, hostname):
        Limage = Image.new('L', (epd.width, epd.height), 0xFF)  # clear for new print
        draw = ImageDraw.Draw(Limage)
        draw.text((10, 10), network_name, font=font24, fill=0)
        draw.text((10, 75), f"Uptime: \n{uptime_info}", font=font24, fill=0)

        # Word wrap the thought to buffer
        max_chars_per_line = 23  # Adjust width as needed
        wrapped_thought_lines = textwrap.wrap(shower_thought, width=max_chars_per_line)
        y_text = 140
        for line in wrapped_thought_lines:
            draw.text((10, y_text), line, font=font24, fill=0)
            y_text += font24.getsize(line)[1]

        # Write current time to buffer
        draw.text((10, 400), time.strftime('%I:%M %p'), font=font48, fill=0)

        # Write Hostname to buffer
        draw.text((10, 450), hostname, font=font24, fill=0)





        # Push buffer to screen
        epd.display_4Gray(epd.getbuffer_4Gray(Limage))

        # Put the display to sleep
        logging.info("Goto Sleep...")
        epd.sleep()
        
# Run 
    logging.info("Print Network and Uptime")
    print_to_display(networkName, uptime, shower_thought, hostname)  
  


# Error handling
except IOError as e:
    logging.error(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd3in7.epdconfig.module_exit(cleanup=True)
    exit()

    # #Display Elder Emo Test Badge
    # epd.init(0)
    # epd.Clear(0xFF, 0)
    # logging.info("Elder Emo Badge")
    # Himage = Image.open(os.path.join(picdir, 'emo-badge.bmp'))
    # epd.display_4Gray(epd.getbuffer_4Gray(Himage))
    # time.sleep(1) #wait