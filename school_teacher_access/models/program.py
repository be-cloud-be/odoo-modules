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
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import logging

from openerp import api, fields, models, tools, _
from openerp.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class view(models.Model):
    _name = 'ir.ui.view'
    _inherit = 'ir.ui.view'

    type = fields.Selection(selection_add=[('school_teacher_dashboard', 'Teacher Dashboard')])

class TeacherReport(models.Model):
    _name = "school.teacher.report"
    _auto = False

    name = fields.Char(string="Name", readonly=True)
    title = fields.Char(string="Title", readonly=True)
    year_id = fields.Many2one('school.year', string='Year', readonly=True)
    teacher_id = fields.Many2one('res.partner', string='Teacher', readonly=True)
    source_course_id = fields.Many2one('school.course', string="Source Course", readonly=True)
    student_count = fields.Integer(string="Student Count")
    dispenses = fields.Integer(string="Dispenses")
    waiting_dispenses = fields.Integer(string="Waiting Dispenses")

    def init(self, cr):
        """ School Teacher Report """
        tools.drop_view_if_exists(cr, 'school_teacher_report')
        cr.execute(""" CREATE VIEW school_teacher_report AS (
            SELECT
                CAST(CAST(school_individual_course.year_id AS text)||
                CAST(school_individual_course.teacher_id AS text)||
                CAST(school_individual_course.source_course_id AS text) AS INTEGER) as id,
                school_individual_course.name,
                school_individual_course.title,
                school_individual_course.year_id,
                school_individual_course.teacher_id,
                school_individual_course.source_course_id,
                COUNT(CAST(CAST(school_individual_course.year_id AS text)||
                CAST(school_individual_course.teacher_id AS text)||
                CAST(school_individual_course.source_course_id AS text) AS INTEGER)) as student_count,
                COUNT(CAST(CAST(school_individual_course.year_id AS text)||
                CAST(school_individual_course.teacher_id AS text)||
                CAST(school_individual_course.source_course_id AS text) AS INTEGER)) filter (where dispense = True) as dispenses,
                COUNT(CAST(CAST(school_individual_course.year_id AS text)||
                CAST(school_individual_course.teacher_id AS text)||
                CAST(school_individual_course.source_course_id AS text) AS INTEGER)) filter (where dispense = True and is_dispense_approved = False) as waiting_dispenses
            FROM
                school_individual_course
            WHERE
                school_individual_course.teacher_id IS NOT NULL
            GROUP BY CAST(CAST(school_individual_course.year_id AS text)||
                CAST(school_individual_course.teacher_id AS text)||
                CAST(school_individual_course.source_course_id AS text) AS INTEGER),
                school_individual_course.name,
                school_individual_course.title,
                school_individual_course.year_id,
                school_individual_course.teacher_id,
                school_individual_course.source_course_id
        )""")
        
    # @api.model
    # def retrieve_teacher_dashboard(self):
    #     teacher = self.env['res.users'].browse(self.env.uid).partner_id
    #     return {
    #         'teacher' : teacher,
    #     }