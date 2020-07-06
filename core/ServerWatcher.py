import os
import sys
import signal
import time
import psutil

def killer(api_pid):
    try:
        os.kill(int(api_pid), signal.SIGKILL) # kill eToro API
    except ProcessLookupError:
        pass

def launch_new_api_instance():
    os.system('python3 eToroWrapperServer.py')

def server_watcher():
    while True:
        if not(psutil.pid_exists(int(sys.argv[1]))) :
            print("eToro Wrapper server registered an error, a new instance will be launched in a few moments")
            killer(sys.argv[1])
            break
        time.sleep(3)
    time.sleep(3)
    print("lanzado")
server_watcher()
