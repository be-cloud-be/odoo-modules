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
from openerp.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class AccountTimesheetReport(models.AbstractModel):
    _name="account.timesheet.report"
    _description="Timesheet Report"
    
    @api.model
    def get_lines(self, context_id, line_id=None):
        if type(context_id) == int:
            context_id = self.env['account.report.context.timesheet'].search([['id', '=', context_id]])
        context = dict(self.env.context)
        context.update({
            'date_from': context_id.date_from,
            'date_to': context_id.date_to,
            'context_id': context_id,
            'company_ids': context_id.company_ids.ids
        })
        base_domain = [('product_uom_id','=',4),('date', '>=', context['date_from']), ('date', '<=', context['date_to']), ('company_id', 'in', context['company_ids'])]
        analytic_lines = self.env['account.analytic.line'].read_group(base_domain, ['partner_id','unit_amount'], ['partner_id'], orderby='partner_id')
        lines = []
        for analytic_line in analytic_lines:
            if analytic_line['partner_id'] :
                lines.append({
                    'id' : analytic_line['partner_id'][0],
                    'name' : analytic_line['partner_id'][1],
                    'type' : 'partner_id',
                    'footnotes': {},
                    'unfoldable' : False,
                    'columns' : [analytic_line['unit_amount']],
                    'level' : 0,
                })
            else :
                lines.append({
                    'id' : '_blank',
                    'name' : '',
                    'type' : 'partner_id',
                    'footnotes': {},
                    'unfoldable' : False,
                    'columns' : [analytic_line['unit_amount']],
                    'level' : 0,
                })
        return lines

    @api.model
    def get_title(self):
        return _("Timesheet Report")

    @api.model
    def get_name(self):
        return 'timesheet'

    @api.model
    def get_report_type(self):
        return 'account_reports.account_report_type_date_range_analytic'

    @api.model
    def get_template(self):
        return 'account_reports.report_financial'
        
class AccountReportContextTimesheet(models.TransientModel):
    _name = "account.report.context.timesheet"
    _description = "A particular context for the generic timesheet report"
    _inherit = "account.report.context.common"

    def get_report_obj(self):
        return self.env['account.timesheet.report']

    def get_columns_names(self):
        return ['Hours']

    @api.multi
    def get_columns_types(self):
        return ['number']

class AccountReportContextCommon(models.TransientModel):
    _inherit = "account.report.context.common"

    def _report_name_to_report_model(self):
        ret = super(AccountReportContextCommon, self)._report_name_to_report_model()
        ret['timesheet'] = 'account.timesheet.report'
        return ret

    def _report_model_to_report_context(self):
        ret = super(AccountReportContextCommon, self)._report_model_to_report_context()
        ret['account.timesheet.report'] = 'account.report.context.timesheet'
        return ret