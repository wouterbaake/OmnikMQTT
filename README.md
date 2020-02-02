[![Travis-CI Build Status](https://travis-ci.org/wouterbaake/OmnikMQTT.svg)](https://travis-ci.org/wouterbaake/OmnikMQTT.svg)
# OmnikMQTT

This program is intended for OmnikSol PV inverters with a wifi datalogger card that has a serial number that starts with 601. These wifi dataloggers do not have the ability to respond to http requests as the later models, but send out the data to Omnikportal.com every 5 minutes. This software is intended to sniff these packets and extract the PV information. The data is then reported via MQTT.

To enable sniffing, the software should run either on the router through which the packets flow, or you should make sure that the packets reach the host on which you're running this software. One option is to use iptables to create a duplicate package that gets sent to your sniffer. That way, you get the benefit of both logging to omnikportal.com and via MQTT.

Add this line to your configuration: 
```
iptables -t mangle -A PREROUTING -s <Omnik IP> -p tcp -j TEE --gateway <Sniffer IP>
```

This require iptables-mod-tee to be installed.

Steps to run program:
- Clone repository
- Edit config-org.cfg and rename to config.cfg
- Edit your router configuration to ensure that packages from the inverter are redirected or duplicated to the IP address of your logger (refer to router manual how to do this, or use command stated above)
- Run "sudo python3 OmnikMQTT.py &"

Run program as root because scapy sniffer requires root privileges to open a raw port.

This software is based on https://github.com/Woutrrr/Omnik-Data-Logger
