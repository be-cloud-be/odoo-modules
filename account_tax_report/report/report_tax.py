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

import time

from openerp import api, fields, models, _
from openerp.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class ReportFinancial(models.AbstractModel):
    _name = 'report.account_tax_report.report_tax'
    _inherit = 'report.account.report_financial'
    
    def get_tax_lines(self, data):
        lines = []
        
        
        return lines
    
    def sum_balances(self, balances):
        res = 0
        for account_id, value in balances.items():
            _logger.info(account_id)
            res += -value['balance']  # TODO Should inverse balance be configurable
        return res
    
    def get_amounts(self, data):
        amounts = {}
        
        amounts["4554"] = self.sum_balances(self.with_context(data.get('used_context'))._compute_account_balance(self.env['account.account'].search([('code', 'like', '70%')])))
        
        return amounts
    
    @api.multi
    def render_html(self, data):
        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.env.context.get('active_model'),
            'data': data['form'],
            'docs': self.env[self.env.context.get('active_model')].browse(self.env.context.get('active_id')),
            'time': time,
            'amounts' : self.get_amounts(data.get('form')),
        }
        return self.env['report'].render('account_tax_report.report_tax', docargs)
