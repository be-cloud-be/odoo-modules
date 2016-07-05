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

class EvaluationSummaryWizard(models.TransientModel):
    _name = "school.evaluation.summary.wizard"
    _description = "School Evaluation Summary Wizard"

    year_id = fields.Many2one('school.year', string='Year', default=lambda self: self.env.user.current_year_id)
    
    domain_id = fields.Many2one('school.domain', string='Domain')
    
    session = fields.Selection([
            ('first','First Session'),
            ('second','Second Session'),
            ], string="Session")
    
    @api.multi
    def generate_summary(self):
        self.ensure_one()
        data = {}
        data['year_id'] = self.year_id.id
        data['domain_id'] = self.domain_id.id
        data['session'] = self.session
        return self.env['report'].get_action(self, 'school_evaluations.evaluation_summary_content', data=data)
        
class ReportEvaluationSummary(models.AbstractModel):
    _name = 'report.school_evaluations.evaluation_summary_content'

    @api.multi
    def render_html(self, data):
        _logger.info('render_html')
        year_id = data['year_id']
        session = data['session']
        domain_id = data['domain_id']
        if session == 'first':
            states = ['postponed','awarded_first_session']
        else:
            states = ['awarded_second_session','failed']
        
        if domain_id:
            records = self.env['school.individual_bloc'].search([('year_id','=',year_id),('source_bloc_domain_id','=',domain_id),('state','in',states)],order="source_bloc_level, name")
        else:
            records = self.env['school.individual_bloc'].search([('year_id','=',year_id),('state','in',states)],order="source_bloc_level, name")
        
        docs = [
            {
                "name" : 'Bac 1',
                'blocs' : [],
            },
            {
                "name" : 'Bac 2',
                'blocs' : [],
            },
            {
                "name" : 'Bac 3',
                'blocs' : [],
            },
            {
                "name" : 'Master 1',
                'blocs' : [],
            },
            {
                "name" : 'Master 2',
                'blocs' : [],
            },
        ]
        
        for record in records:
            docs[int(record.source_bloc_level)-1]['blocs'].append(record)
            
        docargs = {
            'doc_model': 'school.individual_bloc',
            'docs': docs,
            'year' : self.env['school.year'].browse(year_id).name,
        }
        return self.env['report'].render('school_evaluations.evaluation_summary_content', docargs)