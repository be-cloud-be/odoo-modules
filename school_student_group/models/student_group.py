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
    
    _order = 'responsible_id, year_id, name'
    
    state = fields.Selection([
            ('draft','Draft'),
            ('published', 'Published'),
            ('archived', 'Archived'),
        ], string='Status', index=True, readonly=True, default='draft',
        #track_visibility='onchange', TODO : is this useful for this case ?
        copy=False,
        help=" * The 'Draft' status is used when a new group is created and not published yet.\n"
             " * The 'Published' status is when a group is published and available for use.\n"
             " * The 'Archived' status is used when a group is obsolete and not publihed anymore.")
    
    @api.multi
    def unpublish(self):
        return self.write({'state': 'draft'})
    
    @api.multi
    def publish(self):
        return self.write({'state': 'published'})
    
    @api.multi
    def archive(self):
        return self.write({'state': 'archived'})
    
    year_id = fields.Many2one('school.year', string='Year', required=True, default=lambda self: self.env.user.current_year_id)
    responsible_id = fields.Many2one('res.partner', string='Responsible', domain="[('type','=','contact')]", required=True)
    type = fields.Selection([('L','LinkedCourses'),('F','FreeCourses'),('P','Project'),('O','Others')],string="Group Type",default="F", required=True)
    staff_ids = fields.Many2many('res.partner', 'group_staff_rel', 'group_id', 'staff_id', string='Staff', domain="[('type','=','contact')]")
    
    name = fields.Char(string='Name', compute='_compute_name', store=True)
    short_name = fields.Char(string='Name', compute='_compute_name', store=True) 
    title = fields.Char(string='Title')

    course_ids = fields.Many2many('school.course', 'group_course_rel', 'group_id', 'course_id', string='Courses', domain=lambda(self): "[('teacher_ids', '=', responsible_id)]" if self.type in ['L','F'] else "")
    
    domain_id = fields.Many2one('school.domain', computed='_compute_course_info', store=True)
    speciality_id = fields.Many2one('school.speciality', computed='_compute_course_info', store=True)
    cycle_id = fields.Many2one('school.cycle', computed='_compute_course_info', store=True)
    
    @api.one
    @api.depends('course_ids')
    def _compute_course_info(self):
        if len(self.course_ids) > 0:
            self.domain_id = self.course_ids[0].domain_id
            self.speciality_id = self.course_ids[0].speciality_id
            self.cycle_id = self.course_ids[0].cycle_id
        else:
            self.domain_id = None
            self.speciality_id = None
            self.cycle_id = None

    @api.one
    @api.depends('year_id', 'title', 'course_ids', 'responsible_id')
    def _compute_name(self):
        if self.type == 'L':
            title = self.course_ids[0].name if len(self.course_ids) > 0 else ""
            self.name = '%s - %s - %s' % (self.year_id.short_name, self.responsible_id.name, title)
            self.short_name = title
        else:
            self.name = '%s - %s' % (self.year_id.short_name, self.title)
            self.short_name = self.title

    participant_ids = fields.Many2many('res.partner', 'school_group_participants_rel', 'group_id', 'res_partner_id', string='Participipants')
    picked_participant_ids = fields.Many2many('res.partner', 'school_group_res_partner_rel', 'group_id', 'res_partner_id', string='Picked Participipants')
    participant_count = fields.Integer(string="Participant Count", compute="_compute_participant_count")

    individual_course_ids = fields.Many2many('school.individual_course', 'school_group_individual_course_rel', 'group_id', 'individual_course_id', string='Individual Courses', domain="[('year_id','=',year_id)]")
    
    #event_ids = fields.One2many('calendar.event','student_group_id',string='Events')
    
    @api.onchange('type')
    def onchange_type(self):
        # If type change we reset everything : TODO add a user confirmation.
        self.course_ids = []
        self.participant_ids = []
        self.picked_participant_ids = []
        self.individual_course_ids = []
        return {
            'domain' : {'individual_course_ids': [('year_id','=',self.year_id.id)]}
        }
    
    @api.onchange('responsible_id')
    def onchange_responsible_id(self):
        if self.type in ['L','F'] :
            return {
                'domain': {'course_ids': [('teacher_ids', '=', self.responsible_id.id)]}
            }
        
    @api.onchange('course_ids')
    def onchange_course_ids(self):
        if self.course_ids:
            if self.type == 'L':
                self.individual_course_ids = self.env['school.individual_course'].search([('year_id','=',self.year_id.id),('source_course_id','in',self.course_ids.ids)])
            elif self.type == 'F':
                for ic in self.individual_course_ids:
                    if ic.source_course_id not in self.course_ids:
                        raise ValidationError(_('Individual Course %s does not match the course selection, please remove it before changing the Courses' % (ic.name)))
            else:
                raise ValidationError(_('Cannot select Course on this type of group.'))
            return {
                'domain': {'individual_course_ids': [('year_id','=',self.year_id.id),('source_course_id', '=', self.course_ids.ids)]}
            }

    @api.onchange('picked_participant_ids')
    def onchange_picked_participant_ids(self):
        if self.type == 'L':
            if len(self.picked_participant_ids) > 0 :
                raise ValidationError(_('Cannot pick participants on a LinkedCourses type of group, please set Courses instead.'))
        elif self.type == 'F':
            if len(self.picked_participant_ids) > 0 :
                raise ValidationError(_('Cannot pick participants on a FreeCourses type of group, please add Individual Courses instead.'))
        else:
            self.participant_ids = self.picked_participant_ids
        self.participant_count = len(self.participant_ids)
            
    @api.onchange('individual_course_ids')
    def onchange_individual_course_ids(self):
        if self.type == 'L':
            self.participant_ids = self.individual_course_ids.mapped('student_id')
        elif self.type == 'F':
            for ic in self.individual_course_ids:
                if ic.source_course_id not in self.course_ids:
                    raise ValidationError(_('Individual Course %s does not match the course selection' % (ic.name)))
            self.participant_ids = self.individual_course_ids.mapped('student_id')
        elif self.type == 'P':
            student_ids = self.individual_course_ids.mapped('student_id')
            for student in student_ids:
                if student not in self.participant_ids:
                    self.participant_ids |= student
        else:
            raise ValidationError(_('Cannot select Individual Courses on this type of group.'))
        self.participant_count = len(self.participant_ids)

    @api.one    
    def _compute_participant_count(self):
        self.participant_count = len(self.participant_ids)

    @api.multi
    def action_participants_list(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Participants',
            'res_model': 'res.partner',
            'domain': [('id', 'in', self.participant_ids.ids)],
            'view_mode': 'tree',
        }

    @api.one
    def update_linked_students(self):
        if self.type == 'L':
            self.individual_course_ids = self.env['school.individual_course'].search([('year_id','=',self.year_id.id),('source_course_id','in',self.course_ids.ids)])
            self.participant_ids = self.individual_course_ids.mapped('student_id')
            self.participant_count = len(self.participant_ids)
            
    @api.model
    def generate_all_student_course_group(self):
        year_id = self.env.user.current_year_id
        all_blocs = self.env['school.bloc'].search([('year_id','=',year_id.id)])
        # We are going through all courses, of all current blocs
        all_course_ids = set()
        for bloc in all_blocs:
            for course_group in bloc.course_group_ids:
                for course in course_group.course_ids:
                    all_course_ids.add(course.id)
        # For each course we look for students and create the corresponding groups
        for course_id in all_course_ids :      
            course = self.env['school.course'].browse(course_id)
            individual_course_ids = self.env['school.individual_course'].search([('year_id','=',year_id.id),('source_course_id','=',course.id)])
            student_ids = individual_course_ids.mapped('student_id')
            if len(student_ids) > 0 :
                # Only one teacher for this course
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
                        new_group.individual_course_ids = individual_course_ids
                # Several teachers for this course
                elif len(course.teacher_ids) > 1:
                    for teacher in course.teacher_ids:
                        old_group = self.env['school.student_group'].search([('responsible_id','=',teacher.id),('year_id','=',year_id.id),('course_id','=',course.id)])
                        if not old_group:
                            # We create a group for each teacher
                            new_group = self.env['school.student_group'].create({
                                'type': 'C',
                                'year_id': year_id.id,
                                'course_id': course.id,
                                'responsible_id': teacher.id,
                            })
                            # Try to find the group of the previous year
                            for student_id in student_ids:
                                previous_group = self.env['school.student_group'].search([('responsible_id','=',teacher.id),('year_id','=',year_id.previous.id),('course_id.title','=',course.title),('student_ids','=',student_id.id)])
                                if previous_group:
                                    # Set students that were in the previous group
                                    new_group.student_ids = previous_group.student_ids & student_ids
                                    break
                                
class Course(models.Model):
    '''Course'''
    _inherit = 'school.course'
    
    group_ids = fields.Many2many('school.student_group', 'group_course_rel', 'course_id', 'group_id', string='Groups', readonly=True)
    
    
class IndividualCourse(models.Model):
    '''Individual Course'''
    _inherit = 'school.individual_course'
    
    @api.depends('year_id','source_course_id')
    @api.one
    def compute_teacher_id(self):
        student_group = self.env['school.student_group'].search([('year_id','=',self.year_id.id),('course_ids','=',self.source_course_id.id),('participant_ids','=',self.student_id.id)])
        if len(student_group) > 1:
            import wdb
            wdb.set_trace()
        if student_group:
            self.teacher_id = student_group.responsible_id
        else:
            self.teacher_id = None

    group_ids = fields.Many2many('school.student_group', 'group_individual_course_rel', 'individual_course_id', 'group_id', string='Groups', readonly=True)