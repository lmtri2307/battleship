import re
from socket import AF_INET, socket, SOCK_STREAM, MSG_PEEK
from threading import Event, Thread
import json
from tkinter import Entry
import socket as sk
from Encrytor import Encrytor
from GameSever import Game
#import rsa
#crypt

#game

gameid=0
gameRoom={}
invitations={}

#socket
HOST = ""
PORT = 33000
BUFSIZE = 2048
FORMAT="utf-8"
ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
onlineList={} # { conn : "<username>",}
SERVER.bind(ADDR)
SERVER.listen()


 


#.................................................................
def checkDOB(string:str):
    try:
        day,month,year=string.split("/")
        day=int(day)
        month=int(month)
        year=int(year)
        if month<1 or month >12:
            return False
        months=[31,28,31,30,31,30,31,31,30,31,30,31]
        if year % 400 == 0 or (year % 4 ==0 and year % 100 != 0):
            months[1]=29
        return (day <= months[month])
    except:
        return False

def logIn(client:socket,msg):
    print(msg)
    username,password,encrypt=msg
    if encrypt:
        username=Encrytor.Decrypt(username)
        password=Encrytor.Decrypt(password)
    f=open("./accounts.json","r") #mở file đọc
    accounts=json.load(f)
    f.close()
    exist=False
    for i in accounts:
        if username ==i["username"]: # ktra username
            if password == i["password"]: #ktra pass
                msg="accept"
                onlineList[client]=username 
            else:
                msg="Wrong Password !"
            exist=True
            break
    if exist == False: # ko tìm thấy tk.
        msg="Account doesn't exist !"
    client.sendall(bytes(msg,FORMAT)) 
def signUp(client:socket,msg):
    print(msg)
    username,password,dob,note,encrypt=msg #nhận msg signup từ C
    if encrypt:
        username=Encrytor.Decrypt(username)
        password=Encrytor.Decrypt(password)
    if checkDOB(dob) == False:
        client.sendall(bytes("Invalid Date of Birth !",FORMAT))
        return
    f=open("./accounts.json","r")
    accounts=json.load(f)
    f.close()
    exist=False
    for i in accounts: #ktra xem có bị trùng username trong file json
        if username == i["username"]:
            exist=True
            break
    if exist:
        msg="Username \""+username+"\" is used !"
    else:
        #ko trùng thì thêm vào acc
        accounts.append({"username":username,"password":password,"dob":dob,"note":note,"wins": "0"})
        f=open("./accounts.json","w") #ghi file
        f.write(json.dumps(accounts))
        f.close()
        msg="accept"
        onlineList[client]=username
    client.sendall(bytes(msg,FORMAT))
def changePass(client:socket,msg):
    print(msg)
    current,new,encrypt=msg # nhận
    if encrypt:
        current=Encrytor.Decrypt(current)
        new=Encrytor.Decrypt(new)
    username=onlineList[client]
    f=open("./accounts.json","r")
    accounts=json.load(f)
    f.close()
    checkCurrent=False
    for i in accounts:
        if i["username"]==username: #tìm username vừa đổi pass
            if i["password"]==current:
                i["password"]=new
                f=open("./accounts.json","w")
                f.write(json.dumps(accounts))#ghi 
                f.close()
                checkCurrent=True
            break
    if checkCurrent:
        msg="OK"
    else:
        msg="Wrong Password !"
    client.sendall(bytes(msg,FORMAT))
def search(client:socket,username):
    f=open("./accounts.json","r")
    accounts=json.load(f)
    f.close()
    msg=["","","",""]
    for i in accounts:
        if i["username"]==username:
            #lấy in4 của username đang tìm
            msg=[i["username"],i["dob"],i["note"],i["wins"]]
            break
    msg=json.dumps(msg)
    client.sendall(bytes(msg,FORMAT)) # gửi
def online(client:socket):
    usersOnline=list(onlineList.values())
    usersOnline.remove(onlineList[client]) #except ng chơi hiện hành
    usersOnline=json.dumps(usersOnline) #đóng gòi tin danh sách ng onl
    if len(usersOnline) % BUFSIZE == 0: #TH %2048==0
        usersOnline+="."
    client.sendall(bytes(usersOnline,FORMAT)) #gửi ds onl
def waitRoom(client:socket,id):
    # 2 ng chơi phản hồi
    if gameRoom[id][2] != "" and gameRoom[id][3] != "":
        gameRoom[id][4].set()
    else:
        gameRoom[id][4].wait()
    # 2 ng đồng ý
    try:
        if gameRoom[id][2] and gameRoom[id][3]:
            # nếu game chua đc tạo
            if gameRoom[id][5] =="" :
                gameRoom[id][5]=Game()
            msg=["ACCEPT",id]
            msg=json.dumps(msg)
            client.sendall(bytes(msg,FORMAT))
        else:
            msg=["DECLINE",id]
            msg=json.dumps(msg)
            client.sendall(bytes(msg,FORMAT))
            try:
                del gameRoom[id]
            except:
                pass
    except KeyError:
        msg=["DECLINE",id]
        msg=json.dumps(msg)
        client.sendall(bytes(msg,FORMAT))
            
def invite(client:socket,opponent):
    # Lấy conn (socket) của opponent
    for i in list(onlineList.items()):
        if i[1]==opponent:
            client2=i[0]
            break
    # Check opponent có đang trong phòng chơi nào ko
    for i in list(gameRoom.values()):
        if i[0]==client2 or i[1]==client2:
            msg=["BUSY",""]
            msg=json.dumps(msg)
            client.sendall(bytes(msg,FORMAT))
            return
    idlist= list(gameRoom.keys())
    global gameid
    id=gameid
    gameid=gameid+1
    #msg =["invite", ng mời, id phòng]
    msg=["INVITE",onlineList[client],id]
    msg=json.dumps(msg)
    client2.sendall(bytes(msg,FORMAT))
    gameRoom[id]=[client,client2,True,"",Event(),""]
    waitRoom(client,id)
def updateWin(username):
    f=open("./accounts.json","r")
    accounts=json.load(f)
    f.close()
    for i in accounts:
        if i['username']==username:
            i["wins"]=str(int(i['wins'])+1)
            f=open("./accounts.json","w")
            f.write(json.dumps(accounts))
            f.close()
            break
    
def playGame(client:socket,id,playerId):
    game=gameRoom[id][5]
    game.initPlayer(client,playerId)
    run=True
    while run:
        run=game.getPlayerMove(playerId)
        winplayer=game.winPlayer
    if winplayer != -1:
    # Cộng thêm win cho player
        if winplayer == playerId:
            updateWin(onlineList[client])
        if gameRoom[id][4].is_set():
            gameRoom[id]=["","","","",Event(),""]
    
        msg=client.recv(BUFSIZE).decode(FORMAT)
        if msg=="YES":
            if gameRoom[id][0]=="":
                gameRoom[id][0]=client
                gameRoom[id][2]=True
            else:
                gameRoom[id][1]=client
                gameRoom[id][3]=True
        else:
            if gameRoom[id][0]=="":
                gameRoom[id][0]=client
                gameRoom[id][2]=False
            else:
                gameRoom[id][1]=client
                gameRoom[id][3]=False
        waitRoom(client,id)
    else:
        try:
            del gameRoom[id]
        except:
            pass
def handleClient(client:socket):
    while True:
        try:
            option=client.recv(BUFSIZE).decode(FORMAT)
            option=json.loads(option)
            if option[0]=="LOGIN":
                logIn(client,option[1:len(option)])
            elif option[0]=="SIGNUP":
                signUp(client,option[1:len(option)])
            elif option[0]=="CHANGEPASS":
                changePass(client,option[1:len(option)])
            elif option[0]=="SEARCH":
                search(client,option[1])
            elif option[0]=="ONLINE":
                online(client)
            elif option[0]=="INVITE":
                invite(client,option[1])
            elif option[0]=="ACCEPT" :
                gameRoom[option[1]][3]=True
                waitRoom(client,option[1])
            elif option[0]=="DECLINE":
                gameRoom[option[1]][3]=False
                waitRoom(client,option[1])
            elif option[0]=="PLAY":
                if gameRoom[option[1]][0]==client:
                    playGame(client,option[1],0)
                else:
                    playGame(client,option[1],1)
            elif option[0]=="LOGOUT":
                del onlineList[client]
                client.close()
                break
        except:
            print(onlineList[client],"logout")
            del onlineList[client]
            client.close()
            break
def acceptClient():
    while True:
        client,clientadrr=SERVER.accept()
        onlineList[client]=""
        Thread(target=handleClient,args=(client,)).start()
acceptClient()
SERVER.close()
