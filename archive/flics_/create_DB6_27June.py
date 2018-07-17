# -*- coding: utf-8 -*-
"""
Created on Wed Jun 27 15:08:22 2018

@author: bar23
"""

import sys
from PyQt5.QtWidgets import (QMainWindow, QTextEdit, QAction, QApplication,QFileDialog,
                             QPushButton,QLabel,QGridLayout,QWidget,QDockWidget,QListWidget,
                             QListWidgetItem, QVBoxLayout,QHBoxLayout,QLineEdit,QComboBox,
                             QLayout,QFormLayout,QMessageBox,qApp,QDialog,QTableView,QCheckBox)

from PyQt5.QtGui import (QIcon,QImage)
from PyQt5.QtCore import (QCoreApplication,Qt)
import json
import os 
import tifffile
import numpy as np
from PIL import Image

from imageObj6_27June import (Imageobj)
import math

class window(QMainWindow):
    
    def __init__(self):
        super(window,self).__init__()
        self.initUI()
        
    def initUI(self):
        
        """menu bar part
         The menu bar as three main options: 
            (1) file:
                (1.1) open 
                (1.3) save
                (1.4) restart
                (1.5) Quit

        """
        
        #icon's 
        self.fileDir = os.path.dirname(os.path.realpath('__file__'))
        openIcon = os.path.join(self.fileDir, 'icon/new_file.png')
        saveIcon = os.path.join(self.fileDir,'icon/save.png')
        restartIcon = os.path.join(self.fileDir, 'icon/restart.png')
        exitIcon =  os.path.join(self.fileDir, 'icon/exit.png')
        
        menubar=self.menuBar()
        fileMenu = menubar.addMenu('File')        
        # create buttons and connect them to function
        b_open= QAction(QIcon(openIcon),'Open',self)
        b_open.triggered.connect(self.openfile)
        b_save = QAction(QIcon(saveIcon),'Save',self)
        b_save.triggered.connect(self.database_save)
        b_restart = QAction(QIcon(restartIcon),'Restart',self)
        b_restart.triggered.connect(self.restart)
        b_exit = QAction(QIcon(exitIcon), ' &Quit', self)
        b_exit.triggered.connect(self.close)
        fileinfobtn = QAction("File info",self)
        fileinfobtn.triggered.connect(self.show_file_info)
        
        # create menu bar and add buttons
        fileMenu.addAction(b_open)
        fileMenu.addAction(fileinfobtn)
        fileMenu.addSeparator()
        fileMenu.addAction(b_save)
        fileMenu.addSeparator()
        fileMenu.addAction(b_restart)
        fileMenu.addAction(b_exit)
        
        "cental image part"
        self.imageobj = Imageobj()
        self.setCentralWidget(self.imageobj)
        
        "tool bar"
        self.toolbar = self.addToolBar('ToolBar')
        addIcon = os.path.join(self.fileDir, 'icon/add.png')
        self.btnNewroi = QAction(QIcon(addIcon),'New ROI',self)
        self.btnNewroi.triggered.connect(self.addroi)
        self.toolbar.addAction(self.btnNewroi)
        self.roiSELbtn = QAction('1.ROI Position',self)
        self.roiSELbtn.triggered.connect(self.select_roi)
        self.roiSELbtn.setVisible(False)
        self.roiSELbtn.setEnabled(False)
        self.toolbar.addAction(self.roiSELbtn)
        self.vecSELbtn = QAction('2.Flow direction',self)
        self.vecSELbtn.triggered.connect(self.mark_flowdir)
        self.vecSELbtn.setVisible(False)
        self.vecSELbtn.setEnabled(False)
        self.toolbar.addAction(self.vecSELbtn)
        self.diameterSELbtn = QAction('3.Vessel width',self)
        self.diameterSELbtn.triggered.connect(self.mark_diametervec)
        self.diameterSELbtn.setVisible(False)
        self.diameterSELbtn.setEnabled(False)
        self.toolbar.addAction(self.diameterSELbtn)
        self.vesseltypebtn = QAction('4.vessel type',self)
        self.vesseltypebtn.triggered.connect(self.get_vesseltype)
        self.vesseltypebtn.setVisible(False)
        self.vesseltypebtn.setEnabled(False)
        self.toolbar.addAction(self.vesseltypebtn)
        self.stepsButtons = [self.roiSELbtn,self.vecSELbtn,self.diameterSELbtn,self.vesseltypebtn]
        
        delIcon = os.path.join(self.fileDir,'icon/delete.png')
        self.btndelete = QAction(QIcon(delIcon),'Delete ROI',self)
        self.btndelete.triggered.connect(self.deleteroi)
        self.btndelete.setVisible(False)
        self.toolbar.addAction(self.btndelete)
        
        "primary window"
        primaryIcon = os.path.join(self.fileDir, 'icon/database.png')
        self.setWindowIcon(QIcon(primaryIcon))
        self.setWindowTitle("Create Data Base")
        
        
        "vessel type dialog"
        self.type_pop = QDialog(self)
        main_layout = QFormLayout()
        text = QLabel("Define the type of blood vessels in this ROI:")
        self.options = QComboBox()
        options_list = ["---","Pial_Artery","Pial_Vein","PA","PV","Cap"
                        ,"PA_diamOnly","PV_diamOnly"]
        self.options.addItems(options_list)
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.vesseltype_result)
        main_layout.addRow(text)
        main_layout.addRow(self.options)
        self.type_pop.setWindowTitle("Vascular Type classification")
        main_layout.addRow(ok_btn)
        self.type_pop.setLayout(main_layout)
        
        "file info dialog"
        self.fileinfoWindow = QDialog(self)
        self.fileinfoWindow.setWindowTitle("File & scan properties")
        self.fileinfoWindow.setGeometry(100,100,300,300)
        self.scaninfowidget = QWidget(self.fileinfoWindow)
        self.scaninfolist = QFormLayout(self.scaninfowidget)
        
        self.filename_lb = QLabel('Flie Name: ')
        self.filename_text = QLineEdit()
        self.filename_text.setEnabled(True)
        self.scaninfolist.addRow(self.filename_lb,self.filename_text)
        self.dx_lb = QLabel('dx (pixel size in um): ')
        self.dx_text = QLineEdit()
        self.dx_text.setEnabled(True)
        self.scaninfolist.addRow(self.dx_lb,self.dx_text)
        self.w_lb = QLabel('W (lazer beam waist): ')
        self.w_text = QLineEdit()
        self.w_text.setEnabled(True)
        self.scaninfolist.addRow(self.w_lb,self.w_text)
        self.s_lb = QLabel('Photon excitation (1 or 2): ')
        self.s_text =QLineEdit()
        self.s_text.setEnabled(True)
        self.scaninfolist.addRow(self.s_lb,self.s_text)
        self.tau_lb = QLabel("Tau line: ")
        self.tau_text = QLineEdit()
        self.tau_text.setEnabled(True)
        self.scaninfolist.addRow(self.tau_lb,self.tau_text)
        self.frames_lb = QLabel("Frames in file: ")
        self.frames_text = QLineEdit()
        self.frames_text.setEnabled(True)
        self.scaninfolist.addRow(self.frames_lb,self.frames_text)
        self.dt_lb = QLabel("Time between samples: ")
        self.dt_text = QLineEdit()
        self.dt_text.setEnabled(True)
        self.scaninfolist.addRow(self.dt_lb,self.dt_text)
        self.rois_lb = QLabel("ROIs amount: ")
        self.rois_text = QLineEdit()
        self.rois_text.setEnabled(False)
        self.scaninfolist.addRow(self.rois_lb,self.rois_text)
        self.a2_lb = QLabel("radius of the flowing objects: ")
        self.a2_text= QLineEdit()
        self.a2_text.setEnabled(True)
        self.scaninfolist.addRow(self.a2_lb,self.a2_text)
        self.donedit = QPushButton("OK")
        self.donedit.setEnabled(True)
        self.donedit.clicked.connect(self.user_file_info)
        self.scaninfolist.addRow(self.donedit)
        
        "right Dock Widget"
        self.roiItems = QDockWidget("ROI'S",self)
        self.listroi = QListWidget()
        self.listroi.itemDoubleClicked.connect(self.itemD_clicked)
        self.roiItems.setWidget(self.listroi)
        self.addDockWidget(Qt.RightDockWidgetArea, self.roiItems)
        
        self.roiprop = QDockWidget("ROI Properties",self)
        self.roiprop.setMaximumWidth(150)
        self.roipropwidget = QWidget()
        self.roiproplayout = QFormLayout()
        self.label_roiID = QLabel('ROI')  
        self.label_roipos = QLabel('ROI Position:')
        self.label_roisize = QLabel('ROI size:')
        self.label_gamma = QLabel('Gamma[rad]:')
        self.label_diameter = QLabel('Diameter:')
        self.label_roistatus = QLabel('ROI status:')
        self.label_roivesseltype = QLabel('Vessel Type:')

        self.roiproplayout.addRow(self.label_roiID)
        self.roiproplayout.addRow(self.label_roipos)
        self.roiproplayout.addRow(self.label_roisize)
        self.roiproplayout.addRow(self.label_gamma)
        self.roiproplayout.addRow(self.label_diameter)
        self.roiproplayout.addRow(self.label_roistatus)
        self.roiproplayout.addRow(self.label_roivesseltype)
        
        self.roipropwidget.setLayout(self.roiproplayout)
        self.roiprop.setWidget(self.roipropwidget)
        
        self.addDockWidget(Qt.RightDockWidgetArea, self.roiprop)
        
        self.showMaximized()
        
    def openfile(self):
        findfile = QFileDialog.getOpenFileName(self, 'open file')
        filepath = findfile[0]
        self.paths_helper = self.paths_construct(filepath)
        if os.path.exists(self.paths_helper['im2show_path']): #file im2show.png is exist 
           image = QImage(self.paths_helper['im2show_path'])
           self.imageobj.setImage(image)
        else: # file im2show.png not exist
            im2show = self.image_construct(filepath)
            try:
                im2show.save(self.paths_helper['im2show_path'])
            except OSError:
                im2show = self.im2show.convert(mode='I')
                im2show.save(self.paths_helper['im2show_path'])
            self.image = QImage(self.paths_helper['im2show_path'])
            self.imageobj.setImage(self.image)
                    
        if os.path.exists(self.paths_helper['database_path']): # if the file already have db 
            with open(self.paths_helper['database_path'], 'r') as fp:
                self.file_database = json.load(fp)
            self.numberROIs = self.file_database['NumberROIs']
            roi_pos =[]
            gamma_pos =[]
            diameter_pos =[]
            for i in range(1,self.numberROIs+1):
                roi_pos.append(self.file_database["ROI_position"][str(i)])
                gamma_pos.append(self.file_database["Gamma_mark"][str(i)])
                diameter_pos.append(self.file_database["diameter_mark"][str(i)])
                name = "ROI " +str(i)
                item = QListWidgetItem(name)
                self.listroi.addItem(item)
            self.imageobj.create_fromDB(roi_pos,"rois")
            self.imageobj.create_fromDB(gamma_pos,"vector1")
            self.imageobj.create_fromDB(diameter_pos,"vector2")
                
        else:
            self.restart_database()
            with tifffile.TiffFile(filepath) as tif:
                self.file_metadata = tif.scanimage_metadata
            if self.file_metadata is None:
                print ("tiff file does not contain metadata")
                self.file_database['metadata_exists'] = False
                self.file_database['bidirectional'] = False
                self.file_database['frames_amount'] = 0  
            else:
                self.file_database['metadata_exists'] = True
                self.file_database['bidirectional'] = self.file_metadata['FrameData']["SI.hScan2D.bidirectional"]
                self.file_database['frames_amount'] = self.file_metadata['FrameData']['SI.hStackManager.framesPerSlice'] 
                self.get_file_info()
        self.show_file_info()
        
    
    def restart_database(self):
        self.file_database  = {}
        self.file_database["Gamma"]={}
        self.file_database["ROI_position"]={}
        self.file_database["Vessel_Type"]={}
        self.file_database["Gamma_mark"] ={}
        self.file_database["diameter_mark"] ={}
        self.file_database["Status"]={}
        self.numberROIs = 0
        self.file_database["NumberROIs"]= self.numberROIs
        self.file_database["file_Path"]= self.paths_helper["filepath"]
        self.file_database["im2show_path"]=self.paths_helper["im2show_path"]
        self.file_database["filename"]=self.paths_helper["filename"]
        #self.file_database["metadata_path"]= self.paths_helper["metadata_path"]
        #self.get_file_info()
        #self.full_file_info = False
    def restart(self):
        self.listroi.clear()
        self.imageobj.restart_obj()
        self.restart_database()
        self.openfile()
    def paths_construct(self,filepath):
        results_folder_path=os.path.join(self.fileDir, 'results')# main results folder (for all files to come)
        if not os.path.exists(results_folder_path):
            os.makedirs(results_folder_path)      
        paths_helper ={} # dict Contains all the necessary paths
        fileName = filepath.split('/')[-1]
        fileName=fileName[0:len(fileName)-4]
        file_results_folder_path = os.path.join(results_folder_path, fileName)
        if not os.path.exists(file_results_folder_path):
            os.makedirs(file_results_folder_path)         
        database_path = os.path.join(file_results_folder_path,'database.json')
        im2show_path = os.path.join(file_results_folder_path,'im2show.png')
        #metadata_path = os.path.join(file_results_folder_path,'metadata.json')
        paths_helper['filepath'] = filepath
        paths_helper['main_resultsFolder_path'] = results_folder_path
        paths_helper['filename'] = fileName
        paths_helper['results_path'] = file_results_folder_path
        paths_helper['database_path'] = database_path
        paths_helper['im2show_path'] = im2show_path
        #paths_helper['metadata_path'] = metadata_path
        return paths_helper
        
            
    def image_construct(self,filepath):
        print ("image construct..")
        tif_original = tifffile.imread(filepath)
        with tifffile.TiffFile(filepath) as tif:
            file_metadata = tif.scanimage_metadata
        if file_metadata is None:
            print ("tiff file does not contain metadata")
            self.file_database['metadata_exists'] = False
            self.file_database['bidirectional'] = False
            self.file_database['frames_amount'] = 0  
        else:
            self.file_database['metadata_exists'] = True
            self.file_database['bidirectional'] = file_metadata['FrameData']["SI.hScan2D.bidirectional"]
            self.file_database['frames_amount'] = file_metadata['FrameData']['SI.hStackManager.framesPerSlice'] 
            self.get_file_info()
        if self.file_database['frames_amount']==0:
            full_image = tif_original.copy()
        else:
            full_image = tif_original[1].copy()
        if self.file_database['bidirectional']:
            image_original_size = full_image.shape
            image = np.zeros([int(image_original_size[0]/2),image_original_size[1]])
            for r in range(0,int(image_original_size[0]/2)):
                image[r,:]= full_image[r*2,:]
        else:
            image = full_image.copy()       
        im2show=Image.fromarray(image)
        return im2show
    
    def database_save(self):
        self.full_file_info = self.show_file_info()   
        with open(self.paths_helper['database_path'], 'w') as fp:
            json.dump(self.file_database, fp)
            
    def addroi(self):
        if self.imageobj.hasImage():
            self.imageobj.helper_bool2=False
            self.imageobj.helper_bool3=False
            self.imageobj.helper_bool=True
            self.roiSELbtn.setVisible(True)
            self.roiSELbtn.setEnabled(True)
            self.numberROIs = self.numberROIs +1
            self.btnNewroi.setEnabled(False)
            
    def deleteroi(self):
        item =self.listroi.currentItem()
        name = item.text()
        ROI_ID = int(name[4])
        self.imageobj.delete_roi(ROI_ID-1)
        self.file_database["ROI_position"].pop(str(ROI_ID), None)
        self.file_database["Gamma_mark"].pop(str(ROI_ID), None)
        self.file_database["diameter_mark"].pop(str(ROI_ID), None)
        self.file_database["Gamma"].pop(str(ROI_ID), None)
        self.file_database["Vessel_Type"].pop(str(ROI_ID), None)
        self.file_database["Status"].pop(str(ROI_ID), None)
        if self.numberROIs>ROI_ID:
            for k in range(ROI_ID+1,self.numberROIs+1):
                self.file_database["ROI_position"][str(k-1)]=self.file_database["ROI_position"].pop(str(k), None)
                self.file_database["Gamma_mark"][str(k-1)]=self.file_database["Gamma_mark"].pop(str(k), None)
                self.file_database["diameter_mark"][str(k-1)]=self.file_database["diameter_mark"].pop(str(k), None)
                self.file_database["Gamma"][str(k-1)]=self.file_database["Gamma"].pop(str(k), None)
                self.file_database["Vessel_Type"][str(k-1)]=self.file_database["Vessel_Type"].pop(str(k), None)   
                self.file_database["Status"][str(k-1)]=self.file_database["Status"].pop(str(k), None)
        self.numberROIs = self.numberROIs -1
        self.file_database["NumberROIs"]=self.numberROIs
        self.listroi.clear()
        for num in range(1,self.numberROIs+1):
            name = "ROI " +str(num)
            item = QListWidgetItem(name)
            self.listroi.addItem(item)
        self.btndelete.setVisible(False)
    def select_roi(self):
        rect = self.imageobj.roi_pos() #self.rect = [x,y,w,h]
        if all(rect)==0:
            self.userMessage("mark the vessel ROI with the mouse.")
            return
        self.file_database["ROI_position"][self.numberROIs]=rect
        self.imageobj.helper_bool2=True
        self.imageobj.helper_bool=False
        self.imageobj.helper_bool3=False
        self.roiSELbtn.setEnabled(False)
        self.vecSELbtn.setVisible(True)
        self.vecSELbtn.setEnabled(True)
         
        
    def mark_flowdir(self):
        self.flowvec = self.imageobj.line_pos()
        if all(self.flowvec)==0:
            self.userMessage("mark one of the vessel boundary.")
            return
        self.imageobj.helper_bool2=False
        self.imageobj.helper_bool=False
        self.imageobj.helper_bool3=True
        self.vecSELbtn.setEnabled(False) 
        self.diameterSELbtn.setVisible(True)
        self.diameterSELbtn.setEnabled(True)
        dx = self.flowvec[0]-self.flowvec[2]
        dy = self.flowvec[1]-self.flowvec[3]
        gamma = abs(math.degrees(math.atan(dy/dx)))
        if dy < 0:
            gamma = gamma*(-1)
        self.gamma = math.radians(gamma)
        self.file_database["Gamma"][self.numberROIs]=self.gamma
        self.file_database["Gamma_mark"][self.numberROIs]=self.flowvec
        
    def mark_diametervec(self):
        self.diametervec = self.imageobj.line_pos()
        if all(self.diametervec)==0 and self.diametervec==self.file_database["diameter_mark"][self.numberROIs-1]:
            self.userMessage("Mark a vertical line showing the width of the blood vessels")
            return
        self.imageobj.helper_bool3=False
        self.diameterSELbtn.setEnabled(False)  
        self.vesseltypebtn.setVisible(True)
        self.vesseltypebtn.setEnabled(True)
        self.file_database["diameter_mark"][self.numberROIs]=self.diametervec
        
    def get_vesseltype(self):
        self.type_pop.show()
        self.vesseltypebtn.setEnabled(False)
        
    def vesseltype_result(self):
        vessel_type = self.options.currentText()
        self.type_pop.close()
        self.roivesselType = vessel_type
        self.file_database["Vessel_Type"][self.numberROIs]=self.roivesselType
        self.file_database["NumberROIs"] = self.numberROIs
        self.file_database["Status"][self.numberROIs]="Unprocessed"
        for btn in self.stepsButtons:
            btn.setVisible(False)
        self.btnNewroi.setEnabled(True)
        self.imageobj.approve_obj()
        name = "ROI " +str(self.numberROIs)
        item = QListWidgetItem(name)
        self.listroi.addItem(item)
            
    def userMessage(self,text):
        msgBox = QMessageBox()
        msgBox.setWindowTitle('Guidance')
        msgBox.setText(text)
        msgBox.exec()
    
    def get_file_info(self):
        self.file_database["tau_line"]=self.file_metadata["FrameData"]["SI.hRoiManager.linePeriod"]
        self.file_database["dt"]=self.file_metadata["FrameData"]["SI.hRoiManager.scanFramePeriod"]
        self.file_database["frames_amount"]=self.file_metadata["FrameData"]["SI.hStackManager.framesPerSlice"]
        
    def show_file_info(self):
        self.fileinfoWindow.show()
        self.filename_text.setText(self.file_database["filename"])
        self.tau_text.setText(str(self.file_database["tau_line"]))
        self.frames_text.setText(str(self.file_database["frames_amount"]))
        self.dt_text.setText(str(self.file_database["dt"]))
        self.rois_text.setText(str(self.file_database["NumberROIs"]))
        self.a2_text.setText(str(39.2701))
        self.s_text.setText(str(1))
        self.w_text.setText(str(0.2))
        self.dx_text.setText(str(0.04))
        self.full_file_info = False

        return self.full_file_info
    
    def user_file_info(self):
        self.file_database["filename"]= self.filename_text.text()
        self.file_database["tau_line"] = float(self.tau_text.text())
        self.file_database["frames_amount"] = int(self.frames_text.text())
        self.file_database["dt"]=float(self.dt_text.text())
        self.file_database["dx"]=float(self.dx_text.text())
        self.file_database["w2"]=float(self.w_text.text())**2
        self.file_database["a2"]=float(self.a2_text.text())
        self.file_database["s"]= int(self.s_text.text())
        self.full_file_info = True
        self.fileinfoWindow.close()
    
    def itemD_clicked(self,item):
        self.btndelete.setVisible(True)
        num_item = int(item.text()[4])
        self.imageobj.mark_item(num_item-1)
        if not self.full_file_info:
            self.show_file_info()
        
        self.label_roiID.setText('ROI ' + str(num_item)) 
        roi_pos =self.file_database["ROI_position"][num_item]
        self.label_roipos.setText('ROI Position: '+str(roi_pos))
        self.label_roisize.setText('ROI size: '+str(roi_pos[2])+'x'+str(roi_pos[3]))
        gamma = self.file_database["Gamma"][num_item]
        self.label_gamma.setText('Gamma[rad]: '+ ("%.2f" % gamma))
        diameter_pos = self.file_database['diameter_mark'][num_item]
        diameter_size = (diameter_pos[2]**2+diameter_pos[3]**2)**0.5
        approx_diameter = diameter_size * float(self.file_database["dx"])
        self.label_diameter.setText('Diameter: '+ ("%.2f" % approx_diameter))
        self.label_roistatus.setText('ROI status: ')
        self.label_roivesseltype.setText('Vessel Type: '+self.file_database["Vessel_Type"][num_item])
        
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
            self.database_save()
                    
            
    def keyPressEvent(self, event):
        """Close application from escape key.

        results in QMessageBox dialog from closeEvent, good but how/why?
        """
        if event.key() == Qt.Key_Escape:
            self.close()

if __name__ == '__main__':  
    app = QCoreApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    else:
        print('QApplication instance already exists: %s' % str(app))
    ex = window()
    ex.show()
    app.exec_()
    