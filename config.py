import time
import sys
import os
import socket
import time
import traceback
import tensorflow as tf
from threading import Thread

# config
batch_size = 128
learning_rate = 0.1
training_epochs = 10
numWorkers = 1
numNeurons = 100
logs_path = "/tmp/mnist/1"
default_ports = [":2223", ":2224", ":2225", ":2226", ":2227", ":2228", ":2229"]
default_ps_port = ":2222"
prevMsg = ''
newMsg = ''
messageArray = []
file_inputs_loc = 'mnist_inputs.csv'
file_targets_loc = 'mnist_targets.csv'