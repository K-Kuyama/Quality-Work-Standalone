import os
import threading
import time
import signal
from awatch.aw_start import aw_start
from qtserver import server_start
import configparser

def handler(signum, frame):
    print("Quit programs.")
    raise KeyboardInterrupt
    sys.exit()
    
    
    
CONFIG_FILE = 'config.ini'
EV_PRODUCER_CLASS = "HttpEventProducerLocal"
print("------start-----")
if os.path.exists(CONFIG_FILE):
    config_ini = configparser.ConfigParser()
    config_ini.read(CONFIG_FILE, encoding='utf-8')
    try:
    	EV_PRODUCER_CLASS = config_ini.get('DEFAULT','Ev_producer_class')
    except (configparser.NoSectionError,configparser.NoOptionError):
        print("EventProducer not defined")          

signal.signal(signal.SIGINT, handler)

if EV_PRODUCER_CLASS == "HttpEventProducerLocal":
    #os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),"backend"))
    qts = threading.Thread(target=server_start, daemon=False)
    qts.start()
    

aw = threading.Thread(target=aw_start, daemon=False)
aw_start()

time.sleep(2)
    
#while True:
#	time.sleep(1)