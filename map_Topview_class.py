#!/usr/bin/python
# coding:utf-8

# export display := 0
from __future__ import division
import matplotlib as mpl
mpl.use('Agg')
import os
import cv2
import time
import json
import sys
import new_topview
import math
import numpy as np


class MapTopviewDraw(object):
    def __init__(self,codeRootdir):
        self.codeRootdir = codeRootdir
        self.localpath = self.codeRootdir+"/cache_/graph/"
        self.winsize = 601
        self.sigma = 40

        cfgStr = ""
        try:
            with open(self.codeRootdir+"/param/param.json", "r") as f:
                lines = f.readlines()
                for line in lines:
                    cfgStr = cfgStr + line
        except BaseException, e:
            print e
            # logging.error('__init__:' + e)

        cfgObj = json.loads(cfgStr)
        self.img_height = int(cfgObj["imgheight"])
        self.img_width = int(cfgObj["imgwidth"])
        self.img_scale = int(cfgObj["imgscale"])
        self.db = cfgObj["db"]
        self.dbHost = cfgObj["dbHost"]
        self.dbUserName = cfgObj["dbUserName"]
        self.dbPwd = cfgObj["dbPwd"]
        self.storageAccount = cfgObj["storageAccount"]
        self.accountKey = cfgObj["accountKey"]
        self.AZURE_BINARY = cfgObj["AZURE_BINARY"]

        if self.img_scale != 0:
            self.img_height = int(int(self.img_height) / int(self.img_scale))
            self.img_width = int(int(self.img_width) / int(self.img_scale))


    def cur_file_dir(self):
        path = sys.path[0]
        if os.path.isdir(path):
            return path
        elif os.path.isfile(path):
            return os.path.dirname(path)


    # 1
    def runHeat_topview_ford(self,date,data):

        image = cv2.imread("./bkg/huanqiulama_heatmap_bak.png")
        bkimg = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        camera_list=[]
        camera_det=[]

        self.Zone = np.zeros((20,20))
        pos_colum = [0.2664,0.43,0.61,0.8644,0.8644,0.8644,0.523]
        pos_row = [0.4682,0.234,0.2331,0.325,0.5208,0.8,0.491]
        value = data

        for i in range(len(value)):
            col = int(pos_colum[i] * 20) - 1
            row = int(pos_row[i] *20) - 1
            self.Zone[col][row] = value[i]

        self.delta = 5

        self.Zone_fill = np.zeros((20,20))
        for row in range(20):
            for col in range(20):
                if not self.Zone[col][row] == 0.0:
                    self.set_data_around(col,row)

        Zone = self.Zone + self.Zone_fill
        row = len(Zone)
        coloum = len(Zone[0])
        for i in range(row):
            for j in range(coloum):
                if not Zone[i][j] == 0:
                    cam_t = [(j+1)/(coloum + 1),(i + 1)/(row +1)]
                    camera_list.append(cam_t)
                    camera_det.append(Zone[i][j])

        Heatpath = new_topview.run(bkimg, camera_list, camera_det, self.codeRootdir, self.winsize, self.sigma,date)
        return Heatpath


    def set_data_around(self,col,row):

        start_co = col - self.delta
        start_row = row - self.delta

        for ro in range(self.delta * 2 + 1):
            for co in range(self.delta * 2 + 1):
                co_now = start_co + co
                ro_now = start_row + ro
                if co_now < 20 and co_now >= 0 and ro_now < 20 and ro_now >= 0:
                    time = 1 / (math.fabs(col - co_now) + math.fabs(row - ro_now) + 1)
                    self.Zone_fill[co_now][ro_now] += self.Zone[col][row] * time

