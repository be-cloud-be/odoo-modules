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

class PolicySheetWizard(models.TransientModel):
    _name = "life.policy.wizard"
    _description = "Life Policy Wizard"

    policy_holder_id = fields.Many2one('res.partner', string='Policy Holder', readonly=True, default=lambda self: self.env['res.partner'].browse(self.env.context.get('active_ids', [])))
    policy_id = fields.Many2one('life.policy',string='Select a Policy')#,domain=[('policy_holder_id', 'in', self.env.context.get('active_ids', []))])
    reporting_date = fields.Date(string='Reporting Date')

    @api.multi
    @api.depends('policy_holder_id','policy_id','reporting_date')
    def generate_policy_sheet(self):
        self.ensure_one()
        data = {}
        data['policy_holder_id'] = self.policy_holder_id.id
        data['policy_id'] = self.policy_id.id
        data['reporting_date'] = self.reporting_date
        return self.env['report'].get_action(self, 'life.report_policy_sheet', data=data)

    life_projected_capital = fields.Float(string="Life Projected Capital", compute="compLifeProjectedCapital")

    @api.multi
    def compLifeProjectedCapital(self):
        self.ensure_one()
        baseCapital = (self.policy_holder_id.retirement_date -  self.policy_holder_id.service_from) * self.compData.t5 / 10
        self.life_projected_capital = baseCapital

#     def compLifeAnnuity(self):
#         return self.compLifeProjectedCapital() / self.compData.annuityFactor
#
#     def compLifeEarnedCapital(self, career):
#         return float(career) / self.compData.totalCareer * self.compLifeProjectedCapital()
#
#     def compLifeEarnedReserve(self):
#         return self.compLifeEarnedCapital(self.compData.compCareer) * self.compData.nEx
#
#     def compPolicyLifeCapital(self):
#         return self.compLifeEarnedCapital(self.compData.compCareer)
#
#     def compPolicyLifeReserve(self):
#         return self.compLifeEarnedReserve()
#
#     def compPolicyLifeBonusReserve(self):
#         return 0
#
#     def compPolicyLifeBonus(self):
#         return 0
#
#     def compLifeUniquePremium(self):
# #        if self.prevReport is None:
#         prevReportCompLifeEarnedCapital = 0
# #        else:
# #            z = self.prevReport.compLifeEarnedCapital()
#
#         return self.compData.nEx * (self.compLifeEarnedCapital(self.compData.compCareer) - self.compLifeEarnedCapital(self.compData.compCareer-1))
#
#     def compOrphanAnnuity(self):
#         return self.compOrphanAnnuityCapital() / self.compData.orphanAnnuityFactor
#
#     def compPolicyDeathCapital(self):
#         return 2 * self.compData.currentSalary
#
#     def compOrphanAnnuityCapital(self):
#         return 1.5 * self.compData.currentSalary
#
#     def compDeathUniquePremium(self):
#         return (self.compPolicyDeathCapital() + self.compOrphanAnnuityCapital()) * self.compData.qx

class ReportPolicySheet(models.AbstractModel):
    _name = 'report.life.report_policy_sheet'

    @api.multi
    def render_html(self, data):
        _logger.info('ender_html')
        _logger.info(data)
        docargs = {
            'doc_ids': data['policy_id'],
            'doc_model': 'life.policy',
            'docs': self.env['life.policy'].browse(data['policy_id']),
        }
        _logger.info(docargs)
        return self.env['report'].render('life.report_policy_sheet', docargs)
