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

import numpy as np
from PyQt5.QtGui import QColor, QIcon
from qgis._core import (
    QgsProject,
    QgsRasterLayer,
    QgsVectorLayer,
    QgsRasterShader,
    QgsSingleBandPseudoColorRenderer,
    QgsMessageLog, QgsSvgMarkerSymbolLayer, QgsSymbol,
    QgsGraduatedSymbolRenderer, QgsStyle,
    QgsClassificationQuantile,
    QgsProperty, QgsSymbolLayer,
    QgsGradientColorRamp, QgsGradientStop
)
from osgeo import gdal

import processing


def read_ASCII(file_path, output_path, name, crs):
    """Read ASCII file and extract the required fields"""

    values = []
    cellSize_data = []
    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            fields = line.split()
            if name.split()[0] == "GROUND_ELEVATION":
                x, y, value = (
                    float(fields[0]),
                    float(fields[1]),
                    float(fields[2]),
                )
                values.append((x, y, value))
                if len(cellSize_data) < 2:
                    cellSize_data.append((x, y))
            elif name.split()[0] == "MAXIMUM_DEPOSITION":
                cell, x, y, value = (
                    float(fields[0]),
                    float(fields[1]),
                    float(fields[2]),
                    float(fields[3]),
                )
                values.append((x, y, value))
                if len(cellSize_data) < 2:
                    cellSize_data.append((x, y))
            elif name.split()[0] == "MAXIMUM_SCOUR":
                cell, x, y, value = (
                    float(fields[0]),
                    float(fields[1]),
                    float(fields[2]),
                    float(fields[4]),
                )
                values.append((x, y, value))
                if len(cellSize_data) < 2:
                    cellSize_data.append((x, y))
            elif name.split()[0] == "FINAL_BED_DIFFERENCE":
                cell, x, y, value = (
                    float(fields[0]),
                    float(fields[1]),
                    float(fields[2]),
                    float(fields[5]),
                )
                values.append((x, y, value))
                if len(cellSize_data) < 2:
                    cellSize_data.append((x, y))
            else:
                if fields[0].isnumeric():
                    cell, x, y, value = (
                        float(fields[0]),
                        float(fields[1]),
                        float(fields[2]),
                        float(fields[3]),
                    )
                    values.append((x, y, value))
                    if len(cellSize_data) < 2:
                        cellSize_data.append((x, y))

    sum_values = sum(value for _, _, value in values)
    if sum_values == 0:
        QgsMessageLog.logMessage(name + ' was empty!')
        return None

    # Calculate the differences in X and Y coordinates
    dx = abs(cellSize_data[1][0] - cellSize_data[0][0])
    dy = abs(cellSize_data[1][1] - cellSize_data[0][1])

    # If the coordinate difference is equal 0, assign a huge number
    if dx == 0:
        dx = 9999
    if dy == 0:
        dy = 9999

    cellSize = min(dx, dy)

    # Get the extent and number of rows and columns
    min_x = min(point[0] for point in values)
    max_x = max(point[0] for point in values)
    min_y = min(point[1] for point in values)
    max_y = max(point[1] for point in values)
    num_cols = int((max_x - min_x) / cellSize) + 1
    num_rows = int((max_y - min_y) / cellSize) + 1

    # Convert the list of values to an array.
    raster_data = np.full((num_rows, num_cols), -9999, dtype=np.float32)
    for point in values:
        col = int((point[0] - min_x) / cellSize)
        row = int((max_y - point[1]) / cellSize)
        raster_data[row, col] = point[2]

    # Initialize the raster
    driver = gdal.GetDriverByName("GTiff")
    raster = driver.Create(output_path, num_cols, num_rows, 1, gdal.GDT_Float32)
    raster.SetGeoTransform(
        (
            min_x - cellSize / 2,
            cellSize,
            0,
            max_y + cellSize / 2,
            0,
            -cellSize,
        )
    )
    raster.SetProjection(crs.toWkt())

    band = raster.GetRasterBand(1)
    band.SetNoDataValue(-9999)  # Set a no-data value if needed
    band.WriteArray(raster_data)

    raster.FlushCache()

    layer = QgsRasterLayer(output_path, name)

    return layer


def get_extent(raster, flood_extent_vector, name):
    """Function to get the extent of a raster layer"""
    vectorized = processing.run(
        "gdal:polygonize",
        {
            "INPUT": raster,
            "BAND": 1,
            "FIELD": "DN",
            "EIGHT_CONNECTEDNESS": False,
            "EXTRA": "",
            "OUTPUT": "TEMPORARY_OUTPUT",
        },
    )["OUTPUT"]

    processing.run(
        "native:dissolve",
        {
            "INPUT": vectorized,
            "FIELD": [],
            "SEPARATE_DISJOINT": False,
            "OUTPUT": flood_extent_vector,
        },
    )
    extent = QgsVectorLayer(flood_extent_vector, name)

    return extent


def set_icon(btn, icon_file):
    """
    Function to set the icon
    """
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    idir = os.path.join(os.path.dirname(parent_dir), "img")
    btn.setIcon(QIcon(os.path.join(idir, icon_file)))


def set_raster_style(layer, style):
    """Define the raster styles"""
    colDic = {
        "white": "#ffffff",
        "lightblue": "#9ecae1",
        "blue": "#4292c6",
        "darkblue": "#08306b",
        "lightgreen": "#a1d99b",
        "green": "#41ab5d",
        "darkgreen": "#006d2c",
        "black": "#000000",
        "grey": "#808080",
        "red": "#FF0000",
        "yellow": "#FFFF00",
        "orange": "#FF7f00",
        "risk_red": "#FF0000",
        "risk_orange": "#FFC000",
        "risk_lightgreen": "#92D050",
        "risk_green": "#006600",
        "risk_lightblue": "#BDD6EE",
        "risk_blue": "#0033CC",
        "mud_lightbrown": "#be4d24",
        "mud_brown": "#752c12",
        "mud_darkbrown": "#2c0c00",
        "elev1": "#66cdaa",
        "elev2": "#ffff00",
        "elev3": "#008000",
        "elev4": "#ffa500",
        "elev5": "#8b0000",
        "elev6": "#a52a2a",
        "elev7": "#808080",
        "elev8": "#fffafa",
        "dv1": "#fde725",
        "dv2": "#20928c",
        "dv3": "#440154",
        "sed1": "#440154",
        "sed2": "#27808e",
        "sed3": "#fde725",
        "arr1": "#0033cc",
        "arr2": "#bdd6ee",
        "arr3": "#006600",
        "arr4": "#92d050",
        "arr5": "#ffc000",
        "arr6": "#ff0000",
    }

    provider = layer.dataProvider()
    myRasterShader = QgsRasterShader()

    script_directory = os.path.dirname(os.path.realpath(__file__))
    style_directory = script_directory[:-8] + r"\raster_styles"

    stats = provider.bandStatistics(1)
    min = stats.minimumValue

    max = stats.maximumValue
    range = max - min
    add = range / 2
    interval = min + add
    valueList = [min, interval, max]

    # Flood maps
    if style == 0:
        if stats.minimumValue <= 0.001:
            min = 0.001
        color_list = [QColor(colDic["lightblue"]), QColor(colDic["blue"]), QColor(colDic["darkblue"])]
        set_renderer(layer, color_list, myRasterShader, min, max)

    # Velocity
    elif style == 1:
        if stats.minimumValue <= 0.001:
            min = 0.001
        color_list = [QColor(colDic["lightgreen"]), QColor(colDic["green"]), QColor(colDic["darkgreen"])]
        set_renderer(layer, color_list, myRasterShader, min, max)

    # Hydrodynamic Risk ARR
    elif style == 2:
        color_list = [
            QColor().fromRgb(255, 0, 0, 0),
            QColor(colDic["arr1"]),
            QColor(colDic["arr2"]),
            QColor(colDic["arr3"]),
            QColor(colDic["arr4"]),
            QColor(colDic["arr5"]),
            QColor(colDic["arr6"]),
        ]
        set_renderer(layer, color_list, myRasterShader, min, max)

    # Time variables TODO: Improve this in next versions
    elif style == 3:
        layer.loadNamedStyle(style_directory + r"\time.qml")

    # Flow
    elif style == 4:
        if stats.minimumValue <= 0.001:
            min = 0.001
        color_list = [QColor(colDic["white"]), QColor(colDic["lightblue"]), QColor(colDic["blue"])]
        set_renderer(layer, color_list, myRasterShader, min, max)

    # Mudflow
    elif style == 5:
        if stats.minimumValue <= 0.001:
            min = 0.001
        color_list = [QColor(colDic["mud_lightbrown"]), QColor(colDic["mud_brown"]), QColor(colDic["mud_darkbrown"])]
        set_renderer(layer, color_list, myRasterShader, min, max)

    # Ground Elevation
    elif style == 6:
        color_list = [
            QColor(colDic["elev1"]),
            QColor(colDic["elev2"]),
            QColor(colDic["elev3"]),
            QColor(colDic["elev4"]),
            QColor(colDic["elev5"]),
            QColor(colDic["elev6"]),
            QColor(colDic["elev7"]),
            QColor(colDic["elev8"])
        ]
        set_renderer(layer, color_list, myRasterShader, min, max)

    # Derived
    elif style == 7:
        if stats.minimumValue <= 0.001:
            min = 0.001
        color_list = [QColor(colDic["dv1"]), QColor(colDic["dv2"]), QColor(colDic["dv3"])]
        set_renderer(layer, color_list, myRasterShader, min, max)

    # Static Pressure
    elif style == 8:
        if stats.minimumValue <= 0.001:
            min = 0.001
        color_list = [QColor(colDic["blue"]), QColor(colDic["yellow"]), QColor(colDic["red"])]
        set_renderer(layer, color_list, myRasterShader, min, max)

    # Specific Energy
    elif style == 9:
        if stats.minimumValue <= 0.001:
            min = 0.001
        color_list = [QColor(colDic["green"]), QColor(colDic["yellow"]), QColor(colDic["red"])]
        set_renderer(layer, color_list, myRasterShader, min, max)

    # Sediment
    elif style == 10:
        color_list = [QColor().fromRgb(255, 0, 0, 0), QColor(colDic["sed1"]), QColor(colDic["sed3"])]
        set_renderer(layer, color_list, myRasterShader, min, max)

    # Levee Deficit
    elif style == 11:
        min = 0
        max = 4
        color_list = [
            QColor().fromRgb(255, 0, 0, 0),  # transparent
            QColor(colDic["yellow"]),
            QColor(colDic["risk_orange"]),
            QColor(colDic["orange"]),
            QColor(colDic["red"])
        ]
        set_renderer(layer, color_list, myRasterShader, min, max)

    # Max deposition
    elif style == 12:
        if stats.minimumValue <= 0.001:
            min = 0.001
        color_list = [QColor(colDic["green"]), QColor(colDic["yellow"]), QColor(colDic["red"])]
        set_renderer(layer, color_list, myRasterShader, min, max)

    # Max scour
    elif style == 13:
        if stats.maximumValue == 0:
            max = -0.001
        color_list = [QColor(colDic["red"]), QColor(colDic["yellow"]), QColor(colDic["green"])]
        set_renderer(layer, color_list, myRasterShader, min, max)

    # Final bed difference
    elif style == 14:
        range_distance = max - min
        zero_position = 0 - min
        normalized_position = zero_position / range_distance

        color_ramp = QgsGradientColorRamp(
            QColor(QColor(colDic["blue"])),
            QColor(QColor(colDic["red"])),
            discrete=False, stops=[
                QgsGradientStop(normalized_position, QColor(colDic["green"])),
            ])

        myPseudoRenderer = QgsSingleBandPseudoColorRenderer(
            layer.dataProvider(), layer.type(), myRasterShader
        )

        myPseudoRenderer.setClassificationMin(min)
        myPseudoRenderer.setClassificationMax(max)
        myPseudoRenderer.createShader(color_ramp, clip=True)
        layer.setRenderer(myPseudoRenderer)

    layer.triggerRepaint()


def remove_layer(layer_name):
    """Function to remove layer name based on name"""
    for layer in QgsProject.instance().mapLayers().values():
        if layer.name() == layer_name:
            QgsProject.instance().removeMapLayers([layer.id()])


def set_velocity_vector_style(layer_name, vector_scale):
    """
    Function to set the velocity vector style
    """
    vector_style_directory = os.path.dirname(os.path.realpath(__file__))[:-8] + r"\vector_styles"

    svg_symbol_layer = QgsSvgMarkerSymbolLayer(vector_style_directory + r"\Arrow_06.svg")

    svg_symbol_layer.setDataDefinedProperty(QgsSymbolLayer.PropertyAngle,
                                            QgsProperty().fromField("Direction"))

    expression = f'"Velocity" * {vector_scale}'
    svg_symbol_layer.setDataDefinedProperty(QgsSymbolLayer.PropertyHeight,
                                            QgsProperty().fromExpression(expression))
    svg_symbol_layer.setDataDefinedProperty(QgsSymbolLayer.PropertyWidth,
                                            QgsProperty().fromValue(4, True))
    svg_symbol_layer.setDataDefinedProperty(QgsSymbolLayer.PropertyStrokeWidth,
                                            QgsProperty().fromValue(0, True))

    # Create a symbol using the SVGMarker layer
    symbol = QgsSymbol.defaultSymbol(layer_name.geometryType())  # Assuming your layer is a point layer
    symbol.changeSymbolLayer(0, svg_symbol_layer)

    # Create a graduated symbol renderer
    renderer = QgsGraduatedSymbolRenderer()
    renderer.setClassAttribute("Velocity")

    # Set up the color ramp and classification
    default_style = QgsStyle().defaultStyle()
    color_ramp = default_style.colorRamp("Turbo")
    n_classes = 10
    classification = QgsClassificationQuantile()

    # Update classes and color ramp
    renderer.updateClasses(layer_name, n_classes)
    renderer.updateColorRamp(color_ramp)
    renderer.setClassificationMethod(classification)

    # Set the symbol for the renderer
    renderer.setSourceSymbol(symbol)
    renderer.updateClasses(layer_name, n_classes)

    # Set the renderer to the layer
    layer_name.setRenderer(renderer)

    # Refresh the layer to apply the changes
    layer_name.triggerRepaint()


def set_renderer(layer, color_list, raster_shader, min, max):
    """
    Function to set the render to layer
    """ ""
    # Three colors -> all layers
    if len(color_list) == 3:
        color_ramp = QgsGradientColorRamp(
            QColor(color_list[0]),
            QColor(color_list[2]),
            discrete=False,
            stops=[
                QgsGradientStop(0.5, QColor(color_list[1])),
            ],
        )
    # Levee Deficit
    elif len(color_list) == 5:
        color_ramp = QgsGradientColorRamp(
            QColor(color_list[0]),
            QColor(color_list[4]),
            discrete=False,
            stops=[
                QgsGradientStop(0.25, QColor(color_list[1])),
                QgsGradientStop(0.50, QColor(color_list[2])),
                QgsGradientStop(0.75, QColor(color_list[3])),
            ],
        )
    # ARR
    elif len(color_list) == 7:
        color_ramp = QgsGradientColorRamp(
            QColor(color_list[0]),
            QColor(color_list[6]),
            discrete=False,
            stops=[
                QgsGradientStop(0.167, QColor(color_list[1])),
                QgsGradientStop(0.333, QColor(color_list[2])),
                QgsGradientStop(0.50, QColor(color_list[3])),
                QgsGradientStop(0.667, QColor(color_list[4])),
                QgsGradientStop(0.833, QColor(color_list[5])),
            ],
        )
    # Ground elevation
    else:
        color_ramp = QgsGradientColorRamp(
            QColor(color_list[0]),
            QColor(color_list[7]),
            discrete=False,
            stops=[
                QgsGradientStop(0.143, QColor(color_list[1])),
                QgsGradientStop(0.286, QColor(color_list[2])),
                QgsGradientStop(0.429, QColor(color_list[3])),
                QgsGradientStop(0.572, QColor(color_list[4])),
                QgsGradientStop(0.715, QColor(color_list[5])),
                QgsGradientStop(0.858, QColor(color_list[6])),
            ],
        )

    myPseudoRenderer = QgsSingleBandPseudoColorRenderer(
        layer.dataProvider(), layer.type(), raster_shader
    )

    myPseudoRenderer.setClassificationMin(min)
    myPseudoRenderer.setClassificationMax(max)
    myPseudoRenderer.createShader(color_ramp, clip=True)

    layer.setRenderer(myPseudoRenderer)
