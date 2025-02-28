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
    conn, addr = sock.accept()
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(
        connid=None,  # Initially no connection ID
        addr=addr,
        inb=b"", # Incoming data buffer
        outb=b"", # Outgoing data buffer
        recv_total=0,
        msg_total=0,
        messages=[]
    )
    # SimpleNamespace is a simple object that makes it easy to del or assign attributes easily without having to first define  a class.
    # Printing SimpleNamespace objects will show the attributes and their values.
    # basically a wrapper over a dict that allows you to access the keys as attributes
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def service_connection(key, mask):
    """
    Assumed a well-behaved client (That wil close its connection)
    """
    sock = key.fileobj # Socket object
    data = key.data # SimpleNamespace object
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            # data.outb += recv_data
            print(f"Received {recv_data!r} from connection {data.connid}")
            data.recv_total += len(recv_data)
        if not recv_data or data.recv_total == data.msg_total:
            print(f"Closing connection {data.connid}")
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        print(f"data.messages: {data.messages}")
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        if data.outb:
            print(f"Sending {data.outb!r} to connection {data.connid}")
            sent = sock.send(data.outb)  # Returns number of bytes sent
            data.outb = data.outb[sent:] # Removes the sent data from the buffer

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
            if key.data is None:
                # We know it is the listening socket and we should accept() on it
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()