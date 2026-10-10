import os
from qgis.core import ( # type: ignore
    QgsApplication, QgsProject, QgsVectorLayer,
    QgsMapSettings, QgsMapRendererCustomPainterJob, QgsLineSymbol
)
from PyQt5.QtSvg import QSvgGenerator # type: ignore
from PyQt5.QtGui import QPainter, QColor # type: ignore
from PyQt5.QtCore import QSize, QRectF # type: ignore

import xml.etree.ElementTree as ET
from datetime import datetime
import shutil
import re

# --- QGIS INIT ---
QgsApplication.setPrefixPath(r"C:\OSGeo4W\apps\qgis", True)
qgs = QgsApplication([], False)
qgs.initQgis()

# --- Paths ---
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

gpx_folder = os.path.join(project_root, "data", "gpx")
svg_folder = os.path.join(project_root, "data", "svg")
combined_folder = os.path.join(project_root, "data", "combined")
os.makedirs(svg_folder, exist_ok=True)
os.makedirs(combined_folder, exist_ok=True)

# --- SVG Export Settings ---
svg_size = QSize(1000, 1000)
background = QColor("transparent")
line_color = "#FC4C02"  # Strava-like orange-red
line_width = "0.5" # TODO  when printing the line is too faint, in Adobe Illustrator it shows as 0.183, change to ?

# --- STEP 0: Clear the svg_folder contents ---
for filename in os.listdir(svg_folder):
    file_path = os.path.join(svg_folder, filename)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)  # remove file or link
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)  # remove directory and all contents
    except Exception as e:
        print(f'Failed to delete {file_path}. Reason: {e}')

# --- STEP 1: Export each GPX to SVG ---
for file in os.listdir(gpx_folder):
    if file.endswith('.gpx'):
        gpx_path = os.path.join(gpx_folder, file)
        name = os.path.splitext(file)[0]
        uri = f"{gpx_path}|layername=tracks"
        layer = QgsVectorLayer(uri, name, "ogr")

        if not layer.isValid():
            print(f"Invalid layer: {file}")
            continue

        # Set a simple line symbol with your chosen color (e.g., black)
        symbol = QgsLineSymbol.createSimple({'color': line_color, 'width': line_width})  
        layer.renderer().setSymbol(symbol)
        layer.triggerRepaint()
        QgsProject.instance().addMapLayer(layer)

        if layer.extent().isEmpty():
            print(f"Empty extent: {file}")
            QgsProject.instance().removeMapLayer(layer)
            continue

        settings = QgsMapSettings()
        settings.setLayers([layer])
        settings.setOutputSize(svg_size)
        settings.setExtent(layer.extent())
        settings.setBackgroundColor(background)

        svg_file = os.path.join(svg_folder, f"{name}.svg")
        generator = QSvgGenerator()
        generator.setFileName(svg_file)
        generator.setSize(svg_size)
        generator.setViewBox(QRectF(0, 0, svg_size.width(), svg_size.height()))

        painter = QPainter(generator)
        job = QgsMapRendererCustomPainterJob(settings, painter)
        job.start()
        job.waitForFinished()
        painter.end()

        QgsProject.instance().removeMapLayer(layer)
        print(f"Exported: {svg_file}")

# --- QGIS Cleanup ---
qgs.exitQgis()
