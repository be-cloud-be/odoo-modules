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
    _name = "life.policy.wizard"
    _description = "Life Policy Wizard"

    insured_person_id = fields.Many2one('res.partner', string='Policy Holder', readonly=True, default=lambda self: self.env['res.partner'].browse(self.env.context.get('active_ids', [])))
    policy_id = fields.Many2one('life.policy',string='Select a Policy',default=lambda self: self.env['life.policy'].search([('insured_person_id', '=',self.env.context.get('active_ids', []))])[0])
    reporting_date = fields.Date(string='Reporting Date',default=lambda self: date(date.today().year, 1, 1))

    @api.multi
    def generate_policy_sheet(self):
        self.ensure_one()
        data = {}
        data['id'] = self.id
        return self.env['report'].get_action(self, 'life.report_policy_sheet', data=data)
        
    # Computed amounts

    accomplished_career_duration = fields.Float(string="Accomplished Career Duration",compute="compPolicyAmountsAtReportingDate", digits=dp.get_precision('Career'))
    life_earned_capital = fields.Float(string="Current Earned Capital",compute="compBenefitsAmountsAtReportingDate", digits=dp.get_precision('Financial Amounts'))
    life_earned_reserve = fields.Float(string="Current Earned Reserve",compute="compBenefitsAmountsAtReportingDate", digits=dp.get_precision('Financial Amounts'))
    
    policy_mr = fields.Float(string="Mathematical Reserve",compute="compPolicyAmountsAtReportingDate", digits=dp.get_precision('Financial Amounts'))
    policy_mr_bonus = fields.Float(string="Mathematical Reserve Bonus",compute="compPolicyAmountsAtReportingDate", digits=dp.get_precision('Financial Amounts'))
    policy_capital = fields.Float(string="Capital",compute="compPolicyAmountsAtReportingDate", digits=dp.get_precision('Financial Amounts'))
    policy_capital_bonus = fields.Float(string="Capital Bonus",compute="compPolicyAmountsAtReportingDate", digits=dp.get_precision('Financial Amounts'))
    policy_unique_premium = fields.Float(string="Policy Unique Premium",compute="compBenefitsAmountsAtReportingDate", digits=dp.get_precision('Financial Amounts'))
    
    
    #self.life_unique_premium = float(self.env['ir.config_parameter'].get_param("life.nex")) * (self.compLifeEarnedCapital(dt_reporting_date) - self.compLifeEarnedCapital(dt_reporting_date + relativedelta(years = -1))) 
   
    @api.one
    @api.depends('reporting_date','policy_id','insured_person_id.service_from','insured_person_id.complete_career_duration','policy_id.projected_life_capital')
    def compBenefitsAmountsAtReportingDate(self):
        if self.insured_person_id.service_from and self.reporting_date:
            dt_service_from = datetime.strptime(self.insured_person_id.service_from, DEFAULT_SERVER_DATE_FORMAT)
            dt_reporting_date = datetime.strptime(self.reporting_date, DEFAULT_SERVER_DATE_FORMAT)
            self.accomplished_career_duration = (dt_reporting_date-dt_service_from).days/365.25
            if self.policy_id :
                self.life_earned_capital = self.accomplished_career_duration / self.insured_person_id.complete_career_duration * self.policy_id.projected_life_capital
                self.life_earned_reserve = float(self.env['ir.config_parameter'].get_param("life.nex")) * self.life_earned_capital
                self.policy_unique_premium = float(self.env['ir.config_parameter'].get_param("life.nex")) * (self.life_earned_capital - (self.accomplished_career_duration-1) / self.insured_person_id.complete_career_duration * self.policy_id.projected_life_capital)
        
    @api.one
    @api.depends('life_earned_reserve','life_earned_capital')
    def compPolicyAmountsAtReportingDate(self):
        self.policy_mr = self.life_earned_reserve
        self.policy_mr_bonus = 0
        self.policy_capital = self.life_earned_capital
        self.policy_capital_bonus = 0

class ReportPolicySheet(models.AbstractModel):
    _name = 'report.life.report_policy_sheet'

    @api.multi
    def render_html(self, data):
        _logger.info('render_html')
        docargs = {
            'doc_ids': data['id'],
            'doc_model': 'life.policy.wizard',
            'docs': self.env['life.policy.wizard'].browse(data['id']),
        }
        return self.env['report'].render('life.report_policy_sheet', docargs)