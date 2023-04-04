import asyncio
from cowsay import cowsay, list_cows
import shlex
import time
import sys


def safe_get(l, idx, default = None):
    try:
        return l[idx]
    except IndexError:
        return default

def get_key(d, value, default=None):
    return [k for k in d.keys() if d[k] == value][0] if value in d.values() else default

def list_remove(l, del_list):
    for i in del_list:
        l.remove(i)
    return l

def now():
    return f"({time.ctime(time.time())})"

clients = {}        # {me : asyncio.Queue()}
register_cow = {}   # {name_of_cow : me}
prompt = ">>cow_server>> "

async def chat(reader, writer):
    me = "{}:{}".format(*writer.get_extra_info('peername'))
    print(f"{now()}    {me} connected")
    clients[me] = asyncio.Queue()
    send = asyncio.create_task(reader.readline()) 
    receive = asyncio.create_task(clients[me].get())
    while not reader.at_eof():
        done, pending = await asyncio.wait([send, receive], return_when=asyncio.FIRST_COMPLETED)
        
        for q in done:
            if q is send:
                send = asyncio.create_task(reader.readline())
                comm = q.result().decode()
                print(f"{now()}    {get_key(register_cow, me, me)} "
                                            + f"sent a request '{comm.strip()}'")

                comm = shlex.split(comm)
                if len(comm) == 0:
                    await clients[me].put(f"{prompt}Enter the command please!")

                elif comm[0] == "who":
                    """who — view registered users"""
                    if len(register_cow) == 0:
                        await clients[me].put(f"{prompt}There are no registered cows yet :(")
                    else:
                        out = list(map(str, register_cow.keys()))
                        await clients[me].put(f"{prompt}Registered cows: \n" + ', '.join(out))

                elif comm[0] == "cows":
                    """cows — view free cow names"""
                    out = list_remove(list_cows(), register_cow.keys())
                    if len(out) == 0:
                        await clients[me].put(f"{prompt}There are no free cow names :(")
                    else:
                        await clients[me].put(f"{prompt}Free cow names:\n" + ', '.join(out))
                
                elif comm[0] == "login":
                    """
                    Register under the name 'cow_name'
                    login cow_name
                    """
                    valid_names = set(list_cows()) - set(map(str, register_cow.keys()))
                    if me in register_cow.values():
                        await clients[me].put(f"{prompt}You are already registered!")
                    elif len(comm) == 1:
                        await clients[me].put(f"{prompt}Enter the cow's name please!")
                    elif comm[1] not in valid_names:
                        await clients[me].put(
                                f"{prompt}Name '{comm[1]}' is not suitable :(\n"
                              + f"{prompt}Look at the list of free cow names using the command 'cows'")
                    else:
                        register_cow[comm[1]] = me
                        await clients[me].put(f"{prompt}You have registered under the name '{comm[1]}'")

                elif comm[0] == "say":
                    """
                    Send a message to the user 'cow_name'
                    say cow_name message
                    """
                    valid_names = set(map(str, register_cow.keys()))
                    if me not in register_cow.values():
                        await clients[me].put(f"{prompt}You are not registered :(")
                    elif len(comm) == 1:
                        await clients[me].put(f"{prompt}Enter cow's name to send the message please!")
                    elif comm[1] not in valid_names:
                        await clients[me].put(f"{prompt}The cow  '{comm[1]}' is not registered :(")
                    elif len(comm) == 2:
                        await clients[me].put(f"{prompt}Enter the text of the message please!")
                    else:
                        cow = get_key(register_cow, me)
                        message = cowsay(comm[2], cow = cow)
                        await clients[register_cow[comm[1]]].put(
                                        f"{prompt}Cow '{cow}' tells you:\n{message}")

                elif comm[0] == "yield":
                    """
                    Send a message to all registered users
                    yield message
                    """
                    names = set(register_cow.values()) - {me}
                    if me not in register_cow.values():
                        await clients[me].put(f"{prompt}You are not registered :(")
                    elif len(comm) == 1:
                        await clients[me].put(f"{prompt}Enter the text of the message please!")
                    else:
                        cow = get_key(register_cow, me)
                        message = cowsay(comm[1], cow = cow)
                        for id in names:
                            await clients[id].put(f"{prompt}Cow '{cow}' says:\n{message}")

                elif comm[0] == "quit":
                    """quit — disconnect"""
                    if me not in register_cow.values():
                        await clients[me].put(f"{prompt}You have not been registered :(")
                    else:
                        cow = get_key(register_cow, me)
                        del register_cow[cow]
                        await clients[me].put(f"{prompt}Cow {cow} deleted")

                else:
                    await clients[me].put(f"{prompt}This command is not supported :(")

            elif q is receive:
                receive = asyncio.create_task(clients[me].get())
                writer.write(f"{q.result()}".encode()) #writer.write(f"{q.result()}\n".encode())
                await writer.drain()
    send.cancel()
    receive.cancel()

    print(f"{now()}    {get_key(register_cow, me, me)} disconnected")
    del clients[me]
    if me in register_cow.values():
        del register_cow[get_key(register_cow, me)]

    writer.close()
    await writer.wait_closed()

async def main():
    HOST = 1333
    if len(sys.argv) > 1:
        try:
            HOST = int(sys.argv[1])
        except ValueError:
            print("Error: Enter the correct port number!")
            sys.exit()

    server = await asyncio.start_server(chat, '0.0.0.0', HOST)
    print(f"Server 0.0.0.0:{HOST} started!")
    async with server:
        await server.serve_forever()

asyncio.run(main())

# netcat localhost 1335