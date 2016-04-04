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

_logger = logging.getLogger(__name__)

class IndividualBloc(models.Model):
    '''Individual Bloc'''
    _name='school.individual_bloc'
    _description='Individual Bloc'
    _inherit = ['mail.thread']
    
    name = fields.Char(compute='_compute_name',string='Name')
    
    year_id = fields.Many2one('school.year', string='Year', readonly=True)
    student_id = fields.Many2one('res.partner', string='Student', domain="[('student', '=', '1')]", readonly=True)
    source_bloc_id = fields.Many2one('school.bloc', string="Source Bloc", readonly=True)
    
    course_group_ids = fields.One2many('school.individual_course_group', 'bloc_id', string='Courses Groups')
    
    total_credits = fields.Float(compute='_get_courses_total', string='Total Credits')
    total_hours = fields.Float(compute='_get_courses_total', string='Total Hours')
    total_weight = fields.Float(compute='_get_courses_total', string='Total Weight')
        
    @api.model
    def create(self, vals):
        _logger.info('create')
        _logger.info(vals)
        ret = super(IndividualBloc, self).create(vals)
        if vals.has_key('source_bloc_id') :
            _logger.info('create assign course groups')
            source_bloc = self.env['school.bloc'].browse(vals['source_bloc_id'])
            for course_group in source_bloc.course_group_ids:
                ret.course_group_ids.create({'bloc_id':ret.id,'source_course_group_id': course_group.id})
            ret._get_courses_total()
        _logger.info(ret)
        return ret
    
    @api.one
    @api.onchange('source_bloc_id')
    def onchange_source_bloc(self):
        raise UserError('Not Implemented : Cannot change, delete and create a new one.')
        ## _logger.info('onchange')
        ## _logger.info(self.source_bloc_id)
        ## self.course_group_ids = []
        ## for group in self.source_bloc_id.course_group_ids:   
            ## _logger.info('onchange assign course groups')
            ## self.course_group_ids += self.course_group_ids.new({'bloc_id': self.id,'source_course_group_id': group.id})
    
    @api.one
    @api.depends('course_group_ids')
    def _get_courses_total(self):
        total_hours = 0.0
        total_credits = 0.0
        for course_group in self.course_group_ids:
            total_hours += course_group.total_hours
            total_credits += course_group.total_credits
        self.total_hours = total_hours
        self.total_credits = total_credits
    
    @api.one
    @api.depends('year_id.name','student_id.name')
    def _compute_name(self):
        self.name = "%s - %s" % (self.year_id.name,self.student_id.name)
    
    _sql_constraints = [
	        ('uniq_student_bloc', 'unique(year_id, student_id)', 'A student can only do one bloc in a given year'),
    ]
            
class IndividualCourseGroup(models.Model):
    '''Individual Course Group'''
    _name='school.individual_course_group'
    _description='Individual Course Group'
    
    name = fields.Char(related="source_course_group_id.name")
    
    source_course_group_id = fields.Many2one('school.course_group', string="Source Course Group", required=True)
    bloc_id = fields.Many2one('school.individual_bloc', string="Bloc", required=True, ondelete='cascade', readonly=True)
    course_ids = fields.One2many('school.individual_course', 'course_group_id', string='Courses')
    
    total_credits = fields.Float(compute='_get_courses_total', string='Total Credits')
    total_hours = fields.Float(compute='_get_courses_total', string='Total Hours')
    total_weight = fields.Float(compute='_get_courses_total', string='Total Weight')
    
    @api.model
    def create(self, vals):
        _logger.info('create')
        _logger.info(vals)
        ret = super(IndividualCourseGroup, self).create(vals)
        if vals.has_key('source_course_group_id') :
            source_cg = self.env['school.course_group'].browse(vals['source_course_group_id'])
            for course in source_cg.course_ids:
                ret.course_ids.create({'course_group_id':ret.id,'source_course_id': course.id})
            ret._get_courses_total()
        _logger.info(ret.course_ids)
        return ret
    
    
    @api.onchange('source_course_group_id')
    @api.depends('source_course_group_id','course_ids')
    def onchange_source_course_group_id(self):
        _logger.info(self.id)
        ids = []
        for course in self.source_course_group_id.course_ids:
            ids.append(self.course_ids.new({'course_group_id':self.id,'source_course_id': course.id}).id)
        self.course_ids = ids
        self._get_courses_total()
        _logger.info(self.course_ids)
    
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
    
    name = fields.Char(related="source_course_id.name", readonly=True)
    
    credits = fields.Float(related="source_course_id.credits", readonly=True)
    hours = fields.Float(related="source_course_id.hours", readonly=True)
    weight =  fields.Float(related="source_course_id.weight", readonly=True)
    
    dispense = fields.Boolean(string="Dispensed",default=False)
    
    source_course_id = fields.Many2one('school.course', string="Source Course")
    course_group_id = fields.Many2one('school.individual_course_group', string='Course Groups', required=True,ondelete='cascade')