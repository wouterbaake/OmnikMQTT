import struct               # Converting bytes to numbers
import functools
import logging

logger = logging.getLogger(__name__)

class InverterMsg:
    'Class for Inverter message'
    
    def checkInit(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            if (args[0].rawmsg == None): return None
            else: return func(*args, **kwargs)
        return inner
        
    def __init__(self, msg=None, offset=15):
        self.rawmsg = msg
        self.offset = offset
    
    def clear(self):
        self.rawmsg=None
    
    def initialized(self):
        return not(self.rawmsg==None)
    
    @checkInit
    def __getString(self, begin, end):
        return self.rawmsg[begin:end]
    
    @checkInit
    def __getShort(self, begin, divider=10):
        num = struct.unpack('!H', self.rawmsg[begin:begin+2])[0]
        if num == 65535:
            return -1
        else:
            return float(num)/divider
            
    @checkInit
    def __getLong(self, begin, divider=10):
        return float(struct.unpack('!I', self.rawmsg[begin:begin+4])[0])/divider
        
    def getID(self):
        return self.__getString(self.offset,self.offset+16)

    def getTemp(self):
        return self.__getShort(self.offset+16)
    
    def getPower(self):
        return self.__getShort(self.offset+44)
        
    def getVPV(self, i=1):
        if i  not in range(1, 4):
            i = 1
        num = self.offset+18 + (i-1)*2
        return self.__getShort(num)
        
    def getIPV(self, i=1):
        if i not in range(1, 4):
            i=1
        num = self.offset+24 + (i-1)*2
        return self.__getShort(num)
    
    def getIAC(self, i=1):
        if i not in range(1, 4):
            i=1
        num = self.offset+30 + (i-1)*2
        return self.__getShort(num)
        
    def getVAC(self, i=1):
        if i not in range(1, 4):
            i=1
        num = self.offset+36 + (i-1)*2
        return self.__getShort(num)  

    def getFAC(self, i=1):
        if i not in range(1, 4):
            i=1
        num = self.offset+42 + (i-1)*4
        return self.__getShort(num, 100)          

    def getPAC(self, i=1):
        if i not in range(1, 4):
            i=1
        num = self.offset+44 + (i-1)*4
        return int(self.__getShort(num, 1)) # Don't divide
    
    def getEToday(self):
        return self.__getShort(self.offset+54, 100)     # Divide by 100

    def getETotal(self):
        return int(self.__getLong(self.offset+60, 1))  # Don't divide
    
    def getDict(self):
        d = {'ID':self.getID()}
        d["Temp"]=self.getTemp()
        d["Power"]=self.getPower()
        for i in range(1,4):
            d["VPV"+str(i)]=self.getVPV(i)
            d["IPV"+str(i)]=self.getIPV(i)
            d["VAC"+str(i)]=self.getVAC(i)
            d["IAC"+str(i)]=self.getIAC(i)
            d["FAC"+str(i)]=self.getFAC(i)
            d["PAC"+str(i)]=self.getPAC(i)
        d["EToday"]=self.getEToday()
        d["ETotal"]=self.getETotal()
        return d

    def setMsg(self,msg):
        self.rawmsg=msg
    
    def printDict(self):
        print(self.getDict())
    
    def setAndPrintMsg(self,msg):
        self.rawmsg=msg
        self.printDict()
        
def generate_string(ser):
    '''
    The request string is build from several parts. The first part is a
    fixed 4 char string; the second part is the reversed hex notation of
    the s/n twice; then again a fixed string of two chars; a checksum of
    the double s/n with an offset; and finally a fixed ending char.
    '''
    responseString = '\x68\x02\x40\x30';

    doublehex = hex(ser)[2:]*2
    hexlist = [ doublehex[i:i+2].decode('hex') for i in 
        reversed(range(0, len(doublehex), 2))]

    cs_count = 115 + sum([ ord(c) for c in hexlist])
    cs = hex(cs_count)[-2:].decode('hex')
    responseString += ''.join(hexlist) + '\x01\x00'+cs+'\x16'
    return responseString
