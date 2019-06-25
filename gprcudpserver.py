from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM, gethostname
import threading
from time import sleep
import sys
import os

UDP_ECHO_BACK_HEADER = "Magick Number "
UDP_RECV_PORT = 60001
UDP_SEND_PORT = 60002
TCP_PORT = 60011

class GprcUDPServer:
    """GeneralPurposeRemoteControllerのUDPecho-back機能を提供するクラス
    """
    def __init__(self, serverName = ""):
        self.serverName = serverName    # サーバ名

        self.sockUdp = socket(AF_INET, SOCK_DGRAM)  # UDP用ソケット
        self.sockUdp.bind(("", UDP_RECV_PORT))
        self.sockUdp.settimeout(1)

        self.flagAbort = False  # 受信スレッド用のAbortフラグ

        self.thUdp = threading.Thread(target=self._udpRunning)  #udp受信スレッド
        self.thUdp.setDaemon(True)
        self.thUdp.start()
    
    def _udpRunning(self):
        """udpで受信待ちして、echo-backすることで存在を示すスレッドプロシージャ
        """
        print("udp runnninng...")
        while self.flagAbort == False:
            try:
                msg, address = self.sockUdp.recvfrom(1024)
                if msg.decode() != UDP_ECHO_BACK_HEADER:
                    print("catched, msg:{0}, addr:{1}".format(msg.decode(), address))
                    continue
                
                # addressはhostaddressの文字列とポート番号のタプルから成ることに留意
                print("msg:{0}, addr:{1}".format(msg.decode(), address))
                sockSendUdp = socket(AF_INET, SOCK_DGRAM)
                addrBroad = (self._toBroadcastAddr(address[0]), UDP_SEND_PORT)
                sockSendUdp.sendto((bytes)(self.serverName.encode()), addrBroad)
            except Exception as e:
                if e.__str__() == "timed out":
                    continue
                print(e)
                break
    
    def stop(self):
        """スレッド停止用関数
        スレッドはデーモンで動かしているので、必ずしも呼ぶことが必要なわけではない
        """
        self.flagAbort = True
        self.thUdp.join()
        print("stop")
    
    def _toBroadcastAddr(self, addr):
        addrlist = addr.split(".")
        numAddrlist = list(map(int, addrlist))
        if numAddrlist[0] < 128:
            numAddrlist[1] = 255
        if numAddrlist[0] < 192:
            numAddrlist[2] = 255
        if numAddrlist[0] < 244:
            numAddrlist[3] = 255
        return ("{0}.{1}.{2}.{3}".format(numAddrlist[0],\
                                            numAddrlist[1],\
                                            numAddrlist[2],\
                                            numAddrlist[3]))
