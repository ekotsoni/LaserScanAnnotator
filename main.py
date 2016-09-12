#!/usr/bin/env python
import rosbag_annotator as ra

if __name__ == '__main__':
    ra.start('/home/ekotsoni/ss1_lsN_sc2_rumdag_cgtyia_v.bag','testOut','/scan')