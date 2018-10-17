from pyspark.sql import SparkSession
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

def callHDFS():
    sparkSession = SparkSession.builder.appName("example-pyspark-read-and-write").getOrCreate()
    data = [('First', 1), ('Second', 2), ('Third', 3), ('Fourth', 4), ('Fifth', 5)]
    df = sparkSession.createDataFrame(data)
    print("THIS WORKS?")