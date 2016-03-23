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
    'name': 'Life',
    'category' : 'Accounting & Finance',
    'version': '0.1',
    'license': 'AGPL-3',
    'author': 'be-cloud.be (Jerome Sonnet)',
    'description' : """
Module to manage life insurance contracts.
==========================================

    """,
    'data': ['wizard/policy_sheet_wizard_view.xml',
             'wizard/salary_wizard_view.xml',
             'views/res_partner_view.xml',
             'views/policy.xml',
             'report/report_policy_sheet.xml',
             'data/actuarial_factor.xml',
             #'security/ir.model.access.csv',
             ],
    'depends': ['mail', 'report','decimal_precision'],
    'demo': [],
    'auto_install': False,
    'installable': True,
    'application': True,
}
