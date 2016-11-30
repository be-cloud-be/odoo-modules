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
from openerp.exceptions import MissingError
from openerp.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

class YearOpening(models.TransientModel):
    _name = "school.year_opening"
    _description = "Year Opening Wizard"
    
    year_id = fields.Many2one('school.year', string="Year", required=True, ondelete='cascade')

    program_to_duplicate_ids = fields.Many2many('school.program', string="Program to Duplicate")
    
    @api.model
    def default_get(self, fields):
        cmds = []
        context = dict(self._context or {})
        current_year_id = self.env.user.current_year_id
        
        program_ids = self.env['school.program'].search([['year_id', '=', current_year_id.id]])
        return {
            'program_to_duplicate_ids': [(4, program_id.id, False) for program_id in program_ids],
        }
        
    @api.multi
    @api.depends('year_id','program_to_duplicate_ids')
    def open_year(self):
        ids = []
        for program in self.program_to_duplicate_ids:
            new_program = program.copy(default={
                'year_id':self.year_id.id
            })
            ids.append(new_program.id)
        #return an action showing the created programs
        action = self.env.ref('school_management.action_program_form')
        result = action.read()[0]
        result['domain'] = [('id', 'in', ids)]
        return result