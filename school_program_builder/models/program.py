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

class Bloc(models.Model):
    '''Bloc'''
    _inherit = 'school.bloc'
    
    is_composite = fields.Boolean(string="Is Composite")
    
    child_bloc_ids = fields.Many2many('school.composite_bloc','bloc_composite_bloc_rel', 'parent_id','child_id', string="Child Bloc", copy=True)
    child_course_group_ids = fields.Many2many('school.course_group','bloc_course_group_child_rel', 'parent_id','child_id', string="Child Course Group", ondelete="set null", copy=True)
    
    @api.one
    def populate_course_group_ids(self):
        if self.is_composite :
            ret = self.child_course_group_ids
            for child in self.child_bloc_ids:
                child.populate_course_group_ids()
                ret |= child.course_group_ids
            self.course_group_ids = ret
        
class CompositeBloc(models.Model):
    '''Composite Bloc'''
    _name = 'school.composite_bloc'
    _description = 'Program'
    _inherit = ['mail.thread','school.year_sequence.mixin']
    _order = 'title, sequence'
        
    sequence = fields.Integer(string='Sequence')
    title = fields.Char(required=True, string='Title')
    year_id = fields.Many2one('school.year', string="Year")
    description = fields.Text(string='Description')
    
    level = fields.Selection([('0','Free'),('1','Bac 1'),('2','Bac 2'),('3','Bac 3'),('4','Master 1'),('5','Master 2'),],string='Level')
    
    name = fields.Char(string='Name', compute='compute_name', store=True)
    
    @api.depends('sequence','title','level')
    @api.multi
    def compute_name(self):
        for bloc in self:
            bloc.name = "%s - %s" % (bloc.title,[('0','Free'),('1','Bac 1'),('2','Bac 2'),('3','Bac 3'),('4','Master 1'),('5','Master 2'),][int(bloc.level)][1])
    # TODO Change this to use cycle short name

    total_credits = fields.Integer(compute='_get_courses_total', string='Total Credits')
    total_hours = fields.Integer(compute='_get_courses_total', string='Total Hours')
    total_weight = fields.Float(compute='_get_courses_total', string='Total Weight')
    
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
    
    course_group_ids = fields.Many2many('school.course_group','school_bloc_composite_course_group_rel', id1='bloc_id', id2='group_id',string='Course Groups', copy=True, domain=['|',('active','=',False),('active','=',True)])
    
    parent_bloc_ids = fields.Many2many('school.composite_bloc','composite_bloc_composite_bloc_rel', 'child_id','parent_id', string="Parent Bloc", copy=True)
    child_bloc_ids = fields.Many2many('school.composite_bloc','composite_bloc_composite_bloc_rel', 'parent_id','child_id', string="Child Bloc", copy=True, domain="[('year_id','=',year_id)]")
    
    child_course_group_ids = fields.Many2many('school.course_group','composite_bloc_course_group_child_rel', 'parent_id','child_id', string="Child Course Group", ondelete="set null", copy=True)

    @api.one
    def populate_course_group_ids(self):
        ret = self.child_course_group_ids
        for child in self.child_bloc_ids:
            child.populate_course_group_ids()
            ret |= child.course_group_ids
        self.course_group_ids = ret

class CourseGroup(models.Model):
    '''Course Group'''
    _inherit = 'school.course_group'
    
    composite_parent_ids = fields.Many2many('school.course_group','bloc_course_group_child_rel', 'child_id','parent_id', string="Parent Composite")