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

class GroupEvaluation(models.Model):
    '''Group Evaluation'''
    _name = 'school.group_evaluation'
    _description = 'Group Evaluation'
    
    session_id = fields.Many2one('school.session', string='Session', required=True)
    student_id = fields.Many2one('res.partner', string='Student', domain="[('student', '=', '1')]", required=True)
    teacher_id = fields.Many2one('res.partner', string='Teacher', domain="[('teacher', '=', '1')]", required=True)
    course_group_id = fields.Many2one('school.course_group', string='Course Group', required=True)
    
    acquired = fields.Boolean(string='Acquired', required=True, default=False)
    
    _sql_constraints = [
	        ('uniq_evaluation', 'unique(session_id, student_id, course_group_id)', 'This evaluation already exists.'),
    ]
    
    result = fields.Float(string='result')

class Evaluation(models.Model):
    '''Evaluation'''
    _name = 'school.evaluation'
    _description = 'Evaluation'
    
    session_id = fields.Many2one('school.session', string='Session', required=True)
    student_id = fields.Many2one('res.partner', string='Student', domain="[('student', '=', '1')]", required=True)
    teacher_id = fields.Many2one('res.partner', string='Teacher', domain="[('teacher', '=', '1')]")
    course_id = fields.Many2one('school.course', string='Course', required=True)
    
    _sql_constraints = [
	        ('uniq_evaluation', 'unique(session_id, student_id, course_id)', 'This evaluation already exists.'),
    ]
    
    result = fields.Float(string='result')
    
class Session(models.Model):
    '''Session'''
    _name = 'school.session'
    _description = 'Session'
    
    year_id = fields.Many2one('school.year', string='Year')
    type = fields.Selection([('S1', 'Frist'),('S2', 'Second'),('F','Final')],string="Type")
    
    name = fields.Char(string='Name', compute='compute_name', store=True)
    
    @api.depends('year_id','type')
    @api.multi
    def compute_name(self):
        for session in self:
            session.name = "%s - %s" % (session.year_id.name, session.type)
            
    _sql_constraints = [
	        ('uniq_session', 'unique(year_id, type)', 'This session already exists.'),
    ]