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

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil.relativedelta import relativedelta
from datetime import datetime,date
import openerp.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)

class PolicySheetWizard(models.TransientModel):
    _name = "life.salary.wizard"
    _description = "Life Salary Wizard"
    
    insured_person_id = fields.Many2one('res.partner', string='Insured Person', readonly=True, default=lambda self: self.env['res.partner'].browse(self.env.context.get('active_ids', [])))
    
    salary_index = fields.Float(related="insured_person_id.salary_index",readonly=True)
    
    current_pay_grid_id = fields.Many2one(related="insured_person_id.pay_grid_id",readonly=True)
    current_grade = fields.Integer(related="insured_person_id.grade",readonly=True)
    current_annual_pay = fields.Float(related="insured_person_id.annual_pay",readonly=True)
    
    new_pay_grid_id = fields.Many2one("life.pay_grid",string="Pay Grid", default=lambda self: self.env['res.partner'].browse(self.env.context.get('active_ids', [])).pay_grid_id)
    new_grade = fields.Integer(string="Grade", default=lambda self: self.env['res.partner'].browse(self.env.context.get('active_ids', [])).grade)
    new_annual_pay = fields.Float(string="Annual Pay",compute="compSalary",digits=dp.get_precision('Financial Amounts'))
    
    @api.one
    @api.depends('new_grade','new_pay_grid_id','salary_index')
    def compSalary(self):
        self.new_annual_pay = self.new_pay_grid_id.getSalaryForGrade(self.new_grade) * self.salary_index
        
    @api.multi
    def apply_salary(self):
        self.ensure_one()
        self.insured_person_id.pay_grid_id = self.new_pay_grid_id
        self.insured_person_id.grade = self.new_grade