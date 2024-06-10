# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FLO2DMapCrafter
                                 A QGIS plugin
 This plugin creates maps from FLO-2D output files.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-09-21
        git sha              : $Format:%H$
        copyright            : (C) 2023 by FLO-2D
        email                : contact@flo-2d.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QComboBox
from qgis.PyQt import uic
from qgis._core import QgsMessageLog

uiDialog, qtBaseClass = uic.loadUiType(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "ui", "sd_results_viewer.ui"))


class SDResultsViewer(qtBaseClass, uiDialog):
    def __init__(self, folder_path, nodes_list, links_list, nname_grid):
        # super(SDResultsViewer, self).__init__(parent)
        qtBaseClass.__init__(self)
        uiDialog.__init__(self)
        self.setupUi(self)
        self.folder_path = folder_path
        self.image_paths = []
        self.current_index = 0
        self.nodes_list = nodes_list
        self.links_list = links_list
        self.nname_grid = nname_grid

        self.folder_combo.currentIndexChanged.connect(self.update_subfolders)
        self.subfolder_combo.currentIndexChanged.connect(self.update_image_paths)
        self.name_combo.currentIndexChanged.connect(self.update_image_name)
        self.grid_combo.currentIndexChanged.connect(self.update_image_grid)

        # The image is added into this image_label
        self.image_label.setScaledContents(True)

        self.prev_button.clicked.connect(self.show_prev_image)
        self.next_button.clicked.connect(self.show_next_image)

        self.populate_folders()
        self.populate_subfolders()
        self.update_image_paths()
        self.update_buttons()

    def populate_folders(self):
        folders = [f.name for f in os.scandir(self.folder_path) if f.is_dir() and f.name in ['Nodes', 'Links']]
        self.folder_combo.addItems(folders)

    def populate_subfolders(self):
        subfolders = [f.name for f in os.scandir(os.path.join(self.folder_path, self.folder_combo.currentText())) if
                      f.is_dir()]
        self.subfolder_combo.clear()
        self.subfolder_combo.addItems(subfolders)
        self.name_combo.clear()
        if self.folder_combo.currentText() == "Links":
            self.name_combo.addItems(sorted(self.links_list))
            self.grid_combo.setEnabled(False)
        if self.folder_combo.currentText() == "Nodes":
            self.name_combo.addItems(sorted(self.nodes_list))
            values_list = list(self.nname_grid.values())
            self.grid_combo.addItems(sorted(values_list))
            self.grid_combo.setEnabled(True)

    def update_subfolders(self):
        self.populate_subfolders()
        self.update_image_paths()

    def update_image_paths(self):
        subfolder_path = os.path.join(self.folder_path, self.folder_combo.currentText(),
                                      self.subfolder_combo.currentText())
        image_files = [f for f in os.listdir(subfolder_path) if f.endswith(('.jpg', '.jpeg', '.png'))]
        self.image_paths = sorted([os.path.join(subfolder_path, f) for f in image_files])
        self.grid_combo.setCurrentIndex(0)
        self.name_combo.setCurrentIndex(0)
        self.current_index = 0
        self.show_image()
        self.update_buttons()

    def update_image_name(self):
        subfolder_path = os.path.join(self.folder_path, self.folder_combo.currentText(),
                                      self.subfolder_combo.currentText())
        for filename in os.listdir(subfolder_path):
            if self.name_combo.currentText() in filename:
                self.current_index = self.name_combo.currentIndex()
                if self.folder_combo.currentText() == "Links":
                    image_path = subfolder_path + rf"\{filename}"
                    self.show_image(image_path)
                    self.update_buttons()
                if self.folder_combo.currentText() == "Nodes":
                    grid = self.nname_grid.get(self.name_combo.currentText())
                    if grid:
                        index = self.grid_combo.findText(grid)
                        self.grid_combo.setCurrentIndex(index)
                    else:
                        self.grid_combo.setCurrentIndex(-1)
                    image_path = subfolder_path + rf"\{filename}"
                    self.show_image(image_path)
                    self.update_buttons()

    def update_image_grid(self):
        subfolder_path = os.path.join(self.folder_path, self.folder_combo.currentText(),
                                      self.subfolder_combo.currentText())
        for filename in os.listdir(subfolder_path):
            if self.grid_combo.currentText() in filename:
                if self.folder_combo.currentText() == "Nodes":
                    grid = None
                    for key, value in self.nname_grid.items():
                        if self.grid_combo.currentText() == value:
                            grid = value
                            name = key
                    if grid:
                        index = self.name_combo.findText(name)
                        self.name_combo.setCurrentIndex(index)
                        self.current_index = index
                        image_path = subfolder_path + rf"\{filename}"
                        self.show_image(image_path)
                        self.update_buttons()

    def show_image(self, image_path=None):
        if image_path:
            pixmap = QPixmap(image_path)
            self.image_label.setPixmap(pixmap)
        else:
            if self.image_paths:
                image_path = self.image_paths[self.current_index]
                pixmap = QPixmap(image_path)
                self.image_label.setPixmap(pixmap)

    def update_buttons(self):
        if self.current_index == 0 or not self.image_paths:
            self.prev_button.setEnabled(False)
        else:
            self.prev_button.setEnabled(True)

        if self.current_index == len(self.image_paths) - 1 or not self.image_paths:
            self.next_button.setEnabled(False)
        else:
            self.next_button.setEnabled(True)

    def show_prev_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.name_combo.setCurrentIndex(self.current_index)
            self.show_image()
            self.update_buttons()

    def show_next_image(self):
        if self.current_index < len(self.image_paths) - 1:
            self.current_index += 1
            self.name_combo.setCurrentIndex(self.current_index)
            self.show_image()
            self.update_buttons()