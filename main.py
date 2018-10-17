#from __future__ import print_function

import time
import sys
import os
import socket
import time
import traceback
import tensorflow as tf
from threading import Thread
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import numpy as np
from pyspark.sql import SparkSession

import config
import client
import fileServer
import fileClient
import distFileServer

# PyQt
qtCreatorFile = "controllerGUI.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class controllerGUI(QtWidgets.QDialog, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.label_currentState.setAlignment(QtCore.Qt.AlignCenter)
        self.button_connect.clicked.connect(self.beginHost)
        self.button_idle.clicked.connect(self.beginWorker)
        self.button_stop.clicked.connect(self.command_stop)

        try:
            Thread(target=self.updateMsg).start()
        except:
            print("could not create message handler!")
            traceback.print_exc()

    def beginHost(self):
        self.label_currentState.setText("Connecting..")
        config.batch_size = self.slider_batchsize.value()
        config.learning_rate = (self.slider_learningrate.value()/10)
        config.training_epochs = self.slider_epochs.value()
        config.numWorkers = self.slider_workers.value()

        config.file_inputs_loc = self.input_data_path.text()
        config.file_targets_loc = self.input_target_path.text()
        self.input_data_path.clear()
        self.input_target_path.clear()

        try:
            Thread(target=hostHandle).start()
            self.label_currentState.setText("Hosting")
        except:
            config.messageArray.append("ERROR: could not create host!")
            traceback.print_exc()


    def beginWorker(self):
        try:
            Thread(target=workerHandle).start()
            self.label_currentState.setText("Working")
        except:
            config.messageArray.append("ERROR: could not create worker!")
            traceback.print_exc()

    def command_stop(self):
        config.messageArray.append("Terminating any active processes & connections")
        self.label_currentState.setText("IDLE")

    def updateMsg(self):
        # while(True):
        #     if (config.newMsg != config.prevMsg):
        #         self.listWidget.addItem(config.newMsg)
        #         config.prevMsg = config.newMsg
        #     else:
        #         time.sleep(0.2)
        while(True):
            if not config.messageArray:
                time.sleep(1)
            else:
                self.listWidget.addItem(config.messageArray[0])
                config.messageArray.pop(0)


def hostHandle():
    # config
    batch_size = config.batch_size
    learning_rate = config.learning_rate
    training_epochs = config.training_epochs
    numWorkers = config.numWorkers
    logs_path = config.logs_path

    message = "host" + ' ' + str(numWorkers) + ' ' + str(batch_size) + ' ' + str(learning_rate) + ' ' + str(training_epochs)
    config.messageArray.append("Host Starting with following params:")
    config.messageArray.append("          Batch Size = " + str(batch_size))
    config.messageArray.append("          Learning Rate = " + str(learning_rate))
    config.messageArray.append("          Epochs = " + str(training_epochs))
    config.messageArray.append("          Required Workers = " + str(numWorkers))
    # Contact Matchmaking Server
    result_string = client.connectToServer("host", numWorkers, batch_size, learning_rate, training_epochs)

    #
    # PARSE RESULTS STRING
    #
    numWorkers, batch_size, learning_rate, training_epochs, jobIndex, clusterString = result_string.split(" ", 5)

    numWorkers = int(numWorkers)
    batch_size = int(batch_size)
    learning_rate = float(learning_rate)
    training_epochs = int(training_epochs)

    print(numWorkers)
    print(batch_size)
    print(learning_rate)
    print(training_epochs)
    print(jobIndex)
    print(clusterString)

    # create clusterArray from clusterString and numWorkers
    clusterArray = []
    clusterArray = clusterString.split()
    print("ARRAY: ", clusterArray)

    # Begin Hosting Cluster - Parameter Server
    try:
        print("PS - RUN NEURAL NET CODE HERE")
        Thread(target=client.runNeuralNet, args=("ps", 0, batch_size, learning_rate, training_epochs, numWorkers, clusterArray)).start()
    except:
        print("could not create parameter server!")
        traceback.print_exc()

    # Create Chief Worker
    try:
        print("CHIEF - RUN NEURAL NET CODE HERE")
        Thread(target=client.runNeuralNet, args=("worker", 0, batch_size, learning_rate, training_epochs, numWorkers, clusterArray)).start()
    except:
        print("could not create worker!")
        traceback.print_exc()


def workerHandle():
    # Contact Matchmaking Server
    # try:
    #     return_string = client.connectToServer("worker", 1, 1, 1, 1)
    #     print("RESULT", return_string)
    # except:
    #     print("could not connect!")
    #     traceback.print_exc()
    #
    #handle return string to get params and addresses
    #
    # Create Worker
    config.messageArray.append("Worker Started")
    result_string = client.connectToServer("worker", 1, 1, 1, 1)
    print("RESULTSTRING=", result_string)
    #
    #PARSE RESULTS STRING
    #
    numWorkers, batch_size, learning_rate, training_epochs, jobIndex, clusterString = result_string.split(" ", 5)

    config.messageArray.append("Connected to Host using the following params:")
    config.messageArray.append("          Batch Size = " + str(batch_size))
    config.messageArray.append("          Learning Rate = " + str(learning_rate))
    config.messageArray.append("          Epochs = " + str(training_epochs))
    config.messageArray.append("          Required Workers = " + str(numWorkers))

    numWorkers = int(numWorkers)
    batch_size = int(batch_size)
    learning_rate = float(learning_rate)
    training_epochs = int(training_epochs)

    print(numWorkers)
    print(batch_size)
    print(learning_rate)
    print(training_epochs)
    print(jobIndex)
    print(clusterString)

    # create clusterArray from clusterString and numWorkers
    clusterArray = []
    clusterArray = clusterString.split(" ")
    print("ARRAY: ", clusterArray)

    try:
        print("WORKER {} - RUN NEURAL NET CODE HERE".format(jobIndex))
        Thread(target=client.runNeuralNet, args=("worker", 1, batch_size, learning_rate, training_epochs, numWorkers, clusterArray)).start()
    except:
        print("could not create worker!")
        traceback.print_exc()


if __name__ == "__main__":
    print("Started")
    app = QtWidgets.QApplication(sys.argv)
    window = controllerGUI()
    window.show()
    sys.exit(app.exec_())
    #File Transfer Test
    # fileServer.callFileServer()
    # fileClient.callFileClient()
