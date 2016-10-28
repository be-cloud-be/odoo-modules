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

class StudentGroup(models.Model):
    '''Student Group'''
    _name = 'school.student_group'
    _description = 'Student Group'
    _inherit = ['mail.thread','school.year_sequence.mixin']
    
    _order = 'responsible_id, course_id'
    
    year_id = fields.Many2one('school.year', string='Year', required=True, default=lambda self: self.env.user.current_year_id)
    responsible_id = fields.Many2one('res.partner', string='Responsible', domain="[('type','=','contact')]", required=True)
    type = fields.Selection([('C','Course'),('P','Project'),('O','Orchestre')],string="Group Type",default="C")
    active = fields.Boolean('Active', default=True)
    
    name = fields.Char(string='Name', compute='_compute_name', store=True)
    short_name = fields.Char(string='Name', compute='_compute_name', store=True) 
    title = fields.Char(string='Title')
    
    @api.depends('responsible_id','course_id.name','type','title','year_id')
    @api.multi
    def _compute_name(self):
        for studentg in self:
            if studentg.course_id:
                studentg.name = "%s - %s - %s" % (studentg.year_id.name, studentg.course_id.name, studentg.responsible_id.name)
                studentg.short_name = studentg.course_id.name
            else:
                studentg.name = "%s - %s" % (studentg.year_id.name, studentg.title)
                studentg.short_name = studentg.title
    
    staff_ids = fields.Many2many('res.partner', 'group_staff_rel', 'group_id', 'staff_id', string='Staff', domain="[('type','=','contact')]")
    student_ids = fields.Many2many('res.partner', 'group_student_rel', 'group_id', 'student_id', string='Student', domain="[('student','=','1')]")
    
    student_count = fields.Integer(compute='_compute_student_count', string="Student Count")
	
    @api.one
    def _compute_student_count(self):
        self.student_count = len(self.student_ids)
    
    course_id = fields.Many2one('school.course', string='Course')
    
    cycle_id = fields.Many2one(related='course_id.cycle_id', string='Cycle',store=True)
    level = fields.Integer(related='course_id.level', string='Level',store=True)
    speciality_id = fields.Many2one(related='course_id.speciality_id', string='Speciality',store=True)
    domain_id = fields.Many2one(related='course_id.domain_id', string='Domain',store=True)
    section_id = fields.Many2one(related='course_id.section_id', string='Section',store=True)
    track_id = fields.Many2one(related='course_id.track_id', string='Track',store=True)
    
    @api.model
    def create_student_course_group(self):
        year_id = self.env.user.current_year_id
        all_teacher_ids = self.env['res.partner'].search([('teacher','=',1)])
        for teacher_id in all_teacher_ids:
            current_course_ids = teacher_id.teacher_current_course_ids
            for course_id in current_course_ids:
                student_ids = self.env['school.individual_course'].search([('teacher_id','=',teacher_id.id),('year_id','=',year_id.id),('source_course_id','=',course_id.source_course_id.id)]).mapped('student_id')
                old_group = self.env['school.student_group'].search([('responsible_id','=',teacher_id.id),('year_id','=',year_id.id),('course_id','=',course_id.source_course_id.id)])
                if not old_group and len(student_ids) > 0:
                    new_group = self.env['school.student_group'].create({
                        'type': 'C',
                        'year_id': year_id.id,
                        'course_id': course_id.source_course_id.id,
                        'responsible_id': teacher_id.id,
                        # 'student_ids' : (0, _, student_ids.ids), TODO DOES NOT WORK, WHY ??
                    })
                    new_group.student_ids = student_ids
                    
    @api.model
    def generate_all_student_course_group(self):
        year_id = self.env.user.current_year_id
        all_blocs = self.env['school.bloc'].search([('year_id','=',year_id.id)])
        # We are going through all courses
        all_course_ids = set()
        for bloc in all_blocs:
            for course_group in bloc.course_group_ids:
                for course in course_group.course_ids:
                    all_course_ids.add(course.id)
        for course_id in all_course_ids :      
            course = self.env['school.course'].browse(course_id)
            student_ids = self.env['school.individual_course'].search([('year_id','=',year_id.id),('source_course_id','=',course.id)]).mapped('student_id')
            if len(student_ids) > 0 :
                if len(course.teacher_ids) == 1:
                    old_group = self.env['school.student_group'].search([('responsible_id','=',course.teacher_ids.ids[0]),('year_id','=',year_id.id),('course_id','=',course.id)])
                    if not old_group:
                        new_group = self.env['school.student_group'].create({
                            'type': 'C',
                            'year_id': year_id.id,
                            'course_id': course.id,
                            'responsible_id': course.teacher_ids.ids[0],
                            # 'student_ids' : (0, _, student_ids.ids), TODO DOES NOT WORK, WHY ??
                        })
                        # set all students in as only one theacher
                        new_group.student_ids = student_ids
                elif len(course.teacher_ids) > 1:
                    for teacher in course.teacher_ids:
                        old_group = self.env['school.student_group'].search([('responsible_id','=',teacher.id),('year_id','=',year_id.id),('course_id','=',course.id)])
                        if not old_group:
                            new_group = self.env['school.student_group'].create({
                                'type': 'C',
                                'year_id': year_id.id,
                                'course_id': course.id,
                                'responsible_id': teacher.id,
                            })
                            # try to guess the teacher based on previous year
                            for student_id in student_ids:
                                old_course = self.env['school.individual_course'].search([('student_id','=',student_id.id),('year_id','=',year_id.previous.id),('title', '=', course.title),('teacher_id','=',teacher.id)])
                                if old_course:
                                    new_group.student_ids |= student_id

class Course(models.Model):
    '''Course'''
    _inherit = 'school.course'
    
    group_ids = fields.One2many('school.student_group', 'course_id', string='Groups')
    
    
# class IndividualCourse(models.Model):
#     '''Individual Course'''
#     _inherit = 'school.individual_course'
    
#     teacher_id = fields.Many2one('res.partner', string='Teacher', compute='compute_teacher_id')

#     @api.depends('year_id','source_course_id')
#     @api.one
#     def compute_teacher_id(self):
#         student_group = self.env['school.student_group'].search([('year_id','=',self.year_id.id),('course_id','=',self.source_course_id.id),('student_ids','=',self.id)])
#         if student_group:
#             self.teacher_id = student_group.responsible_id
#         else:
#             self.teacher_id = None
        