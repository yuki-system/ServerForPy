from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM, gethostname
TCP_PORT = 60011
import threading
import sys

from gprctcpsocket import GprcTcpSocket

class GprcTcpConnectionServer:
    """GeneralPurposeRemoteControllerのTCPソケットの接続を提供するクラス
    """
    def __init__(self, argGprcParent, serverName = ""):
        self.serverName = serverName    # サーバ名
        self.gprcParent = argGprcParent # GPRCServer親オブジェクト

        self.flagAbort = False  # 受信スレッド用のAbortフラグ

        self.sockTcp = socket(AF_INET, SOCK_STREAM)
        self.sockTcp.bind((gethostname(), TCP_PORT))
        self.sockTcp.settimeout(5)
        self.sockTcp.listen(5)
        
        self.thTcp = threading.Thread(target=self._tcpRunning)  #Tcp接続待ちスレッド
        self.thTcp.setDaemon(True)
        self.thTcp.start()

        self.listSocket2Cli = []    #対クライアントソケットクラスのリスト
    
    def sendMessage(self, argMessage):
        for sockobj in self.listSocket2Cli:
            sockobj.sendMessage(argMessage)

    def _tcpRunning(self):
        """tcp通信をバックグラウンドでやり取りするスレッドプロシージャ
        """
        while self.flagAbort == False:
            try:
                (clientTcp, addr) = self.sockTcp.accept()   # 接続を待機する
                self.listSocket2Cli.append(GprcTcpSocket(clientTcp, self.gprcParent, self.serverName))
                print("TCP Connect:"+ addr[0])

            except Exception as e:
                if e.__str__() == "timed out":
                    continue
                print("{0}:{1}".format(__class__.__name__ +"."+ sys._getframe().f_code.co_name, e))
                break
    
    def stop(self):
        """スレッド停止用関数
        スレッドはデーモンで動かしているので、必ずしも呼ぶことが必要なわけではない
        """
        self.flagAbort = True
        for sockobj in self.listSocket2Cli:
            sockobj.stop()
        print("stop")


