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

class Evaluation(models.Model):
    '''Evaluation'''
    _name = 'school.evaluation'
    _description = 'Evaluation'
    
    year_id = fields.Many2one('school.year', string='Year')
    student_id = fields.Many2one('res.partner', string='Student', domain="[('student', '=', '1')]")
    teacher_id = fields.Many2one('res.partner', string='Teacher', domain="[('teacher', '=', '1')]")
    course_id = fields.Many2one('school.course', string='Course')
    
    result = fields.Float(string='result')