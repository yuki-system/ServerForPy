from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM, gethostname
import queue
import threading
import sys
import json


class GprcTcpSocket:
    """GeneralPurposeRemoteControllerのクライアントと1対1に通信するソケットに対応するクラス
    """
    def __init__(self, argSock, argGprcParent, serverName=""):
        self.sockTcp = argSock  # 対クライアント通信用1対1TCPソケット
        self.gprcParent = argGprcParent # 親サーバオブジェクト
        self.sockTcp.settimeout(1)

        self.serverName = serverName
        
        self.fifoSend = queue.Queue()

        self.flagAbort = False

        """ スレッドを２つ持っている
        send用とrecv用だ
        そして、queueを持っている。recv結果もしくはサーバ側の命令をsend側に渡す"""
        self.thSend = threading.Thread(target=self._thProcSend)
        self.thSend.setDaemon(True)

        self.thRecv = threading.Thread(target=self._thProcRecv)
        self.thRecv.setDaemon(True)

        self.thSend.start()
        self.thRecv.start()

    
    def sendMessage(self, argMessage):
        """Messageを送信するためのキューに入れる
        """
        self.fifoSend.put(argMessage)
    
    def _thProcSend(self):
        """クライアントへのデータ転送用のプロシージャ
        """
        while self.flagAbort == False:
            try:
                # queueから送るべきメッセージを取得
                ufoMessage = self.fifoSend.get()
                if self.flagAbort == True or ufoMessage == "ABORT":
                    break
                lenMessage = len(ufoMessage) # メッセージ長
                #GPRCをヘッダとし、続く4バイトをメッセージ長のビッグエンディアン表記として送信する
                foSendData = "GPRC".encode() + lenMessage.to_bytes(4, byteorder="big") + ufoMessage.encode()
                lenTotalSent = 0
                print("let's send")
                while lenTotalSent < lenMessage + 8:
                    lenSent = self.sockTcp.send(foSendData[lenTotalSent:])
                    if lenSent == 0:
                        raise RuntimeError("socket connection broken")
                    lenTotalSent += lenSent
            except RuntimeError as e:
                print("{0}:{1}".format(__class__.__name__ +"."+ sys._getframe().f_code.co_name, e))
                self.sockTcp.close()
                return
            except Exception as e:
                print("{0}:{1}".format(__class__.__name__ +"."+ sys._getframe().f_code.co_name, e))
                pass
        pass
    
    def _readLoop(self, argSize):
        datam = b""
        while argSize > 0:
            tdata = self.sockTcp.recv(argSize)
            if len(tdata) == 0:
                raise RuntimeError("socket connection broken")
            datam += tdata
            argSize -= len(tdata)
        return datam
    
    def _thProcRecv(self):
        """メッセージ受信用のスレッドプロシージャ
        """
        while self.flagAbort == False:
            try:
                # ヘッダを読む
                datam = self._readLoop(4)
                if self.flagAbort == True:
                    return
                if datam != "GPRC".encode():
                    continue
                print("head:{0}".format(datam.decode()))
                #データサイズを読む
                datam = self._readLoop(4)
                if self.flagAbort == True:
                    return
                dsize = int.from_bytes(datam, "big")
                print("size:{0}".format(dsize))
                #データを読む
                datam = self._readLoop(dsize)
                if self.flagAbort == True:
                    return
                sdata = datam.decode()
                print(sdata)
                self._parseRecvMessage(sdata)

            except Exception as e:
                if self.flagAbort == True:
                    return
                if e.__str__() == "timed out":
                    continue
                print("{0}:{1}".format(__class__.__name__ +"."+ sys._getframe().f_code.co_name, e))
                return
        pass
    
    def _parseRecvMessage(self, argStrJson):
        """受け取ったJSONテキストを解釈して、適切なレスポンスを行う
        """
        try:
            jsonObj = json.loads(argStrJson)
            if jsonObj["Gprc"] != "c2s":
                return
            if jsonObj["Type"] == "hello":  #接続
                self.sendMessage(self.gprcParent.buttonArray.getJson())
                return
            if jsonObj["Type"] == "button": #ボタン押下
                print("call")
                self.gprcParent.buttonArray.callFunc(jsonObj["Button"])
                return
            
        except Exception as e:
            print("{0}:{1}".format(__class__.__name__ +"."+ sys._getframe().f_code.co_name, e))
            return
        
    
    def stop(self):
        self.flagAbort = True
        self.fifoSend.put("ABORT")
        self.thRecv.join()
        self.thSend.join()
    