from socket import *
import os
import asyncio
import errno
from pydantic import BaseModel
from devtools import pprint

class ConnectionEntry(BaseModel):
    client_src: tuple[str, int] 
    client_dst: tuple[str, int]
    srv_src: tuple[str, int]
    srv_dst: tuple[str,int]
    # Starts with 2 and is decremented everytime 1 socket stops sending data to another => 
    # when we reach 0, we'll remove the entry from active connections
    flows: int = 2
    def __eq__(self, other):
        if not isinstance(other, ConnectionEntry):
            return False
        return self.client_src == other.client_src and self.client_dst == other.client_dst and self.srv_src == other.srv_src and self.srv_dst == other.srv_dst

BUF_SIZE = 512
web_server_hostnames = os.environ.get("WEB_SERVER_HOSTNAMES").split()
server_pointer = 0
active_connections: ConnectionEntry = []

print('----- ENV ------')
print(web_server_hostnames)
print('----- ENV ------')

if len(web_server_hostnames) < 2:
    print("Web server number is too low. Aborting...")
    exit(1)

def decrement_flow(ce: ConnectionEntry):

        print(f'Dropped a connection: {ce}')

def remove_active_conn(ce: ConnectionEntry):
    # Might already be removed from the other send_traffic_from_to call
    if ce in active_connections:
        print(f'Dropping connection: {ce}')
        active_connections.remove(ce)

async def send_traffic_from_to(src, dst, ce: ConnectionEntry):
    global active_connections
    if ce not in active_connections:
        try:
            src.close()
        except:
            pass
        try:
            dst.close()
        except:
            pass
        return
    loop = asyncio.get_event_loop()
    while True:
        try:
            traffic = await loop.sock_recv(src, BUF_SIZE)
            if not traffic:
                # Connection terminated with FIN
                remove_active_conn(ce)
                return
            await loop.sock_sendall(dst, traffic)
        except (ConnectionResetError, BrokenPipeError):
            # RST Flag received
            remove_active_conn(ce)
            return

async def balance_traffic(s_from_client, s_to_server, ce: ConnectionEntry):
    # print('Balancing for')
    # print(s_from_client)
    # print(s_to_server)
    await asyncio.gather(
        send_traffic_from_to(s_from_client, s_to_server, ce),
        send_traffic_from_to(s_to_server  , s_from_client, ce)
    )

def assign_server_to_client() -> tuple[str, int]:
    global server_pointer
    assigned_server = web_server_hostnames[server_pointer]
    server_pointer = (server_pointer + 1 ) % len(web_server_hostnames)
    return (assigned_server, 80)

async def wait_for_connections():
    s = socket(AF_INET, SOCK_STREAM)
    HOST = gethostbyname(gethostname())
    # https://docs.python.org/3/library/socket.html#timeouts-and-the-connect-method
    print(f"Host is: {HOST}")
    s.bind((HOST, 8000))
    s.listen(20)
    s.setblocking(False)
    loop = asyncio.get_event_loop()

    while True:
        conn, _ = await loop.sock_accept(s)
        assigned_server_socket: tuple[str, int] = assign_server_to_client()
        local_s: tuple[str, int] = conn.getsockname()
        remote_s: tuple[str, int] = conn.getpeername()
        print(f'Assigned {remote_s} to {assigned_server_socket}!')
        s_to_server = socket(AF_INET, SOCK_STREAM)
        s_to_server.setblocking(False)
        await loop.sock_connect(s_to_server, assigned_server_socket)
        ce = ConnectionEntry(
                client_src=remote_s,
                client_dst=local_s,
                srv_src=s_to_server.getsockname(),
                srv_dst=assigned_server_socket
        )
        active_connections.append(ce)
        loop.create_task(balance_traffic(conn, s_to_server, ce))

async def print_active_connections():
    while True:
        print(f"\n---- Active Connections ({len(active_connections)})----")
        for conn in active_connections:
            print(conn)
        print('----------------------------------------------------------')
        await asyncio.sleep(5)

async def main():
    await asyncio.gather(
        wait_for_connections(),
        print_active_connections()
    )

asyncio.run(main())
