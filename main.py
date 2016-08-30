#!/usr/bin/env python
import rosbag_annotator as ra

if __name__ == '__main__':
    ra.start('/home/ekotsoni/2016-02-23-13-38-26.bag','testOut','/scan')
