from cowsay import cowsay, cowthink, list_cows, make_bubble, THOUGHT_OPTIONS
import cmd, shlex

def input_cycle():
    while not (s := input("Введи: ").strip()):
        pass
    return s


def safe_list_get (l, idx, default = None):
    try:
        return l[idx]
    except IndexError:
        return default


class cmdline(cmd.Cmd):
    intro = "Hey, it's cowshell!"
    prompt = "moo> "

    def body_cowsay_cowthink(self, arg, type):
        """type - cowsay or cowthink"""
        arg = shlex.split(arg)

        if len(arg) == 0:
            print(f"Error: What will the cow {type[3:]}?!")
            return

        message, *cow_param = arg
        cow = "default"
        eyes = "oo"
        tongue = "  "
        
        while len(cow_param) != 0:
            if cow_param[0] == "cow":
                cow = safe_list_get(cow_param, 1)
            elif cow_param[0] == "eyes":
                eyes = safe_list_get(cow_param, 1)
            elif cow_param[0] == "tongue":
                tongue = safe_list_get(cow_param, 1)
            else:
                print(f"""Error: Parameter "{cow_param[0]}" is not supported!""")
                return
            
            if None in {cow, eyes, tongue}:
                print(f"Error: What type of {cow_param[0]}?!")
                return
            else:
                cow_param = cow_param[2:]

        eyes = eyes[:2]
        tongue = tongue[:2]
        if type == "cowsay":
            print(cowsay(message, cow=cow, eyes=eyes, tongue=tongue))
        elif type == "cowthink":
            print(cowthink(message, cow=cow, eyes=eyes, tongue=tongue))


    def do_cowsay(self, arg):
        """
        What will the cow say
        cowsay message [cow COW_STRING] [eyes EYE_STRING] [tongue TONGUE_STRING]
        """
        self.body_cowsay_cowthink(arg, "cowsay")
        

    def do_cowthink(self, arg):
        """
        What will the cow think
        cowthink message [cow COW_STRING] [eyes EYE_STRING] [tongue TONGUE_STRING]
        """
        self.body_cowsay_cowthink(arg, "cowthink")
    
    
    def body_complete_cowsay_cowthink(self, pfx, line, beg, end):
        """ 
        pfx - the last word entered, if there is no space after it, otherwise - ""
        line - the whole row, including cowsay/cowthink
        """
        compl = list_cows() # подсказка
        compl_eyes =   ['==', 'XX', '$$', '@@', '**', '--', 'OO', '..']
        compl_tongue = ['U ', 'O ', 'Y ', 'UU', 'W ', 'V ', '--', '..']
        compl_flag = ["cow", "eyes", "tongue"]
        line = shlex.split(line)
        line = line[2:] # убрали cowsay/cowthink и message

        if ((safe_list_get(line, -1) == "cow" and pfx == "") or 
            (safe_list_get(line, -2) == "cow" and pfx != "")):
            # либо ввели пробел и не написали *тип коровы*
            # либо ввели часть *типа коровы* и не нажали пробел
            return [s for s in compl if s.startswith(pfx)]
        
        elif ((safe_list_get(line, -1) == "eyes" and pfx == "") or 
              (safe_list_get(line, -2) == "eyes" and pfx != "")): 
            return [s for s in compl_eyes if s.startswith(pfx)]
        
        elif ((safe_list_get(line, -1) == "tongue" and pfx == "") or 
              (safe_list_get(line, -2) == "tongue" and pfx != "")): 
            return [s for s in compl_tongue if s.startswith(pfx)]
        
        else: # подсказки флагов cow, eyes, tongue
            return [s for s in compl_flag if s.startswith(pfx)]


    def complete_cowsay(self, pfx, line, beg, end):
        return self.body_complete_cowsay_cowthink(pfx, line, beg, end)


    def complete_cowthink(self, pfx, line, beg, end):
        return self.body_complete_cowsay_cowthink(pfx, line, beg, end)


    def do_list_cows(self, arg):
        """List of all cowfiles"""
        print(list_cows())


    def do_make_bubble(self, arg):
        """
        This is the text that appears above the cows
        make_bubble message [cowsay/cowthink]
        """
        arg = shlex.split(arg)

        if len(arg) == 0:
            print("Error: What is written in the bubble?!")
            return
        
        message, *action = arg

        if len(action) == 0:
            action = "cowsay"
        else:
            action = action[0]

        if action not in {"cowsay", "cowthink"}:
            print(f"Error: The action can be cowsay or cowthink, not {action}!")
            return

        print(make_bubble(message, brackets = THOUGHT_OPTIONS[action]))


    def complete_make_bubble(self, pfx, line, beg, end):
        """ 
        pfx - the last word entered, if there is no space after it, otherwise - ""
        line - the whole row, including "make_bubble"
        """
        compl = "cowsay", "cowthink"
        line = shlex.split(line)
        print(f"\n{pfx=}, {line=}, {beg=}, {end=}\n")
        if (len(line) == 2 and pfx == "") or (len(line) == 3 and pfx != ""):
            # либо ввели пробел и не написали cowsay или cowthink
            # либо ввели часть cowsay или cowthink и не нажали пробел
            return [s for s in compl if s.startswith(pfx)]


if __name__ == "__main__":
    commandline = cmdline()
    commandline.cmdloop()