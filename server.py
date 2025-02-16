import sys
import socket
import selectors
import types

sel = selectors.DefaultSelector()

HOST = 'localhost'
PORT = 65535


## ECHO SERVER
# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:    # SOCK_STREAM -> TCP
#     s.bind((HOST, PORT))
#     s.listen() # makes the server a listening socket
#     conn, addr = s.accept() #conn is a NEW socket object that represent the connection
#     with conn:
#         print('Connected by', addr) #address of the client
#         while True:
#             # Infinite loop over blocking calls to conn.recv()
#             data = conn.recv(1024)
#             if not data: break
#             conn.sendall(data) # Continues sending data using send() until all data is sent

## MULTI CONN SERVER USING SELECTORS
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((HOST, PORT))
lsock.listen()
print(f"Listening on {(HOST, PORT)}")
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            data.outb += recv_data
        else:
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print(f"Echoing {data.outb!r} to {data.addr}")
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]

try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()