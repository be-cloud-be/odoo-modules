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

from math import floor

_logger = logging.getLogger(__name__)

class Partner(models.Model):
    '''Partner'''
    _inherit = 'res.partner'

    employee_ident = fields.Char(string="Employee Id")
    grade = fields.Integer(string="Grade")
    pay_grid_id = fields.Many2one("life.pay_grid",string="Pay Grid")

    sex = fields.Selection([('m', 'Male'),('f', 'Female')])
    family_status = fields.Selection([('s', 'Solo'),('m', 'Maried'),('c', 'Legal cohabitor')])
    birthdate = fields.Date(string="Birthdate")
    partner_birthdate = fields.Date(string="Partner Birthdate")
    children = fields.Integer(string="Number of children")

    service_from = fields.Date(string="Service From")
    retirement_date = fields.Date(string="Retirement Date")
    activity_percentage = fields.Float(string="Activity Percentage",default=1)
    salary_index = fields.Float(string="Salary Index",digits=(7, 6))
    
    # Computed fields

    annual_pay = fields.Float(string="Annual Pay",compute="compSalary",digits=dp.get_precision('Financial Amounts'))

    complete_career_duration = fields.Float(string="Complete Career", compute="compComputePersonnalFields", digits=dp.get_precision('Career'))
    remaining_career_duration = fields.Float(string="Remaining Career", compute="compComputePersonnalFields", digits=dp.get_precision('Career'))
    accomplished_career_duration = fields.Float(string="Remaining Career", compute="compComputePersonnalFields", digits=dp.get_precision('Career'))
    final_annual_pay = fields.Float(string="Final Annual Pay",compute="compComputePersonnalFields", digits=dp.get_precision('Financial Amounts'))
    t5 = fields.Float(string="T5",compute="compComputePersonnalFields", digits=dp.get_precision('Financial Amounts'))

    policy_ids = fields.One2many('life.policy','insured_person_id',string='Policies')
    career_history_ids = fields.One2many('life.career_history', 'partner_id', string="Career History")

    @api.one
    @api.depends('grade','pay_grid_id','salary_index')
    def compSalary(self):
        self.annual_pay = self.pay_grid_id.getSalaryForGrade(self.grade) * self.salary_index

    @api.one
    @api.depends('retirement_date','service_from','annual_pay')
    def compComputePersonnalFields(self):
        # TODO : compute the career duration in complete year, shoud be a fragment ?
        if self.retirement_date and self.service_from :
            dt_retirement_date = datetime.strptime(self.retirement_date, DEFAULT_SERVER_DATE_FORMAT)
            dt_service_from = datetime.strptime(self.service_from, DEFAULT_SERVER_DATE_FORMAT)
            self.complete_career_duration = (dt_retirement_date-dt_service_from).days/365.25
        else:
            self.complete_career_duration = None
        # TODO : compute the career duration in complete year, shoud be a fragment ?
        if self.retirement_date :
            self.remaining_career_duration = self.compAccomplishedCareerDuration()[0]
        else :
            self.remaining_career_duration = None
        if self.complete_career_duration and self.remaining_career_duration :
            self.accomplished_career_duration = self.complete_career_duration - self.remaining_career_duration
            self.final_annual_pay = self.annual_pay + floor(self.remaining_career_duration) * 500
            self.t5 = self.final_annual_pay - (5 * 500) / 2
        else :
            self.accomplished_career_duration = None
            self.final_annual_pay = None
            self.t5 = None
            
    @api.one
    @api.depends('retirement_date','service_from')
    def compAccomplishedCareerDuration(self,reporting_date=None):
        if self.retirement_date and reporting_date:
            dt_retirement_date = datetime.strptime(self.retirement_date, DEFAULT_SERVER_DATE_FORMAT)
            if type(reporting_date) is not datetime.date:
                dt_reporting_date = datetime.strptime(reporting_date, DEFAULT_SERVER_DATE_FORMAT)
            else:
                dt_reporting_date = reporting_date
            return (dt_retirement_date - dt_reporting_date).days/365.25
        elif self.retirement_date:
            dt_retirement_date = datetime.strptime(self.retirement_date, DEFAULT_SERVER_DATE_FORMAT)
            return (dt_retirement_date - datetime.now()).days/365.25
        else:
            return -1

class CareerHistory(models.Model):
    '''Career History'''
    _name = 'life.career_history'
    _description = 'Career History'

    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    grade_id = fields.Many2one("life.grade",string="Grade")
    pay_grid_id = fields.Many2one("life.pay_grid",string="Pay Grid")
    function = fields.Char(string="Job Position")
    employer = fields.Many2one("res.partner",string="Employer",domain=[('is_company', '=', True)])

    partner_id = fields.Many2one('res.partner', required=True, string='Partner')

class PayGrid(models.Model):
    '''Pay Grid'''
    _name = 'life.pay_grid'
    _description = 'Pay Grid'

    name = fields.Char(string="Name")
    base_salary = fields.Float(string="Base Salary")
    salary_increment = fields.Float(string="Salary Increment")
    
    def getSalaryForGrade(self,grade):
        return self.base_salary + grade * self.salary_increment