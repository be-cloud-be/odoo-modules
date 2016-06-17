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

from openerp import api, fields, models, tools, _
from openerp.exceptions import UserError

_logger = logging.getLogger(__name__)

class IndividualBloc(models.Model):
    '''Individual Bloc'''
    _name='school.individual_bloc'
    _description='Individual Bloc'
    _inherit = ['mail.thread']
    
    _order = 'name'
    
    name = fields.Char(compute='_compute_name',string='Name', readonly=True, store=True)
    
    year_id = fields.Many2one('school.year', string='Year', readonly=True)
    student_id = fields.Many2one('res.partner', string='Student', domain="[('student', '=', '1')]", readonly=True, auto_join=True)
    student_name = fields.Char(related='student_id.name', string="Student Name", readonly=True, store=True)
    source_bloc_id = fields.Many2one('school.bloc', string="Source Bloc", readonly=True, auto_join=True)
    source_bloc_name = fields.Char(related='source_bloc_id.name', string="Source Bloc Name", readonly=True)
    source_bloc_title = fields.Char(related='source_bloc_id.name', string="Source Bloc Name", readonly=True)
    source_bloc_level = fields.Selection([('0','Free'),('1','Bac 1'),('2','Bac 2'),('3','Bac 3'),('4','Master 1'),('5','Master 2'),],related='source_bloc_id.level', string="Source Bloc Level", readonly=True)
    source_bloc_domain_id = fields.Many2one(related='source_bloc_id.domain_id', string='Domain', readonly=True)
    
    image = fields.Binary('Image', attachment=True, related='student_id.image')
    image_medium = fields.Binary('Image', attachment=True, related='student_id.image_medium')
    image_small = fields.Binary('Image', attachment=True, related='student_id.image_small')
    
    course_group_ids = fields.One2many('school.individual_course_group', 'bloc_id', string='Courses Groups')
    
    total_credits = fields.Integer(compute='_get_courses_total', string='Credits')
    total_hours = fields.Integer(compute='_get_courses_total', string='Hours')
    total_weight = fields.Float(compute='_get_courses_total', string='Weight')

    @api.one
    @api.depends('source_bloc_id','course_group_ids')
    def assign_source_bloc(self, source_bloc_id):
        self.source_bloc_id = source_bloc_id
        cg_ids = []
        for group in source_bloc_id.course_group_ids:
            _logger.info('assign course groups : ' + group.name)
            cg = self.course_group_ids.create({'bloc_id': self.id,'source_course_group_id': group.id, 'acquiered' : 'NA'}) # TODO FIX DEPENDENCIE TO EVALUATION
            courses = []
            for course in group.course_ids:
                _logger.info('assign course : ' + course.name)
                courses.append((0,0,{'source_course_id': course.id}))
            _logger.info(courses)
            cg.write({'course_ids': courses})

    @api.one
    @api.depends('course_group_ids')
    def _get_courses_total(self):
        total_hours = 0.0
        total_credits = 0.0
        total_weight = 0.0
        for course_group in self.course_group_ids:
            total_hours += course_group.total_hours
            total_credits += course_group.total_credits
            total_weight += course_group.weight
        self.total_hours = total_hours
        self.total_credits = total_credits
        self.total_weight = total_weight
    
    @api.one
    @api.depends('year_id.name','student_id.name')
    def _compute_name(self):
        self.name = "%s - %s" % (self.year_id.name,self.student_id.name)
    
    _sql_constraints = [
	        ('uniq_student_bloc', 'unique(year_id, student_id, source_bloc_id)', 'This individual bloc already exists.'),
    ]
            
class IndividualCourseGroup(models.Model):
    '''Individual Course Group'''
    _name='school.individual_course_group'
    _description='Individual Course Group'
    _inherit = ['mail.thread']
    
    _order = 'sequence'
    
    name = fields.Char(related="source_course_group_id.name", readonly=True)
    title = fields.Char(related="source_course_group_id.title", readonly=True, store=True)
    
    sequence = fields.Integer(related="source_course_group_id.sequence", readonly=True, store=True)
    
    year_id = fields.Many2one(related="bloc_id.year_id", string='Year', store=True)
    student_id = fields.Many2one(related="bloc_id.student_id", string='Student', store=True, domain=[('student', '=', True)])
    teacher_id = fields.Many2one('res.partner', string='Teacher', store=True, domain=[('teacher', '=', True)])
    
    image = fields.Binary('Image', attachment=True, related='student_id.image')
    image_medium = fields.Binary('Image', attachment=True, related='student_id.image_medium')
    image_small = fields.Binary('Image', attachment=True, related='student_id.image_small')
    
    source_course_group_id = fields.Many2one('school.course_group', string="Source Course Group")
    bloc_id = fields.Many2one('school.individual_bloc', string="Bloc", ondelete='cascade', readonly=True)
    course_ids = fields.One2many('school.individual_course', 'course_group_id', string='Courses')
    
    total_credits = fields.Integer(compute='_get_courses_total', string='Credits')
    total_hours = fields.Integer(compute='_get_courses_total', string='Hours')
    total_weight = fields.Float(compute='_get_courses_total', string='Total Weight')
    weight = fields.Integer(related="source_course_group_id.weight",string='Weight')
    
    code_ue =  fields.Char(related="source_course_group_id.code_ue", readonly=True)
    
    @api.onchange('source_course_group_id')
    def onchange_source_cg(self):
        courses = []
        for course in self.source_course_group_id.course_ids:
            _logger.info('assign course : ' + course.name)
            courses.append((0,0,{'source_course_id':course.id}))
        _logger.info(courses)
        self.update({'course_ids': courses})

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
    
class IndividualCourse(models.Model):
    '''Individual Course'''
    _name = 'school.individual_course'
    _description = 'Individual Course'
    _inherit = ['mail.thread']
    
    _order = 'sequence'
    
    name = fields.Char(related="source_course_id.name", readonly=True, store=True)
    title = fields.Char(related="source_course_id.title", readonly=True, store=True)
    level = fields.Integer(related="source_course_id.level", readonly=True)
    
    sequence = fields.Integer(related="source_course_id.sequence", readonly=True, store=True)
    
    year_id = fields.Many2one('school.year', related="course_group_id.bloc_id.year_id",store=True)
    student_id = fields.Many2one('res.partner', related="course_group_id.bloc_id.student_id",store=True)
    teacher_id = fields.Many2one('res.partner', string='Teacher', domain=[('teacher', '=', True)], store=True)

    image = fields.Binary('Image', attachment=True, related='student_id.image')
    image_medium = fields.Binary('Image', attachment=True, related='student_id.image_medium')
    image_small = fields.Binary('Image', attachment=True, related='student_id.image_small')

    credits = fields.Integer(related="source_course_id.credits", readonly=True)
    hours = fields.Integer(related="source_course_id.hours", readonly=True)
    weight =  fields.Float(related="source_course_id.weight", readonly=True)
    
    dispense = fields.Boolean(string="Dispensed",default=False)
    
    source_course_id = fields.Many2one('school.course', string="Source Course", auto_join=True)
    
    source_bloc_id = fields.Many2one('school.bloc', string="Source Bloc", related='course_group_id.bloc_id.source_bloc_id', readonly=True, store=True)
    source_bloc_name = fields.Char(related='course_group_id.bloc_id.source_bloc_name', string="Source Course Bloc Name", readonly=True, store=True)
    source_bloc_level = fields.Selection([('0','Free'),('1','Bac 1'),('2','Bac 2'),('3','Bac 3'),('4','Master 1'),('5','Master 2'),],related='course_group_id.bloc_id.source_bloc_level', string="Source Course Bloc Level", readonly=True, store=True)
    
    course_group_id = fields.Many2one('school.individual_course_group', string='Course Groups', ondelete='cascade', readonly=True)
    bloc_id = fields.Many2one('school.individual_bloc', string='Bloc', related='course_group_id.bloc_id', readonly=True)
    
    
class IndividualCourseProxy(models.Model):
    _name = 'school.individual_course_proxy'
    _auto = False

    name = fields.Char(string="Name", readonly=True)
    title = fields.Char(string="Title", readonly=True)
    
    year_id = fields.Many2one('school.year', string='Year', readonly=True)
    teacher_id = fields.Many2one('res.partner', string='Teacher', readonly=True)
    source_course_id = fields.Many2one('school.course', string="Source Course", readonly=True)

    def init(self, cr):
        """ School Individual Course Proxy """
        tools.drop_view_if_exists(cr, 'school_individual_course_proxy')
        cr.execute(""" CREATE VIEW school_individual_course_proxy AS (
            SELECT
                CAST(CAST(school_individual_course.year_id AS text)||
                CAST(school_individual_course.teacher_id AS text)||
                CAST(school_individual_course.source_course_id AS text) AS INTEGER) as id,
                school_individual_course.name,
                school_individual_course.title,
                school_individual_course.year_id,
                school_individual_course.teacher_id,
                school_individual_course.source_course_id
            FROM
                school_individual_course
            WHERE
                school_individual_course.teacher_id IS NOT NULL
            GROUP BY CAST(CAST(school_individual_course.year_id AS text)||
                CAST(school_individual_course.teacher_id AS text)||
                CAST(school_individual_course.source_course_id AS text) AS INTEGER),
                school_individual_course.name,
                school_individual_course.title,
                school_individual_course.year_id,
                school_individual_course.teacher_id,
                school_individual_course.source_course_id
        )""")
        
        
    @api.multi
    def edit_course(self):
        self.ensure_one()
        value = {
            'domain': "[]",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'school.individual_course',
            'view_id': False,
            'context': dict(self._context or {}),
            'type': 'ir.actions.act_window',
            'search_view_id': False
        }
        return value