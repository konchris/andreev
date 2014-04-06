import serial
class serialport():
    maxread=200
    def __init__(self,port='COM1', baudrate=115200,bytesize=8,parity='N',stopbits=1,xonxoff=0,rtscts=0,term_chars='\r',term_char_read='\n'):
        self.port=serial.Serial(port=port,baudrate=baudrate,bytesize=bytesize,parity=parity,stopbits=stopbits,timeout=1,xonxoff=xonxoff,rtscts=rtscts)
        self.term_chars=term_chars
        self.term_char_read=term_char_read
    def write(self,data):
        self.port.write(data+self.term_chars)
    def read(self):
        return self.port.readline()
    def ask(self,data):
        self.port.write(data+self.term_chars)
        return self.port.readline()
    def clear(self):
        self.port.flushInput()
        self.port.flushOutput()
    def __del__(self):
        self.port.close()
        


