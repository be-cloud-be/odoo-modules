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

_logger = logging.getLogger(__name__)

class PolicySheetWizard(models.TransientModel):
    _name = "life.policy.wizard"
    _description = "Life Policy Wizard"

    policy_holder_id = fields.Many2one('res.partner', string='Policy Holder', readonly=True, default=lambda self: self.env['res.partner'].browse(self.env.context.get('active_ids', [])))
    policy_id = fields.Many2one('life.policy',string='Select a Policy')#,default=lambda self: self.env['life.policy'].search([('policy_holder_id', '=',self.policy_holder_id)])[0])
    reporting_date = fields.Date(string='Reporting Date')

    @api.multi
    @api.depends('policy_holder_id','policy_id','reporting_date')
    def generate_policy_sheet(self):
        self.ensure_one()
        data = {}
        data['id'] = self.id
        return self.env['report'].get_action(self, 'life.report_policy_sheet', data=data)
        
    # Computed amounts

    accomplished_career_duration = fields.Float(string="Accomplished Career Duration",compute="compPolicyAmountsAtReportingDate")
    life_earned_capital = fields.Float(string="Projected Capital",compute="compPolicyAmountsAtReportingDate")
    life_earned_reserve = fields.Float(string="Life Annuity",compute="compPolicyAmountsAtReportingDate")
   
    @api.one
    @api.depends('reporting_date','policy_id','policy_holder_id.service_from','policy_holder_id.complete_career_duration','policy_id.projected_life_capital')
    def compPolicyAmountsAtReportingDate(self):
        if self.policy_holder_id.service_from and self.reporting_date:
            dt_service_from = datetime.strptime(self.policy_holder_id.service_from, DEFAULT_SERVER_DATE_FORMAT)
            dt_reporting_date = datetime.strptime(self.reporting_date, DEFAULT_SERVER_DATE_FORMAT)
            self.accomplished_career_duration = (dt_reporting_date-dt_service_from).days/365.25
            if self.policy_id :
                self.life_earned_capital = self.accomplished_career_duration / self.policy_holder_id.complete_career_duration * self.policy_id.projected_life_capital
                self.life_earned_reserve = self.life_earned_capital * float(self.env['ir.config_parameter'].get_param("life.nex"))
        
        
        
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