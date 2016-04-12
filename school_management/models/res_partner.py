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
from openerp.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

class Partner(models.Model):
    '''Partner'''
    _inherit = 'res.partner'
    
    student = fields.Boolean("Student",default=False)
    teacher = fields.Boolean("Teacher",default=False)
    employee = fields.Boolean("Teacher",default=False)
    
    sex = fields.Selection([('m', 'Male'),('f', 'Female')])
    birthdate = fields.Date(string="Birthdate")
    
    minerval_ids = fields.One2many('school.minerval', 'student_id', string='Minerval')
    has_paid_current_minerval = fields.Boolean(compute='_has_paid_current_minerval',string="Has paid current minerval")
    student_current_program_id = fields.Many2one('school.bloc', compute='_get_student_current_program_id', string='Program')
    
    teacher_current_assigment_ids = fields.One2many('school.assignment', compute='_get_teacher_current_assigment_ids', string="Current Assignments")
    
    @api.one
    @api.depends('minerval_ids')
    def _has_paid_current_minerval(self):
        current_year_id = safe_eval(self.env['ir.config_parameter'].get_param('school.current_year_id','1'))
        res = self.env['school.minerval'].search([['year_id', '=', current_year_id], ['student_id', '=', self.id]])
        self.has_paid_current_minerval = len(res) > 0
        
    @api.one
    @api.depends('has_paid_current_minerval')
    def pay_current_minerval(self):
        if not self.has_paid_current_minerval:
            current_year_id = safe_eval(self.env['ir.config_parameter'].get_param('school.current_year_id','1'))
            self.env['school.minerval'].create({'student_id': self.id,'year_id': current_year_id})
        
    @api.one
    def _get_student_current_program_id(self):
        current_year_id = safe_eval(self.env['ir.config_parameter'].get_param('school.current_year_id','1'))
        res = self.env['school.individual_bloc'].search([['year_id', '=', current_year_id], ['student_id', '=', self.id]])
        if len(res) > 0:
            self.student_current_program_id = res[0].source_bloc_id
    
    @api.one
    def _get_teacher_current_assigment_ids(self):
        current_year_id = safe_eval(self.env['ir.config_parameter'].get_param('school.current_year_id','1'))
        res = self.env['school.assignment'].search([['year_id', '=', current_year_id], ['teacher_id', '=', self.id]])
        self.teacher_current_assigment_ids = res
        
class Minerval(models.Model):
    '''Minerval'''
    _name = 'school.minerval'
    
    year_id = fields.Many2one('school.year', string='Year', readonly=True)
    student_id = fields.Many2one('res.partner', string='Student', domain="[('student', '=', '1')]", readonly=True)
    payment_date = fields.Date(string='Payment Date',default=fields.Date.context_today)