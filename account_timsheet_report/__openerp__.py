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
    'name': 'Account Timesheet report',
    'version': '0.1',
    'category': 'Tools',
    'description': """
    Add a report on timesheet by customer.
    """,
    "author": "be-cloud.be (Jerome Sonnet)",
    "website": "http://www.be-cloud.be",
    'depends': ['account_reports'],
    'init_xml': [],
    'data': [
        'views/account_timsheet_report.xml',
    ],
    'images': [
        'static/src/img/*.png',
        'static/src/img/*.svg',
    ],
    'installable': True,
    'active': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: