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

from PyQt5.QtWidgets import QProgressDialog
from matplotlib import pyplot as plt

try:
    import swmmio
    from swmmio import dataframe_from_rpt, Model
except ImportError:
    import pathlib as pl
    import subprocess
    import sys

    qgis_Path = pl.Path(sys.executable)
    qgis_python_path = (qgis_Path.parent / "python3.exe").as_posix()

    subprocess.check_call(
        [qgis_python_path, "-m", "pip", "install", "--user", "swmmio==0.6.11"]
    )
    import swmmio
    from swmmio import dataframe_from_rpt

class StormDrainPlots:

    def __init__(self, units_switch):
        """
        Class constructor
        :param units_switch: 0 english 1 metric
        """
        self.units_switch = units_switch

    def create_plots(self, storm_drain_rbs, flo2d_results_dir, sd_output_dir):
        """
        Function to create the plots
        """

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

        for plot in (nodes_plots + links_plots):
            if plot in nodes_plots:
                if storm_drain_rbs.get(plot):
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
                            nodes_df = dataframe_from_rpt(swmm_rpt, "Node Results", node)
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

                                # Customize the plot (if needed)
                                plt.title(f'Node {node} {plot}')
                                plt.xlabel('hours')
                                plt.ylabel(unit)

                                sd_node_dir = sd_node_output_dir + rf"\{plot}"
                                if not os.path.exists(sd_node_dir):
                                    os.makedirs(sd_node_dir)

                                # Save the plot to a file
                                plt.savefig(sd_node_dir + rf"\{node}_{plot}.png")

                            progDialog.setValue(i)
                            i += 1
                        except:
                            pass

            if plot in links_plots:
                if storm_drain_rbs.get(plot):
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
                            links_df = dataframe_from_rpt(swmm_rpt, "Link Results", link)
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
                                plt.title(f'Link {link} {plot}')
                                plt.xlabel('hours')
                                plt.ylabel(unit)

                                sd_link_dir = sd_link_output_dir + rf"\{plot}"
                                if not os.path.exists(sd_link_dir):
                                    os.makedirs(sd_link_dir)

                                # Save the plot to a file
                                plt.savefig(sd_link_dir + rf"\{link}_{plot}.png")

                            progDialog.setValue(i)
                            i += 1
                        except:
                            pass




