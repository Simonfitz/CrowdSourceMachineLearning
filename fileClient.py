#fileGet

import socket
import csv
import config

def callFilleClient():
    TCP_IP = 'localhost'
    TCP_PORT = 9001
    BUFFER_SIZE = 1024

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
