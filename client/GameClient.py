import pygame
import openpyxl
from socket import socket
import json
from time import sleep



COLS=ROWS=SIZE=20
SQUARE_SIZE=20

WHITE=(255,255,255)
BLACK=(0,0,0)
RED=(255,0,0)
BLUE=(0,0,255)
YELLOW = (255, 255, 0)
ORANGE=(193,134,44)
GREY=(112,112,112)


BUFSIZE = 2048
FORMAT="utf-8"
def recvObj(conn,buffsize=BUFSIZE):
    response=conn.recv(buffsize)
    response=response.decode(FORMAT)
    list=json.loads(response)
    return list
def sendObj(conn,list):
    msg=json.dumps(list,ensure_ascii=False)
    conn.sendall(bytes(msg.encode(FORMAT)))


class ShipDataList:
    def __init__(self,filename) -> None:
        self.shipPosList=self.makeShipData(self.readFile(filename))
    def readFile(self,filename):
        sheet=openpyxl.load_workbook(filename)['Sheet1']
        g = sheet.iter_rows(min_row=1, max_row=20, min_col=1, max_col=20)
        cells_list=list(g)
        data=[]
        for i in range(0,20):
            for j in range(0,20):
                if cells_list[i][j].value != None:
                    data.append((i,j))
        return data
    def makeShipData(self,data):
        shipList=[]
        for i in data:
            newShip=True
            for ship in shipList:
                for square in ship:
                    deltax=i[0]-square[0]
                    deltay=i[1]-square[1]
                    if (deltax == 1 and deltay==0) or (deltax==0 and deltay == 1):
                        ship.append(i)
                        newShip=False
                        break
            if newShip:
                shipList.append([i,])
        for ship in shipList:
            while len(ship) > 2:
                del ship[1]
        return shipList

class Square:
    def __init__(self,x,y,boardStart):
        self.pressed=False
        self.pos=(x,y)
        self.start=(x*SQUARE_SIZE+boardStart[0],y*SQUARE_SIZE+boardStart[1])
        self.drawOption=0

    def check(self,pos):
        if self.start[0]< pos[0] <self.start[0]+SQUARE_SIZE and self.start[1]<pos[1]<self.start[1]+SQUARE_SIZE:
            if self.pressed == False:
                return True
        return False
    def cross(self,win):
        #if self.pressed:
        pygame.draw.line(win,RED,self.start,(self.start[0]+SQUARE_SIZE,self.start[1]+SQUARE_SIZE))
        pygame.draw.line(win,RED,(self.start[0]+SQUARE_SIZE,self.start[1]),(self.start[0],self.start[1]+SQUARE_SIZE))
    def color(self,color,win ):
        #self.pressed=True
        pygame.draw.rect(win,color,((self.start[0],self.start[1]),(SQUARE_SIZE,SQUARE_SIZE)))
    def draw(self,win):
        if self.pressed==True:
            if self.drawOption ==1 :
                self.cross(win)
            elif self.drawOption == 2:
                self.color(RED,win)
            elif self.drawOption == 3:
                self.color(BLUE,win)


class Board:
    def __init__(self,x,y,player):
        self.boardStart=[x,y]
        self.square_list=[]
        self.player=player
        for i in range(SIZE):
            a_row=[]
            for j in range(SIZE):
                a= Square(j,i,self.boardStart)
                a_row.append(a)
            self.square_list.append(a_row)
    def draw(self,win,Font):
        pygame.draw.rect(win,GREY,((self.boardStart[0],self.boardStart[1]),(SQUARE_SIZE*SIZE,SQUARE_SIZE*SIZE)))
        # Kẻ bảng
        for i in range(ROWS+1):
            pygame.draw.line(win,BLACK,(self.boardStart[0],self.boardStart[1]+i*SQUARE_SIZE),(self.boardStart[0]+COLS*SQUARE_SIZE,self.boardStart[1]+i*SQUARE_SIZE))
            pygame.draw.line(win,BLACK,(i*SQUARE_SIZE+self.boardStart[0],self.boardStart[1]),(i*SQUARE_SIZE+self.boardStart[0],ROWS*SQUARE_SIZE+self.boardStart[1]))
        # Vẽ các ô theo tính chất
        for i in range(SIZE):
            for j in range(SIZE):
                self.square_list[i][j].draw(win)
        self.boardNameDisplay(win,Font)
        # for i in self.shipdatalist.ship_list:
        #     i.colorShip()
    def boardNameDisplay(self,WIN,Font):
        msg="Player "+ str(self.player)+"'s Board"
        msg=Font.render(msg,True,YELLOW)
        WIN.blit(msg,[self.boardStart[0]+108,self.boardStart[1]-35])
    def check(self,pos):
        for i in range(SIZE):
            for j in range(SIZE):
                if self.square_list[i][j].check(pos):
                    return (i,j)
        return False
class Game:
    def __init__(self,sever:socket,filename) -> None:
        self.sever=sever
        self.boards=[Board(0,30,1),Board(520,30,2)] #tạo 2 bàn cờ
        self.turn = 0
        shipPosList=ShipDataList(filename).shipPosList # đọc data từ file
        sendObj(self.sever,shipPosList) # gửi S list vị trí thuyền.
        self.player=int(self.sever.recv(BUFSIZE).decode(FORMAT))# nhận thông tin của Player từ S
        self.winPlayer=-1

        pygame.init()
        self.background = pygame.image.load('gameBG.jpg')
        self.background = pygame.transform.scale(self.background, (920, 500))
        self.WIN=pygame.display.set_mode((920,500))
        pygame.display.set_caption('Ship game')
        self.Font=pygame.font.SysFont("comicsansms",25)
        self.Font2=pygame.font.SysFont("comicsansms",75)
        self.clock=pygame.time.Clock()

        self.run=True
        self.close=False
    def start(self):
        #Thread(target=self.updateFromSever).start()
        while self.run and (self.close == False):
            self.clock.tick(60)
            #pygame.display.flip()
            self.WIN.blit(self.background,(0,0))
            #self.WIN.fill(WHITE)
            self.updateFromSever()  # hàm gửi update, 
            self.boards[0].draw(self.WIN,self.Font)
            self.boards[1].draw(self.WIN,self.Font)
            self.turnDisplay()
            self.yourePlayerDisplay()
            pygame.display.update()

            for event in pygame.event.get():
                # Exit game
                if event.type == pygame.QUIT:
                    msg=["END",""]
                    msg=json.dumps(msg) 
                    self.sever.sendall(bytes(msg,FORMAT))
                    self.close=True
                    self.run=False
                # Mouse Click
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos=pygame.mouse.get_pos() #nhấn chọn ô vuông
                    print(pos)
                    if self.turn==self.player:
                        pos= self.boards[(self.player+1)%2].check(pos) # ktra lượt đi
                        # Chọn trúng ô
                        if pos != False: # đứng lượt chơi
                            pos=["POS",pos] # gửi vị trí ô vừa chọn cho S (msg POS)
                            pos=json.dumps(pos)
                            self.sever.sendall(bytes(pos,FORMAT))   
        if self.close == False:
            #pygame.display.update()
            sleep(1)
        while self.close == False:
            self.WIN.blit(self.background,(0,0))
            self.win()
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    self.close=True
        pygame.quit()
    def updateFromSever(self):
        msg=["UPDATE",""]
        msg=json.dumps(msg)
        self.sever.sendall(bytes(msg,FORMAT)) # gửi msg up
        update=recvObj(self.sever,5000) # nhận 
            #break
        if update[0]=="UPDATE":
            update=update[1]
            for square in update["board0"]:
                self.boards[0].square_list[square[0][0]][square[0][1]].pressed=square[1]
                self.boards[0].square_list[square[0][0]][square[0][1]].drawOption=square[2]
            for square in update["board1"]:
                self.boards[1].square_list[square[0][0]][square[0][1]].pressed=square[1]
                self.boards[1].square_list[square[0][0]][square[0][1]].drawOption=square[2]
            self.turn=update["turn"]
            if update["winPlayer"] != -1:
                self.winPlayer=update["winPlayer"]
                self.run=False
                msg=["END",""]
                msg=json.dumps(msg)
                self.sever.sendall(bytes(msg,FORMAT))
        
        elif update[0]=="LEFT":
            self.close=True
            msg=["END",""]
            msg=json.dumps(msg)
            self.sever.sendall(bytes(msg,FORMAT))
    def win(self):
        if self.winPlayer == self.player:
            msg="You WIN"
        else:
            msg="You LOSE"
        msg=self.Font2.render(msg,True,YELLOW)
        self.WIN.blit(msg,[288,130])

    def turnDisplay(self):
        msg=self.Font.render("TURN:",True,RED)
        self.WIN.blit(msg,[425,47])
        msg="Player "+ str(self.turn+1)
        msg=self.Font.render(msg,True,ORANGE)
        self.WIN.blit(msg,[416,77])
    def yourePlayerDisplay(self):
        msg="You're Player "+str(self.player+1)
        msg=self.Font.render(msg,True,YELLOW)
        self.WIN.blit(msg,[372,435])
    