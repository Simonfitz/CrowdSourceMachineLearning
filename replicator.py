import time
import sys
import os
import socket
import time
import traceback
import socket
import csv
import config
import math
from sys import argv
from os.path import exists
mapArray = []

#find next node jump
def nextNode(step, currNode):
    next = int(2 ** (step-1))
    return math.ceil(next + currNode)

#get max steps of replication
def maxSteps(n):
    max = math.log(n, 2)
    return math.ceil(max)

def fileCheck(filename):
    target = open(filename)
    print("file exists: ",  exists(filename))
    return True


#test replicator
def pseudoReplicate():
    n = 20
    nodes = []
    step = 0
    hasfile = 1

    # create array of nodes
    for x in range(0, n + 1):
        nodes.append(0)

    nodes[0] = 1
    maxStep = maxSteps(n)
    print("MAX STEPS", maxStep)
    #time.sleep(6)

    while(step <= maxStep):

        nextnode = int(2 ** (step - 1))
        print("NEXT= ",nextnode)
        print("STEP: ", step)

        if (nodes[0] == hasfile):
            try:
                nodes[nextnode + 0] = 1
                print("Node 0 has trasnferred to Node ", nextnode)
            except IndexError:
                print("ERROR")
                print("FAILED TO TRANSFER FILE FROM NODE 0 TO NODE ", nextnode + 0)

        if (nodes[1] == hasfile):
            try:
                nodes[nextnode + 1] = 1
                print("Node 1 has trasnferred to Node ", nextnode + 1)
            except IndexError:
                print("ERROR")
                print("FAILED TO TRANSFER FILE FROM NODE 1 TO NODE ", nextnode + 1)

        if (nodes[2] == hasfile):
            try:
                nodes[nextnode + 2] = 1
                print("Node 2 has trasnferred to Node ", nextnode + 2)
            except IndexError:
                print("ERROR")
                print("FAILED TO TRANSFER FILE FROM NODE 2 TO NODE ", nextnode + 2)

        if (nodes[3] == hasfile):
            try:
                nodes[nextnode + 3] = 1
                print("Node 3 has trasnferred to Node ", nextnode + 3)
            except IndexError:
                print("ERROR")
                print("FAILED TO TRANSFER FILE FROM NODE 3 TO NODE ", nextnode + 3)

        if (nodes[4] == hasfile):
            try:
                nodes[nextnode + 4] = 1
                print("Node 4 has trasnferred to Node ", nextnode + 4)
            except IndexError:
                print("ERROR")
                print("FAILED TO TRANSFER FILE FROM NODE 4 TO NODE ", nextnode + 4)

        if (nodes[5] == hasfile):
            try:
                nodes[nextnode + 5] = 1
                print("Node 5 has trasnferred to Node ", nextnode + 5)
            except IndexError:
                print("ERROR")
                print("FAILED TO TRANSFER FILE FROM NODE 5 TO NODE ", nextnode + 5)

        if (nodes[6] == hasfile):
            try:
                nodes[nextnode + 6] = 1
                print("Node 5 has trasnferred to Node ", nextnode + 6)
            except IndexError:
                print("ERROR")
                print("FAILED TO TRANSFER FILE FROM NODE 6 TO NODE ", nextnode + 6)

        if (nodes[7] == hasfile):
            try:
                nodes[nextnode + 7] = 1
                print("Node 5 has trasnferred to Node ", nextnode + 7)
            except IndexError:
                print("ERROR")
                print("FAILED TO TRANSFER FILE FROM NODE 7 TO NODE ", nextnode + 7)

        print("NODES:", nodes)
        step += 1

    print("WE DID IT?")
    print(nodes)

#Map out nodes to contact for each node
def nodeMap(n):
    global mapArray

    step = 1
    hasfile = 1
    nodes = []
    # create array of nodes
    for x in range(0, n + 1):
        nodes.append(0)

    # create array for address map for each node
    mapArray = []
    # create array of nodes
    for x in range(0, n + 1):
        mapArray.append('')

    nodes[0] = 1 #set host to have file
    maxStep = maxSteps(n) #get ceiling of steps needed
    print("MAX STEPS", maxStep)

    while(step <= maxStep):
        nextnode = int(2 ** (step - 1))
        print("NEXT= ", nextnode)
        print("STEP: ", step)

        for x in range (n, -1, -1):
            if (nodes[x] == hasfile):
                try:
                    nodes[nextnode + x] = 1
                    print("Node ", x, " has transferred to Node ", nextnode + x)
                    mapArray[x] = mapArray[x] + ' ' + str(nextnode + x)
                except IndexError:
                    print("ERROR")
                    print("FAILED TO TRANSFER FILE FROM NODE ", x, " TO NODE ", nextnode + x)
        step += 1
    print (mapArray)

def getmapArray(currNode):
    addressList = mapArray[currNode].split()
    addressList = [int(i) for i in addressList]
    return addressList

nodeMap(100)
print("ARRAY : ", getmapArray(0))

#pseudoReplicate()
