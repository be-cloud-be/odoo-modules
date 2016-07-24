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

class AssignProgram(models.TransientModel):
    _name = "school.assign.program"
    _description = "Assign Program to Student"
    
    year_id = fields.Many2one('school.year', string='Year', default=lambda self: self.env.user.current_year_id)
    student_id = fields.Many2one('res.partner', string='Students', domain="[('student', '=', '1')]")
    program_id = fields.Many2one('school.individual_program', string="Program", domain="[('student_id', '=', student_id)]")
    source_bloc_id = fields.Many2one('school.bloc', string="Source Bloc")
    
    @api.multi
    @api.depends('year_id','student_id','source_bloc_id')
    def assign_program(self):
        if self.student_id:
            _logger.info("Assing program to %s" % self.student_id.name)
            program = self.env['school.individual_bloc'].create({'year_id':self.year_id.id,'student_id': self.student_id.id,'source_bloc_id':self.source_bloc_id.id,'program_id':self.program_id.id})
            program.assign_source_bloc()
            # Hack to recompute
            self.student_id._get_student_current_program_id()
            # Return an action showing the created program
            action = self.env.ref('school_management.action_individual_bloc_form')
            result = action.read()[0]
            result['views'] = [(False, 'form')]
            result['res_id'] = program.id
            return result
        else :
            context = dict(self._context or {})
            student_ids = context.get('active_ids')
            ids = []
            for student in self.env['res.partner'].browse(student_ids):
                _logger.info("Assing program to %s" % student.id)
                program = self.env['school.individual_bloc'].create({'year_id':self.year_id.id,'student_id': student.id,'source_bloc_id':self.source_bloc_id,'program_id':self.program_id.id})
                program.assign_source_bloc()
                # Hack to recompute
                student._get_student_current_program_id()
                ids.append(program.id)
            # Return an action showing the created programs
            action = self.env.ref('school_management.action_individual_bloc_form')
            result = action.read()[0]
            result['domain'] = [('id', 'in', ids)]
            return result
            
            