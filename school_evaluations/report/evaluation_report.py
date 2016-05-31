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
import time

from openerp import api, fields, models, tools, _
from openerp.exceptions import MissingError

_logger = logging.getLogger(__name__)

class ReportEvaluationByTeacher(models.AbstractModel):
    _name = 'report.school_evaluation.report_evaluation_by_teacher_content'
    
    @api.multi
    def render_html(self, data):
        docargs = {
            'doc_ids': data.mapped('id'),
            'doc_model': self.env['school.individual_course'],
            'docs': data.sorted(key=lambda r: r.teacher_id),
            'time': time,
        }
        return self.env['report'].render('school_evaluation.report_evaluation_by_teacher_content', docargs)