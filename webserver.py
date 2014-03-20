import time
import devices_probestation_lockin as PS
import time

import cherrypy

class HelloWorld:
    def index(self):
        s = "<html><head><meta http-equiv=\"refresh\" content=\"10\">"
        s = s+"<title>CryoControl</title></head>"
        s = s+"<body>"
        s = s+"<p><b>Pressure:</b> %1.2e mbar"%(PS.single_gauge.get_pressure())+"</p>"
        s = s+"<p>"+time.ctime()+"</p>"
        s = s+"</body>"
        return s
    index.exposed = True

cherrypy.server.socket_port = 80
cherrypy.server.socket_host = "134.34.143.60"
cherrypy.quickstart(HelloWorld())
