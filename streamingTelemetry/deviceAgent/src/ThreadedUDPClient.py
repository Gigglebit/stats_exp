import socket
import threading
import SocketServer

def client(ip, port, message):

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print 'The client is sending message: '+ str(message) 
    print sock.getsockname()
    try:
        sock.sendto(str(message) + "\n", (ip, port))
    finally:
        sock.close()

if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    ip, port = "127.0.0.1", 9999

    threads = []
    for i in range(5):
        t = threading.Thread(target=client, args=(ip, port, 'Hello World ' + str(i),))
        t.daemon = True
        threads.append(t)
        t.start()
    
