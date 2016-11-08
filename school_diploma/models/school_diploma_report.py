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
import locale
from datetime import datetime, date, timedelta

from openerp import api, fields, models, _
from openerp.exceptions import UserError, ValidationError
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT

_logger = logging.getLogger(__name__)

class SchoolDiplomaReport(models.AbstractModel):
    _name = 'report.school_diploma.report_diploma_content'
    
    @api.v7
    def render_html(self, cr, uid, ids, data=None, context=None):
        report = self.pool['report']._get_report_from_name(cr, uid, 'school_diploma.report_diploma_content')
        report_obj = self.pool[report.model]
        docs = report_obj.browse(cr, uid, ids, context=context)
        docargs = {
            'doc_ids': ids,
            'doc_model': report.model,
            'docs': docs,
            'locale' : locale,
        }
        return self.pool['report'].render(cr, uid, [], report.report_name, docargs, context=context)
