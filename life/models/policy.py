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

class Policy(models.Model):
    '''Policy'''
    _name = 'life.policy'
    _description = 'Policy'

    number = fields.Integer(string="Policy Number")
    insured_person_id = fields.Many2one('res.partner',string='Insured Person')
    policy_holder_id = fields.Many2one('res.partner',string='Policy Holder',store='True',compute='_compute_policy_holder_id')
    
    @api.one
    @api.depends('insured_person_id.parent_id')
    def _compute_policy_holder_id(self):
        if self.insured_person_id.parent_id:
            self.policy_holder_id = self.insured_person_id.parent_id
    
    name = fields.Char(string="Name",compute='_compute_name')

    @api.one
    @api.depends('policy_holder_id','number')
    def _compute_name(self):
        self.name = "%s - %s" % (self.policy_holder_id.name,self.number)
    
    life_type = fields.Selection([('pure', 'Pure endowment')],string = "Life Type")
    life_number = fields.Integer(string="Life Policy Number")
    death_type = fields.Selection([('oneterm', 'One-year term insurance')],string = "Death Type")
    death_number = fields.Integer(string="Death Policy Number")

    # Computed amounts

    term_year = fields.Integer(string="Term Year",compute="compPolicyAmounts")
    projected_life_capital = fields.Float(string="Projected Capital",compute="compPolicyAmounts",digits=dp.get_precision('Financial Amounts'))
    projected_life_annuity = fields.Float(string="Projected Equivalent Annuity",compute="compPolicyAmounts",digits=dp.get_precision('Financial Amounts'))
    
    orphan_annuity_capital = fields.Float(string="Orphan Annuity Capital",compute="compPolicyAmounts",digits=dp.get_precision('Financial Amounts'))
    orphan_annuity_per_child = fields.Float(string="Orphan Annuity By Child",compute="compPolicyAmounts",digits=dp.get_precision('Financial Amounts'))
    orphan_annuity = fields.Float(string="Orphan Annuity",compute="compPolicyAmounts",digits=dp.get_precision('Financial Amounts'))
    death_capital = fields.Float(string="Death Capital",compute="compPolicyAmounts",digits=dp.get_precision('Financial Amounts'))
    death_unique_premium = fields.Float(string="Death Unique Premium",compute="compPolicyAmounts",digits=dp.get_precision('Financial Amounts'))
    
    @api.one
    @api.depends('insured_person_id.retirement_date','insured_person_id.complete_career_duration','insured_person_id.t5','insured_person_id.children','insured_person_id.annual_pay')
    def compPolicyAmounts(self):
        self.term_year = datetime.strptime(self.insured_person_id.retirement_date, DEFAULT_SERVER_DATE_FORMAT).year
        self.projected_life_capital = self.insured_person_id.complete_career_duration * self.insured_person_id.t5 / 10
        self.projected_life_annuity = self.projected_life_capital / float(self.env['ir.config_parameter'].get_param("life.annuityFactor"))
        self.orphan_annuity_capital = 0.5 * self.insured_person_id.children * self.insured_person_id.annual_pay
        self.orphan_annuity = self.orphan_annuity_capital / float(self.env['ir.config_parameter'].get_param("life.orphanAnnuityFactor"))
        self.orphan_annuity_per_child = self.orphan_annuity / self.insured_person_id.children
        self.death_capital = 2 * self.insured_person_id.annual_pay
        self.death_unique_premium = (self.death_capital + self.orphan_annuity_capital) * float(self.env['ir.config_parameter'].get_param("life.qx"))
        
    @api.one
    def compLifeUniquePremium(self, reporting_date):
        dt_reporting_date = datetime.strptime(reporting_date, DEFAULT_SERVER_DATE_FORMAT)
        self.life_unique_premium = float(self.env['ir.config_parameter'].get_param("life.nex")) * (self.compLifeEarnedCapital(dt_reporting_date) - self.compLifeEarnedCapital(dt_reporting_date + relativedelta(years = -1))) 
        
    @api.one
    @api.depends('projected_life_capital','insured_person_id','insured_person_id.complete_career_duration')
    def compLifeEarnedCapital(self, reporting_date):
        return self.insured_person_id.compAccomplishedCareerDuration(reporting_date) / self.insured_person_id.complete_career_duration * self.projected_life_capital