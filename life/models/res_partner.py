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
from openerp.tools import float_compare, float_round

from math import floor

_logger = logging.getLogger(__name__)

class Partner(models.Model):
    '''Partner'''
    _inherit = 'res.partner'

    employee_ident = fields.Char(string="Employee Id")
    grade_id = fields.Many2one("life.grade",string="Grade")
    pay_grid_id = fields.Many2one("life.pay_grid",string="Pay Grid")

    sex = fields.Selection([('m', 'Male'),('f', 'Female')])
    family_status = fields.Selection([('s', 'Solo'),('m', 'Married'),('c', 'Legal cohabitor')])
    birthdate = fields.Date(string="Birthdate")
    partner_birthdate = fields.Date(string="Partner Birthdate")
    children = fields.Integer(string="Number of children")

    service_from = fields.Date(string="Service From")
    retirement_date = fields.Date(string="Retirement Date")
    annual_pay = fields.Float(string="Annual Pay",digits_compute=dp.get_precision('Financial Amount'))
    activity_percentage = fields.Float(string="Activity Percentage",default=1)
    salary_index = fields.Float(string="Salary Index",digits=(7, 6))
    
    # Computed fields
    
    complete_career_duration = fields.Float(string="Complete Career", compute="compComputePersonnalFields")
    remaining_career_duration = fields.Float(string="Remaining Career", compute="compComputePersonnalFields")
    accomplished_career_duration = fields.Float(string="Remaining Career", compute="compComputePersonnalFields")
    t5 = fields.Float(string="T5",compute="compComputePersonnalFields")

    policy_ids = fields.One2many('life.policy','policy_holder_id',string='Policies')
    career_history_ids = fields.One2many('life.career_history', 'partner_id', string="Career History")

    @api.one
    @api.depends('retirement_date','service_from','annual_pay')
    def compComputePersonnalFields(self):
        # TODO : compute the career duration in complete year, shoud be a fragment ?
        if self.retirement_date and self.service_from :
            dt_retirement_date = datetime.strptime(self.retirement_date, DEFAULT_SERVER_DATE_FORMAT)
            dt_service_from = datetime.strptime(self.service_from, DEFAULT_SERVER_DATE_FORMAT)
            self.complete_career_duration = float_round((dt_retirement_date-dt_service_from).days/365.25, precision_digits=dp.get_precision('Career'))
        else:
            self.complete_career_duration = None
        # TODO : compute the career duration in complete year, shoud be a fragment ?
        if self.retirement_date :
            dt_retirement_date = datetime.strptime(self.retirement_date, DEFAULT_SERVER_DATE_FORMAT)
            self.remaining_career_duration = (dt_retirement_date - datetime.now()).days/365.25
        else :
            self.remaining_career_duration = None
        if self.complete_career_duration and self.remaining_career_duration :
            self.accomplished_career_duration = self.complete_career_duration - self.remaining_career_duration
            self.t5 = self.annual_pay + floor(self.remaining_career_duration) * 500 - (5 * 500) / 2
        else :
            self.accomplished_career_duration = None
            self.t5 = None

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

class Grade(models.Model):
    '''Grade'''
    _name = 'life.grade'
    _description = 'Grade'

    name = fields.Char(string="Name")

class PayGrid(models.Model):
    '''Pay Grid'''
    _name = 'life.pay_grid'
    _description = 'Pay Grid'

    name = fields.Char(string="Name")
