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

from xml.dom import minidom
from xml.dom.minidom import Document

def prepare_svg(path, scale):
    xmldoc = minidom.parse(path)
    doc_root = xmldoc.documentElement

    itemlist = xmldoc.getElementsByTagName('rect')

    style = 'fill:#000000;fill-opacity:1;stroke:none;stroke-width:0.5;stroke-linecap:butt;stroke-linejoin:miter;stroke-miterlimit:0;stroke-dasharray:none;stroke-opacity:1'

    for s in itemlist:
        if(s.attributes['id'].value == 'horizontal_slices'):
            doc_root.removeChild(s)

            rect = xmldoc.createElement('rect')
            rect.setAttribute('style', style);
            rect.setAttribute('width', str(scale));
            rect.setAttribute('height', s.attributes['height'].value)
            rect.setAttribute('x', s.attributes['x'].value);
            rect.setAttribute('y', s.attributes['y'].value);
            doc_root.appendChild(rect)

            rect = xmldoc.createElement('rect')
            rect.setAttribute('style', style);
            rect.setAttribute('width', str(scale));
            rect.setAttribute('height', s.attributes['height'].value)
            rect.setAttribute('x', str(int(s.attributes['width'].value) - scale));
            rect.setAttribute('y', s.attributes['y'].value);
            doc_root.appendChild(rect)
        elif(s.attributes['id'].value == 'vertical_slices'):
            doc_root.removeChild(s)

            rect = xmldoc.createElement('rect')
            rect.setAttribute('style', style);
            rect.setAttribute('width', s.attributes['width'].value);
            rect.setAttribute('height', str(scale))
            rect.setAttribute('x', s.attributes['x'].value);
            rect.setAttribute('y', s.attributes['y'].value);
            doc_root.appendChild(rect)

            rect = xmldoc.createElement('rect')
            rect.setAttribute('style', style);
            rect.setAttribute('width', s.attributes['width'].value);
            rect.setAttribute('height', str(scale))
            rect.setAttribute('x', s.attributes['x'].value);
            rect.setAttribute('y', str(int(s.attributes['height'].value) - scale));
            doc_root.appendChild(rect)

    f = open(path.replace('.svg', '.temp.svg'),'w')
    f.write(xmldoc.toxml())
    f.close()

    return path.replace('.svg', '.temp.svg')
