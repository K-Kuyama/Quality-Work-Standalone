import os
import sys
from django.conf import settings
from django.core.wsgi import get_wsgi_application
from django.core.servers.basehttp import run


#print(f"syspath={sys.path}")
#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
#hdl = get_wsgi_application()
#run(
#	"127.0.0.1",
#	8000,
#	hdl
#)

def server_start():
	#os.chdir(os.path.dirname(os.path.abspath(__file__)))
	#print(f"=>{os.path.dirname(os.path.abspath(__file__))}")
	sys.path.append(os.getcwd())
	print(f"syspath={sys.path}")
	print(f"cwd=>{os.getcwd()}")
	os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
	#settings.configure()
	hdl = get_wsgi_application()
	run(
		"127.0.0.1",
		8000,
		hdl
	)

