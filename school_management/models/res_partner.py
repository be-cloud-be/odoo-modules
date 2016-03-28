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
    
    student_program_id = fields.Many2one('school.program', string='Program')
    
    teacher_current_assigment_ids = fields.One2many('school.assignment', compute='_get_teacher_current_assigment_ids', string="Current Assignments")
    
    @api.one
    def _get_teacher_current_assigment_ids(self):
        current_year_id = safe_eval(self.env['ir.config_parameter'].get_param('school.current_year_id','1'))
        res = self.env['school.assignment'].search([['year_id', '=', current_year_id], ['teacher_id', '=', self.id]])
        self.teacher_current_assigment_ids = res