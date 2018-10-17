# server.py
import sys
import os
import socket
import time
import traceback
import tweepy
from threading import Thread
from PyQt5 import QtCore, QtGui, QtWidgets, uic

# Global Variables
worker_IPs = []
host_IPs = []
current_worker = ''
current_host = ''
number_of_connections = 0
number_of_workers = 0
number_of_hosts = 0
command = 'no'
address = ''
clusterArray = []
clusterReady = False
cluster_numWorkers = ''
cluster_batch_size = ''
cluster_learning_rate = ''
cluster_epochs = ''

default_port = "2223"
default_ps_port = "2222"

def client_thread(conn, ip, port, MAX_BUFFER_SIZE = 4096):
    global command, address, tweet, worker_IPs, host_IPs, number_of_connections, clusterArray, clusterReady
    global cluster_numWorkers, cluster_batch_size, cluster_learning_rate, cluster_epochs
    # size check
    input_from_client_bytes = conn.recv(MAX_BUFFER_SIZE)
    siz = sys.getsizeof(input_from_client_bytes)
    if siz >= MAX_BUFFER_SIZE:
        print("The length of input is probably too long: {}".format(siz))

    # decode input
    input_from_client = input_from_client_bytes.decode("utf8").rstrip()
    print("Job Type:{} received from ip: {}".format(input_from_client, ip))
    job_type, numWorkers, batch_size, learning_rate, training_epochs = input_from_client.split(' ', 4)
    print("Job Type: ", job_type)
    print("Workers Required: ", numWorkers)
    print("Batch Size: ", batch_size)
    print("Learning Rate: ", learning_rate)
    print("Epochs: ", training_epochs)

    if (job_type == 'worker'):
        worker_IPs.append(ip)
        print("Worker {} has the IP: {}".format(number_of_workers, worker_IPs[number_of_workers]))
        print("Current worker_ips: ", worker_IPs)
        print(len(worker_IPs))

        taskPos = -1
        #wait until worker is part of active cluster
        while taskPos < 0:
            if clusterReady == True:
                taskPos = checkClusterIP(ip)
                time.sleep(5)
        print("ACTIVE STATE NUMBER:", taskPos)

        print("IAMACTIVE: ", job_type)
        # reply
        res = 'no'
        stringOfAddress = ' '.join(clusterArray)
        stringOfParams = cluster_numWorkers + ' ' + cluster_batch_size + ' ' + cluster_learning_rate + ' ' + cluster_epochs + ' ' + str(taskPos)
        res = stringOfParams + ' ' + stringOfAddress
        print(res)
        print("WAIT")
        resCheck = res.encode("utf8")  # encode the result string
        print("Sent back: " + res)
        conn.sendall(resCheck)  # send it to client

        worker_IPs.remove(ip)
        conn.close()  # close connection
        print('Connection ' + ip + ':' + port + " ended")

    elif (job_type == 'host'):
        host_IPs.append(ip)
        print("Host {} has the IP: {}".format(number_of_hosts, host_IPs[number_of_hosts]))
        while ip != host_IPs[0]:
            #wait until host is at front of queue
            time.sleep(5)
        cluster_numWorkers = numWorkers
        cluster_batch_size = batch_size
        cluster_learning_rate = learning_rate
        cluster_epochs = training_epochs
        matchmaking(int(numWorkers))

        print("IAMACTIVE: ", job_type)
        # reply
        res = 'no'
        taskPos = 0
        stringOfAddress = ' '.join(clusterArray)
        stringOfParams = cluster_numWorkers + ' ' + cluster_batch_size + ' ' + cluster_learning_rate + ' ' + cluster_epochs + ' ' + str(taskPos)
        res = stringOfParams + ' ' + stringOfAddress
        print(res)
        print("WAIT")
        resCheck = res.encode("utf8")  # encode the result string
        print("Sent back: " + res)
        conn.sendall(resCheck)  # send it to client

        host_IPs.remove(ip)
        conn.close()  # close connection
        print('Connection ' + ip + ':' + port + " ended")


def start_server():
    # Global Variables
    global number_of_connections, worker_IPs, host_IPs, command

    # declare socket
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # this is for easy starting/killing the app
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print('Socket created')

    try:
        soc.bind(("127.0.0.1", 12345))
        print('Socket bind complete')
    except socket.error as msg:
        print('Bind failed. Error : ' + str(sys.exc_info()))
        sys.exit()

    #Start listening on socket
    soc.listen(100)
    print('Socket now listening')

    # infinite loop for server
    while True:

        conn, addr = soc.accept()
        ip, port = str(addr[0]), str(addr[1])
        print('Accepting connection...')
        #worker_IPs.append(ip + ':' + port)
        #print("Connection {} has the IP: {}".format(number_of_connections, worker_IPs[number_of_connections]))
        number_of_connections = number_of_connections + 1
        try:
            Thread(target=client_thread, args=(conn, ip, port)).start()
        except:
            print("error!")
            traceback.print_exc()
    soc.close()

def matchmaking(numWorkers):
    global clusterArray, clusterReady
    clusterArray = []
    counter = 0
    clusterArray.append(host_IPs[0]) #ps
    clusterArray.append(host_IPs[0]) #chief
    while counter < numWorkers:
        if(len(worker_IPs) >= numWorkers):
            clusterArray.append(worker_IPs[counter]) #workers
            print("ADDED: ", worker_IPs[counter])
            print("Current cluster: ", clusterArray)
            counter += 1
        else:
            time.sleep(3)
            print("Not enough workers - waiting for more")
            print("Current cluster: ", clusterArray)

    print("THIS IS THE CLUSTER: ", clusterArray)
    clusterReady = True

def checkClusterIP(ip):
    global clusterArray
    for x in range(2, len(clusterArray)):
        if(ip==clusterArray[x]):
            return x

    return -1


if __name__ == "__main__":
    try:
        Thread(target=start_server).start()
    except:
        print("error starting server!")
        traceback.print_exc()

    # while(True):
    #     print("List of Workers: ", worker_IPs)
    #     print("List of Hosts: ", host_IPs)
    #     time.sleep(3)


