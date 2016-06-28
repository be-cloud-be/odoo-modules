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

_logger = logging.getLogger(__name__)

class CourseGroup(models.Model):
    '''Courses Group'''
    _name = 'school.course_group'
    _description = 'Courses Group'
    _inherit = ['mail.thread']
    _order = 'sequence'
    
    sequence = fields.Integer(string='Sequence', required=True)
    
    title = fields.Char(required=True, string='Title')
    
    speciality_id = fields.Many2one('school.speciality', string='Speciality')
    domain_id = fields.Many2one(related='speciality_id.domain_id', string='Domain',store=True)
    section_id = fields.Many2one(related='speciality_id.section_id', string='Section',store=True)
    track_id = fields.Many2one(related='speciality_id.track_id', string='Track',store=True)
    
    level = fields.Integer(string='Level')
    
    description = fields.Text(string='Description')
    
    course_ids = fields.One2many('school.course', 'course_group_id', string='Courses', copy=True, ondelete="cascade")

    bloc_ids = fields.Many2many('school.bloc','school_bloc_course_group_rel', id1='group_id', id2='bloc_id',string='Blocs', copy=False)
    
    name = fields.Char(string='Name', compute='compute_name', store=True)
    
    @api.depends('title','level','speciality_id.name')
    @api.multi
    def compute_name(self):
        for course_g in self:
            if course_g.level:
                course_g.name = "%s - %s - %s" % (course_g.title, course_g.speciality_id.name, course_g.level)
            else:
                course_g.name = "%s - %s" % (course_g.title, course_g.speciality_id.name)
            
    code_ue = fields.Char(string='Code UE', compute='compute_code_ue', store=True)
    
    @api.multi
    def compute_code_ue(self):
        for course_g in self:
            course_g.code_ue = "UE " % ()
    
    total_credits = fields.Integer(compute='_get_courses_total', string='Total Credits')
    total_hours = fields.Integer(compute='_get_courses_total', string='Total Hours')
    total_weight = fields.Float(compute='_get_courses_total', string='Total Weight')

    weight = fields.Integer(string='Weight')

    @api.one
    @api.depends('course_ids')
    def _get_courses_total(self):
        total_hours = 0.0
        total_credits = 0.0
        total_weight = 0.0
        for course in self.course_ids:
            total_hours += course.hours
            total_credits += course.credits
            total_weight += course.weight
        self.total_hours = total_hours
        self.total_credits = total_credits
        self.total_weight = total_weight
    
    notes = fields.Text(string='Notes')
    
class Course(models.Model):
    '''Course'''
    _name = 'school.course'
    _description = 'Course'
    _inherit = ['mail.thread']
    
    sequence = fields.Integer(string='Sequence')
    title = fields.Char(required=True, string='Title')
    
    description = fields.Text(string='Description')
    
    url_ref = fields.Char(string='Url Reference')
    
    course_group_id = fields.Many2one('school.course_group', string='Course Group')
    
    level = fields.Integer(related='course_group_id.level',string='Level', readonly=True)
    
    speciality_id = fields.Many2one(related='course_group_id.speciality_id', string='Speciality',store=True, readonly=True)
    domain_id = fields.Many2one(related='course_group_id.domain_id', string='Domain',store=True, readonly=True)
    section_id = fields.Many2one(related='course_group_id.section_id', string='Section',store=True, readonly=True)
    track_id = fields.Many2one(related='course_group_id.track_id', string='Track',store=True, readonly=True)
    
    hours = fields.Integer(string = 'Hours')
    credits = fields.Integer(string = 'Credits')
    weight =  fields.Float(string = 'Weight',digits=(6,2))
    
    notes = fields.Text(string='Notes')
    
    name = fields.Char(string='Name', compute='compute_name', store=True)
    
    @api.depends('title','level','speciality_id.name')
    @api.multi
    def compute_name(self):
        for course in self:
            if course.level:
                course.name = "%s - %s - %s" % (course.title, course.speciality_id.name, course.level)
            else:
                course.name = "%s - %s" % (course.title, course.speciality_id.name)
    
    current_teacher_ids = fields.Many2many('res.partner',compute='_get_teacher_ids',string='Current Teachers')
    
    @api.one
    def _get_teacher_ids(self):
        current_year_id = safe_eval(self.env['ir.config_parameter'].get_param('school.current_year_id','1'))
        res = self.env['school.course_session'].search([['year_id', '=', current_year_id], ['course_id', '=', self.id]])
        self.teacher_ids = res
        
    
    #_sql_constraints = [
	#        ('uniq_course', 'unique(course_group_id, sequence)', 'There shall be only one course with a given sequence within a course group'),
    #]

class Bloc(models.Model):
    '''Bloc'''
    _name = 'school.bloc'
    _description = 'Program'
    _inherit = ['mail.thread']
    _order = 'program_id,sequence'
    
    @api.one
    @api.depends('course_group_ids')
    def _get_courses_total(self):
        total_hours = 0.0
        total_credits = 0.0
        total_weight = 0.0
        for course_group in self.course_group_ids:
            total_hours += course_group.total_hours
            total_credits += course_group.total_credits
            total_weight += course_group.total_weight
        self.total_hours = total_hours
        self.total_credits = total_credits
        self.total_weight = total_weight

    sequence = fields.Integer(string='Sequence')
    title = fields.Char(required=True, string='Title')
    year_id = fields.Many2one('school.year', string="Year", related='program_id.year_id', store=True)
    description = fields.Text(string='Description')
    
    cycle_id = fields.Many2one(related='program_id.cycle_id', string='Cycle',store=True)
    
    level = fields.Selection([('0','Free'),('1','Bac 1'),('2','Bac 2'),('3','Bac 3'),('4','Master 1'),('5','Master 2'),],string='Level')
    
    speciality_id = fields.Many2one(related='program_id.speciality_id', string='Speciality',store=True)
    domain_id = fields.Many2one(related='program_id.domain_id', string='Domain',store=True)
    section_id = fields.Many2one(related='program_id.section_id', string='Section',store=True)
    track_id = fields.Many2one(related='program_id.track_id', string='Track',store=True)
    
    total_credits = fields.Integer(compute='_get_courses_total', string='Total Credits')
    total_hours = fields.Integer(compute='_get_courses_total', string='Total Hours')
    total_weight = fields.Float(compute='_get_courses_total', string='Total Weight')

    notes = fields.Text(string='Notes')
    
    program_id = fields.Many2one('school.program', string='Program', copy=False)

    name = fields.Char(string='Name', compute='compute_name', store=True)
    
    course_group_ids = fields.Many2many('school.course_group','school_bloc_course_group_rel', id1='bloc_id', id2='group_id',string='Course Groups')
    
    @api.depends('sequence','title')
    @api.multi
    def compute_name(self):
        for bloc in self:
            bloc.name = "%s - %d" % (bloc.title,bloc.sequence)

    _sql_constraints = [
	        ('uniq_bloc', 'unique(program_id, sequence)', 'There shall be only one bloc with a given sequence within a program'),
    ]

class Program(models.Model):
    '''Program'''
    _name = 'school.program'
    _description = 'Program made of several Blocs'
    _inherit = ['mail.thread']
    
    @api.one
    @api.depends('bloc_ids')
    def _get_courses_total(self):
        total_hours = 0.0
        total_credits = 0.0
        for bloc in self.bloc_ids:
            total_hours += bloc.total_hours
            total_credits += bloc.total_credits
        self.total_hours = total_hours
        self.total_credits = total_credits
    
    state = fields.Selection([
            ('draft','Draft'),
            ('published', 'Published'),
            ('archived', 'Archived'),
        ], string='Status', index=True, readonly=True, default='draft',
        #track_visibility='onchange', TODO : is this useful for this case ?
        copy=False,
        help=" * The 'Draft' status is used when a new program is created and not published yet.\n"
             " * The 'Published' status is when a program is published and available for use.\n"
             " * The 'Archived' status is used when a program is obsolete and not publihed anymore.")
    
    title = fields.Char(required=True, string='Title')
    year_id = fields.Many2one('school.year', required=True, string="Year")
    description = fields.Text(string='Description')
    
    competency_ids = fields.Many2many('school.competency','school_competency_program_rel', id1='program_id', id2='competency_id', string='Competencies', ondelete='set null')
    
    cycle_id = fields.Many2one('school.cycle', string='Cycle')
    
    speciality_id = fields.Many2one('school.speciality', string='Speciality')
    domain_id = fields.Many2one(related='speciality_id.domain_id', string='Domain',store=True)
    section_id = fields.Many2one(related='speciality_id.section_id', string='Section',store=True)
    track_id = fields.Many2one(related='speciality_id.track_id', string='Track',store=True)
    
    total_credits = fields.Integer(compute='_get_courses_total', string='Total Credits')
    total_hours = fields.Integer(compute='_get_courses_total', string='Total Hours')

    notes = fields.Text(string='Notes')
    
    bloc_ids = fields.One2many('school.bloc', 'program_id', string='Blocs')
    
    name = fields.Char(string='Name', related='title', store=True)
    
    @api.multi
    def unpublish(self):
        return self.write({'state': 'draft'})
    
    @api.multi
    def publish(self):
        return self.write({'state': 'published'})
    
    @api.multi
    def archive(self):
        return self.write({'state': 'archived'})

class Competency(models.Model):
    '''Competency'''
    _name = 'school.competency'
    _order = 'sequence asc'
    sequence = fields.Integer(string='Sequence')
    description = fields.Text(string='Description')
    
    program_ids = fields.Many2many('school.program','school_competency_program_rel', id1='competency_id', id2='program_id', string='Programs', ondelete='set null')
    
class Domain(models.Model):
    '''Domain'''
    _name = 'school.domain'
    name = fields.Char(required=True, string='Name', size=40)
    description = fields.Text(string='Description')
    long_name = fields.Char(required=True, string='Long Name', size=40)
    
class Cycle(models.Model):
    '''Cycle'''
    _name = 'school.cycle'
    name = fields.Char(required=True, string='Name', size=60)
    description = fields.Text(string='Description')
    required_credits = fields.Integer(string='Required Credits')
    type = fields.Selection([
            ('long','Long'),
            ('short', 'Short'),
        ], string='Type')
    grade = fields.Char(required=True, string='Grade', size=60)
    
class Section(models.Model):
    '''Section'''
    _name = 'school.section'
    name = fields.Char(required=True, string='Name', size=40)
    description = fields.Text(string='Description')
    
class Track(models.Model):
    '''Track'''
    _name = 'school.track'
    name = fields.Char(required=True, string='Name', size=40)
    description = fields.Text(string='Description')
    
class Speciality(models.Model):
    '''Speciality'''
    _name = 'school.speciality'
    name = fields.Char(required=True, string='Name', size=40)
    description = fields.Text(string='Description')
    domain_id = fields.Many2one('school.domain', string='Domain')
    section_id = fields.Many2one('school.section', string='Section')
    track_id = fields.Many2one('school.track', string='Track')
    
    _sql_constraints = [
	        ('uniq_speciality', 'unique(domain_id, name)', 'There shall be only one speciality in a domain'),
    ]
    
class Year(models.Model):
    '''Year'''
    _name = 'school.year'
    name = fields.Char(required=True, string='Name', size=15)
    
    
class ReportProgram(models.AbstractModel):
    _name = 'report.school_management.report_program'

    @api.multi
    def render_html(self, data):
        _logger.info('render_html')
        docargs = {
            'doc_ids': data['id'],
            'doc_model': 'school.program',
            'docs': self.env['school.program'].browse(data['id']),
        }
        return self.env['report'].render('school.report_program', docargs)