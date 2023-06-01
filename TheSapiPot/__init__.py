import logging
from scapy.all import *
import scapy.all as scapy
from scapy.layers.inet import IP, TCP
from scapy.layers.http import HTTPRequest
from TheSapiPot.sniff import Sniffer
from TheSapiPot.packetARP import check_MTIM
from TheSapiPot.packetHTTP import modelHTTP
from TheSapiPot.sniffDir import monitor_run

class HoneyPot(object):
    def __init__(self,host,interface,dirfile,logfile):
        self.host = host
        self.interface = interface
        self.dirfile = dirfile
        self.logfile = logfile
        
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
            datefmt='%y-%m-%d %H:%M:%S',
            filename=self.logfile,
            filemode='w'
        )

        self.logger = logging.getLogger(__name__)
        self.logger.info(f'[*] logfile: {self.logfile}')
        self.logger.info("[*] HoneyPot Initializing....... ")
    
    def logging_packet(self,packet: Packet):
        if packet.haslayer(TCP):
            ip = packet[IP]
            tcp = packet[TCP]
            flags = tcp.flags
            if (packet.haslayer(HTTPRequest)and ip.dst == self.host):
                prd = modelHTTP(packet)
                if prd:
                    if packet.haslayer(Raw):
                        self.logger.info(f"[HTTP Attack]\n[*]Packet Summary: {packet.summary()}\n[*]Packet Payload: {packet[Raw].load.decode()}\n[*]AI Prediction: \n{prd.predicts()}\n")  
                    else:  
                        self.logger.info(f"[HTTP Attack]\n[*]Packet Summary: {packet.summary()}\n[*]Packet Payload: {packet[HTTPRequest].Path.decode()}\n[*]AI Prediction: \n{prd.predicts()}\n") 
                else:
                    pass 
            if (flags in ["RA" ,"R", "FA", "F"]) and not ((tcp.dport in [80,8080,443] or tcp.sport in [80,8080,443])):
                print(packet[TCP])
                print(tcp.sport)
                self.logger.info(f"[Port Scan]\n[*]Packet Summary: {packet.summary()}\n")
        if packet.haslayer(ARP):
            if check_MTIM(packet):
                self.logger.info(f"[ARP SPOOF]\n[*]Packet Summary: {packet.summary()}\n")
            else:
                pass
        if packet.haslayer(UDP):
            try:
                ip = packet[IP]
                if ip.dst == self.host:
                    self.logger.info(f"[UDP port scan]\nPacket Summary: {packet.summary()}\n")
            except IndexError:
                pass


    def run(self):
        print(f"[*] Filter: For IpAddress: {self.host}\n[*] Monitoring For Directory or File: {self.dirfile}")
        sniffer = Sniffer(prn=self.logging_packet, interface=self.interface,host_ip=self.host)
        sniffer.run()
        monitor_run(self.dirfile,self.logger)