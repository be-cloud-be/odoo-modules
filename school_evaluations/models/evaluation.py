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

class IndividualCourseGroup(models.Model):
    '''Individual Course Group'''
    _inherit = 'school.individual_course_group'
    
    first_evaluation_result = fields.Float(related='first_evaluation_id.result',string='S1')
    second_evaluation_result = fields.Float(related='second_evaluation_id.result',string='S2')
    final_evaluation_result = fields.Float(compute='get_final_eval',string='Fin')
    acquired = fields.Boolean(compute='get_final_eval',string='Acquired')
    
    first_evaluation_id = fields.Many2one('school.group_evaluation', string='First Session', delete='cascade')
    second_evaluation_id = fields.Many2one('school.group_evaluation', string='Second Session', delete='cascade')
    
    final_evaluation_id = fields.Many2one('school.group_evaluation', compute='get_final_eval')
    
    @api.depends('first_evaluation_id','second_evaluation_id')
    @api.multi
    def get_final_eval(self):
        for cg in self:
            if cg.second_evaluation_id :
                cg.final_evaluation_id = cg.second_evaluation_id
                cg.final_evaluation_result = cg.second_evaluation_id.result
                cg.acquired = cg.second_evaluation_id.acquired
            else:
                cg.final_evaluation_id = cg.first_evaluation_id
                cg.final_evaluation_result = cg.first_evaluation_id.result
                cg.acquired = cg.first_evaluation_id.acquired

class GroupEvaluation(models.Model):
    '''Group Evaluation'''
    _name = 'school.group_evaluation'
    _description = 'Group Evaluation'
    
    computed_result = fields.Float(string='Computed Result')
    deliberated_result = fields.Float(string='Deliberated Result', default=-1)
    acquired = fields.Boolean(string='Acquired', required=True, default=False)
    notes = fields.Text(string='Notes')

    result = fields.Float(string='Result', compute='get_result')
    
    @api.depends('computed_result','deliberated_result')
    @api.multi
    def get_final_eval(self):
        for ge in self:
            if self.deliberated_result < 0:
                ge.result = ge.deliberated_result
            else:
                ge.result = ge.computed_result

class IndividualCourse(models.Model):
    '''Individual Course'''
    _inherit = 'school.individual_course'
    
    first_evaluation_result = fields.Float(related='first_evaluation_id.result',string='S1')
    second_evaluation_result = fields.Float(related='second_evaluation_id.result',string='S2')
    final_evaluation_result = fields.Float(compute='get_final_eval',string='Fin')
    
    first_evaluation_id = fields.Many2one('school.evaluation', string='First Session', delete='cascade')
    second_evaluation_id = fields.Many2one('school.evaluation', string='Second Session', delete='cascade')
    
    final_evaluation_id = fields.Many2one('school.evaluation', compute='get_final_eval')
    
    @api.depends('first_evaluation_id','second_evaluation_id')
    @api.multi
    def get_final_eval(self):
        for ic in self:
            if ic.second_evaluation_id :
                ic.final_evaluation_id = ic.second_evaluation_id
                ic.final_evaluation_result = ic.second_evaluation_id.result
            else:
                ic.final_evaluation_id = ic.first_evaluation_id
                ic.final_evaluation_result = ic.first_evaluation_id.result

class Evaluation(models.Model):
    '''Evaluation'''
    _name = 'school.evaluation'
    _description = 'Evaluation'
    
    result = fields.Float(string='Result')
    notes = fields.Text(string='Notes')