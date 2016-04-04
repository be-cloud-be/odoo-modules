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

_logger = logging.getLogger(__name__)

class AssignProgram(models.TransientModel):
    _name = "school.assign.program"
    _description = "Assign Program to Student"
    
    year_id = fields.Many2one('school.year', string='Year')
    student_id = fields.Many2one('res.partner', string='Student', domain="[('student', '=', '1')]")
    source_bloc_id = fields.Many2one('school.bloc', string="Source Bloc")

    @api.one
    @api.depends('year_id','student_id','source_bloc_id')
    def assign_program(self):
        program = self.env['school.individual_bloc'].create({'year_id':self.year_id.id,'student_id': self.student_id.id})
        program.assign_source_bloc(self.source_bloc_id)