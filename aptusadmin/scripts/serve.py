#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import webbrowser
from threading import Timer
#os.environ["DJANGO_SETTINGS_MODULE"] = "aptuseducat.settings"
import django
django.setup()
import cherrypy
from django.conf import settings
from django.core.handlers.wsgi import WSGIHandler


class DjangoApplication(object):
    HOST = getattr(settings, 'SERVER_HOST', "127.0.0.1")
    PORT = getattr(settings, 'SERVER_PORT', 8001)
    HOSTNAV = "127.0.0.1"

    def mount_static(self, url, root):
        """
        :param url: Relative url
        :param root: Path to static files root
        """
        config = {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': root,
            'tools.expires.on': True,
            'tools.expires.secs': 86400
        }
        cherrypy.tree.mount(None, url,{'/': config})
    def mount_media(self, url, root):
        """
        :param url: Relative url
        :param root: Path to static files root
        """
        config = {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': root,
            'tools.expires.on': True,
            'tools.expires.secs': 86400
        }
        cherrypy.tree.mount(None, url,{'/': config})

    def mount_backup(self, url, root):
        """
        :param url: Relative url
        :param root: Path to static files root
        """
        config = {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': root,
            'tools.expires.on': True,
            'tools.expires.secs': 86400
        }
        cherrypy.tree.mount(None, url,{'/': config})
		
    def cfg_favicon(self, root):
        """Configure a default favicon.
 
        Expects it to be in STATIC_ROOT.
 
        """
        favicon = os.path.join(root, 'aptusadmin/img/favicon.ico')
        config = {
            'tools.staticfile.on': True,
            'tools.staticfile.filename': favicon,
            'tools.expires.on': True,
            'tools.expires.secs': 60 * 60 * 24 * 365, # 1 year
        }
        cherrypy.tree.mount(None, '/favicon.ico', {'/': config})	
		
    def open_browser(self):
        Timer(3, webbrowser.open, ("http://%s:%s/connexion" % (self.HOSTNAV, self.PORT),)).start()

    def run(self):
        cherrypy.config.update({
            'server.socket_host': self.HOST,
            'server.socket_port': self.PORT,
            'engine.autoreload_on': False,
            'log.screen': True
        })
        self.mount_static(settings.STATIC_URL, settings.STATIC_ROOT)
        self.mount_media(settings.MEDIA_URL, settings.MEDIA_ROOT)
        self.mount_media(settings.BACKUP_URL, settings.BACKUP_ROOT)
        self.cfg_favicon(settings.STATIC_ROOT)
        cherrypy.log("Loading and serving Django application")
        cherrypy.tree.graft(WSGIHandler())
        cherrypy.engine.start()


        cherrypy.engine.block()


if __name__ == "__main__":
    print ("Your app is running at http://localhost:8001")
    DjangoApplication().run()
