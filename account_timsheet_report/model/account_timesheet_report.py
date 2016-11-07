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
        return []

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