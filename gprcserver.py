import gprcudpserver
from gprctcpconnectionserver import GprcTcpConnectionServer
from gprcbuttonarray import GprcButtonArray

class GprcServer:
    """GeneralPurposeRemoteControllerのサーバを提供するクラス
    """
    def __init__(self, serverName = ""):
        self.serverName = serverName    # サーバ名

        self.udpServer = gprcudpserver.GprcUDPServer(serverName)
        self.flagAbort = False  # 受信スレッド用のAbortフラグ

        self.tcpServer = GprcTcpConnectionServer(self, serverName)

        self.buttonArray = GprcButtonArray()

    def stop(self):
        """スレッド停止用関数
        スレッドはデーモンで動かしているので、必ずしも呼ぶことが必要なわけではない
        """
        self.flagAbort = True
        self.udpServer.stop()
        self.tcpServer.stop()
        print("stop")
    
def testFunc():
    print("called: 1")

if __name__ == "__main__":
    s = GprcServer("hoge server")
    s.buttonArray.strText = "よ　う　こ　そ"
    s.buttonArray.setFunc("1", testFunc)
    strIn = input()
    s.stop()



