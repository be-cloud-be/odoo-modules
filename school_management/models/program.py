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

class IndividualProgram(models.Model):
    '''Individual Program'''
    _name='school.individual_program'
    _description='Individual Program'
    
    year_id = fields.Many2one('school.year', string='Year')
    student_id = fields.Many2one('res.partner', string='Student', domain="[('student', '=', '1')]")
    source_bloc_id = fields.Many2one('school.bloc', string="Source Bloc")
    bloc_id = fields.Many2one('school.individual_bloc', string="Individual Bloc", readonly=True)
    
    _sql_constraints = [
	        ('uniq_student_bloc', 'unique(year_id, student_id)', 'A student can only do one bloc in a given year'),
    ]
    
    @api.model
    def create(self, vals):
        ret = super(IndividualProgram, self).create(vals)
        if vals['source_bloc_id']:
            _logger.info('HEREHEREHRHERHE')
            ret.write({'bloc_id' : self.env['school.individual_bloc'].create({'source_bloc_id': self.source_bloc_id})})
            _logger.info(ret.bloc_id)
        return ret
    
    @api.onchange('source_bloc_id')
    def _onchange_source_bloc_id(self):
        self.env['school.individual_bloc'].create({'source_bloc_id': self.source_bloc_id})
    
class IndividualBloc(models.Model):
    '''Individual Bloc'''
    _name='school.individual_bloc'
    _description='Individual Bloc'
    
    source_bloc_id = fields.Many2one('school.bloc', string="Source Bloc",readonly=True)
    course_group_ids = fields.One2many('school.individual_course_group', 'bloc_id', string='Courses Groups')
    
    @api.model
    def create(self, vals):
        if vals['source_bloc_id']:
            ret = super(IndividualBloc, self).create(vals)
            for course_group in vals['source_bloc_id'].course_group_ids:
                cg = self.env['school.individual_course_group'].create({'bloc_id':ret.id,'course_groupc_id': course_group})
                self.course_group_ids.append(cg.id)
            return ret
        else:
            UserError('Cannot create an individual bloc without source')
    
class IndividualCourseGroup(models.Model):
    '''Individual Course Group'''
    _name='school.individual_course_group'
    _description='Individual Course Group'
    
    source_course_groupc_id = fields.Many2one('school.course_group', string="Source Course Group")
    
    bloc_id = fields.Many2one('school.school_individual_bloc', string="Bloc", required=True)
    course_ids = fields.One2many('school.individual_course', 'course_group_id', string='Courses')
    
class IndividualCCourse(models.Model):
    '''IndividualC Course'''
    _name = 'school.individual_course'
    _description = 'IndividualC Course'
    
    source_course_id = fields.Many2one('school.course', string="Source Course")
    
    course_group_id = fields.Many2one('school.individual_course_group', string='Course Groups', required=True)