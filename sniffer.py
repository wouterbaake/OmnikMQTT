from scapy.all import *
from select import select
#import InverterMsg
import time
import threading
import logging

logger = logging.getLogger(__name__)

class sniffer(threading.Thread):

    #@classmethod
    def debug_callback(pkt):
        pkt.show()
            
    def __init__(self,iface=None,filter="",minInterval=60,minPacketLength=0,callback=debug_callback):
        logging.getLogger("scapy.runtime").setLevel(logging.ERROR) # Suppress warning messages from Scapy
        threading.Thread.__init__(self)
        self.iface=iface
        self.filter=filter
        self.minInterval=minInterval # The minimum interval between packages to decode (in seconds)
        self.minPacketLength=minPacketLength
        self.callback = callback
        self.lastPacketProcessed=0
        self.halt=False

    def run(self):
        #print("starting sniffer thread on:\n iface: {0}\nfilter: {1}\ncallback: {2}".format(self.iface,self.filter,self.callback.__name__))
        self.sniff(iface=self.iface,prn=self.callbackpkt, filter=self.filter)
        
        
    def callbackpkt(self,pkt):
        logger.debug("sniffer.callbackpkt()")
        if (time.time()-self.lastPacketProcessed)>self.minInterval:
            try:
                if len(pkt[TCP].load)>self.minPacketLength:
                    msg = pkt[TCP].load
                    self.lastPacketProcessed=time.time()
                    self.callback(msg)
            except AttributeError,IndexError:
                logger.warning("sniffer callbackpkt error")
    
    def sniff(self,prn = None, iface=None,filter=None):
        """Sniff packets
        sniff([count=0,] [prn=None,] [store=1,] [offline=None,] [lfilter=None,] + L2ListenSocket args) -> list of packets
        prn: function to apply to each packet. If something is returned,
        it is displayed. Ex:
        ex: prn = lambda x: x.summary()
        """
        L2socket = conf.L2listen
        s = L2socket(type=ETH_P_ALL, iface=iface, filter=filter)
        try:
            while not self.halt:
                sel = select([s],[],[],0.1)
                if s in sel[0]:
                    p = s.recv(MTU)
                    if p is None:
                        break
                    if prn:
                        r = prn(p)
                        if r is not None:
                            print r
        except:
            pass
        #print("exiting sniffer thread on:\n iface: {0}\nfilter: {1}\ncallback: {2}".format(self.iface,self.filter,self.callback.__name__))
    
if __name__ == "__main__":
    #m=InverterMsg.InverterMsg()
    #s=sniffer("eth1","tcp and host 192.168.1.12",minInterval=10,minPacketLength=10,callback=m.setAndPrintMsg)
    s=sniffer(filter="tcp and host 192.168.1.12",minInterval=10,minPacketLength=10)
    s.daemon=True
    s.start()
    try:
        while 1:
            time.sleep(1)
    except KeyboardInterrupt:
        s.halt=True
        s.join()
    print "Exiting Main Thread"