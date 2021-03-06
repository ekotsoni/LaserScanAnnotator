import sys
import os
import random
import matplotlib
import matplotlib.pyplot as plt
import time
import math
import csv
import ast
import functools
#rom scipy import spatial

# Make sure that we are using QT5
matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import Qt, QUrl, pyqtSignal, QFile, QIODevice, QRect
from PyQt5.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QPushButton,
QSizePolicy, QVBoxLayout, QWidget,QLineEdit, QInputDialog, QMenu)

from numpy import arange
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from sets import Set

from enum import Enum

progname = os.path.basename(sys.argv[0])

#Arxikopoihsh global timwn
#Arxikopoihsh metritwn
cnt = -1
timer = None
#Arxikopoihsh grafikwn parastasewn
ax = None
fig = None
fw = None
scan_widget = None
ok = 'No'
nw = None
#Arxikopoihsh annotation
objx = []
objy = []
annotating = False
firstclick = False
secondclick = False
thirdclick = False
colours = ['#FF69B4','#FFFF00','#CD853F','#000000','#8A2BE2','#00BFFF','#ADFF2F','#8B0000']
colour_index = 0
c1 = []
c2 = []
colorName = []
txt = None
annot = []
classes = None
selections = []
le = None
rightClick = None
items = []
write = False
range_max = 0
timeON = 0.0
sel = OrderedSet([])

class Window(FigureCanvas):

    def __init__(self, parent=None, width=10, height=3, dpi=100):

        global fw,fig,ax,bag_file,data

        fw = self

        fig = Figure(figsize=(width, height), dpi=dpi)

        ax = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def icon(self):
        pass

class MyPopup(QWidget):

    def __init__(self):

        global le

        QWidget.__init__(self)
        self.setWindowTitle('Add New Person')
        self.main_widget = QtWidgets.QWidget(self)
        self.le = QLineEdit(self.window())
        self.le.setDragEnabled(True)
        self.le.setPlaceholderText("Write ID:")
        self.Ok = QPushButton("Ok", self)

    def paintEvent(self,e):

        global le

        self.le.setPlaceholderText('Write ID:')
        self.le.setMinimumWidth(100)
        self.le.setDragEnabled(True)
        self.le.move(90,15)
        self.Ok.move(115,60)

        self.le.textChanged.connect(self.personLabel)
        self.Ok.clicked.connect(self.closePerson)

    def personLabel(self,text):
        global txt
        txt = text

    def closePerson(self):
        global txt,le,colour_index,annot,selections,vcolours,ok,scan_widget,cnt,sel,annotID
        txt = self.le.text()
        self.Ok.clicked.disconnect()
        self.close()

        if txt not in sel:
            sel.add(str(txt))

        position = 0
        for i in sel:
            if i == txt:
                break
            position += 1

        colour_index = position%(len(colours))
        ok = 'Yes'
        scan_widget.training()
        #annot[cnt].annotID.append(str(txt))

class LS(Window):

    def ptime(self):

        global timer,timeON

        timer.timeout.connect(self.icon)
        timer.start(timeON*1000)
        #timer.start(0.0000976562732)

    def icon(self):

        global cnt,annot,ok,scan_widget

        if(cnt < len(annot)):
            ok = 'Yes'
            scan_widget.drawLaserScan()
            cnt += 1
        if (cnt == len(annot)):
            cnt=-1
            timer.stop()
            ok = 'No'
            scan_widget.drawLaserScan()

    def drawLaserScan(self):

        global ax,annot,cnt,samex,samey,listofpointsx,listofpointsy,fw,ok,c1,c2,colorName,firstclick,secondclick,colourID,colorName,range_max,ok

        if (ok == 'Yes'):
            ax.clear()
            ax.axis('equal')
            ax.plot(annot[cnt].samex,annot[cnt].samey,'b.')
            if not annot[cnt].listofpointsx == []:
                for j in range(len(annot[cnt].colourID)):
                    ax.plot(annot[cnt].listofpointsx[j],annot[cnt].listofpointsy[j],color=annot[cnt].colourID[j],marker='.')
            fw.draw()
        elif (ok == 'Rect'):
            ax.axis('equal')
            if (cnt>=0) and (cnt<len(annot)):
                ax.plot([c1[0],c2[0]],[c1[1],c1[1]],'r')
                ax.plot([c2[0],c2[0]],[c1[1],c2[1]],'r')
                ax.plot([c2[0],c1[0]],[c2[1],c2[1]],'r')
                ax.plot([c1[0],c1[0]],[c2[1],c1[1]],'r')
                fw.draw()
        elif (ok == 'No'):
            ax.clear()
            fw.draw()

    def training(self):

        global annot,samex,samey,c1,c2,colorName,colours,colour_index,colourID,listofpointsx,listofpointsy,ok,firstclick,secondclick,cnt,scan_widget, bag_file, data,selections,write,annotID,txt

        annot[cnt].annotID.append(str(txt))
        for i in range(len(annot[cnt].samex)):
            if ((annot[cnt].samex[i] >= c1[0]) and (annot[cnt].samex[i] <= c2[0]) and ((annot[cnt].samey[i] >= c2[1]) and (annot[cnt].samey[i] <= c1[1]))):
                colorName = colours[colour_index]
                annot[cnt].colourID.append(colorName)
                annot[cnt].listofpointsx.append(annot[cnt].samex[i])
                annot[cnt].listofpointsy.append(annot[cnt].samey[i])
        ok = 'Yes'
        scan_widget.drawLaserScan()
        colour_index += 1
        if (colour_index == (len(colours))):
           colour_index = 0 
        firstclick = False
        secondclick = False

        #SAVE to CSV
        filename = bag_file.replace(".bag","_laser.csv")
        with open(filename, 'w') as data:
            write = csv.writer(data, quoting = csv.QUOTE_MINIMAL)
            for row in annot:
                row_ = [row.samex, row.samey, row.listofpointsx, row.listofpointsy, row.annotID, row.colourID]
                write.writerow(row_)
            data.close()

class ApplicationWindow(QtWidgets.QMainWindow):

    def __init__(self):

        global scan_widget, classes, le, selections,annot, selections,filename

        QtWidgets.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.main_widget = QtWidgets.QWidget(self)

        scan_widget = LS(self.main_widget)

        #Define buttons
        scanLayout = QHBoxLayout() 
        scanLayout.addWidget(scan_widget)

        playButton = QPushButton("Play")
        pauseButton = QPushButton("Pause")
        prevFrameButton = QPushButton("Previous")
        nextFrameButton = QPushButton("Next")
        stopButton = QPushButton("Stop")

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(playButton)
        buttonLayout.addWidget(pauseButton)
        buttonLayout.addWidget(prevFrameButton)
        buttonLayout.addWidget(nextFrameButton)
        buttonLayout.addWidget(stopButton)
        buttonLayout.setAlignment(Qt.AlignTop)

        layout = QVBoxLayout(self.main_widget)
        layout.addLayout(scanLayout)
        layout.addLayout(buttonLayout)

        #Define Connections
        playButton.clicked.connect(self.bplay)
        pauseButton.clicked.connect(self.bpause)
        prevFrameButton.clicked.connect(self.bprevious)
        nextFrameButton.clicked.connect(self.bnext)
        stopButton.clicked.connect(self.bstop)

        fig.canvas.mpl_connect('button_press_event', self.onClick)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

    def contextMenuEvent(self,event):

        global ok, rightClick,items,classes,submenu,txt,selections,annot,cnt,sel

        rightClick = event.pos()

        if (ok == 'Rect'):

            menu = QMenu(self)

            deleteBox = menu.addAction('Delete Box')
            deleteBox.triggered.connect(self.delBox)
            submenu = menu.addMenu('Choose Person')

            for i in sel:
                classes = submenu.addAction(i)
                classes.triggered.connect(functools.partial(self.chooseClass,i))
            changeId = submenu.addAction('Change Id')
            changeId.triggered.connect(self.chId)
            cancel = menu.addAction('Cancel')
            cancel.triggered.connect(self.cancelannot)

            action = menu.exec_(self.mapToGlobal(event.pos()))

    def delBox(self,action):
        global firstclick,secondclick,cnt,annot,ok,scan_widget,le,Ok
        firstclick = False
        secondclick = False
        if ((cnt>=0) and (cnt<len(annot))):
            ok = 'Yes'
            scan_widget.drawLaserScan()

    def chooseClass(self, txt_):
        global colour_index,annot,selections,txt,colours,ok,scan_widget,items
        txt = txt_
        position = 0
        for i in sel:
            if i == txt:
                break
            position += 1
        colour_index = position%(len(colours))
        ok = 'Yes'
        scan_widget.training()

    def chId(self,action):
        self.new = MyPopup()
        self.new.setGeometry(QRect(500, 100, 300, 100))
        self.new.show()

    def cancelannot(self,action):
        global annot,cnt,samex,samey,c1,c2,listofpointsx,listofpointsy,ok,scan_widget,selections,colourID,annotID

        i=0
        while (i<len(annot[cnt].listofpointsx)):
            if ((annot[cnt].listofpointsx[i] >= c1[0]) and (annot[cnt].listofpointsx[i] <= c2[0]) and ((annot[cnt].listofpointsy[i] >= c2[1]) and (annot[cnt].listofpointsy[i] <= c1[1]))):
                if ((annot[cnt].listofpointsx[i] is not None) and (annot[cnt].listofpointsy[i] is not None)):
                    annot[cnt].listofpointsx.remove(annot[cnt].listofpointsx[i])
                    annot[cnt].listofpointsy.remove(annot[cnt].listofpointsy[i])
            else:
                i += 1 
                print i

        ok = 'Yes'
        scan_widget.drawLaserScan()

    def bplay(self):
        global scan_widget
        scan_widget.ptime()

    def bpause(self):
        global timer
        timer.stop()

    def bprevious(self):
        global cnt, ok, scan_widget,firstclick,secondclick
        cnt = cnt-1
        if (cnt>=0):
            ok = 'Yes'
            scan_widget.drawLaserScan()
            firstclick = False
            secondclick = False
        else:
            ok = 'No'
            cnt = -1
            scan_widget.drawLaserScan()

    def bnext(self):
        global cnt, annot, ok, scan_widget,colour_index,samex,firstclick,secondclick
        colour_index = 0
        cnt = cnt+1
        if (cnt<len(annot)):
            ok = 'Yes'
            scan_widget.drawLaserScan()
            firstclick = False
            secondclick = False
        else:
            ok = 'No'
            cnt= -1
            scan_widget.drawLaserScan()

    def bstop(self):
        global cnt,timer,ax,fw
        cnt = -1
        timer.stop()
        ax.clear()
        fw.draw()

    def onClick(self, event):

        global firstclick, c1, secondclick, c2, ok, scan_widget, thirdclick
        x = event.x
        y = event.y
        if event.button == Qt.LeftButton:
            if firstclick == False:
                if event.inaxes is not None:
                    c1 = [event.xdata,event.ydata]
                    firstclick = True
            elif secondclick == False:
                if event.inaxes is not None:
                    c2 = [event.xdata,event.ydata]
                    if (c2[0]<c1[0]):
                        temp_c = c2
                        c2 = c1
                        c1 = temp_c
                    secondclick = True
                    ok = 'Rect'
                    scan_widget.drawLaserScan()

class laserAnn:

    global c1,c2, objx,objy, s1,s2, txt

    def __init__(self, samex_=None, samey_=None, listofpointsx_=None,listofpointsy_=None, annotID_=None, colourID_=None,selections_=None):

        self.samex = []
        self.samey = []
        self.listofpointsx = []
        self.listofpointsy = []
        self.annotID = []
        self.colourID = []
        self.selections = []

        if samex_ == None:
            self.samex = []
        else:
            self.samex = samex_
        if samey_ == None:
            self.samey = []
        else:
            self.samey = samey_
        if listofpointsx_ == None:
            self.listofpointsx = []
        else:
            self.listofpointsx = listofpointsx_
        if listofpointsy_ == None:
            self.listofpointsy = []
        else:
            self.listofpointsy = listofpointsy_
        if annotID_ == None:
            self.annotID = []
        else:
            self.annotID = annotID_
        if colourID_ == None:
            self.colourID = []
        else:
            self.colourID = colourID_
        if selections_ == None:
            self.selections = []
        else:
            self.selections = selections_

def run(laserx,lasery,bagFile,time_increment):

    global timer,scan_widget,annot,s1,s2,bag_file,colorName,selections,filename,items,range_max,timeON,sel

    timeON = time_increment

    timer = QtCore.QTimer(None)

    bag_file = bagFile
    filename = bag_file.replace(".bag", "_laser.csv")
    if os.path.isfile(filename):
        with open(filename, 'rb') as data:

            if os.path.getsize(filename)>1:
                read = csv.reader(data)
                for row in read:

                    row[0] = row[0][1:-1]
                    row[1] = row[1][1:-1]
                    row[2] = row[2][1:-1]
                    row[3] = row[3][1:-1]
                    row[4] = row[4][1:-1]
                    row[5] = row[5][1:-1]
                    row[5] = row[5].replace("'","")
                    row[4] = row[4].replace("'","")
                    row[0] = row[0].split(", ")
                    row[1] = row[1].split(", ")
                    row[2] = row[2].split(", ")
                    row[3] = row[3].split(", ")
                    row[4] = row[4].split(", ")
                    row[5] = row[5].split(", ")

                    for i in range(0, len(row[0])):
                        if row[0][i] == "":
                            row[0] = []
                            break
                        else:
                            row[0][i] = float(row[0][i])
                    for i in range(0, len(row[1])):
                        if row[1][i] == "":
                            row[1] = []
                            break
                        else:
                            row[1][i] = float(row[1][i])
                    for i in range(0, len(row[2])):
                        if row[2][i] == "":
                            row[2] = []
                            break
                        else:
                            row[2][i] = float(row[2][i])
                    for i in range(0, len(row[3])):
                        if row[3][i] == "":
                            row[3] = []
                            break
                        else:
                            row[3][i] = float(row[3][i])
                    for i in range(0, len(row[4])):
                        if row[4][i] == "":
                            row[4] = []
                            break
                        else:
                            row[4][i] = str(row[4][i])
                    for i in range(0, len(row[5])):
                        if row[5][i] == "":
                            row[5] = []
                            break
                        else:
                            row[5][i] = str(row[5][i])

                    la = laserAnn(row[0], row[1], row[2], row[3], row[4], row[5])
                    annot.append(la)

                    for i in range(len(row[4])):
                        if ((row[4][i] != []) and (row[4][i] not in sel) and (row[4][i] != '\"') and (row[4][i] != '\\') and (row[4][i] != '\'')):
                            sel.add(row[4][i].strip('\''))

                    '''
                    for i in range(len(annot[0].selections)):
                        if annot[0].selections[i] not in items:
                            items.append(annot[0].selections[i])
                    '''
    else:
        for i in range(len(laserx)):
            s1 = laserx[i].tolist()
            s2 = lasery[i].tolist()
            la = laserAnn(samex_=s1,samey_=s2)
            annot.append(la)

    qApp = QtWidgets.QApplication(sys.argv)

    s = ApplicationWindow()

    s.show()

    sys.exit(qApp.exec_())