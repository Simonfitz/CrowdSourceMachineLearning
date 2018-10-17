
import time
import sys
import os
import socket
import time
import traceback
import tensorflow as tf
from threading import Thread
from PyQt5 import QtCore, QtGui, QtWidgets, uic

import config
import client
import fileServer
import fileClient
import distFileServer

def runNeuralNet(job_input, task_input, batch_size, learning_rate, training_epochs, numWorkers, clusterArray):
    tf.reset_default_graph()
    #Hardcode values
    # parameter_servers = ["127.0.0.1:2222"]
    #
    # workers = [
    #     "127.0.0.12:2223",
    #     "127.0.0.12:2224",
    #     #"127.0.0.12:2225"
    # ]
    print("CLUSTER : ", clusterArray[0])
    parameter_servers = [clusterArray[0] + config.default_ps_port]


    #parameter_servers = ["127.0.0.1:2222"]

    workers = []
    for x in range (0, numWorkers+1):
        workers.append(clusterArray[x] + config.default_ports[x])

    print("WORKER ARRAY: ", workers)
    cluster = tf.train.ClusterSpec({"ps": parameter_servers, "worker": workers})

    # FETCH & LOAD DATASET
    if(task_input == 0):
        config.messageArray.append(job_input + " Extracting Data")

    else:
        config.messageArray.append("Data Received from Host")
        config.messageArray.append("Extracting Data")

    from tensorflow.examples.tutorials.mnist import input_data
    mnist = input_data.read_data_sets('MNIST_data', one_hot=True)

    # start a server for a specific task
    server = tf.train.Server(
        cluster,
        job_name=job_input,
        task_index=task_input
    )

    print("Batch Size: ", batch_size)
    print("Learning Rate : ", learning_rate)
    print("Epochs : ", training_epochs)
    print("Workers : ", numWorkers)

    if job_input == "ps":
        server.join()
    elif job_input == "worker":

        # Between-graph replication
        with tf.device(tf.train.replica_device_setter(
                worker_device="/job:worker/task:%d" % task_input,
                cluster=cluster)):

            # count the number of updates
            global_step = tf.get_variable(
                'global_step',
                [],
                initializer=tf.constant_initializer(0),
                trainable=False)

            # input images
            with tf.name_scope('input'):
                # None -> batch size can be any size, 784 -> flattened mnist image
                x = tf.placeholder(tf.float32, shape=[None, 784], name="x-input")
                # target 10 output classes
                y_ = tf.placeholder(tf.float32, shape=[None, 10], name="y-input")

            # model parameters will change during training so we use tf.Variable
            tf.set_random_seed(1)
            with tf.name_scope("weights"):
                W1 = tf.Variable(tf.random_normal([784, config.numNeurons]))
                W2 = tf.Variable(tf.random_normal([config.numNeurons, 10]))

            # bias
            with tf.name_scope("biases"):
                b1 = tf.Variable(tf.zeros([config.numNeurons]))
                b2 = tf.Variable(tf.zeros([10]))

            # implement model
            with tf.name_scope("softmax"):
                # y is our prediction
                z2 = tf.add(tf.matmul(x, W1), b1)
                a2 = tf.nn.sigmoid(z2)
                z3 = tf.add(tf.matmul(a2, W2), b2)
                y = tf.nn.softmax(z3)

            # specify cost function
            with tf.name_scope('cross_entropy'):
                # this is our cost
                cross_entropy = tf.reduce_mean(
                    -tf.reduce_sum(y_ * tf.log(y), reduction_indices=[1]))

            # specify optimizer
            with tf.name_scope('train'):
                # optimizer is an "operation" which we can execute in a session
                grad_op = tf.train.GradientDescentOptimizer(learning_rate)
                train_op = grad_op.minimize(cross_entropy, global_step=global_step)

            with tf.name_scope('Accuracy'):
                # accuracy
                correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))
                accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

            # create a summary for our cost and accuracy
            tf.summary.scalar("cost", cross_entropy)
            tf.summary.scalar("accuracy", accuracy)

            # merge all summaries into a single "operation" which we can execute in a session
            summary_op = tf.summary.merge_all()
            init_op = tf.global_variables_initializer()
            print("Variables initialized ...")

        sv = tf.train.Supervisor(is_chief=(task_input == 0),
                                 global_step=global_step,
                                 init_op=init_op)

        begin_time = time.time()
        frequency = 100
        with sv.prepare_or_wait_for_session(server.target) as sess: #PROBLEM IS HERE
            writer = tf.summary.FileWriter(config.logs_path, graph=tf.get_default_graph())
            start_time = time.time()
            config.messageArray.append("Begin Training")

            for epoch in range(training_epochs):

                # number of batches in one epoch
                batch_count = int(mnist.train.num_examples / batch_size)

                count = 0
                for i in range(batch_count):
                    batch_x, batch_y = mnist.train.next_batch(batch_size)

                    # perform the operations we defined earlier on batch
                    _, cost, summary, step = sess.run(
                        [train_op, cross_entropy, summary_op, global_step],
                        feed_dict={x: batch_x, y_: batch_y})
                    writer.add_summary(summary, step)

                    count += 1
                    if count % frequency == 0 or i + 1 == batch_count:
                        elapsed_time = time.time() - start_time
                        start_time = time.time()
                        print("Step: %d," % (step + 1),
                              " Epoch: %2d," % (epoch + 1),
                              " Batch: %3d of %3d," % (i + 1, batch_count),
                              " Cost: %.4f," % cost,
                              " AvgTime: %3.2fms" % float(elapsed_time * 1000 / frequency))
                        config.messageArray.append("Step: " + str(step+1) + "|| Epoch: " + str(epoch+1))
                        count = 0
            if(task_input==0):
                config.messageArray.append("Completed Network Training - Testing Network")
                config.messageArray.append("Final Test Accuracy : %2.2f" % sess.run(accuracy, feed_dict={x: mnist.test.images, y_: mnist.test.labels}))
            print("Total Time: %3.2fs" % float(time.time() - begin_time))
            print("Final Cost: %.4f" % cost)
        if (task_input != 0):
            config.messageArray.append("Completed Network Training")
            config.messageArray.append("Disconnecting from Host")
        sv.stop()
        print("done")
        sys.exit()

def runNeuralNet2():
    print("NEW NN")

def connectToServer(hostOrworker, numWorkers, batch_size, learning_rate, training_epochs):
    # Try connect continuously to match making server
    hostIP = "127.0.0.1"
    config.messageArray.append("Attempting connection to matchmaking server: " + hostIP)
    while True:
        try:
            soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            soc.connect((hostIP, 12345))
        except:
            print("No connection available - retrying")
            soc.close()
            time.sleep(3)
            continue
        break
    config.messageArray.append("Successfully connected with server")
    # send message
    # clients_input = input("What you want to proceed my dear Master?\n")
    clients_input = hostOrworker + ' ' + str(numWorkers) + ' ' + str(batch_size) + ' ' + str(learning_rate) + ' ' + str(training_epochs)

    try:
        soc.send(clients_input.encode("utf8"))  # we must encode the string to bytes
    except ConnectionResetError:
        print("Connection was ended by the server")
        #continue

    try:
        # receive reply
        result_bytes = soc.recv(4096)  # the number means how the response can be in bytes
        result_string = result_bytes.decode("utf8")  # the return will be in bytes, so decode
    except ConnectionResetError:
        print("Connection was ended by the server")
        #continue

    return result_string