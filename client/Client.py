
import tkinter as tk
from tkinter import ttk, messagebox as mbox
from socket import AF_INET, socket, SOCK_STREAM, MSG_PEEK
import json
from tkinter import *
from threading import Thread, Event
from GameClient import Game
from Encrytor import Encrytor

client_socket = socket(AF_INET, SOCK_STREAM)

BUFSIZE = 2048
FORMAT = "utf-8"



class ClientGUI(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry("500x300")
        self.resizable(width=False, height=False)
        self.protocol("WM_DELETE_WINDOW", self.onClosing)
        self.online = Event()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (ConnectionPage, StartPage,GamePage, ChangePasswordPage, LoginPage,  SignupPage, SearchPage, OnlinePage, WaitingPage, GetFilePage):
            frame = F(self, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")
        self.showFrame(ConnectionPage)

    def showFrame(self, container):
        frame = self.frames[container]
        self.geometry(frame.geometry)
        self.title(frame.title)
        tk.Misc.lift(frame, aboveThis=None)
        frame.clear()
        frame.focus_force()

    def onClosing(self):
        if askYesNo("Quit?", "Do you want to quit ?") == False:
            return
        try:
            msg = ["LOGOUT", ""]
            msg = json.dumps(msg)
            client_socket.sendall(bytes(msg, FORMAT))
        except:
            pass
        self.destroy()

    def replyMsg(self, opponent="Your opponent"):
        msg = client_socket.recv(BUFSIZE).decode(FORMAT)
        msg = json.loads(msg)
        if msg[0] == "ACCEPT":
            infMsg("Accepted", opponent+" has accepted your invitation")
            msg = ["PLAY", msg[1]]
            msg = json.dumps(msg)
            client_socket.sendall(bytes(msg, FORMAT))
            self.showFrame(GetFilePage)
        elif msg[0] == "DECLINE":
            infMsg("Declined", opponent+" has declined your invitation")
            self.showFrame(OnlinePage)
        elif msg[0] == "BUSY":
            infMsg("Invite Incomplete", opponent +
                   " is playing or invited by other player")
            self.showFrame(OnlinePage)

    def playGame(self, filename):
        try:
            x = Game(client_socket, filename)
        except:
            errorMsg("Can't read your file! Please your check filename")
            self.showFrame(GetFilePage)
            return
        # self.showFrame(PlayingPage)
        self.withdraw()
        x.start()
        self.deiconify()
        if x.winPlayer != -1:
            if askYesNo("Rematch", "Do you want to rematch ?"):
                client_socket.sendall(bytes("YES", FORMAT))
                self.showFrame(WaitingPage)
                Thread(target=self.replyMsg, daemon=True).start()
            else:
                client_socket.sendall(bytes("NO", FORMAT))
                client_socket.recv(BUFSIZE)
                self.showFrame(GamePage)
        elif x.run == True:
            errorMsg("Your opponent has left the game")
            self.showFrame(GamePage)
        else:
            self.showFrame(GamePage)


class ConnectionPage(tk.Frame):
    def __init__(self, parent, controller: ClientGUI):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.title = "Input Sever"
        self.geometry = "500x200"

        self.configure(bg="bisque2")
        label_ip = tk.Label(self, text="IP ", fg='#20639b',
                            bg="bisque2", font='verdana 10 ')
        label_port = tk.Label(self, text="PORT ", fg='#20639b',
                              bg="bisque2", font='verdana 10 ')

        self.entry_ip = tk.Entry(self, width=20, bg='light yellow')
        self.entry_port = tk.Entry(self, width=20, bg='light yellow')
        self.entry_port.bind("<Return>", self.connect)

        button_connect = tk.Button(
            self, text="CONNECT", bg="#20639b", fg='floral white', command=self.connect)

        label_ip.pack()
        self.entry_ip.pack()
        label_port.pack()
        self.entry_port.pack()
        button_connect.pack()

    def clear(self):
        self.controller.online.clear()
        self.entry_ip.delete(0, "end")
        self.entry_port.delete(0, "end")

    def connect(self, e=None):
        ip = self.entry_ip.get()
        port = self.entry_port.get()
        try:
            port = int(port)
        except:
            errorMsg("Invalid Input !")
            return
        try:
            client_socket.connect((ip, port))
            self.controller.showFrame(StartPage)
        except:
            errorMsg("Can't connect to sever !")
            return


class StartPage(tk.Frame):
    def __init__(self, parent, controller: ClientGUI):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.title = "Battle Ship"
        self.geometry = "500x200"

        button_LOGIN = tk.Button(self,
                                 text="Already have an account!",
                                 command=lambda: self.controller.showFrame(LoginPage))
        button_LOGIN.pack(fill='both', expand=True)
        button_SIGNUP = tk.Button(self, text="Create an account",
                                  command=lambda: self.controller.showFrame(SignupPage))
        button_SIGNUP.pack(fill='both', expand=True)

    def clear(self):
        pass


class GamePage(tk.Canvas):
    def __init__(self, parent, controller: ClientGUI):
        tk.Canvas.__init__(self, parent, bg="#ffffff", height=551,
                           width=987, bd=0, highlightthickness=0, relief="ridge")
        self.controller = controller
        self.title = "Battle Ship"
        self.geometry = "987x551"

        self.background_img = PhotoImage(file=f"./MenuGame/background.png")
        background = self.create_image(
            493.5, 275.5,
            image=self.background_img)

        self.img0 = PhotoImage(file=f"./MenuGame/img0.png")
        b0 = Button(self,
                    image=self.img0,
                    borderwidth=0,
                    highlightthickness=0,
                    command=self.online,
                    relief="flat")

        b0.place(
            x=342, y=228,
            width=277,
            height=58)

        self.img1 = PhotoImage(file=f"./MenuGame/img1.png")
        b1 = Button(self,
                    image=self.img1,
                    borderwidth=0,
                    highlightthickness=0,
                    command=self.changePassword,
                    relief="flat")

        b1.place(
            x=220, y=304,
            width=537,
            height=58)

        self.img2 = PhotoImage(file=f"./MenuGame/img2.png")
        b2 = Button(self,
                    image=self.img2,
                    borderwidth=0,
                    highlightthickness=0,
                    command=self.exit,
                    relief="flat")

        b2.place(
            x=342, y=461,
            width=277,
            height=58)

        self.img3 = PhotoImage(file=f"./MenuGame/img3.png")
        b3 = Button(self,
                    image=self.img3,
                    borderwidth=0,
                    highlightthickness=0,
                    command=self.search,
                    relief="flat")

        b3.place(
            x=342, y=379,
            width=277,
            height=58)

        Thread(target=self.listenForInvitation, daemon=True).start()

    def online(self):
        self.controller.showFrame(OnlinePage)

    def changePassword(self):
        self.controller.showFrame(ChangePasswordPage)

    def exit(self):
        self.controller.onClosing()

    def search(self):
        self.controller.showFrame(SearchPage)

    def listenForInvitation(self):
        while True:
            self.controller.online.wait()
            try:
                # đọc lén
                msg = client_socket.recv(BUFSIZE, MSG_PEEK).decode(FORMAT)
                msg = json.loads(msg)
                if msg[0] == "INVITE":
                    client_socket.recv(BUFSIZE).decode(FORMAT)
                    if askYesNo("Invitation", "Would you like to join a game with "+msg[1]):
                        msg = ["ACCEPT", msg[2]]
                        msg = json.dumps(msg)
                        client_socket.sendall(bytes(msg, FORMAT))

                        msg = client_socket.recv(BUFSIZE).decode(FORMAT)
                        msg = json.loads(msg)
                        msg = ["PLAY", msg[1]]
                        msg = json.dumps(msg)
                        client_socket.sendall(bytes(msg, FORMAT))
                        self.controller.showFrame(GetFilePage)
                    else:
                        msg = ["DECLINE", msg[2]]
                        msg = json.dumps(msg)
                        client_socket.sendall(bytes(msg, FORMAT))
                        client_socket.recv(BUFSIZE)
            except:
                pass

    def clear(self):
        pass


class SignupPage(tk.Canvas):
    def __init__(self, parent, controller: ClientGUI):
        tk.Canvas.__init__(self, parent, bg="#ffffff", height=442,
                           width=867, bd=0, highlightthickness=0, relief="ridge")
        self.controller = controller
        self.geometry = "867x442"
        self.title = "Signup Page"

        self.background_img = PhotoImage(file=f"./Signuppage/background.png")
        background = self.create_image(
            433.5, 221.0,
            image=self.background_img)

        self.entry0_img = PhotoImage(file=f"./Signuppage/img_textBox0.png")
        entry0_bg = self.create_image(
            599.0, 217.5,
            image=self.entry0_img)

        self.password_box = Entry(master=self,
                                  show="*",
                                  bd=0,
                                  bg="#aa9a9a",
                                  highlightthickness=0)

        self.password_box.place(
            x=418, y=205,
            width=362,
            height=23)

        self.entry1_img = PhotoImage(file=f"./Signuppage/img_textBox1.png")
        entry1_bg = self.create_image(
            599.0, 271.5,
            image=self.entry1_img)

        self.dob_box = Entry(master=self,
                             bd=0,
                             bg="#aa9a9a",
                             highlightthickness=0)

        self.dob_box.place(
            x=418, y=259,
            width=362,
            height=23)

        self.entry2_img = PhotoImage(file=f"./Signuppage/img_textBox2.png")
        entry2_bg = self.create_image(
            599.0, 325.5,
            image=self.entry2_img)

        self.note_box = Entry(master=self,
                              bd=0,
                              bg="#aa9a9a",
                              highlightthickness=0)

        self.note_box.place(
            x=418, y=313,
            width=362,
            height=23)

        self.entry3_img = PhotoImage(file=f"./Signuppage/img_textBox3.png")
        entry3_bg = self.create_image(
            599.0, 160.0,
            image=self.entry3_img)

        self.username_box = Entry(master=self,
                                  bd=0,
                                  bg="#aa9a9a",
                                  highlightthickness=0)

        self.username_box.place(
            x=418, y=149,
            width=362,
            height=20)

        self.img0 = PhotoImage(file=f"./Signuppage/img0.png")
        b0 = Button(master=self,
                    image=self.img0,
                    borderwidth=0,
                    highlightthickness=0,
                    command=self.back,
                    relief="flat")

        b0.place(
            x=9, y=392,
            width=148,
            height=40)

        self.img1 = PhotoImage(file=f"./Signuppage/img1.png")
        b1 = Button(master=self,
                    image=self.img1,
                    borderwidth=0,
                    highlightthickness=0,
                    command=self.signUp,
                    relief="flat")

        b1.place(
            x=652, y=392,
            width=148,
            height=40)

    def clear(self):
        self.dob_box.delete(0, "end")
        self.note_box.delete(0, "end")
        self.password_box.delete(0, "end")
        self.password_box.delete(0, "end")

    def back(self):
        self.controller.showFrame(StartPage)

    def signUp(self):
        username = self.username_box.get()  # get in4 in the box
        if username == "":
            errorMsg("Username can't be blank")
            return
        password = self.password_box.get()
        if password == "":
            errorMsg("Password can't be blank")
            return
        dob = self.dob_box.get()
        if dob == "":
            errorMsg("DOB can't be blank")
            return
        note = self.note_box.get()
        if askYesNo("Encrypt?", "Do you want to encrypt message before sending ?"):
            msg = ["SIGNUP", Encrytor.Encrypt(
                username), Encrytor.Encrypt(password), dob, note, True]
        else:
            msg = ["SIGNUP", username, password, dob, note, False]
        msg = json.dumps(msg)
        if len(msg) > BUFSIZE:
            msg = ["SIGNUP", username, password, dob]
            msg = json.dumps(msg)
            errorMsg("This note is too long ! Note's length must be under " +
                     str(2040-len(msg))+" characters")
            return
        try:
            client_socket.sendall(bytes(msg, FORMAT))
        except:
            errorMsg("Sever is close !")
            self.controller.showFrame(ConnectionPage)
            return
        msg = client_socket.recv(BUFSIZE).decode(FORMAT)
        if msg == "accept":  # nhận msg từ S
            self.controller.online.set()
            self.controller.showFrame(GamePage)
        else:
            errorMsg(msg)


class SearchPage(tk.Canvas):
    def __init__(self, parent, controller: ClientGUI):
        tk.Canvas.__init__(self, parent, bg="#ffffff", height=442,
                           width=867, bd=0, highlightthickness=0, relief="ridge")
        self.controller = controller
        self.geometry = "867x442"
        self.title = "Search"

        self.name = tk.StringVar()
        self.dob = tk.StringVar()
        self.wins = tk.StringVar()
        self.note = tk.StringVar()

        self.background_img = PhotoImage(file=f"./Search/background.png")
        background = self.create_image(
            433.5, 221.0,
            image=self.background_img)

        self.img0 = PhotoImage(file=f"./Search/img0.png")
        b0 = Button(self,
                    image=self.img0,
                    borderwidth=0,
                    highlightthickness=0,
                    command=self.back,
                    relief="flat")

        b0.place(
            x=21, y=384,
            width=96,
            height=40)

        self.entry0_img = PhotoImage(file=f"./Search/img_textBox0.png")
        entry0_bg = self.create_image(
            442.5, 46.0,
            image=self.entry0_img)

        self.search_box = Entry(self,
                                bd=0,
                                bg="#698498",
                                highlightthickness=0)

        self.search_box.place(
            x=175, y=30,
            width=535,
            height=30)

        self.entry1_img = PhotoImage(file=f"./Search/img_textBox1.png")
        entry1_bg = self.create_image(
            518.5, 300.0,
            image=self.entry1_img)

        note_box = Label(self, textvariable=self.note,
                         bd=0,
                         bg="#698498",
                         highlightthickness=0)

        note_box.place(
            x=251, y=284,
            width=535,
            height=30)

        self.entry2_img = PhotoImage(file=f"./Search/img_textBox2.png")
        entry2_bg = self.create_image(
            518.5, 238.0,
            image=self.entry2_img)

        wins_box = Label(self, textvariable=self.wins,
                         bd=0,
                         bg="#698498",
                         highlightthickness=0)

        wins_box.place(
            x=251, y=222,
            width=535,
            height=30)

        self.entry3_img = PhotoImage(file=f"./Search/img_textBox3.png")
        entry3_bg = self.create_image(
            518.5, 176.0,
            image=self.entry3_img)

        dob_box = Label(self, textvariable=self.dob,
                        bd=0,
                        bg="#698498",
                        highlightthickness=0)

        dob_box.place(
            x=251, y=160,
            width=535,
            height=30)

        self.entry4_img = PhotoImage(file=f"./Search/img_textBox4.png")
        entry4_bg = self.create_image(
            518.5, 114.0,
            image=self.entry4_img)

        name_box = Label(self, textvariable=self.name,
                         bd=0,
                         bg="#698498",
                         highlightthickness=0)

        name_box.place(
            x=251, y=98,
            width=535,
            height=30)

        self.img1 = PhotoImage(file=f"./Search/img1.png")
        b1 = Button(self,
                    image=self.img1,
                    borderwidth=0,
                    highlightthickness=0,
                    command=self.search,
                    relief="flat")

        b1.place(
            x=734, y=24,
            width=52,
            height=44)

    def clear(self):
        self.search_box.delete(0, "end")
        self.note.set("")
        self.dob.set("")
        self.name.set("")
        self.wins.set("")

    def back(self):
        self.controller.showFrame(GamePage)

    def search(self):
        search = self.search_box.get()
        msg = ["SEARCH", search]  # lấy thông tin nhập gửi
        msg = json.dumps(msg)
        try:
            client_socket.sendall(bytes(msg, FORMAT))
        except:
            errorMsg("Sever is close !")
            self.controller.showFrame(ConnectionPage)
            return
        # nhận thông tin vừa tìm
        msg = client_socket.recv(BUFSIZE).decode(FORMAT)
        msg = json.loads(msg)
        name, dob, note, wins = msg
        self.name.set(name)
        self.dob.set(dob)
        self.note.set(note)
        self.wins.set(wins)
        if name == "":
            errorMsg("No player found !")


class OnlinePage(tk.Canvas):
    def __init__(self, parent, controller: ClientGUI):
        tk.Canvas.__init__(self, parent, bg="#ffffff", height=442,
                           width=867, bd=0, highlightthickness=0, relief="ridge")
        self.controller = controller
        self.geometry = "867x442"
        self.title = "Online List"
        self.list = []
        # ......
        self.background_img = PhotoImage(file=f"./OnlineList/background.png")
        background = self.create_image(
            433.5, 221.0,
            image=self.background_img)

        self.entry0_img = PhotoImage(file=f"./OnlineList/img_textBox0.png")
        entry0_bg = self.create_image(
            433.5, 34.0,
            image=self.entry0_img)

        self.find_box = Entry(
            self,
            bd=0,
            bg="#a5bdcf",
            highlightthickness=0)

        self.find_box.place(
            x=166, y=18,
            width=535,
            height=30)
        self.find_box.bind("<KeyRelease>", self.find)
        # entry1_img = PhotoImage(file = f"OnlineList/img_textBox1.png")
        # entry1_bg = canvas.create_image(
        #     433.0, 218.5,
        #     image = entry1_img)
        #           Tree view
        columns = ("username")
        self.tree = ttk.Treeview(self, columns=columns, show='tree')
        # headings
        self.tree.heading('username', text='User name')

        self.tree.place(
            x=87, y=74, width=692, height=287)

        self.tree.bind("<<TreeviewSelect>>", self.itemSelect)
        #           Scroll bar
        self.scrollbar = ttk.Scrollbar(
            self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=self.scrollbar.set)
        self.scrollbar.place(x=779, y=74, height=287)

        ######################
        self.img0 = PhotoImage(file=f"./OnlineList/img0.png")
        b0 = Button(
            self,
            image=self.img0,
            borderwidth=0,
            highlightthickness=0,
            command=self.back,
            relief="flat")

        b0.place(
            x=21, y=384,
            width=96,
            height=40)

        self.img1 = PhotoImage(file=f"./OnlineList/img1.png")
        b1 = Button(self,
                    image=self.img1,
                    borderwidth=0,
                    highlightthickness=0,
                    command=self.invite,
                    relief="flat")

        b1.place(
            x=719, y=384,
            width=131,
            height=40)

    def getOnlineList(self):
        msg = ["ONLINE", ""]
        msg = json.dumps(msg)
        client_socket.sendall(bytes(msg, FORMAT))
        msg = b''
        while True:
            recv = client_socket.recv(BUFSIZE)
            msg = msg+recv
            if len(recv) < BUFSIZE:  # len recv's <2048->break
                break
        # ko decode liền đc vì bị ngắt nếu rev's len>2048
        msg = msg.decode(FORMAT)
        try:
            msg = json.loads(msg)
        except:
            msg = msg[0:(len(msg)-1)]  # xóa kí tự '.'
            msg = json.loads(msg)
        list = []
        for i in msg:
            x = []
            x.append(i)
            x = tuple(x)
            list.append(x)
        return list

    def itemSelect(self, e=None):
        try:
            self.find_box.delete(0, "end")
            item = self.tree.item(self.tree.selection(), option="values")[0]
            self.find_box.insert(0, item)
        except:
            pass

    def find(self, e=None):
        key = self.find_box.get()
        newList = []
        if key == "":
            newList = self.list
        else:
            for i in self.list:
                if key.lower() in i[0].lower():
                    newList.append(i)
        for i in self.tree.get_children():
            self.tree.delete(i)
        for i in newList:
            self.tree.insert("", tk.END, values=i)

    def clear(self):
        self.find_box.delete(0, "end")
        self.list = self.getOnlineList()
        for i in self.tree.get_children():
            self.tree.delete(i)
        for i in self.list:
            self.tree.insert("", tk.END, values=i)

    def back(self):
        self.controller.showFrame(GamePage)

    def invite(self):
        opponent = self.find_box.get()
        msg = ["INVITE", opponent]
        msg = json.dumps(msg)
        client_socket.sendall(bytes(msg, FORMAT))
        self.controller.showFrame(WaitingPage)
        Thread(target=self.controller.replyMsg, args=(opponent,)).start()


class WaitingPage(tk.Canvas):
    def __init__(self, parent, controller: ClientGUI):
        tk.Canvas.__init__(self, parent, bg="#ffffff", height=442,
                           width=867, bd=0, highlightthickness=0, relief="ridge")
        self.controller = controller
        self.geometry = "867x442"
        self.title = "Waiting"

        self.background_img = PhotoImage(file=f"./Waiting/background.png")
        background = self.create_image(
            433.5, 221.0,
            image=self.background_img)

    def clear(self):
        pass

class GetFilePage(tk.Canvas):
    def __init__(self, parent, controller: ClientGUI):
        tk.Canvas.__init__(self, parent, bg="#ffffff", height=442,
                           width=867, bd=0, highlightthickness=0, relief="ridge")
        self.controller = controller
        self.geometry = "867x442"
        self.title = "Input Your Shipfile"

        self.background_img = PhotoImage(file=f"./MapName/background.png")
        background = self.create_image(
            433.5, 221.0,
            image=self.background_img)

        self.entry0_img = PhotoImage(file=f"./MapName/img_textBox0.png")
        entry0_bg = self.create_image(
            420.5, 192.5,
            image=self.entry0_img)

        self.file_box = Entry(self,
                              bd=0,
                              bg="#fff6ec",
                              highlightthickness=0)

        self.file_box.place(
            x=243, y=172,
            width=355,
            height=39)

        self.img0 = PhotoImage(file=f"./MapName/img0.png")
        b0 = Button(self,
                    image=self.img0,
                    borderwidth=0,
                    highlightthickness=0,
                    command=self.getFile,
                    relief="flat")

        b0.place(
            x=352, y=229,
            width=117,
            height=39)

    def clear(self):
        self.file_box.delete(0, "end")

    def getFile(self):
        filename = self.file_box.get()
        self.controller.showFrame(WaitingPage)
        Thread(target=self.controller.playGame,
               args=(filename,), daemon=True).start()

class LoginPage(Canvas):
    def __init__(self, parent, controller: ClientGUI):
        Canvas.__init__(self, parent, bg="#ffffff", height=437,
                        width=867, bd=0, highlightthickness=0, relief="ridge")
        self.geometry = "867x437"
        self.title = "Login Page"
        self.controller = controller

        self.background_img = PhotoImage(file=f"LOGINpage/background.png")
        background = self.create_image(
            433.5, 229.0,
            image=self.background_img)

        self.entry_img = PhotoImage(file=f"LOGINpage/img_textBox.png")
        entry0_bg = self.create_image(
            647.5, 316.0,
            image=self.entry_img)

        a = Frame
        self.password_box = Entry(
            master=self,
            bd=0,
            bg="#aa9a9a",
            highlightthickness=0,
            show="*")

        self.password_box.place(
            x=509, y=298,
            width=277,
            height=34)
        self.password_box.bind("<Return>", self.LogIn)

        entry1_bg = self.create_image(
            647.5, 237.0,
            image=self.entry_img)

        self.username_box = Entry(
            master=self,
            bd=0,
            bg="#aa9a9a",
            highlightthickness=0)

        self.username_box.place(
            x=509, y=219,
            width=277,
            height=34)
        self.username_box.bind("<Return>", self.LogIn)

        self.img0 = PhotoImage(file=f"LOGINpage/loginButton.png")
        b0 = Button(
            master=self,
            image=self.img0,
            borderwidth=0,
            highlightthickness=0,
            command=self.LogIn,
            relief="flat")

        b0.place(
            x=580, y=371,
            width=144,
            height=42)

        self.img1 = PhotoImage(file=f"LOGINpage/backButton.png")
        b1 = Button(
            master=self,
            image=self.img1,
            borderwidth=0,
            highlightthickness=0,
            command=self.Back,
            relief="flat")

        b1.place(
            x=30, y=371,
            width=144,
            height=42)

    def Back(self):
        self.controller.showFrame(StartPage)

    def LogIn(self, e=None):
        username = self.username_box.get()
        if username == "":
            errorMsg("Username can't be blank")
            return
        password = self.password_box.get()
        if password == "":
            errorMsg("Password can't be blank")
            return
        if askYesNo("Encrypt?", "Do you want to encrypt message before sending ?"):
            msg = ["LOGIN", Encrytor.Encrypt(
                username), Encrytor.Encrypt(password), True]
        else:
            msg = ["LOGIN", username, password, False]
        msg = json.dumps(msg)
        try:
            client_socket.sendall(bytes(msg, FORMAT))
        except:
            errorMsg("Sever is close !")
            self.controller.showFrame(ConnectionPage)
            return
        msg = client_socket.recv(BUFSIZE).decode(FORMAT)
        if msg == "accept":
            self.controller.online.set()
            self.controller.showFrame(GamePage)
        else:
            errorMsg(msg)

    def clear(self):
        self.username_box.delete(0, "end")
        self.password_box.delete(0, "end")

class ChangePasswordPage(tk.Canvas):

    def __init__(self, parent, controller:ClientGUI):
        tk.Canvas.__init__(self, parent, bg="#ffffff", height=442,
                           width=867, bd=0, highlightthickness=0, relief="ridge")
        self.controller = controller

        self.geometry = "867x442"
        self.title = "Change Password"

        self.background_img = tk.PhotoImage(file=f"ChangePass/background.png")
        background = self.create_image(
            433.5, 221.0,
            image=self.background_img)

        self.entry0_img = tk.PhotoImage(file=f"ChangePass/img_textBox0.png")
        entry0_bg = self.create_image(
            599.0, 221.5,
            image=self.entry0_img)

        self.newPassword_box = tk.Entry(self,
                                        show="*",
                                        bd=0,
                                        bg="#aa9a9a",
                                        highlightthickness=0)

        self.newPassword_box.place(
            x=418, y=209,
            width=362,
            height=23)

        self.entry1_img = tk.PhotoImage(file=f"ChangePass/img_textBox1.png")
        entry1_bg = self.create_image(
            599.0, 160.0,
            image=self.entry1_img)

        self.currentPassword_box = tk.Entry(self,
                                            show="*",
                                            bd=0,
                                            bg="#aa9a9a",
                                            highlightthickness=0)

        self.currentPassword_box.place(
            x=418, y=149,
            width=362,
            height=20)

        self.img0 = tk.PhotoImage(file=f"ChangePass/img0.png")
        b0 = tk.Button(self,
                       image=self.img0,
                       borderwidth=0,
                       highlightthickness=0,
                       command=self.back,
                       relief="flat")

        b0.place(
            x=9, y=392,
            width=148,
            height=40)

        self.img1 = tk.PhotoImage(file=f"ChangePass/img1.png")
        b1 = tk.Button(self,
                       image=self.img1,
                       borderwidth=0,
                       highlightthickness=0,
                       command=self.changePassword,
                       relief="flat")

        b1.place(
            x=490, y=252,
            width=148,
            height=40)

    def clear(self):
        self.currentPassword_box.delete(0, "end")
        self.newPassword_box.delete(0, "end")

    def back(self):
        self.controller.showFrame(GamePage)

    def changePassword(self):
        currentPassword = self.currentPassword_box.get()
        if currentPassword == "":
            errorMsg("Current Password can't be blank")
            return
        newPassword = self.newPassword_box.get()
        if newPassword == "":
            errorMsg("New Password can't be blank")
            return
        if askYesNo("Encrypt?", "Do you want to encrypt message before sending ?"):
            msg = ["CHANGEPASS", Encrytor.Encrypt(
                currentPassword), Encrytor.Encrypt(newPassword), True]
        else:
            msg = ["CHANGEPASS", currentPassword, newPassword, False]
        msg = json.dumps(msg)
        try:
            client_socket.sendall(bytes(msg, FORMAT))  # gửi
        except:
            errorMsg("Sever is close !")
            self.controller.showFrame(ConnectionPage)
            return
        msg = client_socket.recv(BUFSIZE).decode(FORMAT)  # nhận
        if msg == "OK":
            infMsg("Successful", "Change Password Completed")
            self.controller.showFrame(GamePage)
        else:
            errorMsg(msg)



def errorMsg(msg, title="Error"):
    mbox.showerror(title, msg)


def askYesNo(title, msg):
    return mbox.askyesno(title, msg)


def infMsg(title, msg):
    return mbox.showinfo(title, msg)


app=ClientGUI()
app.mainloop()