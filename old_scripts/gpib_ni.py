from ctypes import *
from time import sleep
dll=WinDLL('gpib-32.dll')
timeout=1000
if dll.ibdev(0,1,0,timeout,1,0)<0: raise Exception('GPIB load failed.')
ibsta=c_uint16.in_dll(dll, "user_ibsta")
iberr=c_uint16.in_dll(dll, "user_iberr")
ibcnt=c_uint16.in_dll(dll, "user_ibcnt")
ibcntl=c_int.in_dll(dll, "user_ibcntl")

#for ICS-cards
#ibsta,iberr,ibcnt,ibcntl=c_uint16(),c_uint16(),c_uint16(),c_int()
#dll.ibptrs(pointer(ibsta), pointer(iberr), pointer(ibcnt), pointer(ibcntl))

boardnr=c_uint16(0)
DABend = c_uint16(1)
readbuff=create_string_buffer(20000+2)
readp=pointer(readbuff)
bufflen=c_int(len(readbuff)-2)

def get_instruments_list():
    addrlist=c_uint16*30
    addresslist=addrlist(*range(1,31))
    resultlist=addrlist()
    addresslist[-1]=-1
    dll.FindLstn(boardnr,pointer(addresslist),pointer(resultlist),c_int(30))
    return list(resultlist)[:ibcntl.value]
    
class instrument():
    def __init__(self,addr,term_chars='',term_char_read=None, delay=0):
        self.delay=delay
        self.addr=c_uint16(addr)
        self.term_chars=term_chars
        self.term_char_read=term_char_read
        if term_char_read is None:
            self.STOPend =c_uint16(0x0100)
        else:
            self.STOPend=c_uint16(ord(term_char_read))
    def setreadbuffer(self,buffsize):
        global readbuff,readp,bufflen
        readbuff=create_string_buffer(buffsize+2)
        readp=pointer(readbuff)
        bufflen=c_int(buffsize)
    def write(self,data):
        print(data)
        buff=create_string_buffer(data+self.term_chars)
        dll.Send(boardnr,self.addr,pointer(buff),c_int(len(buff.value)),DABend)
    def write_a(self,data):
        """Writes to Agilent and asks for occuring errors"""
        self.write(data)
        i = 0
        while i < 10:
            answer = self.ask(':SYST:ERR?')
            if answer[1] == '0':
                break
            else:
                i = i+1
                print data +': '+answer
    def read(self):
        dll.Receive(boardnr,self.addr,readp,bufflen,self.STOPend)
        return readbuff.value[:ibcnt.value]
    def ask(self,data):
        buff=create_string_buffer(data+self.term_chars)
        dll.Send(boardnr,self.addr,pointer(buff),c_int(len(buff.value)),DABend)
        if self.delay>0: sleep(self.delay)
        dll.Receive(boardnr,self.addr,readp,bufflen,self.STOPend)
        return readbuff.value[:ibcnt.value].rstrip()
    def ask_a(self,data):
        buff=create_string_buffer(data+self.term_chars)
        dll.Send(boardnr,self.addr,pointer(buff),c_int(len(buff.value)),DABend)
        if self.delay>0: sleep(self.delay)
        dll.Receive(boardnr,self.addr,readp,bufflen,self.STOPend)
        backup_return = readbuff.value[:ibcnt.value].rstrip()
        i = 0
        while i < 10:
            answer = self.ask(':SYST:ERR?')
            if answer[1] == '0':
                if i==0:
                    print data
                break
            else:
                i = i+1
                print data +': '+answer
        return backup_return
    def clear(self):
        dll.DevClear(boardnr,self.addr)


