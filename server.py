import socket
from _thread import *
import sys

server = socket.gethostbyname(socket.gethostname())
port = 5050

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(2)
print("Waiting for a connection, Server Started")
 
def threaded_client(conn):
    conn.send(str.encode("Connected"))
    reply = ""
    while True:
        try:
            data = conn.recv(2048)

            if not data:
                print("Disconnected")
                break

            reply = data.decode("utf-8")

            print("Received:", reply)
            print("Sending:", reply)

            conn.sendall(data)

        except Exception as e:
            print("Error:", e)
            break
    print("Lost connection")
    conn.close()


while True:
    conn, addr = s.accept()
    print("Connected by", addr)

    start_new_thread(threaded_client, (conn, ))
