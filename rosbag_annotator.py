#!/usr/bin/env python
import roslib
import cv2
from sensor_msgs.msg import Image
from sensor_msgs.msg import CompressedImage
from sensor_msgs.msg import LaserScan
from cv_bridge import CvBridge, CvBridgeError
import rospy
from std_msgs.msg import String
import signal
import os
import sys
import time
import threading
import rosbag
import yaml
import numpy as np
import matplotlib.pyplot as plt
import argparse
import textwrap
import math
import laserscan_gui


programmName = os.path.basename(sys.argv[0])
laserDistances = []
theta = []
sx = []
sy = []
input_topic = None
range_max = 0
time_incr = 0

def play_bag_file(bag_file):

	global laserDistances, sx, sy, theta, input_topic, range_max,time_incr

	bag = rosbag.Bag(bag_file)
	info_dict = yaml.load(bag._get_yaml_info())
	topics =  info_dict['topics']
	topic = topics[1]
	messages =  topic['messages']
	duration = info_dict['duration']
	topic_type = topic['type']

	g = bag.read_messages(topics=[input_topic])
	topic, msg, t = g.next()
	range_max = msg.range_max
	time_incr = msg.time_increment
	tmp = np.arange(msg.angle_min, msg.angle_max, msg.angle_increment)

	if len(tmp) < len(msg.ranges):
		tmp = np.arange(msg.angle_min, msg.angle_max+msg.angle_increment, msg.angle_increment)
	theta = tmp
		#theta.append(msg.angle_max+msg.angle_increment)
	theta = np.degrees(theta)

	#Loop through the rosbag
	for topic, msg, t in bag.read_messages(topics=[input_topic]):
		#Get the scan
		#laserDistances.append(np.array(msg.ranges))
		tmp = np.array(msg.ranges)
		for i in range(len(tmp)):
			if tmp[i] > msg.range_max:
				tmp[i] = 'inf'
		laserDistances.append(tmp)
		x = np.cos(np.radians(theta)) * laserDistances[-1]
		y = np.sin(np.radians(theta)) * laserDistances[-1]
		sx.append(x)
		sy.append(y)
	laserDistances = []
	bag.close()

def start(input_file,output_file,scan_topic):

	global sx, sy, input_topic, range_max,time_incr

	bag_file = input_file
	output_file = output_file
	input_topic = scan_topic

	#Create results file
	if(output_file is None):
		feature_file = bag_file.split(".")[0].split("/")[-1] + "_RES"
	else:
		feature_file = output_file

	if os.path.exists(feature_file) and not append:
		os.remove(feature_file)

	#print feature_file

	#Open bag and get framerate	
	play_bag_file(bag_file)

	laserscan_gui.run(sx, sy, bag_file, time_incr)
