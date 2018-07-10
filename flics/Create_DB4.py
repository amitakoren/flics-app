# -*- coding: utf-8 -*-
"""
Created on Tue Dec 12 15:55:11 2017

@author: bar23
"""


import sys
from PyQt5.QtWidgets import (QMainWindow, QTextEdit, QAction, QApplication,QFileDialog,
                             QPushButton,QLabel,QGridLayout,QWidget,QDockWidget,QListWidget,
                             QListWidgetItem, QVBoxLayout,QHBoxLayout,QLineEdit,QComboBox,
                             QLayout,QFormLayout,QMessageBox,qApp,QDialog,QTableView)

from PyQt5.QtGui import (QIcon,QImage)
from PyQt5.QtCore import (QCoreApplication,Qt)


import json

#import cv2
#import numpy as np
import pandas as pd

from imageObj4 import (Imageobj)
import os 
import math

import details_window


class window(QMainWindow):
    
    def __init__(self):
        super(window,self).__init__()
        self.initUI()
        
    def initUI(self):
        self.statusBar().showMessage('Ready')
        
        """menu bar part
         The menu bar as three main options: 
            (1) file:
                (1.1) open new file
                (1.2) open exist file
                (1.3) save
                (1.4) restart
                (1.5) Quit
            (2) Edit:
                (2.1) undo last action, let the user the option to cancel
                roi/vector mark insteed of approve
                (2.2) add roi, if the user want to add roi while open an exist 
                db file, make the "select roi" button able
                (2.3) delete roi, when roi is selected from list 
    
    
        """
        
        
        menubar=self.menuBar()
        #icon's 
        self.fileDir = os.path.dirname(os.path.realpath('__file__'))
        fileIcon = os.path.join(self.fileDir, 'icon/new_file.png')
        saveIcon = os.path.join(self.fileDir,'icon/save.png')
        restartIcon = os.path.join(self.fileDir, 'icon/restart.png')
        exitIcon =  os.path.join(self.fileDir, 'icon/exit.png')
        undoIcon =  os.path.join(self.fileDir, 'icon/undo.png')
        readmeIcon = os.path.join(self.fileDir, 'icon/readme.png')
        primaryIcon = os.path.join(self.fileDir, 'icon/database.png')
        
        fileMenu = menubar.addMenu('File')
        b_newfile= QAction(QIcon(fileIcon),'Open new file',self)
        b_newfile.triggered.connect(self.open_newfile)
        b_existfile = QAction('Open exist file',self)
        b_existfile.triggered.connect(self.open_exist_file)     
        b_save = QAction(QIcon(saveIcon),'Save',self)
        b_save.triggered.connect(self.df_save)
        b_restart = QAction(QIcon(restartIcon),'Restart',self)
        b_restart.triggered.connect(self.msg_obj)
        b_exit = QAction(QIcon(exitIcon), ' &Quit', self)
        b_exit.triggered.connect(self.close)
        b_exit.setShortcut('Ctrl+Q')
        b_exit.setStatusTip('Exit application')
        self.statusBar()  
        fileMenu.addAction(b_newfile)
        fileMenu.addAction(b_existfile)
        fileMenu.addSeparator()
        fileMenu.addAction(b_save)
        fileMenu.addSeparator()
        fileMenu.addAction(b_restart)
        fileMenu.addAction(b_exit)
        
        editMenu = menubar.addMenu('Edit')
        self.b_undo = QAction(QIcon(undoIcon),'Undo last action',self)
        self.b_undo.triggered.connect(self.undo)
        self.add_roi = QAction('Add ROI',self)
        self.add_roi.triggered.connect(self.addROI)
        
        self.b_delet = QAction('Delete ROI',self)
        self.b_delet.setDisabled(True)
        self.b_delet.triggered.connect(self.delet_roi)

        self.b_edit_rois = QAction("Edit ROI's",self)
        self.b_edit_rois.setDisabled(True)
        #b_edit_rois.triggered.connect(self.edit_rois)
        self.b_edit_vector = QAction('Edit velocity vector',self)
        self.b_edit_vector.setDisabled(True)
        #b_edit_vector.triggered.connect(self.edit_v)
        self.show_roi_info = QAction("Show ROI's Properties",self)
        #self.show_roi_info.setDisabled(True)
        self.show_roi_info.triggered.connect(self.rois_details)
    
        editMenu.addAction(self.show_roi_info)
        editMenu.addAction(self.b_undo)
        editMenu.addAction(self.add_roi)
        editMenu.addSeparator()
        editMenu.addAction(self.b_delet)
        
        editMenu.addAction(self.b_edit_rois)
        editMenu.addAction(self.b_edit_vector)
        
        helpMenu = menubar.addMenu('Help')
        b_readme = QAction(QIcon(readmeIcon),'READ ME',self)
        #b_readme.triggered.connect(self.readme)
        helpMenu.addAction(b_readme)
        
        "left Dock Widget"
        self.roiItems = QDockWidget("ROI'S",self)
        self.listroi = QListWidget()
        self.listroi.itemDoubleClicked.connect(self.itemD_clicked)

        self.roiItems.setMaximumWidth(150)
        self.roiItems.setWidget(self.listroi)
        self.addDockWidget(Qt.RightDockWidgetArea, self.roiItems)
        
        self.scaninfo = QDockWidget("Scan info",self)
        self.scaninfo.setMaximumWidth(150)
        self.scanwidget = QWidget()
        self.scaninfolist = QFormLayout()
        
        self.editbtn = QPushButton("Edit",self.scanwidget)
        self.editbtn.move(20,120)
        self.editbtn.clicked.connect(self.edit_info_mode)
        
        self.donedit = QPushButton("Save",self.scanwidget)
        self.donedit.move(20,160)
        self.donedit.setEnabled(False)
        self.donedit.clicked.connect(self.done_edit)
        
        self.dx_lb = QLabel('dx')
        self.dx_text = QLineEdit()
        #self.dx_text.setText('0.07e-6')
        self.dx_text.setEnabled(False)
        
        self.fline_lb =QLabel ('fline')
        self.fline_text = QLineEdit()
        
        
        self.fline_text.setEnabled(False)
        
        self.filename_lb = QLabel('Flie Name')
        self.filename_text = QLineEdit()
        self.filename_text.setEnabled(False)
        

        self.scaninfolist.addRow(self.filename_lb,self.filename_text)
        self.scaninfolist.addRow(self.fline_lb,self.fline_text)
        self.scaninfolist.addRow(self.dx_lb,self.dx_text)
        
        self.scanwidget.setLayout(self.scaninfolist)
        self.scaninfo.setWidget(self.scanwidget)
            
        self.addDockWidget(Qt.RightDockWidgetArea, self.scaninfo)
        
        "Image part"
        self.imageobj = Imageobj()
        self.setCentralWidget(self.imageobj)
        
        "tools bar"
        self.roiSELbtn = QAction('1. Select ROI',self)
        self.roiSELbtn.triggered.connect(self.select_roi)
        self.roiSELbtn.setVisible(True)
        self.roiSELbtn.setEnabled(False)
 
        self.vecSELbtn = QAction('2. Mark vector',self)
        self.vecSELbtn.triggered.connect(self.select_vec)
        self.vecSELbtn.setVisible(True)
        self.vecSELbtn.setEnabled(False)

        self.approvebtn = QAction('3. Approve ROI',self)
        self.approvebtn.triggered.connect(self.type_setting_window)
        self.approvebtn.setVisible(True)
        self.approvebtn.setEnabled(False)        
        
        self.toolbar = self.addToolBar('My ToolBar')
        self.toolbar.addAction(self.roiSELbtn)        
        self.toolbar.addAction(self.vecSELbtn)
        self.toolbar.addAction(self.approvebtn)
        
        "primary window"
        self.setWindowIcon(QIcon(primaryIcon))
        self.setWindowTitle("Create Data Base")
        self.showMaximized()
        self.show()
        
        
        "need to build this window, so the user will able to see simultaneously the db"
    def rois_details(self):
        global df,new_win
        #print (df)
        new_win = details_window.details_win(df)
        new_win.show()
        #new_win = welcom_win.welcom()
        #new_win.show()
        #roi_detaile = details_window.details_window()
        #roi_detaile.show()
        
    def closeEvent(self,event):
        """Generate 'question' dialog on clicking 'X' button in title bar.

        Reimplement the closeEvent() event handler to include a 'Question'
        dialog with options on how to proceed - Save, Close, Cancel buttons
        """
        reply = QMessageBox.question(
            self, "Message",
            "Are you sure you want to quit? Any unsaved work will be lost.",
            QMessageBox.Save | QMessageBox.Close | QMessageBox.Cancel,
            QMessageBox.Save)
        
        if reply == QMessageBox.Close:
            event.accept()
        elif reply == QMessageBox.Cancel:
            if type(event)==bool:
                pass
            else:
                event.ignore()
        else:
            self.df_save()
                    
            

    def keyPressEvent(self, event):
        """Close application from escape key.

        results in QMessageBox dialog from closeEvent, good but how/why?
        """
        if event.key() == Qt.Key_Escape:
            self.close()
        
    def create_DataFrame(self):
        global df,Vascular_types
        df = pd.DataFrame(columns = ['ID','Status','Position','gamma','gamma_position','dx','Tline','Vessel_Type'])
        Vascular_types= []
        #key= "db_path"
        #if not key in file_data:
        #    db_fileName= "DB.json"
        #   db_path = results_dir+'\\'+ db_fileName
        #    file_data["db_path"]=db_path
        
    def collect_metadata(self):
        global file_metadata,file_data

        if bool(file_metadata):
            file_data["bidirectional"]= file_metadata["SI.hScan2D.bidirectional"]
            file_data["Tline"]=file_metadata["SI.hRoiManager.linePeriod"]
            file_data["dt_frame"]= file_metadata["SI.hRoiManager.scanFramePeriod"]
            '''
            file_data["sample_coord"]=file_metadata["SI.hRoiManager.imagingFovUm"]
            image_coord = file_metadata["SI.hRoiManager.imagingFovUm"]
            imageX_size = (image_coord[2][0]-image_coord[0][0]) #*(10**-6)
            imageX_size= float("%.9f" % imageX_size)
            pixel_size = imageX_size/file_data["lines"]
            '''
            file_data["lines"]=file_metadata["SI.hRoiManager.linesPerFrame"]
            zoom_factor = file_metadata["SI.hRoiManager.scanZoomFactor"]
            file_data["zoom_factor"]=zoom_factor
            if zoom_factor==5:
                pixel_size = 0.4 #um
            elif zoom_factor ==4:
                pixel_size = 0.5  #um
            file_data["dx"]=pixel_size
            #adding data to interface
            fline = 1/file_data["Tline"]
            file_data["fline"]=fline
            
            self.fline_text.setText(str("%.2f" % fline))
            self.filename_text.setText(file_data["fileName"])
            self.dx_text.setText(str(pixel_size))
        else:
            file_data["Tline"]=1
            file_data["dx"] =0.4
            fline = 1000
            file_data["fline"]=fline
            self.fline_text.setText(str(fline))
            self.filename_text.setText(file_data["fileName"])
            self.dx_text.setText(str(file_data["dx"]))
            
    def open_newfile(self,filePath=""):
        global file_metadata,file_data
        if self.imageobj.hasImage(): #clean window
            self.restart("new")
        
        if os.path.isfile(filePath):
            filepath = filePath
        else:
            findfile= QFileDialog.getOpenFileName(self, 'open file')
            filepath = findfile[0]
        file_data["filePath"]= filepath            
        # create folder name "results"   
        directory=os.path.join(self.fileDir, 'results')             
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        fileName=filepath.split('/')[-1]
        fileType = fileName[len(fileName)-3:len(fileName)]
        file_data["fileType"]=fileType
        fileName=fileName[0:len(fileName)-4]
        file_data["fileName"]= fileName        
        #create folder inside results neam "file name_results"
        res_folderName=fileName+'_results'
        results_dir = 'results\\'+ res_folderName
        results_dir = os.path.join(self.fileDir, results_dir)
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
        file_data["results_dir"]=results_dir  
        db_path = results_dir + "\\DB.json"
        file_data["db_path"]=db_path
        im2show_path = results_dir+ "\\im2show.png"
        file_data["im2show_path"]=im2show_path
        metadata_path = results_dir + "\\metadata.json"
        file_data["metadata_path"]=metadata_path
        if len(filepath) and os.path.isfile(filepath):
            file_metadata=self.imageobj.Extract_image_and_metadata(file_data)
            image = QImage(im2show_path)
            self.imageobj.setImage(image)
        if self.imageobj.hasImage():
             self.roiSELbtn.setEnabled(True)
        self.collect_metadata()
        self.create_DataFrame()
          
    def open_exist_file(self):
        global df, file_metadata,file_data
        if self.imageobj.hasImage():
            self.restart("new")
            
        findfile= QFileDialog.getOpenFileName(self, 'open file')
        filepath = findfile[0]
        file_data["filePath"]= filepath 
        
        fileName=filepath.split('/')[-1]
        fileType = fileName[len(fileName)-3:len(fileName)]
        file_data["fileType"]=fileType
        fileName=fileName[0:len(fileName)-4]
        file_data["fileName"]= fileName  
        
        folder_directory= 'results\\'+fileName+'_results'
        folder_directory = os.path.join(self.fileDir, folder_directory)
        file_data["results_dir"]=folder_directory
        
        im2show_path = folder_directory + '\\im2show.png'
        file_data["im2show_path"]=im2show_path
        db_path = folder_directory +'\\DB.json'
        file_data["db_path"]=db_path
        metadata_path = folder_directory + '\\metadata.json' 
        file_data["metadata_path"]=metadata_path
        
        Files_required = [os.path.exists(folder_directory),os.path.exists(im2show_path)
        ,os.path.exists(db_path),os.path.exists(metadata_path)]
        if all(Files_required):
            with open(metadata_path, 'r') as fp:
                file_metadata = json.load(fp) 
            self.collect_metadata()
            image = QImage(im2show_path)
            self.imageobj.setImage(image)
            df = pd.read_json(db_path)
            items_list = ['ROI '+str(i) for i in range(1,df.index.max()+2)]
            self.listroi.addItems(items_list)
            rois_pos_list = list(df['Position'])
            self.imageobj.create_fromDB(rois_pos_list,"rois")
            vec_pos_list = list(df['gamma_position'])
            self.imageobj.create_fromDB(vec_pos_list,"vector")
            

        else:
            print ("some files required missing")
            print (os.path.exists(folder_directory))
            print (os.path.exists(im2show_path))
            print (os.path.exists(db_path))
            print (os.path.exists(metadata_path))
            print ("open new file")
            self.open_newfile()
        #print("folder exist:",os.path.exists(folder_directory))
        #print(folder_directory)
        #print("im2show exist:",os.path.exists(image2show_path))
        #print(image2show_path)
        #print("db exist:",os.path.exists(db_path))
        #print(db_path)
        #print ("metadata exist:",os.path.exists(metadata_path))
        #print(metadata_path)
    def done_edit(self):
        global file_data
        print ("done edit")
        self.fline_text.setEnabled(False)
        fline = self.fline_text.text()
        self.filename_text.setEnabled(False)
        fileName = self.filename_text.text()
        self.dx_text.setEnabled(False)
        dx = self.dx_text.text()
        self.donedit.setEnabled(False)
        if not fline == str("%.2f" % file_data["fline"]):
            file_data["fline"]=float(fline)
            tline = 1/float(fline)
            df["Tline"]=tline
            file_data["Tline"]=tline
            print ("fline has changed and saved jjjj")
        if not fileName == file_data["fileName"]:
            db_old_path = file_data["db_path"]
            new_db_path = db_old_path[:len(db_old_path)-7] + fileName +"_"+ db_old_path[len(db_old_path)-7:]
            file_data["db_path"]=new_db_path
            print ("changing file Name will cause errors")
        if not dx == str(file_data["dx"]):
            file_data["dx"]=float(dx)
            df["dx"]=float(dx)
            print ("dx has changed and saved")
        
    def edit_info_mode(self):
        self.fline_text.setEnabled(True)
        self.filename_text.setEnabled(True)
        self.dx_text.setEnabled(True)
        self.donedit.setEnabled(True)
        
   
    def select_roi(self):
        if self.imageobj.hasImage():
            self.imageobj.helper_bool2=False
            self.imageobj.helper_bool=True
            self.roiSELbtn.setEnabled(False)
            self.vecSELbtn.setEnabled(True)
        
    def select_vec(self):
        self.imageobj.helper_bool=False
        self.imageobj.helper_bool2=True
        self.vecSELbtn.setEnabled(False)
        self.approvebtn.setEnabled(True)
        
    def find_gamma(self,start_point,end_point):
        dx = end_point[0]-start_point[0]
        dy = end_point[1]-start_point[1]
        gamma = abs(math.degrees(math.atan(dy/dx)))
        if dy < 0:
            gamma = gamma*(-1)
        return gamma
        
    def approve_roi(self):
        global df
        print ("approval")
        #vessel_type = self.type_setting_window()
        
        self.imageobj.helper_bool2=False
        self.imageobj.helper_bool=False
        self.approvebtn.setEnabled(False)
        self.roiSELbtn.setEnabled(True)

        points_rect,v_start,v_end = self.imageobj.approve_obj()
        points_rect = points_rect.getRect()
        v_start=(v_start.x(),v_start.y())
        v_end=(v_end.x(),v_end.y())
        gamma =self.find_gamma(v_start,v_end)
        dx=file_data["dx"]
        Tline=file_data["Tline"]
        status = '0'

        roi_index = len(df.index)
        if roi_index==0:
            roi_ID=1
        else:
            roi_ID = df.at[roi_index-1,"ID"] + 1
        vessel_type = Vascular_types[roi_index]
        df.at[roi_index,"ID"]=int(roi_ID)
        df.at[roi_index,"Position"]= points_rect
        df.at[roi_index,"Status"]=status
        df.at[roi_index,"gamma"]=gamma
        df.at[roi_index,'gamma_position']=v_start,v_end
        df.at[roi_index,"dx"]=dx
        df.at[roi_index,"Tline"]=Tline
        df.at[roi_index,"Vessel_Type"]= vessel_type

        name = "ROI " +str(roi_ID)
        print(name)
        item = QListWidgetItem(name)
        self.listroi.addItem(item)
        
    def type_setting_window(self):
        
        self.type_pop = QDialog(self)
        main_layout = QFormLayout()
        text = QLabel("Define the type of blood vessels in this ROI:")
        self.options = QComboBox()
        options_list = ["---","Pial_Artery","Pial_Vein","PA","PV","Cap"
                        ,"PA_diamOnly","PV_diamOnly"]
        self.options.addItems(options_list)
        ok_btn = QPushButton("OK")
        
        main_layout.addRow(text)
        main_layout.addRow(self.options)
        self.type_pop.setWindowTitle("Vascular Type classification")
        main_layout.addRow(ok_btn)
        self.type_pop.setLayout(main_layout)
        ok_btn.clicked.connect(self.type_setting_result)
        self.type_pop.show()

    
    def type_setting_result(self):
        vessel_type = self.options.currentText()
        self.type_pop.close()
        Vascular_types.append(vessel_type)
        #print (vessel_type, "from results function")
        file_data["vessels_types"]=Vascular_types
        self.approve_roi()
      
    def undo(self):
        self.imageobj.helper_bool2=False
        self.imageobj.helper_bool=False
        self.approvebtn.setEnabled(False)
        self.vecSELbtn.setEnabled(False)
        self.roiSELbtn.setEnabled(True)
        self.imageobj.scene.removeItem(self.imageobj.rect)
        self.imageobj.scene.removeItem(self.imageobj.linegroup)
        
    def addROI(self):
        self.roiSELbtn.setEnabled(True)

        
    def df_save(self):
        fileName = file_data["fileName"]
        filePath = file_data["filePath"]
        db_path =file_data["db_path"]
        for i in range(len(df.index)):
            df.at[i,"fileName"]=fileName
            df.at[i,"filePath"]=filePath

        df.to_json(db_path)
        print ('db saved at path:')
        print(db_path)
        
    def itemD_clicked(self,item):
        self.b_delet.setDisabled(False)
        self.b_edit_rois.setDisabled(False)
        self.b_edit_vector.setDisabled(False)
        num_item = int(item.text()[4])
        self.imageobj.mark_item(num_item-1)
        
        #print ("num item double clicked:" ,num_item)
        
    def update_objectes(self):
        global df
        numberOfROIs = len(df.index)
        i = range(numberOfROIs)
        df["ID"]=list(int(k+1) for k in i)
        for k in i:
            item = self.listroi.item(k)
            item.setText(item.text()[:4]+str(k+1))
            
    def delet_roi(self):
        global df
        item =self.listroi.currentItem()
        name = item.text()
        index = int(name[4])-1
        df=df.drop(df.index[index])
        df=df.reset_index(drop=True)
        self.listroi.takeItem(index)
        self.imageobj.delete_roi(index)
        self.update_objectes()
    
    def msgbtn(self,i):
        ans = i.text()
        print(ans)
        if ans=='Save':
            self.df_save()
            self.restart("clear")
        elif ans == 'Cancel':
            pass
        elif ans =='Discard':
            self.restart("clear")
        
    def msg_obj(self):
        global file_data
        if not df.empty:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Question)
            msg.setText("The document has been modified.")
            msg.setInformativeText("Do you want to save your changes?")
            msg.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            msg.setDefaultButton(QMessageBox.Save)
            msg.buttonClicked.connect(self.msgbtn)
            msg.exec_()
        else:
            self.restart("clear")
        
    def restart(self,command=""):
        global file_data
        if command == "clear":
            self.listroi.clear()
            filePath = file_data["filePath"]
            self.open_newfile(filePath)
            self.imageobj.restart_obj()
        elif command=="new":
            self.listroi.clear()
            self.imageobj.restart_obj()
            file_data ={}
            


if __name__ == '__main__':  
    file_data={}
    app = QCoreApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    else:
        print('QApplication instance already exists: %s' % str(app))
    ex = window()
    ex.show()
    app.exec_()
    
