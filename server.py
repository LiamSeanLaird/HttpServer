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

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    # SimpleNamespace is a simple object that makes it easy to del or assign attributes easily without having to first define  a class.
    # Printing SimpleNamespace objects will show the attributes and their values.
    # basically a wrapper over a dict that allows you to access the keys as attributes
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

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((HOST, PORT))
lsock.listen()
print(f"Listening on {(HOST, PORT)}")
lsock.setblocking(False) # Non-blocking mode. Return immediately. Need a way of handling operations that would block
sel.register(lsock, selectors.EVENT_READ, data=None) # Uses selectors to monitor the listening socket

try:
    while True: # Event loop
        events = sel.select(timeout=None)
        i=0
        for key, mask in events:
            print(f"Event {i}")
            i+=1
            print("key:", key)
            print("mask:", mask)
            if key.data is None:
                # We know it is the listening socket and we should accept() on it
                accept_wrapper(key.fileobj)
            else:
                # Client sokcet alreadsy accepted, we should service the connection
                service_connection(key, mask)
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()