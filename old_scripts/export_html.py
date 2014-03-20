# -*- coding: utf-8 -*-
"""
Created on Sat Nov 02 17:21:47 2013

@author: David Weber
"""

def export_html(self, parent, filename="C:\\test.html"):    
        form_objects = inspect.getmembers(parent)
        
        f = open(filename,"w")
        f.write("<html><head><title>Test</title>")
        f.write("<style type=\"text/css\">\n")
        
        # background
        f.write("body {background-color: #BBBBBB}\n")   
        
        # inputs
        for element in form_objects:
            try:
                if element[1].__class__.__name__ == 'QLineEdit':
                    f.write("form #%s {position: absolute; top: %ipx; left: %ipx; width: %ipx; height: %ipx}\n"%(
                        element[1].objectName(),element[1].mapToGlobal(QPoint(0,0)).y(),element[1].mapToGlobal(QPoint(0,0)).x(),int(element[1].width()),int(element[1].height())))
            except Exception,e:
                print e
                print str(element[1].__class__.__name__)
                f.write("dada!")
                pass
        f.write("</style>\n")
        f.write("</head>")
        
        
        f.write("<body>\n")
        f.write("<form>\n")
        for element in form_objects:
            try:
                if element[1].__class__.__name__ == 'QLineEdit':
                    f.write("<div id=\"%s\"><input type=\"text\" name=\"%s\" value=\"%s\" style=\"width: %ipx;\"/></div>\n"%(
                        str(element[1].objectName()),str(element[1].objectName()),str(element[1].text()),element[1].width()))

            
            except Exception,e:
                print e
        f.write("</form></body></html>")
        f.flush()