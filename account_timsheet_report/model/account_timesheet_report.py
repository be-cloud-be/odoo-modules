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
import time
from datetime import datetime, date, timedelta

from openerp import api, fields, models, _
from openerp.exceptions import UserError, ValidationError
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT

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
        analytic_lines = self.env['account.analytic.line'].search(base_domain, order='partner_id, date')
        lines = []
        current_partner = False
        for analytic_line in analytic_lines:
            if analytic_line.partner_id != current_partner:
                lines.append({
                    'id' : analytic_line.partner_id.id,
                    'name' : analytic_line.partner_id.name if analytic_line.partner_id.name else "NO PARTNER",
                    'type' : 'partner_id',
                    'footnotes': {},
                    'unfoldable' : False,
                    'columns' : [],
                    'level' : 1,
                })
                current_partner = analytic_line.partner_id
            lines.append({
                'id' : analytic_line.id,
                'name' : analytic_line.name,
                'type' : '',
                'footnotes': {},
                'unfoldable' : False,
                'columns' : [analytic_line.date, analytic_line.unit_amount],
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
        return 'account_reports.account_report_type_date_range_no_comparison'

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
        return ['Date','Hours']

    @api.multi
    def get_columns_types(self):
        return ['date','number']

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
        
class AccountReportTimesheetWizard(models.TransientModel):
    _name="account.timesheet.report.wizard"
    _description="Account Timesheet Report Wizard"
    
    partner_ids = fields.Many2many('res.partner', relation='account_timsheet_report_partner')
    date_from = fields.Date(string="Date From",default=lambda s:  (date.today().replace(day=1) - timedelta(days=1)).replace(day=1))
    date_to = fields.Date(string="Date To",default=lambda s: date.today().replace(day=1) - timedelta(days=1))
    company_ids = fields.Many2many('res.company', relation='account_timsheet_report_company', default=lambda s: [(6, 0, [s.env.user.company_id.id])])
    
    @api.multi
    def print_report(self, data):
        self.ensure_one()
        data['date_from'] = self.date_from
        data['date_to'] = self.date_to
        data['company_ids'] = self.company_ids.ids
        if self.partner_ids:
            data['partner_ids'] = self.partner_ids.ids
        else :
            data['partner_ids'] = data.get('active_ids',False)
        return self.env['report'].get_action(self, 'account_timsheet_report.report_tr_pdf_content', data=data)
    

class AccountReportTimesheetPDF(models.AbstractModel):
    _name = 'report.account_timsheet_report.report_tr_pdf_content'
    
    @api.multi
    def render_html(self, data):
        res_data = []
        context = dict(self.env.context)
        base_domain = [('product_uom_id','=',4),('date', '>=', data['date_from']), ('date', '<=', data['date_to']), ('company_id', 'in', data['company_ids'])]
        if data['partner_ids']:
            base_domain.append(('partner_id','in',data['partner_ids']))
        
        analytic_lines = self.env['account.analytic.line'].search(base_domain, order='partner_id, date')
        current_partner = False
        line_data = False
        for line in analytic_lines:
            if line.partner_id != current_partner:
                if line_data:
                    res_data.append(line_data)
                line_data = {
                    'partner_id' : line.partner_id,
                    'lines' : [],
                    'total' : 0,
                }
                current_partner = line.partner_id
            line_data['lines'].append(line)
            line_data['total'] += line.unit_amount
        if line_data:
            res_data.append(line_data)
            
        date_from = datetime.strptime(data['date_from'], DEFAULT_SERVER_DATE_FORMAT)
        date_to = datetime.strptime(data['date_to'], DEFAULT_SERVER_DATE_FORMAT)
        docargs = {
            'date_from' : date_from,
            'date_to' : date_to,
            'data': res_data,
            'time': time,
        }
        return self.env['report'].render('account_timsheet_report.report_tr_pdf_content', docargs)