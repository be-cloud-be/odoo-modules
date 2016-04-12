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
import logging

from openerp import api, fields, models, tools, _
from openerp.exceptions import MissingError

_logger = logging.getLogger(__name__)

class StudentReport(models.Model):
    _name = "school.student.report"
    _auto = False

    year_id = fields.Many2one('school.year', string="Year")
    student_id = fields.Many2one('res.partner', string="Student")
    program_id = fields.Many2one('school.program', string="Program")
    bloc_id = fields.Many2one('school.bloc', string="Bloc")
    sex = fields.Selection([('m', 'Male'),('f', 'Female')])
    has_paid_current_minerval = fields.Integer(string="Has paid current minerval")
    dispenses = fields.Integer(string="Dispenses")

    def init(self, cr):
        """ School Student main report """
        tools.drop_view_if_exists(cr, 'school_student_report')
        cr.execute(""" CREATE VIEW school_student_report AS (
            SELECT
                school_individual_bloc.id as id,
                school_year.id as year_id,
                res_partner.id as student_id,
                school_program.id as program_id,
                school_bloc.id as bloc_id,
                res_partner.sex as sex,
                (SELECT COUNT(school_minerval.id) from school_minerval WHERE school_minerval.student_id = res_partner.id AND school_minerval.year_id = school_year.id) AS has_paid_current_minerval,
                (SELECT COUNT(school_individual_course.id) from school_individual_course,school_individual_course_group WHERE school_individual_course.dispense = TRUE AND school_individual_course_group.bloc_id = school_individual_bloc.id AND school_individual_course.course_group_id = school_individual_course_group.id) as dispenses
            FROM
                school_individual_bloc,
                school_year,
                res_partner,
                school_program,
                school_bloc
            WHERE
                res_partner.student = TRUE AND
                school_individual_bloc.year_id = school_year.id AND
                school_individual_bloc.student_id = res_partner.id AND
                school_individual_bloc.source_bloc_id = school_bloc.id AND
                school_bloc.program_id = school_program.id
        )""")