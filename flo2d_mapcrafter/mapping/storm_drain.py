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

from PyQt5.QtCore import Qt, QMetaType
from PyQt5.QtWidgets import QProgressDialog, QApplication, QMessageBox
from matplotlib import pyplot as plt

from qgis._core import Qgis, QgsVectorLayer, QgsProject, QgsMessageLog, QgsField, QgsFeature, QgsPointXY, QgsGeometry, \
    QgsVectorFileWriter, QgsCoordinateReferenceSystem
from shapely.geometry import Point


class StormDrainPlots:

    def __init__(self, units_switch, iface):
        """
        Class constructor
        :param units_switch: 0 english 1 metric
        """
        self.iface = iface
        self.units_switch = units_switch

    def create_plots(self, storm_drain_rbs, flo2d_results_dir, sd_output_dir):
        """
        Function to create the plots
        """
        try:
            import swmmio
        except ImportError:
            message = "The swmmio library is not found in your python environment. This external library is required to " \
                      "run some processes related to swmm files. More information on: https://swmmio.readthedocs.io/en/v0.6.11/.\n\n" \
                      "Would you like to install it automatically or " \
                      "manually?\n\nSelect automatic if you have admin rights. Otherwise, contact your admin and " \
                      "follow the manual steps."
            title = "External library not found!"
            button1 = "Automatic"
            button2 = "Manual"

            msgBox = QMessageBox()
            msgBox.setWindowTitle(title)
            msgBox.setText(message)
            msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Close)
            msgBox.setDefaultButton(QMessageBox.Yes)
            buttonY = msgBox.button(QMessageBox.Yes)
            buttonY.setText(button1)
            buttonN = msgBox.button(QMessageBox.No)
            buttonN.setText(button2)
            install_options = msgBox.exec_()

            if install_options == QMessageBox.Yes:
                QApplication.setOverrideCursor(Qt.WaitCursor)
                try:
                    import pathlib as pl
                    import subprocess
                    import sys

                    qgis_Path = pl.Path(sys.executable)
                    qgis_python_path = (qgis_Path.parent / "python3.exe").as_posix()

                    subprocess.check_call(
                        [qgis_python_path, "-m", "pip", "install", "--user", "swmmio==0.6.11"]
                    )
                    import swmmio
                    QApplication.restoreOverrideCursor()

                except ImportError as e:
                    QApplication.restoreOverrideCursor()
                    msgBox = QMessageBox()
                    msgBox.setText("Error while installing h5py. Install it manually. " + str(e))
                    msgBox.setWindowTitle("FLO-2D")
                    icon = QMessageBox.Critical
                    msgBox.setIcon(icon)
                    msgBox.exec_()

            # Manual Installation
            elif install_options == QMessageBox.No:
                QApplication.restoreOverrideCursor()
                message = "1. Run OSGeo4W Shell as admin\n" \
                          "2. Type this command: pip install swmmio==0.6.11\n\n" \
                          "Wait the process to finish and rerun this process.\n\n" \
                          "For more information, access https://flo-2d.com/contact/"
                msgBox = QMessageBox()
                msgBox.setText(message)
                msgBox.setWindowTitle("FLO-2D")
                icon = QMessageBox.Information
                msgBox.setIcon(icon)
                msgBox.exec_()
                return
            else:
                return

        was_created = False

        nodes_plots = [
            "Inflow",
            "Flooding",
            "Node Depth",
            "Head"
        ]

        links_plots = [
            "Flow",
            "Velocity",
            "Link Depth",
            "Percent Full"
        ]

        swmm_inp = swmmio.Model(flo2d_results_dir + r"\swmm.inp")
        swmm_rpt = flo2d_results_dir + r"\swmm.rpt"

        nname_grid = self.get_nname_grid(flo2d_results_dir)

        for plot in (nodes_plots + links_plots):
            if plot in nodes_plots:
                storm_drain_values = storm_drain_rbs.get(plot)
                if storm_drain_values[0]:
                    was_created = True
                    plot_type = nodes_plots.index(plot) + 1
                    sd_node_output_dir = sd_output_dir + r"\Nodes"
                    if not os.path.exists(sd_node_output_dir):
                        os.makedirs(sd_node_output_dir)
                    nodes = swmm_inp.nodes().index
                    total_nodes = len(nodes)

                    progDialog = QProgressDialog(f"Creating {plot} plots...", None, 0, total_nodes)
                    progDialog.setModal(True)
                    progDialog.setValue(0)
                    progDialog.show()
                    i = 0
                    for node in nodes:
                        try:
                            nodes_df = swmmio.dataframe_from_rpt(swmm_rpt, "Node Results", node)
                            # Create a plot
                            x_string = list(nodes_df.iloc[:, 0])
                            x_numeric = [(int(str(t).split(':')[0]) * 60 + int(str(t).split(':')[1])) / 60
                                         for t in x_string if isinstance(t, str) and ':' in t]

                            plt.clf()
                            if len(x_numeric) == len(list(nodes_df.iloc[:, plot_type])):

                                if plot_type in [1, 2]:
                                    if self.units_switch == "0":
                                        unit = "cfs"
                                    else:
                                        unit = "cms"
                                if plot_type in [3, 4]:
                                    if self.units_switch == "0":
                                        unit = "ft"
                                    else:
                                        unit = "m"

                                plt.plot(x_numeric, list(nodes_df.iloc[:, plot_type]))

                                if nname_grid.get(node):
                                    plt.title(f'{node} {nname_grid.get(node)} Node')
                                else:
                                    plt.title(f'{node} Node')
                                plt.xlabel('hours')
                                plt.ylabel(unit)

                                sd_node_dir = sd_node_output_dir + rf"\{plot}"
                                if not os.path.exists(sd_node_dir):
                                    os.makedirs(sd_node_dir)

                                # Save the plot to a file
                                if nname_grid.get(node):
                                    plt.savefig(sd_node_dir + fr'\{node}_{nname_grid.get(node)}_Node.png')
                                else:
                                    plt.savefig(sd_node_dir + fr'\{node}_Node.png')

                            progDialog.setValue(i)
                            i += 1
                        except:
                            pass

            if plot in links_plots:
                storm_drain_values = storm_drain_rbs.get(plot)
                if storm_drain_values[0]:
                    was_created = True
                    plot_type = links_plots.index(plot) + 1
                    sd_link_output_dir = sd_output_dir + r"\Links"
                    if not os.path.exists(sd_link_output_dir):
                        os.makedirs(sd_link_output_dir)
                    links = swmm_inp.links().index
                    total_links = len(links)

                    progDialog = QProgressDialog(f"Creating {plot} plots...", None, 0, total_links)
                    progDialog.setModal(True)
                    progDialog.setValue(0)
                    progDialog.show()
                    i = 0
                    for link in links:
                        try:
                            links_df = swmmio.dataframe_from_rpt(swmm_rpt, "Link Results", link)
                            # Create a plot
                            x_string = list(links_df.iloc[:, 0])
                            x_numeric = [(int(str(t).split(':')[0]) * 60 + int(str(t).split(':')[1])) / 60
                                         for t in x_string if isinstance(t, str) and ':' in t]

                            plt.clf()
                            if len(x_numeric) == len(list(links_df.iloc[:, plot_type])):
                                if plot_type == 1:
                                    if self.units_switch == "0":
                                        unit = "cfs"
                                    else:
                                        unit = "cms"
                                if plot_type == 2:
                                    if self.units_switch == "0":
                                        unit = "fts"
                                    else:
                                        unit = "mps"
                                if plot_type == 3:
                                    if self.units_switch == "0":
                                        unit = "ft"
                                    else:
                                        unit = "m"
                                if plot_type == 4:
                                    unit = "%"

                                plt.plot(x_numeric, list(links_df.iloc[:, plot_type]))

                                # Customize the plot (if needed)
                                if nname_grid.get(link):
                                    plt.title(f'{link} {nname_grid.get(link)} Link')
                                else:
                                    plt.title(f'{link} Link')
                                plt.xlabel('hours')
                                plt.ylabel(unit)

                                sd_link_dir = sd_link_output_dir + rf"\{plot}"
                                if not os.path.exists(sd_link_dir):
                                    os.makedirs(sd_link_dir)

                                # Save the plot to a file
                                if nname_grid.get(link):
                                    plt.savefig(sd_link_dir + fr'\{link}_{nname_grid.get(link)}_Link.png')
                                else:
                                    plt.savefig(sd_link_dir + fr'\{link}_Link.png')

                            progDialog.setValue(i)
                            i += 1
                        except:
                            pass

        return was_created

    def plot_graphics(self, storm_drain_rbs, flo2d_results_dir, sd_output_dir, authid, mapping_group):
        """
        Function to create the graphics plot
        """
        try:
            import swmmio
        except ImportError:
            message = "The swmmio library is not found in your python environment. This external library is required to " \
                      "run some processes related to swmm files. More information on: https://swmmio.readthedocs.io/en/v0.6.11/.\n\n" \
                      "Would you like to install it automatically or " \
                      "manually?\n\nSelect automatic if you have admin rights. Otherwise, contact your admin and " \
                      "follow the manual steps."
            title = "External library not found!"
            button1 = "Automatic"
            button2 = "Manual"

            msgBox = QMessageBox()
            msgBox.setWindowTitle(title)
            msgBox.setText(message)
            msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Close)
            msgBox.setDefaultButton(QMessageBox.Yes)
            buttonY = msgBox.button(QMessageBox.Yes)
            buttonY.setText(button1)
            buttonN = msgBox.button(QMessageBox.No)
            buttonN.setText(button2)
            install_options = msgBox.exec_()

            if install_options == QMessageBox.Yes:
                QApplication.setOverrideCursor(Qt.WaitCursor)
                try:
                    import pathlib as pl
                    import subprocess
                    import sys

                    qgis_Path = pl.Path(sys.executable)
                    qgis_python_path = (qgis_Path.parent / "python3.exe").as_posix()

                    subprocess.check_call(
                        [qgis_python_path, "-m", "pip", "install", "--user", "swmmio==0.6.11"]
                    )
                    import swmmio
                    QApplication.restoreOverrideCursor()

                except ImportError as e:
                    QApplication.restoreOverrideCursor()
                    msgBox = QMessageBox()
                    msgBox.setText("Error while installing h5py. Install it manually. " + str(e))
                    msgBox.setWindowTitle("FLO-2D")
                    icon = QMessageBox.Critical
                    msgBox.setIcon(icon)
                    msgBox.exec_()

            # Manual Installation
            elif install_options == QMessageBox.No:
                QApplication.restoreOverrideCursor()
                message = "1. Run OSGeo4W Shell as admin\n" \
                          "2. Type this command: pip install swmmio==0.6.11\n\n" \
                          "Wait the process to finish and rerun this process.\n\n" \
                          "For more information, access https://flo-2d.com/contact/"
                msgBox = QMessageBox()
                msgBox.setText(message)
                msgBox.setWindowTitle("FLO-2D")
                icon = QMessageBox.Information
                msgBox.setIcon(icon)
                msgBox.exec_()
                return
            else:
                return

        graphics_plots = [
            "Hours Flooded",
            "Maximum Flooding",
            "Total Flooding",
            "Maximum Pond"
        ]

        sd_output_dir = os.path.join(sd_output_dir, "Graphics")
        if not os.path.exists(sd_output_dir):
            os.makedirs(sd_output_dir)

        for plot in graphics_plots:
            storm_drain_values = storm_drain_rbs.get(plot)
            if storm_drain_values[0]:
                storm_drain_group_name = "Storm Drain"
                if mapping_group.findGroup(storm_drain_group_name):
                    storm_drain_group = mapping_group.findGroup(storm_drain_group_name)
                else:
                    storm_drain_group = mapping_group.insertGroup(0, storm_drain_group_name)

                mymodel = swmmio.Model(flo2d_results_dir)

                nodes = swmmio.Nodes(
                    model=mymodel,
                    inp_sections=['junctions', 'storages', 'outfalls'],
                    rpt_sections=['Node Flooding Summary'],
                )

                # access data
                nodes = nodes.dataframe

                if plot == "Hours Flooded":
                    filtered_nodes = nodes.loc[nodes.HoursFlooded > float(storm_drain_values[1])]
                    if not filtered_nodes.empty:
                        flooded_series = nodes.loc[nodes.HoursFlooded > float(storm_drain_values[1]), 'TotalFloodVol']
                        flood_vol = sum(flooded_series)  # total flood volume (million gallons)
                        flooded_count = len(flooded_series)  # count of flooded nodes

                        nodes['draw_color'] = '#787882'  # default node color
                        nodes.loc[nodes.HoursFlooded > float(storm_drain_values[1]), 'draw_color'] = '#FF0000'
                        nodes.loc[nodes.HoursFlooded > float(storm_drain_values[1]), 'draw_size'] = 10

                        links = mymodel.links.dataframe
                        links['draw_color'] = '#787882'
                        links['draw_size'] = 2

                        # Ensure CRS is properly set
                        crs = QgsCoordinateReferenceSystem(authid)

                        # Create a memory layer for the nodes with proper CRS
                        vl = QgsVectorLayer("Point?crs=" + crs.authid(), f'HoursFlooded_{storm_drain_values[1]}',
                                            "memory")
                        pr = vl.dataProvider()

                        # Define fields for the shapefile
                        pr.addAttributes([QgsField("X", QMetaType.Type.Double),
                                          QgsField("Y", QMetaType.Type.Double),
                                          QgsField("HoursFlooded", QMetaType.Type.Double, len=10, prec=4),
                                          QgsField("TotalFloodVol", QMetaType.Type.Double, len=10, prec=4)])
                        vl.updateFields()

                        # Add features (geometry and attributes) to the layer
                        for idx, row in filtered_nodes.iterrows():
                            feature = QgsFeature()
                            point = QgsPointXY(float(row['X']), float(row['Y']))
                            feature.setGeometry(QgsGeometry.fromPointXY(point))
                            feature.setAttributes([row['X'], row['Y'], round(row['HoursFlooded'], 4), round(row['TotalFloodVol'], 4)])
                            pr.addFeature(feature)

                        vl.updateExtents()

                        # Save the memory layer as a shapefile
                        output_shapefile = os.path.join(sd_output_dir, rf'HoursFlooded_{storm_drain_values[1]}.shp')
                        # Save the shapefile
                        options = QgsVectorFileWriter.SaveVectorOptions()
                        options.driverName = "ESRI Shapefile"
                        options.layerName = f'HoursFlooded_{storm_drain_values[1]}'
                        options.fileEncoding = 'utf-8'

                        coordinateTransformContext = QgsProject.instance().transformContext()

                        QgsVectorFileWriter.writeAsVectorFormatV3(vl, output_shapefile, coordinateTransformContext, options)

                        layer = QgsVectorLayer(output_shapefile, f'HoursFlooded_{storm_drain_values[1]}', "ogr")
                        QgsProject.instance().addMapLayer(layer, False)
                        storm_drain_group.insertLayer(0, layer)

                        # Add an informative annotation, and draw:
                        file = os.path.join(sd_output_dir, rf'\HoursFlooded_{storm_drain_values[1]}.png')
                        annotation = 'Flooded Volume: {}MG\nTotal Nodes:{}'.format(round(flood_vol), flooded_count)
                        swmmio.draw_model(model=None, nodes=nodes, conduits=links, parcels=None, title=annotation,
                                          annotation=None, file_path=file, bbox=None, px_width=2048.0)

                if plot == "Maximum Flooding":
                    filtered_nodes = nodes.loc[nodes.MaxQFlooding > float(storm_drain_values[1])]
                    if not filtered_nodes.empty:

                        # nodes in a graphic
                        nodes['draw_color'] = '#787882'  # grey
                        nodes.loc[nodes.MaxQFlooding > float(storm_drain_values[1]), 'draw_color'] = '#FF0000'
                        nodes.loc[nodes.MaxQFlooding > float(storm_drain_values[1]), 'draw_size'] = 10
                        nodes_count = len(nodes.loc[nodes.MaxQFlooding > float(storm_drain_values[1])])

                        links = mymodel.links.dataframe
                        links['draw_color'] = '#787882'  # grey
                        links['draw_size'] = 2

                        # Set up CRS
                        crs = QgsCoordinateReferenceSystem(authid)

                        # Create a memory layer for the nodes with proper CRS
                        vl = QgsVectorLayer("Point?crs=" + crs.authid(), f'MaxQFlooding_{storm_drain_values[1]}',
                                            "memory")
                        pr = vl.dataProvider()

                        # Define fields for the shapefile
                        pr.addAttributes([QgsField("X", QMetaType.Type.Double),
                                          QgsField("Y", QMetaType.Type.Double),
                                          QgsField("MaxQFlooding", QMetaType.Type.Double, len=10, prec=4)])
                        vl.updateFields()

                        # Add features (geometry and attributes) to the layer
                        for idx, row in filtered_nodes.iterrows():
                            feature = QgsFeature()
                            point = QgsPointXY(float(row['X']), float(row['Y']))
                            feature.setGeometry(QgsGeometry.fromPointXY(point))
                            feature.setAttributes([row['X'], row['Y'], round(row['MaxQFlooding'], 4)])
                            pr.addFeature(feature)

                        vl.updateExtents()

                        # Save the memory layer as a shapefile
                        output_shapefile = os.path.join(sd_output_dir, rf'MaxQFlooding_{storm_drain_values[1]}.shp')

                        # Save the shapefile using QgsVectorFileWriter
                        options = QgsVectorFileWriter.SaveVectorOptions()
                        options.driverName = "ESRI Shapefile"
                        options.layerName = f'MaxQFlooding_{storm_drain_values[1]}'
                        options.fileEncoding = 'utf-8'

                        coordinateTransformContext = QgsProject.instance().transformContext()

                        QgsVectorFileWriter.writeAsVectorFormatV3(vl, output_shapefile, coordinateTransformContext,
                                                                  options)

                        # add an informative annotation, and draw:
                        file = sd_output_dir + rf'\MaxQFlooding_{storm_drain_values[1]}.png'
                        annotation = f'Total Nodes: {nodes_count}'
                        swmmio.draw_model(model=None, nodes=nodes, conduits=links, parcels=None, title=annotation,
                                          annotation=None, file_path=file, bbox=None, px_width=2048.0)

                        layer = QgsVectorLayer(output_shapefile, f'MaxQFlooding_{storm_drain_values[1]}', "ogr")
                        QgsProject.instance().addMapLayer(layer, False)
                        storm_drain_group.insertLayer(0, layer)

                # TotalFloodVol
                if plot == 'Total Flooding':
                    filtered_nodes = nodes.loc[nodes.TotalFloodVol > float(storm_drain_values[1])]
                    if not filtered_nodes.empty:
                        # nodes in a graphic
                        nodes['draw_color'] = '#787882'  # grey
                        nodes.loc[nodes.TotalFloodVol > float(storm_drain_values[1]), 'draw_color'] = '#FF0000'
                        nodes.loc[nodes.TotalFloodVol > float(storm_drain_values[1]), 'draw_size'] = 10

                        nodes_count = len(nodes.loc[nodes.TotalFloodVol > float(storm_drain_values[1])])

                        links = mymodel.links.dataframe
                        links['draw_color'] = '#787882'  # grey
                        links['draw_size'] = 2

                        # Set up CRS
                        crs = QgsCoordinateReferenceSystem(authid)

                        # Create a memory layer for the nodes with proper CRS
                        vl = QgsVectorLayer("Point?crs=" + crs.authid(), f'TotalFloodVol_{storm_drain_values[1]}',
                                            "memory")
                        pr = vl.dataProvider()

                        # Define fields for the shapefile
                        pr.addAttributes([QgsField("X", QMetaType.Type.Double),
                                          QgsField("Y", QMetaType.Type.Double),
                                          QgsField("TotalFloodVol", QMetaType.Type.Double, len=10, prec=4)])
                        vl.updateFields()

                        # Add features (geometry and attributes) to the layer
                        for idx, row in filtered_nodes.iterrows():
                            feature = QgsFeature()
                            point = QgsPointXY(float(row['X']), float(row['Y']))
                            feature.setGeometry(QgsGeometry.fromPointXY(point))
                            feature.setAttributes([row['X'], row['Y'], round(row['TotalFloodVol'], 4)])
                            pr.addFeature(feature)

                        vl.updateExtents()

                        # Save the memory layer as a shapefile
                        output_shapefile = os.path.join(sd_output_dir, rf'TotalFloodVol_{storm_drain_values[1]}.shp')

                        # Save the shapefile using QgsVectorFileWriter
                        options = QgsVectorFileWriter.SaveVectorOptions()
                        options.driverName = "ESRI Shapefile"
                        options.layerName = f'TotalFloodVol_{storm_drain_values[1]}'
                        options.fileEncoding = 'utf-8'

                        coordinateTransformContext = QgsProject.instance().transformContext()

                        QgsVectorFileWriter.writeAsVectorFormatV3(vl, output_shapefile, coordinateTransformContext,
                                                                  options)

                        # add an informative annotation, and draw:
                        file = sd_output_dir + rf'\TotalFloodVol_{storm_drain_values[1]}.png'
                        annotation = f'Total Nodes: {nodes_count}'
                        swmmio.draw_model(model=None, nodes=nodes, conduits=links, parcels=None, title=annotation,
                                          annotation=None, file_path=file, bbox=None, px_width=2048.0)

                        layer = QgsVectorLayer(output_shapefile, f'TotalFloodVol_{storm_drain_values[1]}', "ogr")
                        QgsProject.instance().addMapLayer(layer, False)
                        storm_drain_group.insertLayer(0, layer)

                        # return [output_shapefile, f'TotalFloodVol_{storm_drain_values[1]}']

                if plot == "Maximum Pond":
                    filtered_nodes = nodes.loc[nodes.MaximumPondDepth > float(storm_drain_values[1])]
                    if not filtered_nodes.empty:
                        # nodes in a graphic
                        nodes['draw_color'] = '#787882'  # grey
                        nodes.loc[nodes.MaximumPondDepth > float(storm_drain_values[1]), 'draw_color'] = '#FF0000'
                        nodes.loc[nodes.MaximumPondDepth > float(storm_drain_values[1]), 'draw_size'] = 10
                        nodes_count = len(nodes.loc[nodes.MaximumPondDepth > float(storm_drain_values[1])])

                        links = mymodel.links.dataframe
                        links['draw_color'] = '#787882'  # grey
                        links['draw_size'] = 2

                        # Set up CRS
                        crs = QgsCoordinateReferenceSystem(authid)

                        # Create a memory layer for the nodes with proper CRS
                        vl = QgsVectorLayer("Point?crs=" + crs.authid(), f'MaximumPondDepth_{storm_drain_values[1]}',
                                            "memory")
                        pr = vl.dataProvider()

                        # Define fields for the shapefile
                        pr.addAttributes([QgsField("X", QMetaType.Type.Double),
                                          QgsField("Y", QMetaType.Type.Double),
                                          QgsField("MaximumPondDepth", QMetaType.Type.Double, len=10, prec=4)])
                        vl.updateFields()

                        # Add features (geometry and attributes) to the layer
                        for idx, row in filtered_nodes.iterrows():
                            feature = QgsFeature()
                            point = QgsPointXY(float(row['X']), float(row['Y']))
                            feature.setGeometry(QgsGeometry.fromPointXY(point))
                            feature.setAttributes([row['X'], row['Y'], round(row['MaximumPondDepth'], 4)])
                            pr.addFeature(feature)

                        vl.updateExtents()

                        # Save the memory layer as a shapefile
                        output_shapefile = os.path.join(sd_output_dir, rf'MaximumPondDepth_{storm_drain_values[1]}.shp')

                        # Save the shapefile using QgsVectorFileWriter
                        options = QgsVectorFileWriter.SaveVectorOptions()
                        options.driverName = "ESRI Shapefile"
                        options.layerName = f'MaximumPondDepth_{storm_drain_values[1]}'
                        options.fileEncoding = 'utf-8'

                        coordinateTransformContext = QgsProject.instance().transformContext()

                        QgsVectorFileWriter.writeAsVectorFormatV3(vl, output_shapefile, coordinateTransformContext,
                                                                  options)

                        # add an informative annotation, and draw:
                        file = sd_output_dir + rf'\MaximumPondDepth_{storm_drain_values[1]}.png'
                        annotation = f'Total Nodes: {nodes_count}'
                        swmmio.draw_model(model=None, nodes=nodes, conduits=links, parcels=None, title=annotation,
                                          annotation=None, file_path=file, bbox=None, px_width=2048.0)

                        layer = QgsVectorLayer(output_shapefile, f'MaximumPondDepth_{storm_drain_values[1]}', "ogr")
                        QgsProject.instance().addMapLayer(layer, False)
                        storm_drain_group.insertLayer(0, layer)

                        # return [output_shapefile, f'MaximumPondDepth_{storm_drain_values[1]}']

    def storm_drain_profile(self, storm_drain_rbs, flo2d_results_dir, sd_output_dir, plot=False):
        """
        Function to plot the storm drain profile
        """
        try:
            import swmmio
        except ImportError:
            message = "The swmmio library is not found in your python environment. This external library is required to " \
                      "run some processes related to swmm files. More information on: https://swmmio.readthedocs.io/en/v0.6.11/.\n\n" \
                      "Would you like to install it automatically or " \
                      "manually?\n\nSelect automatic if you have admin rights. Otherwise, contact your admin and " \
                      "follow the manual steps."
            title = "External library not found!"
            button1 = "Automatic"
            button2 = "Manual"

            msgBox = QMessageBox()
            msgBox.setWindowTitle(title)
            msgBox.setText(message)
            msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Close)
            msgBox.setDefaultButton(QMessageBox.Yes)
            buttonY = msgBox.button(QMessageBox.Yes)
            buttonY.setText(button1)
            buttonN = msgBox.button(QMessageBox.No)
            buttonN.setText(button2)
            install_options = msgBox.exec_()

            if install_options == QMessageBox.Yes:
                QApplication.setOverrideCursor(Qt.WaitCursor)
                try:
                    import pathlib as pl
                    import subprocess
                    import sys

                    qgis_Path = pl.Path(sys.executable)
                    qgis_python_path = (qgis_Path.parent / "python3.exe").as_posix()

                    subprocess.check_call(
                        [qgis_python_path, "-m", "pip", "install", "--user", "swmmio==0.6.11"]
                    )
                    import swmmio
                    QApplication.restoreOverrideCursor()

                except ImportError as e:
                    QApplication.restoreOverrideCursor()
                    msgBox = QMessageBox()
                    msgBox.setText("Error while installing h5py. Install it manually. " + str(e))
                    msgBox.setWindowTitle("FLO-2D")
                    icon = QMessageBox.Critical
                    msgBox.setIcon(icon)
                    msgBox.exec_()

            # Manual Installation
            elif install_options == QMessageBox.No:
                QApplication.restoreOverrideCursor()
                message = "1. Run OSGeo4W Shell as admin\n" \
                          "2. Type this command: pip install swmmio==0.6.11\n\n" \
                          "Wait the process to finish and rerun this process.\n\n" \
                          "For more information, access https://flo-2d.com/contact/"
                msgBox = QMessageBox()
                msgBox.setText(message)
                msgBox.setWindowTitle("FLO-2D")
                icon = QMessageBox.Information
                msgBox.setIcon(icon)
                msgBox.exec_()
                return
            else:
                return

        storm_drain_values = storm_drain_rbs.get("Profile")
        if storm_drain_values[0]:
            mymodel = swmmio.Model(flo2d_results_dir)
            rpt = swmmio.rpt(flo2d_results_dir + r'\swmm.rpt')

            plt.clf()
            plt.close()
            fig = plt.figure(figsize=(11, 9))
            ax = fig.add_subplot(1, 1, 1)

            try:
                path_selection = swmmio.find_network_trace(mymodel, storm_drain_values[1], storm_drain_values[2])
                max_depth = rpt.node_depth_summary.MaxNodeDepth
                ave_depth = rpt.node_depth_summary.AvgDepth
            except:
                self.iface.messageBar().pushMessage("No path found!", level=Qgis.Warning, duration=5)
                plt.clf()
                plt.close()
                return
            profile_config = swmmio.build_profile_plot(ax, mymodel, path_selection)
            swmmio.add_hgl_plot(ax, profile_config, depth=max_depth, color='red', label="Maximum Depth")
            swmmio.add_hgl_plot(ax, profile_config, depth=ave_depth, label="Average Depth")
            swmmio.add_node_labels_plot(ax, mymodel, profile_config)
            swmmio.add_link_labels_plot(ax, mymodel, profile_config)
            ax.legend(loc='best')
            ax.grid('xy')
            ax.get_xaxis().set_ticklabels([])

            if self.units_switch == "0":
                unit = "ft"
            else:
                unit = "m"

            ax.set_xlabel(f"Length ({unit})")
            ax.set_ylabel(f"Elevation ({unit})")

            fig.tight_layout()
            if plot:
                sd_profile_dir = sd_output_dir + fr"\Profile"
                if not os.path.exists(sd_profile_dir):
                    os.makedirs(sd_profile_dir)
                fig.savefig(sd_profile_dir + rf"\{storm_drain_values[1]} - {storm_drain_values[2]}.png")
            plt.show()
            # plt.close()

    def get_nname_grid(self, flo2d_results_dir):
        """
        Function to get a dictionary {"node name":"grid"}
        """
        swmmflo = flo2d_results_dir + r"\SWMMFLO.DAT"
        swmmoutf = flo2d_results_dir + r"\SWMMOUTF.DAT"

        nname_grid = {}

        with open(swmmflo, 'r') as file:
            for line in file:
                line = line.split()
                nname_grid[line[2]] = line[1]
        with open(swmmoutf, 'r') as file:
            for line in file:
                line = line.split()
                nname_grid[line[0]] = line[1]

        return nname_grid
