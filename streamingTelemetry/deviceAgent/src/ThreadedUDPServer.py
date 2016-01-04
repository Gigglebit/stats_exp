import socket
import threading
import SocketServer
import time

class ThreadedUDPRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        data = self.request[0].strip()
        ### get port number
        port = self.client_address[1]
        ### get the communicate socket
        socket = self.request[1]
        ### get client host ip address
        client_address = (self.client_address[0])
        ### proof of multithread
        cur_thread = threading.current_thread()
        print "thread %s" %cur_thread.name
        print "received call from client address :%s" %client_address
        print "received data from port [%s]: %s" %(port,data)
        
        ### assemble a response message to client
        response = "%s %s"%(cur_thread.name, data)
        socket.sendto(data.upper(), self.client_address)

class ThreadedUDPServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer):
    pass


if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "0.0.0.0", 9999

    server = ThreadedUDPServer((HOST, PORT), ThreadedUDPRequestHandler)
    ip, port = server.server_address
    server.serve_forever()
    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    print "Server loop running in thread:", server_thread.name

    server.shutdown()
