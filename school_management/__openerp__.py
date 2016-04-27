# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2015 be-cloud.be
#                       Jerome Sonnet <jerome.sonnet@be-cloud.be>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'School management',
    'version': '0.1',
    'license': 'AGPL-3',
    'author': 'be-Cloud.be (Jerome Sonnet)',
    'website': '',
    'category': 'Association',
    'depends': ['mail'],
    'init_xml': [],
    'update_xml': [
        'school_data.xml',
        'wizard/assignment_generation.xml',
        'wizard/assign_program.xml',
        'views/res_partner_view.xml',
        'views/program_view.xml',
        'views/course_session_view.xml',
        'views/individual_program_view.xml',
        'report/student_report.xml',
        'sequences/school_sequence.xml',
        'security/ir.model.access.csv',
    ],
    'demo_xml': [],
    'description': '''
        This modules add management tools for a school.
    ''',
    'active': False,
    'installable': True,
    'application': True,
}
