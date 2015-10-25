#!python3
# -*- coding: utf-8 -*-

# Android SVG to Android Resource
# Requires:
#   inkscape
#   pngout

import os
import glob
import xml.etree.ElementTree as ET
import subprocess
import platform
import sys
import shelve
import settings

print('RES Builder')
print('----------------------------------------------------------')

# Get inkscape path
if len(settings.inkspace_path) == 0:
    print('Invalid inkspace path. Aborted.')
    exit(-1)
else:
    sys.path.insert(0, settings.inkspace_path)

# Check if PngOut optimization is necessary
if settings.pngout_optmize == 1:
    settings.pngout_optmize = 1
else:
    settings.pngout_optmize = 0

# Target DPI:
# [0.75, 1.0, 1.5, 2.0, 3.0, 4.0]
# ['ldpi', 'mdpi', 'hdpi', 'xhdpi', 'xxhdpi', 'xxxhdpi']
base_dpi = 1.0
dpis_str = ['ldpi', 'mdpi', 'hdpi', 'xhdpi', 'xxhdpi', 'xxxhdpi']
dpis = [0.75/base_dpi, 1.0/base_dpi, 1.5/base_dpi, 2.0/base_dpi, 3.0/base_dpi, 4.0/base_dpi]

print('Densities: ')
print(dpis_str)

# Get target files.
files = glob.glob(settings.input_path + '*.svg')

print('Found ' + str(len(files)) + ' file(s).')
print('Output: ' + settings.output_path)

print('\nWorking:')

for svg in files:
    tree = ET.parse(svg)
    root = tree.getroot()
    widthStr = root.attrib['width']
    heightStr = root.attrib['height']
    
    if widthStr.find('%') != -1:
        viewBox = root.attrib['viewBox'].split(' ')
        widthStr = viewBox[2]
        heightStr = viewBox[3]

    width = float(widthStr)
    height = float(heightStr)

    for index in range(len(dpis)):
        dpi = dpis[index]
        dpi_str = dpis_str[index]

        print(svg.replace(settings.output_path, '') + ' > ' + dpi_str)

        twidth = float(round(width * dpi))
        theight = float(round(height * dpi))

        target = os.path.basename(svg)
        target = target.replace('.svg', '.png')
        target = target.lower()

        if(target == 'ic_launcher.png'):
            current_path = settings.output_path + '/mipmap-' + dpi_str + '/'
        else:
            current_path = settings.output_path + '/drawable-' + dpi_str + '/'

        if not os.path.exists(current_path):
            os.makedirs(current_path)

        subprocess.call([settings.inkspace_path,
                         '--without-gui',
                         '-z',
                         '-e',
                         current_path + target,
                         '-f' + svg,
                         '-w ' + str(twidth),
                         '-h' + str(theight)])