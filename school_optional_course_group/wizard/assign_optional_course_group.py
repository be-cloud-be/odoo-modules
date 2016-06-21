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

class AssignOptionalCourseGroup(models.TransientModel):
    _name = "school.assign.optional.course_group"
    _description = "Assign Optional Course to Student"
    
    bloc_ids = fields.Many2many('school.individual_bloc', string="Blocs", required=True)
    
    optional_course_lines = fields.One2many('school.assign.optional.course_group.line', 'course_group_id', string='Course Lines')
    
    @api.model
    def default_get(self, fields):
        cmds = []
        context = dict(self._context or {})
        if context.get('active_ids', False):
            bloc_ids = self.env['school.individual_bloc'].browse(context.get('active_ids'))
            for bloc_id in bloc_ids:
                for course_group_id in bloc_id.course_group_ids:
                    if course_group_id.source_course_group_id.optional_course_type == 'T':
                        cmds.append(
                            (0, 0, {
                                'year_id' : bloc_id.year_id.id,
                                'student_id' : bloc_id.student_id.id,
                                'bloc_name' : bloc_id.source_bloc_name,
                                'course_group_source_id' : course_group_id.id,
                            })   
                        )           
            return {
                'optional_course_lines': cmds,
            }
            
    @api.multi
    @api.depends('optional_course_lines')
    def assign_options(self):
        self.ensure_one()
        for line in self.optional_course_lines:
            if line.course_group_target_id:
                line.course_group_source_id.source_course_group_id = line.course_group_target_id
    
    
class AssignOptionalCourseGroupLine(models.TransientModel):
    _name = "school.assign.optional.course_group.line"
    _description = "Optional Course Line"
    
    course_group_id = fields.Many2one('school.assign.optional.course_group', string='Course Group')
    
    year_id = fields.Many2one('school.year', string='Year', required=True)
    student_id = fields.Many2one('res.partner', string='Student', required=True)
    bloc_name = fields.Char(string='Program', required=True)
    course_group_source_id = fields.Many2one('school.individual_course_group', string='Target', required=True)
    course_group_target_id = fields.Many2one('school.course_group', string='Source', domain="[('optional_course_type', '=', 'O')]")