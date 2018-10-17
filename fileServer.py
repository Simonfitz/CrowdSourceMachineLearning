# fileHost

import socket
from threading import Thread
from socketserver import ThreadingMixIn
import csv
import config

TCP_IP = 'localhost'
TCP_PORT = 9001
BUFFER_SIZE = 1024
numConnections = 0

class ClientThread(Thread):

    def __init__(self,ip,port,sock):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.sock = sock
        print (" New thread started for "+ip+":"+str(port))

    def run(self):
        filename=config.file_inputs_loc
        f = open(filename,'rb')
        while True:
            l = f.read(BUFFER_SIZE)
            while (l):
                self.sock.send(l)
                #print('Sent ',repr(l))
                l = f.read(BUFFER_SIZE)
            if not l:
                f.close()
                self.sock.close()
                break

def callFileServer(numWorkers):
    global numConnections
    tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcpsock.bind((TCP_IP, TCP_PORT))
    threads = []
    numConnections = numWorkers

    while numConnections!=0:
        tcpsock.listen(5)
        print ("Waiting for incoming connections...")
        (conn, (ip,port)) = tcpsock.accept()
        print ('Got connection from ', (ip,port))
        newthread = ClientThread(ip,port,conn)
        newthread.start()
        threads.append(newthread)
        numConnections = numConnections - 1

    for t in threads:
        t.join()

def callFilleClient():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    with open('test_data.csv', 'wb') as csvfile:
        print ('file opened')
        while True:
            data = s.recv(BUFFER_SIZE)
            print('data=%s', (data))
            if not data:
                csvfile.close()
                print ('file close()')
                break
            # write data to a file
            csvfile.write(data)
    s.close()