#!python3
# -*- coding: utf-8 -*-

# The MIT License (MIT)
#
# Copyright (c) 2015 Lucas Nunes de Lima
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

#-------------------------------------------------------------------------------

# Android SVG to Android Resource
# Requires:
#   inkscape
#   pngout
#   python3 (of course)

import os
import glob
import xml.etree.ElementTree as ET
import subprocess
import platform
import sys
import shelve
import threading
import time
import settings
import ignore
import convert_jpg

print('RES Builder')
print('----------------------------------------------------------')

# Get inkscape path
if len(settings.inkscape_path) == 0:
    print('Invalid inkscape path. Aborted.')
    exit(-1)
else:
    sys.path.insert(0, settings.inkscape_path)

# Target DPI:
# [0.75, 1.0, 1.5, 2.0, 3.0, 4.0]
# ['ldpi', 'mdpi', 'hdpi', 'xhdpi', 'xxhdpi', 'xxxhdpi']
base_dpi = 1.0
dpis = {'ldpi' : 0.75 / base_dpi,  'mdpi' : 1.0 / base_dpi,
        'hdpi' : 1.5 / base_dpi,   'xhdpi' : 2.0 / base_dpi,
        'xxhdpi' : 3.0 / base_dpi, 'xxxhdpi' : 4.0 / base_dpi}

def do_work():
    lock = threading.Lock()
    while 1:
        with lock:
            if len(svgs) == 0:
                break
        process_svg()
        pass

def process_svg():
    global index
    lock = threading.Lock()

    with lock:
        if len(svgs) == 0:
            return
        svg = svgs[0]
        svgs.remove(svg)

    svg = os.path.normpath(svg)
    svg = svg.replace('\\\\','/').replace('\\','/').replace('//','/')

    tree = ET.parse(svg)
    root = tree.getroot()
    widthStr = root.attrib['width']
    heightStr = root.attrib['height']

    base_path = svg.replace(working_dir, '')
    print_name = base_path.replace(current_input_path, '')

    if widthStr.find('%') != -1:
        viewBox = root.attrib['viewBox'].split(' ')
        widthStr = viewBox[2]
        heightStr = viewBox[3]

    widthStr = widthStr.replace('px','')
    heightStr = heightStr.replace('px','')

    width = float(widthStr)
    height = float(heightStr)

    for index in range(len(settings.output_quality)):
        dpi_name = settings.output_quality[index]
        dpi = dpis[dpi_name]

        twidth = float(round(width * dpi))
        theight = float(round(height * dpi))

        target = os.path.basename(svg)
        target = target.replace('.svg', '.png')
        target = target.lower()

        ignore_it = False
        for ignored_file in ignore.files:
            if os.path.normpath(ignored_file) == os.path.normpath(base_path):
                ignore_it = True
                break

        thread_name = '[' + threading.current_thread().name + '] '

        if ignore_it:
            with lock:
                print(thread_name + print_name + ' > ignored')
            break
        else:
            with lock:
                print(thread_name + print_name + ' > ' + dpi_name)

        is_mipmap = 'ic_launcher' in os.path.normpath(base_path)
        is_adaptive = 'ic_launcher_adaptive' in os.path.normpath(base_path)

        if is_mipmap:
            if is_adaptive:
                current_path = current_output_path + '/mipmap-' + dpi_name + '-v26/'
            else:
                current_path = current_output_path + '/mipmap-' + dpi_name + '/'
        else:
            current_path = current_output_path + '/drawable-' + dpi_name + '/'

        if not os.path.exists(current_path):
            os.makedirs(current_path)

        work_target = current_path + target
        work_target = os.path.normpath(work_target)
        work_target = work_target.replace('\\\\','/').replace('\\','/').replace('//','/')
        
        if os.path.isfile(work_target) or os.path.isfile(work_target.replace('.png','.jpg')):
            continue

        ls = subprocess.Popen([settings.inkscape_path, svg, '-z',
                               '-e' + work_target,
                               '-w' + str(twidth),
                               '-h' + str(theight)],
                               shell = True,
                               stdout = subprocess.PIPE, stderr = subprocess.PIPE)

        ls.wait()

        if not is_mipmap:
            export_to_jpg = False
            for export_file in convert_jpg.files:
                if os.path.normpath(export_file) in os.path.normpath(base_path):
                    export_to_jpg = True
                    break

            if export_to_jpg:
                print(thread_name + print_name + ' > converted')
                ls = subprocess.Popen([settings.image_magick, work_target, '-quality', '50',
                                       work_target.replace('.png','.jpg')],
                           shell = True,
                           stdout = subprocess.PIPE, stderr = subprocess.PIPE)
                ls.wait()
                print(thread_name + print_name + ' > removed')
                os.remove(work_target)

## -------------

# Get target svgs.
for i in range(len(settings.input_path)):
    current_input_path = settings.input_path[i]

    if len(settings.output_path) == 1:
        current_output_path = settings.output_path[0]
    else:
        current_output_path = settings.output_path[i]

    svgs = []

    for root, dirs, files in os.walk(current_input_path):
        for file in files:
            if file.endswith('.svg'):
                print(os.path.join(root, file))
                svgs.append(os.path.join(root, file))

    #files = glob.glob(current_input_path + '*.svg')
    #files = files + glob.glob(current_input_path + '*/*.svg')

    print('Found ' + str(len(svgs)) + ' file(s).')
    print('Output: ' + current_output_path)

    print('\nWorking:')

    working_dir = os.path.dirname(os.path.abspath(__file__))
    working_dir = working_dir.replace('\\', '/')

    index = 0

    for index in range(len(settings.output_quality)):
        dpi_name = settings.output_quality[index]
        current_path = current_output_path + '/mipmap-' + dpi_name + '/'
        if not os.path.exists(current_path):
            os.makedirs(current_path)
        current_path = current_output_path + '/drawable-' + dpi_name + '/'
        if not os.path.exists(current_path):
            os.makedirs(current_path)

    threads = []

    for current_thread in range(settings.number_of_threads):
        try:
            tr = threading.Thread(target=do_work)
            tr.daemon = True
            tr.start()
            threads.append(tr)
        except:
            print('Error: unable to start thread')

    # join all threads
    for t in threads:
        t.join()
    pass
