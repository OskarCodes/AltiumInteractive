import matplotlib.pyplot as plt
import csv
import os
import sys
import ezdxf
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QIcon, QPainter, QBrush, QPen
from PyQt5.QtCore import Qt
import math
from typing import Iterable, cast, Union, List
from ezdxf.lldxf import const
from ezdxf.addons.drawing.backend import Backend
from ezdxf.addons.drawing.properties import (
    RenderContext, VIEWPORT_COLOR, Properties, set_color_alpha, Filling
)
from ezdxf.addons.drawing.text import simplified_text_chunks
from ezdxf.addons.drawing.utils import get_tri_or_quad_points
from ezdxf.entities import (
    DXFGraphic, Insert, MText, Polyline, LWPolyline, Spline, Hatch, Attrib,
    Text, Polyface, Wipeout,
)
from ezdxf.entities.dxfentity import DXFTagStorage, DXFEntity
from ezdxf.layouts import Layout
from ezdxf.math import Vector, Z_AXIS
from ezdxf.render import MeshBuilder, TraceBuilder, Path
from ezdxf import reorder

# Replace the variables below with the file paths you are using
projectname = 'SDSense'
csvdir = 'C:/Users/Public/Documents/Altium/Projects/' + projectname + '/Project Outputs for ' + projectname + '/Pick Place for ' + projectname + '.csv'
dxfdir = 'C:/Users/Public/Documents/Altium/Projects/' + projectname + '/' + projectname + '.dxf'

# What row the data starts in the P&P CSV file... Really bad way of doing it but I'm just testing around here =)
startrow = 14
render_layers = ['Mechanical1', 'Mechanical5', 'Mechanical15', 'Mechanical16', 'Mechanical42']

try:
    doc = ezdxf.readfile(dxfdir)
except IOError:
    print(f'Not a DXF file or a generic I/O error.')
except ezdxf.DXFStructureError:
    print(f'Invalid or corrupted DXF file.')

msp = doc.modelspace()


def getCentres():
    # This gets the centres of each component from the P&P CSV. No usage of this as of yet though
    xval = []
    yval = []
    with open(csvdir, newline='') as parameters:
        read = csv.reader(parameters, delimiter=',', quotechar='"')
        x = 0
        for row in read:
            if x < (startrow - 1):
                x += 1
                continue
            x += 1
            xval.append(float(row[4]))
            yval.append(float(row[5]))
    return xval, yval


def linedrawer(painter, scaler, boardlen, boardwid):
    # Right now this is disabled as I am just testing the Hatch drawing
    """for e in msp:
        print(e.dxftype())"""
    """for e in msp.query("CIRCLE"):
        ocs = e.ocs()
        radius = e.dxf.radius
        wcs_center = ocs.to_wcs(e.dxf.center)
        painter.drawEllipse(wcs_center[0] * scaler, wcs_center[1] * scaler, (radius / 2) * scaler,
                            (radius / 2) * scaler)"""

    for e in msp.query('LINE'):
        if e.dxf.layer in render_layers:
            start = e.dxf.start
            end = e.dxf.end
            startx = start[0] * scaler
            starty = start[1] * scaler
            endx = end[0] * scaler
            endy = end[1] * scaler
            # Right now this is disabled as I am just testing the Hatch drawing
            # painter.drawLine(startx, starty, endx, endy)
    for hatch in msp:
        try:
            if hatch.dxftype() == "HATCH" and hatch.dxf.layer in render_layers:
                ocs = hatch.ocs()
                for p in hatch.paths:
                    # For each path of a hatch
                    if p.PATH_TYPE == 'EdgePath':
                        path = Path.from_hatch_edge_path(p, ocs, 0)
                        for counter, vector in enumerate(path.approximate()):
                            if counter == 0:
                                oldvector = vector
                            sxs = vector[0] * scaler
                            sys = (boardlen - vector[1]) * scaler
                            sxe = oldvector[0] * scaler
                            sye = (boardlen - oldvector[1]) * scaler
                            oldvector = vector
                            painter.drawLine(sxs, sys, sxe, sye)
        except:
            print("Error!")
            continue
    for region in msp:
        try:
            if region.dxftype() == "REGION" and region.dxf.layer in render_layers:
                print("REGION found")
        except:
            print("Error!")
            continue


class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'AltiumInteractive'

        # How many times larger than the board should the window be?
        self.scaler = 25

        # Board dimensions in mm
        self.boardlen = 35
        self.boardwid = 34

        self.height = self.boardlen * self.scaler
        self.width = self.boardwid * self.scaler

        # Padding values
        self.left = 10
        self.top = 10

        self.xvals = []
        self.yvals = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)

        # Sets window dimensions to board dimensions multiplied by scaler
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        self.xvals, self.yvals = getCentres()
        for counter, x in enumerate(self.xvals):
            y = self.yvals[counter]
            y = self.boardlen - y
            x *= self.scaler
            y *= self.scaler
            painter.drawEllipse(x, y, 5, 5)
        linedrawer(painter, self.scaler, self.boardlen, self.boardwid)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())

# plt.scatter(xval, yval)
# plt.show()
