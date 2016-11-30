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

class LinkedGroupWizard(models.TransientModel):
    _name = "school.linked_group_wizard"
    _description = "Linked Group Wizard"
    
    year_id = fields.Many2one('school.year', string="Year", required=True, default=lambda self: self.env.user.current_year_id, ondelete='cascade')
    domain_id = fields.Many2one('school.domain', string="Domain", required=True, ondelete='cascade')
    
    @api.one
    def generate_all_linked_student_group(self):
        all_blocs = self.env['school.bloc'].search([('year_id','=',self.year_id.id),('domain_id','=',self.domain_id.id)])
        # We are going through all courses, of all current blocs
        all_course_ids = set()
        for bloc in all_blocs:
            for course_group in bloc.course_group_ids:
                for course in course_group.course_ids:
                    all_course_ids.add(course.id)
        # For each course we look for students and create the corresponding groups
        for course_id in all_course_ids :
            course = self.env['school.course'].browse(course_id)
            teacher_ids = self.env['school.individual_course'].read_group([('year_id','=',self.year_id.id),('source_course_id','=',course.id)], ['teacher_id'],['teacher_id'])
            for teacher_id in teacher_ids:
                # If a teacher is defined, orphan course are not concerned at this time
                if teacher_id['teacher_id']:
                    individual_course_ids = self.env['school.individual_course'].search([('year_id','=',self.year_id.id),('source_course_id','=',course.id),('teacher_id', '=', teacher_id['teacher_id'][0])])
                    student_ids = individual_course_ids.mapped('student_id')
                    old_group = self.env['school.student_group'].search([('responsible_id','=',teacher_id['teacher_id'][0]),('year_id','=',self.year_id.id),('course_ids','=',course.id)])
                    if not old_group:
                        new_group = self.env['school.student_group'].create({
                            'type': 'L',
                            'year_id': self.year_id.id,
                            'responsible_id': teacher_id['teacher_id'][0],
                            # 'student_ids' : (0, _, student_ids.ids), TODO DOES NOT WORK, WHY ??
                        })
                        # set all students in as only one theacher
                        new_group.course_ids |= course
                        new_group.individual_course_ids = individual_course_ids
                        new_group.participant_ids = student_ids
                        new_group.participant_count = len(student_ids)