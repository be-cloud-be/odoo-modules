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

class CourseGroup(models.Model):
    '''Course Group'''
    _inherit = 'school.course_group'
    
    pre_requisit_ids = fields.One2many('school.prerequisit', 'course_id', 'Prerequisits')
    co_requisit_ids = fields.One2many('school.corequisit', string='Corequisits', compute='_compute_co_requisit_ids')
    co_requisit_course_ids = fields.One2many('school.course_group', string='Corequisits', compute='_compute_co_requisit_ids')

    @api.one
    def _compute_co_requisit_ids(self):
        self.co_requisit_ids = self.env['school.corequisit'].search(['|',('course1_id','=',self.id),('course2_id','=',self.id)])
        ret_ids = []
        for co_requisit in self.co_requisit_ids:
            if co_requisit.course1_id == self:
                ret_ids.append(co_requisit.course2_id.id)
            else:
                ret_ids.append(co_requisit.course1_id.id)
        self.co_requisit_course_ids = ret_ids
        
        
class PreRequisit(models.Model):
    '''PreRequisit'''
    _name = 'school.prerequisit'
    
    course_id = fields.Many2one('school.course_group', 'Course')
    preriquisit_id = fields.Many2one('school.course_group', 'Prerequisit')
    
class CoRequisit(models.Model):
    '''CoRequisit'''
    _name = 'school.corequisit'
    
    course1_id = fields.Many2one('school.course_group', 'Course 1')
    course2_id = fields.Many2one('school.course_group', 'Course 2')