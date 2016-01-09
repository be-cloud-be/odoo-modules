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
from openerp import api, fields, models, _
from openerp.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class AccountFinancialReport(models.Model):
    _inherit = 'account.financial.report'

    @api.multi
    @api.depends('parent_id', 'parent_id.report_name')
    def _get_report_name(self):
        '''Returns the name of the Root Account which correspond to the 
            Report Name.'''
        for report in self:
            name = self.name
            if report.parent_id:
                name = report.parent_id.report_name
            report.report_name = name

    report_name = fields.Char(string="Report Name" ,compute="_get_report_name")