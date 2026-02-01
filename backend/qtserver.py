import os
import sys
import logging
from django.conf import settings
from django.core.wsgi import get_wsgi_application
from django.core.servers.basehttp import run



logger = logging.getLogger(f"QualityWork.{__name__}")

def server_start():
	sys.path.append(os.getcwd())
	logger.info("------Web server start-----")
	os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
	hdl = get_wsgi_application()
	run(
		"127.0.0.1",
		8000,
		hdl
	)

