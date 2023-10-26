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
from qgis._core import QgsProject, QgsVectorLayer, QgsField, QgsFeature, QgsPointXY, QgsGeometry, QgsVectorFileWriter

from flo2d_mapcrafter.mapping.scripts import read_ASCII, set_raster_style, set_velocity_vector_style


class TwophaseMaps():

    def check_twophase_files(self, output_dir):
        """
        Function to check the two-phase files and return a dictionary with the available maps
        """

        twophase_files = {
            r"TOPO.DAT": None,
            r"DEPTH.OUT": None,
            r"DEPFPMAX_MUD.OUT": None,
            r"DEPTHMAX_2PHASE_COMBINED.OUT": None,
            r"VELFP.OUT": None,
            r"VELFP_MUD.OUT": None,
            r"VELDIREC.OUT": None,
            r"VELDIREC_MUD.OUT": None,
            r"CVFPMAX.OUT": None,
            r"CVFPMAX_MUD.OUT": None,
            #r"FINALCVFP.OUT": None,
            r"FINALCVFP_MUD.OUT": None,
            #r"MAXWSELEV.OUT": None,
            r"FINALDEP.OUT": None,
            r"FINALDEP_MUD.OUT": None,
            r"FINALDEP_COMBO.OUT": None,
            r"FINALVEL.OUT": None,
            r"FINALVEL_MUD.OUT": None,
            r"FINALDIR.OUT": None,
            r"FINALDIR_MUD.OUT": None,
            r"VEL_X_DEPTH.OUT": None,
            r"TIMEONEFT.OUT": None,
            r"TIMETWOFT.OUT": None,
            r"TIMETOPEAK.OUT": None,
            r"DEPCH.OUT": None,
            r"VELCHFINAL.OUT": None,
            r"VELOC.OUT": None,
            r"DEPCHFINAL.OUT": None,
            r"LEVEEDEFIC.OUT": None,
            r"SPECENERGY.OUT": None,
            r"STATICPRESS.OUT": None,
        }

        files = os.listdir(output_dir)
        for file in files:
            for key, value in twophase_files.items():
                if file.startswith(key):
                    twophase_files[key] = True

        return twophase_files

    def create_maps(self, twophase_rbs, flo2d_results_dir, map_output_dir, mapping_group, crs):
        """
        Function to create the maps
        """

        mapping_group_name = "Two-phase Maps"

        if mapping_group.findGroup(mapping_group_name):
            mapping_group = mapping_group.findGroup(mapping_group_name)
        else:
            mapping_group = mapping_group.insertGroup(0, mapping_group_name)

        vector_style_directory = os.path.dirname(os.path.realpath(__file__))[:-8] + r"\vector_styles"
        raster_style_directory = os.path.dirname(os.path.realpath(__file__))[:-8] + r"\raster_styles"

        # Ground elevation
        if twophase_rbs.get(r"TOPO.DAT"):
            name = "GROUND_ELEVATION"
            raster = map_output_dir + r"\GROUND_ELEVATION.tif"
            file = flo2d_results_dir + r"\TOPO.DAT"
            self.process_maps(name, raster, file, crs, mapping_group, 6)

        # Maximum Flood Depth
        if twophase_rbs.get(r"DEPTH.OUT"):
            name = "MAXIMUM_FLOOD_DEPTH"
            raster = map_output_dir + r"\MAXIMUM_FLOOD_DEPTH.tif"
            file = flo2d_results_dir + r"\DEPTH.OUT"
            self.process_maps(name, raster, file, crs, mapping_group, 0)

        # Maximum Mudflow Depth
        if twophase_rbs.get(r"DEPFPMAX_MUD.OUT"):
            name = "MAXIMUM_MUDFLOW_DEPTH"
            raster = map_output_dir + r"\MAXIMUM_MUDFLOW_DEPTH.tif"
            file = flo2d_results_dir + r"\DEPFPMAX_MUD.OUT"
            self.process_maps(name, raster, file, crs, mapping_group, 5)

        # Maximum Combined Depth
        if twophase_rbs.get(r"DEPTHMAX_2PHASE_COMBINED.OUT"):
            name = "MAXIMUM_COMBINED_DEPTH"
            raster = map_output_dir + r"\MAXIMUM_COMBINED_DEPTH.tif"
            file = flo2d_results_dir + r"\DEPTHMAX_2PHASE_COMBINED.OUT"
            self.process_maps(name, raster, file, crs, mapping_group, 5)

        # Maximum Flood Velocity
        if twophase_rbs.get(r"VELFP.OUT"):
            name = "MAXIMUM_FLOOD_VELOCITY"
            raster = map_output_dir + r"\MAXIMUM_FLOOD_VELOCITY.tif"
            file = flo2d_results_dir + r"\VELFP.OUT"
            self.process_maps(name, raster, file, crs, mapping_group, 1)

        # Maximum Mudflow Velocity
        if twophase_rbs.get(r"VELFP_MUD.OUT"):
            name = "MAXIMUM_MUDFLOW_VELOCITY"
            raster = map_output_dir + r"\MAXIMUM_MUDFLOW_VELOCITY.tif"
            file = flo2d_results_dir + r"\VELFP_MUD.OUT"
            self.process_maps(name, raster, file, crs, mapping_group, 1)

        # Maximum Flood Sediment Concentration
        if twophase_rbs.get(r"CVFPMAX.OUT"):
            name = "MAXIMUM_FLOOD_SEDIMENT_CONCENTRATION"
            raster = map_output_dir + r"\MAXIMUM_FLOOD_SEDIMENT_CONCENTRATION.tif"
            file = flo2d_results_dir + r"\CVFPMAX.OUT"
            self.process_maps(name, raster, file, crs, mapping_group, 10)

        # Maximum Mudflow Sediment Concentration
        if twophase_rbs.get(r"CVFPMAX_MUD.OUT"):
            name = "MAXIMUM_MUDFLOW_SEDIMENT_CONCENTRATION"
            raster = map_output_dir + r"\MAXIMUM_MUDFLOW_SEDIMENT_CONCENTRATION.tif"
            file = flo2d_results_dir + r"\CVFPMAX_MUD.OUT"
            self.process_maps(name, raster, file, crs, mapping_group, 10)

        # Final Flood Depth
        if twophase_rbs.get(r"FINALDEP.OUT"):
            name = "FINAL_FLOOD_DEPTH"
            raster = map_output_dir + r"\FINAL_FLOOD_DEPTH.tif"
            file = flo2d_results_dir + r"\FINALDEP.OUT"
            self.process_maps(name, raster, file, crs, mapping_group, 0)

        # Final Mudflow Depth
        if twophase_rbs.get(r"FINALDEP_MUD.OUT"):
            name = "FINAL_MUDFLOW_DEPTH"
            raster = map_output_dir + r"\FINAL_MUDFLOW_DEPTH.tif"
            file = flo2d_results_dir + r"\FINALDEP_MUD.OUT"
            self.process_maps(name, raster, file, crs, mapping_group, 5)

        # Final Combined Depth
        if twophase_rbs.get(r"FINALDEP_COMBO.OUT"):
            name = "FINAL_COMBINED_DEPTH"
            raster = map_output_dir + r"\FINAL_COMBINED_DEPTH.tif"
            file = flo2d_results_dir + r"\FINALDEP_COMBO.OUT"
            self.process_maps(name, raster, file, crs, mapping_group, 5)

        # Final Flood Velocity
        if twophase_rbs.get(r"FINALVEL.OUT"):
            name = "FINAL_FLOOD_VELOCITY"
            raster = map_output_dir + r"\FINAL_FLOOD_VELOCITY.tif"
            file = flo2d_results_dir + r"\FINALVEL.OUT"
            self.process_maps(name, raster, file, crs, mapping_group, 1)

        # Final Mudflow Velocity
        if twophase_rbs.get(r"FINALVEL_MUD.OUT"):
            name = "FINAL_MUDFLOW_VELOCITY"
            raster = map_output_dir + r"\FINAL_MUDFLOW_VELOCITY.tif"
            file = flo2d_results_dir + r"\FINALVEL_MUD.OUT"
            self.process_maps(name, raster, file, crs, mapping_group, 1)

        # Final Mudflow Sediment Concentration
        if twophase_rbs.get(r"FINALCVFP_MUD.OUT"):
            name = "FINAL_MUDFLOW_SEDIMENT_CONCENTRATION"
            raster = map_output_dir + r"\FINAL_MUDFLOW_SEDIMENT_CONCENTRATION.tif"
            file = flo2d_results_dir + r"\FINALCVFP_MUD.OUT"
            self.process_maps(name, raster, file, crs, mapping_group, 10)

        # Depth x Velocity
        if twophase_rbs.get(r"VEL_X_DEPTH.OUT"):
            name = "DEPTH_X_VELOCITY"
            raster = map_output_dir + r"\DEPTH_X_VELOCITY.tif"
            file = flo2d_results_dir + r"\VEL_X_DEPTH.OUT"
            self.process_maps(name, raster, file, crs, mapping_group, 7)

        # Time to one ft
        if twophase_rbs.get(r"TIMEONEFT.OUT"):
            name = "TIME_ONE_FT"
            raster = map_output_dir + r"\TIME_ONE_FT.tif"
            file = flo2d_results_dir + r"\TIMEONEFT.OUT"
            self.process_maps(name, raster, file, crs, mapping_group, 3)

        # Time to two ft
        if twophase_rbs.get(r"TIMETOPEAK.OUT"):
            name = "TIME_TWO_FT"
            raster = map_output_dir + r"\TIME_TWO_FT.tif"
            file = flo2d_results_dir + r"\TIMETWOFT.OUT"
            self.process_maps(name, raster, file, crs, mapping_group, 3)

        # Time to peak
        if twophase_rbs.get(r"TIMETOPEAK.OUT"):
            name = "TIME_TO_MAX"
            raster = map_output_dir + r"\TIME_TO_MAX.tif"
            file = flo2d_results_dir + r"\TIMETOPEAK.OUT"
            self.process_maps(name, raster, file, crs, mapping_group, 3)

        # Static pressure
        if twophase_rbs.get(r"STATICPRESS.OUT"):
            name = "STATIC_PRESSURE"
            raster = map_output_dir + r"\STATIC_PRESSURE.tif"
            file = flo2d_results_dir + r"\STATICPRESS.OUT"
            self.process_maps(name, raster, file, crs, mapping_group, 8)

        # Static pressure
        if twophase_rbs.get(r"SPECENERGY.OUT"):
            name = "SPECIFIC_ENERGY"
            raster = map_output_dir + r"\SPECIFIC_ENERGY.tif"
            file = flo2d_results_dir + r"\SPECENERGY.OUT"
            self.process_maps(name, raster, file, crs, mapping_group, 9)

        # Maximum channel depth
        if twophase_rbs.get(r"DEPCH.OUT"):
            name = "MAXIMUM_CHANNEL_DEPTH"
            raster = map_output_dir + r"\MAXIMUM_CHANNEL_DEPTH.tif"
            file = flo2d_results_dir + r"\DEPCH.OUT"
            self.process_maps(name, raster, file, crs, mapping_group, 5)

        # Final channel depth
        if twophase_rbs.get(r"DEPCHFINAL.OUT"):
            name = "FINAL_CHANNEL_DEPTH"
            raster = map_output_dir + r"\FINAL_CHANNEL_DEPTH.tif"
            file = flo2d_results_dir + r"\DEPCHFINAL.OUT"
            self.process_maps(name, raster, file, crs, mapping_group, 5)

        # Maximum channel velocity
        if twophase_rbs.get(r"VELOC.OUT"):
            name = "MAXIMUM_CHANNEL_VELOCITY"
            raster = map_output_dir + r"\MAXIMUM_CHANNEL_VELOCITY.tif"
            file = flo2d_results_dir + r"\VELOC.OUT"
            self.process_maps(name, raster, file, crs, mapping_group, 1)

        # Final channel velocity
        if twophase_rbs.get(r"VELCHFINAL.OUT"):
            name = "FINAL_CHANNEL_VELOCITY"
            raster = map_output_dir + r"\FINAL_CHANNEL_VELOCITY.tif"
            file = flo2d_results_dir + r"\VELCHFINAL.OUT"
            self.process_maps(name, raster, file, crs, mapping_group, 1)

        # Levee Deficit
        if twophase_rbs.get(r"LEVEEDEFIC.OUT"):
            name = "LEVEE_DEFICIT"
            raster = map_output_dir + r"\LEVEE_DEFICIT.tif"
            file = flo2d_results_dir + r"\LEVEEDEFIC.OUT"
            self.process_maps(name, raster, file, crs, mapping_group, 1)

        # Maximum Velocity Vector
        if twophase_rbs.get(r"VELDIREC.OUT"):
            name = "MAXIMUM_FLOOD_VELOCITY_VECTORS"
            shapefile = map_output_dir + r"\MAXIMUM_FLOOD_VELOCITY_VECTORS.shp"
            value_file = flo2d_results_dir + r"\VELFP.OUT"
            direction_file = flo2d_results_dir + r"\VELDIREC.OUT"
            self.process_vectors(name, shapefile, value_file, direction_file, crs, mapping_group)

        # Final Velocity Vector
        if twophase_rbs.get(r"FINALDIR.OUT"):
            name = "FINAL_FLOOD_VELOCITY_VECTORS"
            shapefile = map_output_dir + r"\FINAL_FLOOD_VELOCITY_VECTORS.shp"
            value_file = flo2d_results_dir + r"\FINALVEL.OUT"
            direction_file = flo2d_results_dir + r"\FINALDIR.OUT"
            self.process_vectors(name, shapefile, value_file, direction_file, crs, mapping_group)

        # Maximum Velocity Vector
        if twophase_rbs.get(r"VELDIREC_MUD.OUT"):
            name = "MAXIMUM_MUDFLOW_VELOCITY_VECTORS"
            shapefile = map_output_dir + r"\MAXIMUM_MUDFLOW_VELOCITY_VECTORS.shp"
            value_file = flo2d_results_dir + r"\VELFP_MUD.OUT"
            direction_file = flo2d_results_dir + r"\VELDIREC_MUD.OUT"
            self.process_vectors(name, shapefile, value_file, direction_file, crs, mapping_group)

        # Final Velocity Vector
        if twophase_rbs.get(r"FINALDIR_MUD.OUT"):
            name = "FINAL_MUDFLOW_VELOCITY_VECTORS"
            shapefile = map_output_dir + r"\FINAL_MUDFLOW_VELOCITY_VECTORS.shp"
            value_file = flo2d_results_dir + r"\FINALVEL_MUD.OUT"
            direction_file = flo2d_results_dir + r"\FINALDIR_MUD.OUT"
            self.process_vectors(name, shapefile, value_file, direction_file, crs, mapping_group)

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
