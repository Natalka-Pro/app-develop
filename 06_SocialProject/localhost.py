import cmd
import threading
import readline
import socket
import shlex
import sys


class cow_cmd(cmd.Cmd):
    def __init__(self):
        """
        self.WAIT_ANSWER - constant, indicating that an answer is expected from the server
        self.wait - equal to either False (initialization), 
                          or self.WAIT_ANSWER,
                          or contains the server answer
        """
        super().__init__()
        self.intro = "Hey, it's cowshell!"
        self.prompt = ">>>> "
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.HOST = 1333
        if len(sys.argv) > 1:
            try:
                self.HOST = int(sys.argv[1])
            except ValueError:
                print("Error: Enter the correct port number!")
                sys.exit()

        self.sock.connect(('localhost', self.HOST))
        print(f"Connected to 0.0.0.0:{self.HOST} server!")

        self.WAIT_ANSWER = 404
        self.wait = False


    def do_who(self, arg):
        message = f"who {arg}\n"
        arg = shlex.split(arg)

        if len(arg) != 0:
            print("Error: Arguments aren't needed for the function 'who'!")
            return
        
        self.sock.send(message.encode())


    def do_cows(self, arg):
        message = f"cows {arg}\n"
        arg = shlex.split(arg)

        if len(arg) != 0:
            print("Error: Arguments aren't needed for the function 'cows'!")
            return

        self.sock.send(message.encode())


    def do_login(self, arg):
        message = f"login {arg}\n"
        self.sock.send(message.encode())


    def complete_login(self, pfx, line, beg, end):
        """ 
        pfx - the last word entered, if there is no space after it, otherwise - ""
        line - the whole row, including "login"
        """
        # dragon-and-cow - pfx неправильно определяется :(
        self.sock.send("cows\n".encode())

        self.wait = self.WAIT_ANSWER
        while self.wait == self.WAIT_ANSWER:
            pass

        compl = self.wait.split("\n")
        compl = compl[1].replace(",", " ").split()
        return [s for s in compl if s.startswith(pfx)]


    def do_say(self, arg):
        message = f"say {arg}\n"
        self.sock.send(message.encode())


    def complete_say(self, pfx, line, beg, end):
        """ 
        pfx - the last word entered, if there is no space after it, otherwise - ""
        line - the whole row, including "login"
        """
        self.sock.send("who\n".encode())

        self.wait = self.WAIT_ANSWER
        while self.wait == self.WAIT_ANSWER:
            pass

        compl = self.wait.split("\n")
        compl = compl[1].replace(",", " ").split()
        return [s for s in compl if s.startswith(pfx)]


    def do_yield(self, arg):
        message = f"yield {arg}\n"
        self.sock.send(message.encode())


    def do_quit(self, arg):
        message = f"quit {arg}\n"
        self.sock.send(message.encode())


    def receiver(self):
        while True:
            ans = self.sock.recv(1024).decode()
            
            if self.wait == self.WAIT_ANSWER:
                self.wait = ans
            else:
                print(f"\n{ans}", flush=True)
                print(f"{self.prompt}{readline.get_line_buffer()}", flush=True, end="")      

            # ans = shlex.split(ans)
            # self.prompt = ">>>> "
            # print("     !")      


commandline = cow_cmd()
task = threading.Thread(target=commandline.receiver, args=())
task.start()
commandline.cmdloop()
