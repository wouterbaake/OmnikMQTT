#!/usr/bin/python

import InverterMsg      # Import the Msg handler
import socket               # Needed for talking to inverter
import datetime             # Used for timestamp
import time                 # Used for sleep function
import sys
import signal
import logging
import ConfigParser, os
import daemon
import paho.mqtt.publish as publish
import sniffer



def MQTTcallback(pkt):
    logger.debug("Callback")
    msg.setMsg(pkt)
    now = datetime.datetime.now()

    logger.debug("ID: {0}".format(msg.getID())) 

    if mqtt_enabled:
        d=msg.getDict()
        msgs=list()
        for key in d:
            msgs.append((mqtt_topic+"/"+key,d[key],0,False))
        logger.debug("Publishing packet data to MQTT broker")
        publish.multiple(msgs,hostname=mqtt_host,port=mqtt_port)
    msg.clear()

        
if __name__ == "__main__":
    mydir = os.path.dirname(os.path.abspath(__file__))
    config = ConfigParser.RawConfigParser()
    # Load the setting file
    config.read([mydir + '/config-org.cfg', mydir + '/config.cfg'])
    
    ip              = config.get("inverter","ip")
    sniff_iface     = config.get("inverter",'sniff_iface')

    log_enabled     = config.getboolean('log','log_enabled')
    log_filename    = mydir + '/' + config.get('log','log_filename')

    mqtt_enabled    = config.getboolean('mqtt','mqtt_enabled')
    mqtt_host       = config.get('mqtt','mqtt_host')
    mqtt_port       = config.get('mqtt','mqtt_port')
    mqtt_topic      = config.get('mqtt','mqtt_topic')
    
    logger = logging.getLogger(__name__)
    hdlr = logging.FileHandler(log_filename)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr) 
    logger.setLevel(logging.DEBUG)
    
    msg = InverterMsg.InverterMsg()

    logging.getLogger("scapy.runtime").setLevel(logging.ERROR) # Suppress warning messages from Scapy

    if mqtt_enabled:
        logger.debug('publishing to MQTT: %s : %s' % (mqtt_topic,"OmnikExport running"))
        publish.single(mqtt_topic,"OmnikExport running",hostname=mqtt_host,port=mqtt_port)
    
    logger.info('sniffing data with filter %s on %s. Callback function = %s' % ("tcp and host "+ip,sniff_iface,MQTTcallback))
    sn=sniffer.sniffer(sniff_iface,"tcp and host "+ip,minInterval=10,minPacketLength=120,callback=MQTTcallback)
    sn.daemon=True
    sn.start()
    
    while True:
        time.sleep(5)
        
    if mqtt_enabled:
        publish.single(mqtt_topic,"OmnikExport stopping",hostname=mqtt_host,port=mqtt_port)