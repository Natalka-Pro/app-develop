import asyncio
from cowsay import cowsay, list_cows
import shlex

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

clients = {}        # {me : asyncio.Queue()}
register_cow = {}   # {name_of_cow : me}

async def chat(reader, writer):
    me = "{}:{}".format(*writer.get_extra_info('peername'))
    # print(f"@1")
    print(f"{me} connected")
    # очередь для каждого клиента
    clients[me] = asyncio.Queue()
    # почитать из входного потока
    # print(f"@2 {len(clients)}")
    send = asyncio.create_task(reader.readline()) 
    # посмотреть ненаписали ли нам сообщение, чтение из очереди
    receive = asyncio.create_task(clients[me].get())
    # print(f"@1 {me}")
    while not reader.at_eof():
        # либо получаем, либо отправляем, какая первая придёт
        # print(f"@2 {me}")
        done, pending = await asyncio.wait([send, receive], return_when=asyncio.FIRST_COMPLETED)
        # print(f"@3 {me}")

        for q in done:
            if q is send:
                # print(f"send {me}")
                send = asyncio.create_task(reader.readline())
                comm = shlex.split(q.result().decode())

                if len(comm) == 0:
                    await clients[me].put(">>> Enter the command please!")

                elif comm[0] == "who":
                    """who — просмотр зарегистрированных пользователей"""
                    if len(register_cow) == 0:
                        await clients[me].put(">>> There are no registered cows yet :(")
                    else:
                        out = list(map(str, register_cow.keys()))
                        await clients[me].put("Registered cows: \n" + ', '.join(out))

                elif comm[0] == "cows":
                    """cows — просмотр свободных имён коров"""
                    out = list_remove(list_cows(), register_cow.keys())
                    if len(out) == 0:
                        await clients[me].put(">>> There are no free cow names :(")
                    else:
                        await clients[me].put("Free cow names:\n" + ', '.join(out))
                
                elif comm[0] == "login":
                    """login название_коровы — зарегистрироваться под именем название_коровы"""
                    valid_names = set(list_cows()) - set(map(str, register_cow.keys()))
                    if me in register_cow.values():
                        await clients[me].put(">>> You are already registered!")
                    elif len(comm) == 1:
                        await clients[me].put(">>> Enter the cow's name please!")
                    elif comm[1] not in valid_names:
                        await clients[me].put(">>> This name is not suitable :(\n" +
                                ">>> Look at the list of free cow names using the command 'cows'")
                    else:
                        register_cow[comm[1]] = me
                        await clients[me].put(f">>> You have registered under the name '{comm[1]}'")

                elif comm[0] == "say":
                    """say название_коровы текст сообщения — послать сообщение пользователю название_коровы"""
                    valid_names = set(map(str, register_cow.keys()))
                    if me not in register_cow.values():
                        await clients[me].put(">>> You are not registered :(")
                    elif len(comm) == 1:
                        await clients[me].put(">>> Enter cow's name to send the message please!")
                    elif comm[1] not in valid_names:
                        await clients[me].put(f">>> The cow  '{comm[1]}' is not registered :(")
                    elif len(comm) == 2:
                        await clients[me].put(">>> Enter the text of the message please!")
                    else:
                        cow = get_key(register_cow, me)
                        message = cowsay(comm[2], cow = cow)
                        await clients[register_cow[comm[1]]].put(f"Cow '{cow}' tells you:\n{message}")

                elif comm[0] == "yield":
                    """yield текст сообщения — послать сообщение всем зарегистрированным пользователям """
                    names = set(register_cow.values()) - {me}
                    if me not in register_cow.values():
                        await clients[me].put(">>> You are not registered :(")
                    elif len(comm) == 1:
                        await clients[me].put(">>> Enter the text of the message please!")
                    else:
                        cow = get_key(register_cow, me)
                        message = cowsay(comm[1], cow = cow)
                        for id in names:
                            await clients[id].put(f"Cow '{cow}' says:\n{message}")

                elif comm[0] == "quit":
                    """quit — отключиться"""
                    if me not in register_cow.values():
                        await clients[me].put(">>> You have not been registered :(")
                    else:
                        cow = get_key(register_cow, me)
                        del register_cow[cow]
                        await clients[me].put(f">>> Cow {cow} deleted")

                else:
                    await clients[me].put(">>> This command is not supported :(")

            elif q is receive:
                receive = asyncio.create_task(clients[me].get())
                writer.write(f"{q.result()}\n".encode())
                await writer.drain()
    send.cancel()
    receive.cancel()
    print(get_key(register_cow, me, me), "disconnected")
    del clients[me]
    writer.close()
    await writer.wait_closed()

async def main():
    addr = 1335
    server = await asyncio.start_server(chat, '0.0.0.0', addr)
    async with server:
        await server.serve_forever()

asyncio.run(main())

# netcat localhost 1335