# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (c) 2010-2012 Elico Corp. All Rights Reserved.
#
#    Author: Yannick Gouin <yannick.gouin@elico-corp.com>
#            Jerome Sonnet <jerome.sonnet@be-cloud.be> port to 9.0
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    'name': 'Web Material',
    'version': '0.1',
    'category': 'Styling',
    'description': """
        This module use the materializecss to improve web client
        look and feel to Material Design.
    """,
    "author": "be-cloud.be (Jerome Sonnet)",
    "website": "http://www.be-cloud.be",
    'depends': ['web'],
    'init_xml': [],
    'data': ['web_material_view.xml'],
    'qweb' : [
        "static/src/xml/*.xml",
    ],
    'installable': True,
    'active': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: