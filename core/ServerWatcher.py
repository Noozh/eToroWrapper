import os
import sys
import signal
import time
import psutil
import subprocess

def server_watcher():
    print(sys.argv[1])
    while True:
        if not(psutil.pid_exists(int(sys.argv[1]))) :
            print("eToro Wrapper server registered an error, a new instance will be launched in a few moments")
            subprocess.Popen(['python3', 'eToroWrapperServer.py'])
            break
        time.sleep(3)
    time.sleep(3)
    print("lanzado")
    exit()

server_watcher()
