import json
import math
import os
import pandas as pd

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import (QMainWindow, QAction, QFileDialog, QPushButton,
                             QLabel, QWidget, QDockWidget, QListWidget,
                             QListWidgetItem, QLineEdit, QComboBox,
                             QFormLayout, QMessageBox, QDialog)

from .imageObj4 import Imageobj
from .resources import get_icon

file_data = {}
RESULTS_DIR = os.path.abspath('results')


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()

    def initUI(self):
        self.statusBar().showMessage('Ready')

        self.create_actions()
        self.create_menus()
        self.create_left_dock()

        self.image_view = Imageobj()
        self.setCentralWidget(self.image_view)

        self.create_toolbar()

        self.setWindowIcon(get_icon('window'))
        self.setWindowTitle("Create Data Base")
        self.showMaximized()
        self.show()

    def create_actions(self):
        self.new_file_action = QAction(
            parent=self,
            icon=get_icon('new_file'),
            text='New File',
            statusTip='Open a new file...',
            triggered=self.create_new_file,
        )

        self.open_file_action = QAction(
            parent=self,
            text='Open File',
            statusTip='Open a new file...',
            triggered=self.open_file,
        )

        self.save_action = QAction(
            parent=self,
            icon=get_icon('save'),
            text='Save',
            statusTip='Save to file...',
            triggered=self.df_save,
        )

        self.restart_action = QAction(
            parent=self,
            icon=get_icon('restart'),
            text='Restart',
            triggered=self.pop_save_changes_message,
        )

        self.exit_action = QAction(
            parent=self,
            icon=get_icon('exit'),
            text=' &Quit',
            statusTip='Exit application...',
            shortcut='Ctrl+Q',
            triggered=self.close,
        )

        self.undo_action = QAction(
            parent=self,
            icon=get_icon('undo'),
            text='Undo',
            statusTip='Undo last action...',
            shortcut='Ctrl+Z',
            triggered=self.undo,
        )

        self.add_roi_action = QAction(
            parent=self,
            text='Add ROI',
            statusTip='Create a new ROI...',
            shortcut='Ctrl+Shift+N',
            triggered=self.add_roi)

        self.delete_roi_action = QAction(
            parent=self,
            text='Delete ROI',
            statusTip='Delete an existing ROI...',
            shortcut='Ctrl+Del',
            triggered=self.delete_roi,
        )
        self.delete_roi_action.setDisabled(True)

        self.edit_rois_action = QAction(
            parent=self,
            text="Edit ROIs",
            statusTip='Edit an existing ROI definition file...',
            # triggered=self.edit_rois,
        )
        self.edit_rois_action.setDisabled(True)

        self.edit_vector_action = QAction(
            parent=self,
            text='Edit velocity vector',
            statusTip='Edit velocity vector configuration...',
            # triggered=self.edit_v,
        )
        self.edit_vector_action.setDisabled(True)

        self.show_roi_info = QAction(
            parent=self,
            text="Show ROI Properties",
            statusTip='Show the properties of the configured ROIs...',
        )
        # self.show_roi_info.setDisabled(True)

        self.readme_action = QAction(
            parent=self,
            icon=get_icon('readme'),
            text='READ ME',
            # triggered=self.readme,
        )

        # Toolbar actions
        self.select_roi_action = QAction(
            text='Select ROI',
            parent=self,
            triggered=self.select_roi,
        )
        self.select_roi_action.setVisible(True)
        self.select_roi_action.setEnabled(False)

        self.mark_vector_action = QAction(
            text='Mark vector',
            parent=self,
            triggered=self.select_vec,
        )
        self.mark_vector_action.setVisible(True)
        self.mark_vector_action.setEnabled(False)

        self.approve_roi_action = QAction(
            text='Approve ROI',
            parent=self,
            triggered=self.type_setting_window,
        )
        self.approve_roi_action.setVisible(True)
        self.approve_roi_action.setEnabled(False)

    def create_menus(self):
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
        # File menu
        self.file_menu = self.menuBar().addMenu('File')
        self.file_menu.addAction(self.new_file_action)
        self.file_menu.addAction(self.open_file_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.save_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.restart_action)
        self.file_menu.addAction(self.exit_action)

        # Edit menu
        self.edit_menu = self.menuBar().addMenu('Edit')
        self.edit_menu.addAction(self.show_roi_info)
        self.edit_menu.addAction(self.undo_action)
        self.edit_menu.addAction(self.add_roi_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.delete_roi_action)
        self.edit_menu.addAction(self.edit_rois_action)
        self.edit_menu.addAction(self.edit_vector_action)

        # Help menu
        self.help_menu = self.menuBar().addMenu('Help')
        self.help_menu.addAction(self.readme_action)

    def create_scan_info_form(self):
        self.dx_label = QLabel(text='dx')
        self.dx_text = QLineEdit()
        # self.dx_text.setText('0.07e-6')
        self.dx_text.setEnabled(False)

        self.fline_label = QLabel(text='fline')
        self.fline_text = QLineEdit()
        self.fline_text.setEnabled(False)

        self.file_name_label = QLabel(text='File Name')
        self.file_name_text = QLineEdit()
        self.file_name_text.setEnabled(False)

        self.scan_info_list = QFormLayout()
        self.scan_info_list.addRow(self.file_name_label, self.file_name_text)
        self.scan_info_list.addRow(self.fline_label, self.fline_text)
        self.scan_info_list.addRow(self.dx_label, self.dx_text)

    def create_scan_widget(self):
        self.scan_widget = QWidget()

        self.edit_button = QPushButton(text="Edit", parent=self.scan_widget)
        self.edit_button.move(20, 120)
        self.edit_button.clicked.connect(self.edit_info_mode)

        self.save_button = QPushButton(text="Save", parent=self.scan_widget)
        self.save_button.move(20, 160)
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save_rois)

        self.scan_widget.setLayout(self.scan_info_list)

    def create_scan_info_dock(self):
        self.scan_info = QDockWidget("Scan Info", parent=self)
        self.scan_info.setMaximumWidth(150)
        self.scan_info.setWidget(self.scan_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.scan_info)

    def create_roi_items_dock(self):
        self.list_roi = QListWidget()
        self.list_roi.itemDoubleClicked.connect(self.itemD_clicked)

        self.roi_items = QDockWidget("ROIs", parent=self)
        self.roi_items.setMaximumWidth(150)
        self.roi_items.setWidget(self.list_roi)

        self.addDockWidget(Qt.RightDockWidgetArea, self.roi_items)

    def create_left_dock(self):
        self.create_roi_items_dock()
        self.create_scan_info_form()
        self.create_scan_widget()
        self.create_scan_info_dock()

    def create_toolbar(self):
        self.toolbar = self.addToolBar('My ToolBar')
        self.toolbar.addAction(self.select_roi_action)
        self.toolbar.addAction(self.mark_vector_action)
        self.toolbar.addAction(self.approve_roi_action)

    def create_info_dict(self, path: str):
        if not os.path.isfile(path):
            raise FileNotFoundError('Invalid file path!')
        name, ext = os.path.basename(path).split('.')
        results_dir = os.path.join(RESULTS_DIR, name + '_results')
        db_path = os.path.join(results_dir, 'DB.json')
        im2show_path = os.path.join(results_dir, 'im2show.png')
        metadata_path = os.path.join(results_dir, 'metadata.json')
        d = {
            'path': path,
            'name': name,
            'ext': ext,
            'results_dir': results_dir,
            'db_path': db_path,
            'im2show_path': im2show_path,
            'metadata_path': metadata_path,
        }
        return d

    def closeEvent(self, event):
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
            if type(event) == bool:
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
        global df, Vascular_types
        df = pd.DataFrame(columns=[
            'ID', 'Status', 'Position', 'gamma', 'gamma_position', 'dx',
            'Tline', 'Vessel_Type'
        ])
        Vascular_types = []
        # key= "db_path"
        # if not key in file_data:
        #    db_file_name= "DB.json"
        #   db_path = results_dir+'\\'+ db_file_name
        #    file_data["db_path"]=db_path

    def collect_metadata(self):
        global file_metadata, file_data

        if bool(file_metadata):
            file_data["bidirectional"] = file_metadata[
                "SI.hScan2D.bidirectional"]
            file_data["Tline"] = file_metadata["SI.hRoiManager.linePeriod"]
            file_data["dt_frame"] = file_metadata[
                "SI.hRoiManager.scanFramePeriod"]
            '''
            file_data["sample_coord"]=file_metadata["SI.hRoiManager.imagingFovUm"]
            image_coord = file_metadata["SI.hRoiManager.imagingFovUm"]
            imageX_size = (image_coord[2][0]-image_coord[0][0]) #*(10**-6)
            imageX_size= float("%.9f" % imageX_size)
            pixel_size = imageX_size/file_data["lines"]
            '''
            file_data["lines"] = file_metadata["SI.hRoiManager.linesPerFrame"]
            zoom_factor = file_metadata["SI.hRoiManager.scanZoomFactor"]
            file_data["zoom_factor"] = zoom_factor
            if zoom_factor == 5:
                pixel_size = 0.4  # um
            elif zoom_factor == 4:
                pixel_size = 0.5  # um
            file_data["dx"] = pixel_size
            # adding data to interface
            fline = 1 / file_data["Tline"]
            file_data["fline"] = fline

            self.fline_text.setText(str("%.2f" % fline))
            self.file_name_text.setText(file_data["file_name"])
            self.dx_text.setText(str(pixel_size))
        else:
            file_data["Tline"] = 1
            file_data["dx"] = 0.4
            fline = 1000
            file_data["fline"] = fline
            self.fline_text.setText(str(fline))
            self.file_name_text.setText(file_data["name"])
            self.dx_text.setText(str(file_data["dx"]))

    def prep_new_or_open(self, path: str = ''):
        # Clean window
        if self.image_view.hasImage():
            self.restart('new')

        if not os.path.isfile(path):
            if path:
                title = 'Open file...'
            else:
                title = 'Create new file...'
            path = QFileDialog.getOpenFileName(self, title)[0]

        global file_data
        file_data = self.create_info_dict(path)

        if not os.path.exists(file_data['results_dir']):
            os.makedirs(file_data['results_dir'])

    def create_new_file(self, path: str = ''):

        self.prep_new_or_open(path)

        global file_metadata, file_data

        file_metadata = self.image_view.Extract_image_and_metadata(file_data)
        image = QImage(file_data['im2show_path'])
        self.image_view.setImage(image)
        if self.image_view.hasImage():
            self.select_roi_action.setEnabled(True)
        self.collect_metadata()
        self.create_DataFrame()

    def check_load_reqirements(self):
        global file_data
        fields = ['results_dir', 'im2show_path', 'db_path', 'metadata_path']
        if all([os.path.exists(file_data[field]) for field in fields]):
            return True
        raise FileNotFoundError('Could not find required files!')

    def open_file(self):

        self.prep_new_or_open()
        global df, file_metadata, file_data

        if self.check_load_reqirements():
            with open(file_data['metadata_path'], 'r') as fp:
                file_metadata = json.load(fp)
            self.collect_metadata()
            image = QImage(file_data['im2show_path'])
            self.image_view.setImage(image)
            df = pd.read_json(file_data['db_path'])
            items_list = [
                'ROI ' + str(i) for i in range(1,
                                               df.index.max() + 2)
            ]
            self.list_roi.addItems(items_list)
            rois_pos_list = list(df['Position'])
            self.image_view.create_fromDB(rois_pos_list, "rois")
            vec_pos_list = list(df['gamma_position'])
            self.image_view.create_fromDB(vec_pos_list, "vector")

    def save_rois(self):
        global file_data
        print("done edit")
        self.fline_text.setEnabled(False)
        fline = self.fline_text.text()
        self.file_name_text.setEnabled(False)
        file_name = self.file_name_text.text()
        self.dx_text.setEnabled(False)
        dx = self.dx_text.text()
        self.save_button.setEnabled(False)
        if not fline == str("%.2f" % file_data["fline"]):
            file_data["fline"] = float(fline)
            tline = 1 / float(fline)
            df["Tline"] = tline
            file_data["Tline"] = tline
            print("fline has changed and saved jjjj")
        if not file_name == file_data["file_name"]:
            db_old_path = file_data["db_path"]
            new_db_path = db_old_path[:len(db_old_path) -
                                      7] + file_name + "_" + db_old_path[len(
                                          db_old_path) - 7:]
            file_data["db_path"] = new_db_path
            print("changing file Name will cause errors")
        if not dx == str(file_data["dx"]):
            file_data["dx"] = float(dx)
            df["dx"] = float(dx)
            print("dx has changed and saved")

    def edit_info_mode(self):
        self.fline_text.setEnabled(True)
        self.file_name_text.setEnabled(True)
        self.dx_text.setEnabled(True)
        self.save_button.setEnabled(True)

    def select_roi(self):
        if self.image_view.hasImage():
            self.image_view.helper_bool2 = False
            self.image_view.helper_bool = True
            self.select_roi_action.setEnabled(False)
            self.mark_vector_action.setEnabled(True)

    def select_vec(self):
        self.image_view.helper_bool = False
        self.image_view.helper_bool2 = True
        self.mark_vector_action.setEnabled(False)
        self.approve_roi_action.setEnabled(True)

    def find_gamma(self, start_point, end_point):
        dx = end_point[0] - start_point[0]
        dy = end_point[1] - start_point[1]
        gamma = abs(math.degrees(math.atan(dy / dx)))
        if dy < 0:
            gamma = gamma * (-1)
        return gamma

    def approve_roi(self):
        global df
        print("approval")
        # vessel_type = self.type_setting_window()

        self.image_view.helper_bool2 = False
        self.image_view.helper_bool = False
        self.approve_roi_action.setEnabled(False)
        self.select_roi_action.setEnabled(True)

        points_rect, v_start, v_end = self.image_view.approve_obj()
        points_rect = points_rect.getRect()
        v_start = (v_start.x(), v_start.y())
        v_end = (v_end.x(), v_end.y())
        gamma = self.find_gamma(v_start, v_end)
        dx = file_data["dx"]
        Tline = file_data["Tline"]
        status = '0'

        roi_index = len(df.index)
        if roi_index == 0:
            roi_ID = 1
        else:
            roi_ID = df.at[roi_index - 1, "ID"] + 1
        vessel_type = Vascular_types[roi_index]
        df.at[roi_index, "ID"] = int(roi_ID)
        df.at[roi_index, "Position"] = points_rect
        df.at[roi_index, "Status"] = status
        df.at[roi_index, "gamma"] = gamma
        df.at[roi_index, 'gamma_position'] = v_start, v_end
        df.at[roi_index, "dx"] = dx
        df.at[roi_index, "Tline"] = Tline
        df.at[roi_index, "Vessel_Type"] = vessel_type

        name = "ROI " + str(roi_ID)
        print(name)
        item = QListWidgetItem(name)
        self.list_roi.addItem(item)

    def type_setting_window(self):

        self.type_pop = QDialog(self)
        main_layout = QFormLayout()
        text = QLabel("Define the type of blood vessels in this ROI:")
        self.options = QComboBox()
        options_list = [
            "---", "Pial_Artery", "Pial_Vein", "PA", "PV", "Cap",
            "PA_diamOnly", "PV_diamOnly"
        ]
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
        # print (vessel_type, "from results function")
        file_data["vessels_types"] = Vascular_types
        self.approve_roi()

    def undo(self):
        self.image_view.helper_bool2 = False
        self.image_view.helper_bool = False
        self.approve_roi_action.setEnabled(False)
        self.mark_vector_action.setEnabled(False)
        self.select_roi_action.setEnabled(True)
        self.image_view.scene.removeItem(self.image_view.rect)
        self.image_view.scene.removeItem(self.image_view.linegroup)

    def add_roi(self):
        self.select_roi_action.setEnabled(True)

    def df_save(self):
        file_name = file_data["name"]
        path = file_data["path"]
        db_path = file_data["db_path"]
        for i in range(len(df.index)):
            df.at[i, "file_name"] = file_name
            df.at[i, "path"] = path

        df.to_json(db_path)
        print('db saved at path:')
        print(db_path)

    def itemD_clicked(self, item):
        self.b_delet.setDisabled(False)
        self.b_edit_rois.setDisabled(False)
        self.b_edit_vector.setDisabled(False)
        num_item = int(item.text()[4])
        self.image_view.mark_item(num_item - 1)

        # print ("num item double clicked:" ,num_item)

    def update_objects(self):
        global df
        numberOfROIs = len(df.index)
        i = range(numberOfROIs)
        df["ID"] = list(int(k + 1) for k in i)
        for k in i:
            item = self.list_roi.item(k)
            item.setText(item.text()[:4] + str(k + 1))

    def delete_roi(self):
        global df
        item = self.list_roi.currentItem()
        name = item.text()
        index = int(name[4]) - 1
        df = df.drop(df.index[index])
        df = df.reset_index(drop=True)
        self.list_roi.takeItem(index)
        self.image_view.delete_roi(index)
        self.update_objects()

    def save_changes_handler(self, i):
        ans = i.text()
        print(ans)
        if ans == 'Save':
            self.df_save()
            self.restart("clear")
        elif ans == 'Cancel':
            pass
        elif ans == 'Discard':
            self.restart("clear")

    def pop_save_changes_message(self):
        global file_data
        if not df.empty:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Question)
            msg.setText("The document has been modified.")
            msg.setInformativeText("Do you want to save your changes?")
            msg.setStandardButtons(QMessageBox.Save | QMessageBox.Discard
                                   | QMessageBox.Cancel)
            msg.setDefaultButton(QMessageBox.Save)
            msg.buttonClicked.connect(self.save_changes_handler)
            msg.exec_()
        else:
            self.restart("clear")

    def restart(self, command=""):
        global file_data
        if command == "clear":
            self.list_roi.clear()
            path = file_data["path"]
            self.create_new_file(path)
            self.image_view.restart_obj()
        elif command == "new":
            self.list_roi.clear()
            self.image_view.restart_obj()
            file_data = {}
