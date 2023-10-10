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

from qgis._core import QgsProject, QgsMessageLog

from flo2d_mapcrafter.mapping.scripts import read_ASCII, get_extent, remove_layer, set_raster_style


class FloodMaps():

    def check_flood_files(self, output_dir):
        """
        Function to check the flood files and return a dictionary with the available maps
        """

        flood_files = {
            r"TOPO.DAT": False,
            r"DEPTH.OUT": False,
            r"VELFP.OUT": False,
            r"MAXWSELEV.OUT": False,
            r"FINALDEP.OUT": False,
            r"FINALVEL.OUT": False,
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
        }

        files = os.listdir(output_dir)
        for file in files:
            for key, value in flood_files.items():
                if file.startswith(key):
                    flood_files[key] = True

        return flood_files

    def create_maps(self, flood_rbs, flo2d_results_dir, map_output_dir, mapping_group, crs):
        """
        Function to create the maps
        """

        mapping_group_name = "Flood Maps"

        if mapping_group.findGroup(mapping_group_name):
            mapping_group = mapping_group.findGroup(mapping_group_name)
        else:
            mapping_group = mapping_group.insertGroup(0, mapping_group_name)

        vector_style_directory = os.path.dirname(os.path.realpath(__file__))[:-8] + r"\vector_styles"
        raster_style_directory = os.path.dirname(os.path.realpath(__file__))[:-8] + r"\raster_styles"

        # Ground elevation
        if flood_rbs.get(r"TOPO.DAT"):
            name = "GROUND_ELEVATION"
            raster = map_output_dir + r"\GROUND_ELEVATION.tif"
            file = flo2d_results_dir + r"\TOPO.DAT"
            self.process_maps(name, raster, file, crs, mapping_group, 6)

        # Maximum Depth
        if flood_rbs.get(r"DEPFP.OUT"):
            name = "MAXIMUM_DEPTH"
            raster = map_output_dir + r"\MAXIMUM_DEPTH.tif"
            file = flo2d_results_dir + r"\DEPFP.OUT"
            self.process_maps(name, raster, file, crs, mapping_group, 0)

        # Maximum Velocity
        if flood_rbs.get(r"VELFP.OUT"):
            name = "MAXIMUM_VELOCITY"
            raster = map_output_dir + r"\MAXIMUM_VELOCITY.tif"
            file = flo2d_results_dir + r"\VELFP.OUT"
            self.process_maps(name, raster, file, crs, mapping_group, 1)

        # Maximum WSE - CHECK
        if flood_rbs.get(r"MAXWSELEV.OUT"):
            name = "MAXIMUM_WSE"
            raster = map_output_dir + r"\MAXIMUM_WSE.tif"
            file = flo2d_results_dir + r"\MAXWSELEV.OUT"
            self.process_maps(name, raster, file, crs, mapping_group, 6)

        # Final Depth
        if flood_rbs.get(r"FINALDEP.OUT"):
            name = "FINAL_DEPTH"
            raster = map_output_dir + r"\FINAL_DEPTH.tif"
            file = flo2d_results_dir + r"\FINALDEP.OUT"
            self.process_maps(name, raster, file, crs, mapping_group, 0)

        # Final Velocity
        if flood_rbs.get(r"FINALVEL.OUT"):
            name = "FINAL_VELOCITY"
            raster = map_output_dir + r"\FINAL_VELOCITY.tif"
            file = flo2d_results_dir + r"\FINALVEL.OUT"
            self.process_maps(name, raster, file, crs, mapping_group, 1)

        # Depth x Velocity
        if flood_rbs.get(r"VEL_X_DEPTH.OUT"):
            name = "DEPTH_X_VELOCITY"
            raster = map_output_dir + r"\DEPTH_X_VELOCITY.tif"
            file = flo2d_results_dir + r"\VEL_X_DEPTH.OUT"
            self.process_maps(name, raster, file, crs, mapping_group, 7)

        # Time to one ft
        if flood_rbs.get(r"TIMEONEFT.OUT"):
            name = "TIME_ONE_FT"
            raster = map_output_dir + r"\TIME_ONE_FT.tif"
            file = flo2d_results_dir + r"\TIMEONEFT.OUT"
            self.process_maps(name, raster, file, crs, mapping_group, 3)

        # Time to two ft
        if flood_rbs.get(r"TIMETOPEAK.OUT"):
            name = "TIME_TWO_FT"
            raster = map_output_dir + r"\TIME_TWO_FT.tif"
            file = flo2d_results_dir + r"\TIMETWOFT.OUT"
            self.process_maps(name, raster, file, crs, mapping_group, 3)

        # Time to peak
        if flood_rbs.get(r"TIMETOPEAK.OUT"):
            name = "TIME_TO_MAX"
            raster = map_output_dir + r"\TIME_TO_MAX.tif"
            file = flo2d_results_dir + r"\TIMETOPEAK.OUT"
            self.process_maps(name, raster, file, crs, mapping_group, 3)

        # Static pressure
        if flood_rbs.get(r"STATICPRESS.OUT"):
            name = "STATIC_PRESSURE"
            raster = map_output_dir + r"\STATIC_PRESSURE.tif"
            file = flo2d_results_dir + r"\STATICPRESS.OUT"
            self.process_maps(name, raster, file, crs, mapping_group, 8)

        # Static pressure
        if flood_rbs.get(r"SPECENERGY.OUT"):
            name = "SPECIFIC_ENERGY"
            raster = map_output_dir + r"\SPECIFIC_ENERGY.tif"
            file = flo2d_results_dir + r"\SPECENERGY.OUT"
            self.process_maps(name, raster, file, crs, mapping_group, 9)

        # Maximum channel depth
        if flood_rbs.get(r"DEPCH.OUT"):
            name = "MAXIMUM_CHANNEL_DEPTH"
            raster = map_output_dir + r"\MAXIMUM_CHANNEL_DEPTH.tif"
            file = flo2d_results_dir + r"\DEPCH.OUT"
            self.process_maps(name, raster, file, crs, mapping_group, 0)

        # Final channel depth
        if flood_rbs.get(r"DEPCHFINAL.OUT"):
            name = "FINAL_CHANNEL_DEPTH"
            raster = map_output_dir + r"\FINAL_CHANNEL_DEPTH.tif"
            file = flo2d_results_dir + r"\DEPCHFINAL.OUT"
            self.process_maps(name, raster, file, crs, mapping_group, 0)

        # Maximum channel velocity
        if flood_rbs.get(r"VELOC.OUT"):
            name = "MAXIMUM_CHANNEL_VELOCITY"
            raster = map_output_dir + r"\MAXIMUM_CHANNEL_VELOCITY.tif"
            file = flo2d_results_dir + r"\VELOC.OUT"
            self.process_maps(name, raster, file, crs, mapping_group, 1)

        # Final channel velocity
        if flood_rbs.get(r"VELCHFINAL.OUT"):
            name = "FINAL_CHANNEL_VELOCITY"
            raster = map_output_dir + r"\FINAL_CHANNEL_VELOCITY.tif"
            file = flo2d_results_dir + r"\VELCHFINAL.OUT"
            self.process_maps(name, raster, file, crs, mapping_group, 1)

        # Levee Deficit
        if flood_rbs.get(r"LEVEEDEFIC.OUT"):
            name = "LEVEE_DEFICIT"
            raster = map_output_dir + r"\LEVEE_DEFICIT.tif"
            file = flo2d_results_dir + r"\LEVEEDEFIC.OUT"
            self.process_maps(name, raster, file, crs, mapping_group, 1)

        # if flood_rbs.get(r"DEPTH.OUT"):
        #
        #     name = "FLOOD_EXTENT"
        #     raster = map_output_dir + r"\FLOOD_EXTENT.tif"
        #     vector = map_output_dir + r"\FLOOD_EXTENT.shp"
        #     file = flo2d_results_dir + r"\DEPTH.OUT"
        #
        #     # remove_layer("FLOOD_EXTENT")
        #
        #     # files = os.listdir(map_output_dir)
        #     # for file in files:
        #     #     if file.startswith("FLOOD_EXTENT"):
        #     #         file_path = os.path.join(map_output_dir, file)
        #     #         os.remove(file_path)
        #
        #     raster_processed = read_ASCII(
        #         file, raster, "FLOOD_EXTENT_RASTER", crs
        #     )
        #
        #     vector_processed = get_extent(raster, vector, name)
        #
        #     QgsProject.instance().addMapLayer(vector_processed, False)
        #     vector_processed.loadNamedStyle(vector_style_directory + r"\extent.qml")
        #
        #     mapping_group.insertLayer(0, vector_processed)
        #     # mapping_group.removeLayer(flood_extent)
        #     # root.removeLayer(flood_extent)

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
