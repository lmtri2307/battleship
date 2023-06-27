
import json
from socket import socket
from threading import Event

BUFSIZE = 2048
FORMAT="utf-8"
COLS=ROWS=SIZE=20
SQUARE_SIZE=20
# nhận obj
def recvObj(conn,buffsize=BUFSIZE):
    response=conn.recv(buffsize)
    response=response.decode(FORMAT)
    list=json.loads(response)
    return list
# gửi obj0
def sendObj(conn,list):
    msg=json.dumps(list,ensure_ascii=False)
    conn.sendall(bytes(msg.encode(FORMAT)))

class Ship:
    # create ship
    def __init__(self,board,pos_start,pos_end) :
        try:
            self.squares=[]
            for i in range(pos_start[0],pos_end[0]+1):
                for j in range(pos_start[1],pos_end[1]+1):
                    board.square_list[i][j].ship=self
                    self.squares.append(board.square_list[i][j])
            self.chose=False #thuyền chưa đc chọn
        except:
            print("Ship")
    def checkShip(self):
        for square in self.squares: 
            if square.pressed == False:
                return
        self.chose=True # chọn thuyền
        for square in self.squares:
            square.draw=3
            square.updated=["",""]
class ShipDataList:
    def __init__(self,board,shipPosList) -> None:
        self.ship_list=[]
        try:
            for ship in shipPosList:
                self.ship_list.append(Ship(board,ship[0],ship[len(ship)-1]))
        except:
            print("ShipdataList")
    def checkAllShip(self): #kiểm tra xem all thuyền đc chọn 
        for i in self.ship_list:
            if i.chose==False:
                return False
        return True

class Square:
    def __init__(self,x,y):
        self.updated=[True,True]
        self.pressed=False
        self.pos=(x,y)
        self.ship=None
        self.draw=0 # 0:ko vẽ |1: vẽ X|2:tô đỏ|3:tô xanh
        #self.change=0 # ô ko thay đổi
    def check(self):
        self.updated=["",""]
        self.pressed=True
        self.draw=1
        if self.ship != None: # nếu có thuyền
            self.draw=2
            self.ship.checkShip()
            return True  # Chọn trúng thuyền hay không
        return False
#tạo bàn cờ
class Board:
    def __init__(self,shipPosList):
        self.square_list=[]
        for i in range(SIZE):
            a_row=[]
            for j in range(SIZE):
                a= Square(j,i)
                a_row.append(a)
            self.square_list.append(a_row)
        self.shipdatalist=ShipDataList(self,shipPosList)
     #this   
    def check(self,pos):
        if self.square_list[pos[0]][pos[1]].check():
            if self.shipdatalist.checkAllShip():
                return [True,True] 
            else:
                return [True,False]
        return [False,False]
    def getData(self,player):
        list=[]
        for i in range(0,SQUARE_SIZE):
            for j in range(0,SQUARE_SIZE):
                if self.square_list[i][j].updated[player]!=True:
                    self.square_list[i][j].updated[player]=True
                    list.append([[i,j],self.square_list[i][j].pressed,self.square_list[i][j].draw])
        return list
    
class Player:
    def __init__(self,conn:socket) -> None:
        self.conn=conn
        self.playing=True
        self.turn=Event()
        shipdataPosList=recvObj(self.conn)
        self.board=Board(shipdataPosList)
class Game:
    def __init__(self) -> None:
        self.players=["",""] #khởi tạo 2 ng chơi
        self.playerscount=0 # đang có 0 ng chơi
        self.start=Event()
        self.end=Event()    
        self.winPlayer=-1 #không ng thắng
        self.turn=0 #0,1
    def initPlayer(self,client:socket,playerID):
        self.players[playerID]=Player(client) #Tạo player
        self.playerscount=self.playerscount+1 #đếm player
        if self.playerscount != 2:
            self.start.wait()   #chưa đủ 2, đợi
        else:
            self.start.set()    #đủ 2
        client.sendall(bytes(str(playerID),FORMAT))  # gửi cho client biết mình là player mấy
    # def startGame(self):
    #     player=0
    #     while not self.end.is_set():
    #         if self.getPlayerMove(player):
    #             player=(player+1)%2
    def getPlayerMove(self,player:int):
        try:
            #nhận msg POS từ Client
            pos=self.players[player].conn.recv(BUFSIZE).decode(FORMAT)
        except:
            self.players[player].playing=False
            return False
        pos=json.loads(pos)
        if pos[0]=="POS":
            pos=pos[1]
            result=self.players[(player+1) %2].board.check(pos)
            if result[0]: # ktra xem có ng thắng chưa
                if result[1]:
                    self.winPlayer=player
            else:
                self.turn=(self.turn+1)%2# đổi lượt
        elif pos[0]=="UPDATE":
            self.updateToClient(player,self.winPlayer,self.players[0].board.getData(player),self.players[1].board.getData(player),self.turn)
        elif pos[0]=="END":
            self.players[player].playing=False
            return False
        return True
    def updateToClient(self,player,winPlayer,board0,board1,turn):
        if self.players[(player+1)%2].playing or winPlayer!=-1:# nếu đối thủ còn chơi 
            msg=["UPDATE",{"winPlayer":winPlayer,"board0":board0,"board1":board1,"turn":turn}]
        else: # nếu đối thủ rời
            msg=["LEFT",""]
        #gửi C thông tin của ván chơi hiện tại
        sendObj(self.players[player].conn,msg)
