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

from openerp import api, fields, models, _
from openerp.exceptions import UserError

_logger = logging.getLogger(__name__)

class Course(models.Model):
    '''Course'''
    _name = 'school.course'
    _inherit = ['mail.thread']
    
    code = fields.Char(required=True, string='Code', size=8)
    name = fields.Char(required=True, string='Name')
    description = fields.Text(required=True, string='Description')
    
    credits = fields.Integer(required=True, string = 'Credits')
    hours = fields.Integer(required=True, string = 'Hours')
    
    notes = fields.Text(string='Notes')
    
    program_ids = fields.Many2many('school.program', 'school_course_program_rel', id1='course_id', id2='program_id', string='Programs')
    
class Program(models.Model):
    '''Progral'''
    _name = 'school.program'
    _inherit = ['mail.thread']
    
    @api.one
    @api.depends('course_ids')
    def _get_courses_total(self):
        total_hours = 0.0
        total_credits = 0.0
        for course in self.course_ids:
            total_hours += course.hours
            total_credits += course.credits
        self.total_hours = total_hours
        self.total_credits = total_credits
        
    code = fields.Char(required=True, string='Code', size=8)
    name = fields.Char(required=True, string='Name')
    description = fields.Text(required=True, string='Description')
    
    total_credits = fields.Integer(compute='_get_courses_total', string='Total Credits')
    total_hours = fields.Integer(compute='_get_courses_total', string='Total Hours')
    
    notes = fields.Text(string='Notes')
    
    course_ids = fields.Many2many('school.course', 'school_course_program_rel', id1='program_id', id2='course_id', string='Courses')