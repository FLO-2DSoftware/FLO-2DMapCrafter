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

from PyQt5.QtCore import QVariant
from qgis._core import QgsProject, QgsMessageLog, QgsVectorLayer, QgsField, QgsFeature, QgsGeometry, QgsPointXY, \
    QgsVectorFileWriter, QgsProcessingFeedback

from flo2d_mapcrafter.mapping.check_data import check_project_id, check_mapping_group, check_raster_file, \
    check_vector_file
from flo2d_mapcrafter.mapping.scripts import read_ASCII, get_extent, remove_layer, set_raster_style, \
    set_velocity_vector_style


class FloodMaps:

    def __init__(self, units_switch):
        """
        Class constructor
        :param units_switch: 0 english 1 metric
        """
        self.units_switch = units_switch

    def check_flood_files(self, output_dir):
        """
        Function to check the flood files and return a dictionary with the available maps
        """

        flood_files = {
            r"TOPO.DAT": False,
            r"DEPTH.OUT": False,
            r"VELFP.OUT": False,
            r"VELDIREC.OUT": False,
            r"MAXWSELEV.OUT": False,
            r"FINALDEP.OUT": False,
            r"FINALVEL.OUT": False,
            r"FINALDIR.OUT": False,
            r"VEL_X_DEPTH.OUT": False,
            r"TIMEONEFT.OUT": False,
            r"TIMETWOFT.OUT": False,
            r"TIMETOPEAK.OUT": False,
            r"DEPCH.OUT": False,
            r"VELCHFINAL.OUT": False,
            r"VELOC.OUT": False,
            r"DEPCHFINAL.OUT": False,
            r"LEVEEDEFIC.OUT": False,
            r"SPECENERGY.OUT": False,
            r"STATICPRESS.OUT": False,
            r"IMPACT.OUT": False,
        }

        files = os.listdir(output_dir)
        for file in files:
            for key, value in flood_files.items():
                if file.startswith(key):
                    flood_files[key] = True

        return flood_files

    def create_maps(self, flood_rbs, flo2d_results_dir, map_output_dir, mapping_group, crs, project_id):
        """
        Function to create the maps
        """
        mapping_group_name = check_project_id("Flood Maps", project_id)
        mapping_group = check_mapping_group(mapping_group_name, mapping_group)

        vector_style_directory = os.path.dirname(os.path.realpath(__file__))[:-8] + r"\vector_styles"
        raster_style_directory = os.path.dirname(os.path.realpath(__file__))[:-8] + r"\raster_styles"

        # Site Characteristics
        sc_group_name = "Site Characteristics"
        if mapping_group.findGroup(sc_group_name):
            sc_group = mapping_group.findGroup(sc_group_name)
        else:
            sc_group = mapping_group.insertGroup(0, sc_group_name)

        # Basic
        bv_group_name = "Basic"
        if mapping_group.findGroup(bv_group_name):
            bv_group = mapping_group.findGroup(bv_group_name)
        else:
            bv_group = mapping_group.insertGroup(0, bv_group_name)

        # Derived
        dv_group_name = "Derived"
        if mapping_group.findGroup(dv_group_name):
            dv_group = mapping_group.findGroup(dv_group_name)
        else:
            dv_group = mapping_group.insertGroup(0, dv_group_name)

        # Derived
        tv_group_name = "Time"
        if mapping_group.findGroup(tv_group_name):
            tv_group = mapping_group.findGroup(tv_group_name)
        else:
            tv_group = mapping_group.insertGroup(0, tv_group_name)

        # Channel
        cv_group_name = "Channel"
        if mapping_group.findGroup(cv_group_name):
            cv_group = mapping_group.findGroup(cv_group_name)
        else:
            cv_group = mapping_group.insertGroup(0, cv_group_name)

        # Structures
        sv_group_name = "Structures"
        if mapping_group.findGroup(sv_group_name):
            sv_group = mapping_group.findGroup(sv_group_name)
        else:
            sv_group = mapping_group.insertGroup(0, sv_group_name)

        # Hydraulics
        hv_group_name = "Hydraulics"
        if mapping_group.findGroup(hv_group_name):
            hv_group = mapping_group.findGroup(hv_group_name)
        else:
            hv_group = mapping_group.insertGroup(0, hv_group_name)

        # Ground elevation
        if flood_rbs.get(r"TOPO.DAT"):
            name = check_project_id("GROUND_ELEVATION", project_id)
            name, raster = check_raster_file(name, map_output_dir)
            file = flo2d_results_dir + r"\TOPO.DAT"
            self.process_maps(name, raster, file, crs, sc_group, 6)

        # Maximum Depth
        if flood_rbs.get(r"DEPTH.OUT"):
            name = check_project_id("MAXIMUM_DEPTH", project_id)
            name, raster = check_raster_file(name, map_output_dir)
            file = flo2d_results_dir + r"\DEPFP.OUT"
            self.process_maps(name, raster, file, crs, bv_group, 0)

        # Maximum Velocity
        if flood_rbs.get(r"VELFP.OUT"):
            name = check_project_id("MAXIMUM_VELOCITY", project_id)
            name, raster = check_raster_file(name, map_output_dir)
            file = flo2d_results_dir + r"\VELFP.OUT"
            self.process_maps(name, raster, file, crs, bv_group, 1)

        # Maximum WSE - TODO: Check this map
        if flood_rbs.get(r"MAXWSELEV.OUT"):
            name = check_project_id("MAXIMUM_WSE", project_id)
            name, raster = check_raster_file(name, map_output_dir)
            file = flo2d_results_dir + r"\MAXWSELEV.OUT"
            self.process_maps(name, raster, file, crs, bv_group, 6)

        # Final Depth
        if flood_rbs.get(r"FINALDEP.OUT"):
            name = check_project_id("FINAL_DEPTH", project_id)
            name, raster = check_raster_file(name, map_output_dir)
            file = flo2d_results_dir + r"\FINALDEP.OUT"
            self.process_maps(name, raster, file, crs, bv_group, 0)

        # Final Velocity
        if flood_rbs.get(r"FINALVEL.OUT"):
            name = check_project_id("FINAL_VELOCITY", project_id)
            name, raster = check_raster_file(name, map_output_dir)
            file = flo2d_results_dir + r"\FINALVEL.OUT"
            self.process_maps(name, raster, file, crs, bv_group, 1)

        # Depth x Velocity
        if flood_rbs.get(r"VEL_X_DEPTH.OUT"):
            name = check_project_id("DEPTH_X_VELOCITY", project_id)
            name, raster = check_raster_file(name, map_output_dir)
            file = flo2d_results_dir + r"\VEL_X_DEPTH.OUT"
            self.process_maps(name, raster, file, crs, dv_group, 7)

        # Time to one ft
        if flood_rbs.get(r"TIMEONEFT.OUT"):
            name = check_project_id("TIME_ONE_FT", project_id)
            name, raster = check_raster_file(name, map_output_dir)
            file = flo2d_results_dir + r"\TIMEONEFT.OUT"
            self.process_maps(name, raster, file, crs, tv_group, 3)

        # Time to two ft
        if flood_rbs.get(r"TIMETWOFT.OUT"):
            name = check_project_id("TIME_TWO_FT", project_id)
            name, raster = check_raster_file(name, map_output_dir)
            file = flo2d_results_dir + r"\TIMETWOFT.OUT"
            self.process_maps(name, raster, file, crs, tv_group, 3)

        # Time to peak
        if flood_rbs.get(r"TIMETOPEAK.OUT"):
            name = check_project_id("TIME_TO_MAX", project_id)
            name, raster = check_raster_file(name, map_output_dir)
            file = flo2d_results_dir + r"\TIMETOPEAK.OUT"
            self.process_maps(name, raster, file, crs, tv_group, 3)

        # Static pressure
        if flood_rbs.get(r"STATICPRESS.OUT"):
            name = check_project_id("STATIC_PRESSURE", project_id)
            name, raster = check_raster_file(name, map_output_dir)
            file = flo2d_results_dir + r"\STATICPRESS.OUT"
            self.process_maps(name, raster, file, crs, hv_group, 8)

        # Specific Energy
        if flood_rbs.get(r"SPECENERGY.OUT"):
            name = check_project_id("SPECIFIC_ENERGY", project_id)
            name, raster = check_raster_file(name, map_output_dir)
            file = flo2d_results_dir + r"\SPECENERGY.OUT"
            self.process_maps(name, raster, file, crs, hv_group, 9)

        # Maximum channel depth
        if flood_rbs.get(r"DEPCH.OUT"):
            name = check_project_id("MAXIMUM_CHANNEL_DEPTH", project_id)
            name, raster = check_raster_file(name, map_output_dir)
            file = flo2d_results_dir + r"\DEPCH.OUT"
            self.process_maps(name, raster, file, crs, cv_group, 0)

        # Final channel depth
        if flood_rbs.get(r"DEPCHFINAL.OUT"):
            name = check_project_id("FINAL_CHANNEL_DEPTH", project_id)
            name, raster = check_raster_file(name, map_output_dir)
            file = flo2d_results_dir + r"\DEPCHFINAL.OUT"
            self.process_maps(name, raster, file, crs, cv_group, 0)

        # Maximum channel velocity
        if flood_rbs.get(r"VELOC.OUT"):
            name = check_project_id("MAXIMUM_CHANNEL_VELOCITY", project_id)
            name, raster = check_raster_file(name, map_output_dir)
            file = flo2d_results_dir + r"\VELOC.OUT"
            self.process_maps(name, raster, file, crs, cv_group, 1)

        # Final channel velocity
        if flood_rbs.get(r"VELCHFINAL.OUT"):
            name = check_project_id("FINAL_CHANNEL_VELOCITY", project_id)
            name, raster = check_raster_file(name, map_output_dir)
            file = flo2d_results_dir + r"\VELCHFINAL.OUT"
            self.process_maps(name, raster, file, crs, cv_group, 1)

        # Levee Deficit
        if flood_rbs.get(r"LEVEEDEFIC.OUT"):
            name = check_project_id("LEVEE_DEFICIT", project_id)
            name, raster = check_raster_file(name, map_output_dir)
            file = flo2d_results_dir + r"\LEVEEDEFIC.OUT"
            self.process_maps(name, raster, file, crs, sv_group, 1)

        # Impact Force
        if flood_rbs.get(r"IMPACT.OUT"):
            name = check_project_id("IMPACT_FORCE", project_id)
            name, raster = check_raster_file(name, map_output_dir)
            file = flo2d_results_dir + r"\IMPACT.OUT"
            self.process_maps(name, raster, file, crs, hv_group, 1)

        # Maximum Velocity Vector
        if flood_rbs.get(r"VELDIREC.OUT"):
            name = check_project_id("MAXIMUM_VELOCITY_VECTORS", project_id)
            name, vector = check_vector_file(name, map_output_dir)
            value_file = flo2d_results_dir + r"\VELFP.OUT"
            direction_file = flo2d_results_dir + r"\VELDIREC.OUT"
            self.process_vectors(name, vector, value_file, direction_file, crs, bv_group)

        # Final Velocity Vector
        if flood_rbs.get(r"FINALDIR.OUT"):
            name = check_project_id("FINAL_VELOCITY_VECTORS", project_id)
            name, vector = check_vector_file(name, map_output_dir)
            value_file = flo2d_results_dir + r"\FINALVEL.OUT"
            direction_file = flo2d_results_dir + r"\FINALDIR.OUT"
            self.process_vectors(name, vector, value_file, direction_file, crs, bv_group)

        # Uncheck and Collapse the layers added
        allLayers = mapping_group.findLayers()
        for layer in allLayers:
            if not layer.name().split()[0] == "GROUND_ELEVATION":
                lyr = QgsProject.instance().layerTreeRoot().findLayer(layer.layerId())
                lyr.setItemVisibilityChecked(False)
                lyr.setExpanded(False)

    def process_maps(self, name, raster, file, crs, mapping_group, style):
        """
        Function to process the maps
        """

        raster_processed = read_ASCII(
            file, raster, name, crs
        )

        QgsProject.instance().addMapLayer(raster_processed, False)
        set_raster_style(raster_processed, style)

        mapping_group.insertLayer(0, raster_processed)

    def process_vectors(self, name, shapefile, value_file, direction_file, crs, mapping_group):
        """
        Function to create vector maps
        """
        # Read VELFP.OUT file
        with open(value_file, 'r') as f1:
            vel_fp_lines = f1.readlines()

        # Read VELDIREC.OUT file
        with open(direction_file, 'r') as f2:
            vel_direc_lines = f2.readlines()

        # Combine data based on IDs
        combined_lines = []
        for vel_fp_line, vel_direc_line in zip(vel_fp_lines, vel_direc_lines):
            vel_fp_data = vel_fp_line.split()
            vel_direc_data = vel_direc_line.split()

            if vel_fp_data and vel_direc_data:
                combined_line = f"{vel_fp_data[0]} {vel_fp_data[1]} {vel_fp_data[2]}  {vel_fp_data[3]} {vel_direc_data[1]}\n"
                combined_lines.append(combined_line)

        # Create a temporary memory layer
        vl = QgsVectorLayer(f"Point?crs={crs.authid()}&index=yes", name, 'memory')
        pr = vl.dataProvider()

        # Add fields to the layer
        vl.startEditing()
        pr.addAttributes([QgsField('ID', QVariant.Int), QgsField('Velocity', QVariant.Double), QgsField('Direction', QVariant.Int)])
        vl.updateFields()
        vl.commitChanges()

        for line in combined_lines:
            parts = line.split()
            x, y, velocity, direction = float(parts[1]), float(parts[2]), float(parts[3]), int(parts[4])
            if velocity != 0:
                feature = QgsFeature()
                feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x, y)))
                feature.setAttributes([int(parts[0]), velocity, self.dir_to_angle(direction)])
                pr.addFeature(feature)

        # Update the layer's extent
        vl.updateExtents()

        # Save the shapefile
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "ESRI Shapefile"
        options.layerName = name
        options.fileEncoding = 'utf-8'
        # TODO: this is deprecated. Check the new function
        QgsVectorFileWriter.writeAsVectorFormat(vl, shapefile, options)

        # Add the layer to the project
        velocity_vector_lyr = QgsVectorLayer(shapefile, name, 'ogr')
        QgsProject.instance().addMapLayer(velocity_vector_lyr, False)
        set_velocity_vector_style(velocity_vector_lyr)

        mapping_group.insertLayer(0, velocity_vector_lyr)

    def dir_to_angle(self, direction):
        """
        Function to convert FLO-2D direction to angle
        """
        directions = {
            1: 0,  # North
            2: 90,  # East
            3: 180,  # South
            4: 270,  # West
            5: 45,  # Northeast
            6: 135,  # Southeast
            7: 225,  # Southwest
            8: 315  # Northwest
        }
        return directions.get(direction)

