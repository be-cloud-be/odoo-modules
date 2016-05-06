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
    
    ## First Session ##
    
    first_session_computed_result = fields.Float(computed='compute_results', string='First Session Computed Result')
    first_session_computed_result_bool= fields.Boolean(string='First Session Computed Active')
    first_session_deliberated_result = fields.Float(string='First Session Deliberated Result')
    first_session_deliberated_result_bool= fields.Boolean(string='First Session Deliberated Active')
    first_session_result= fields.Float(computed='compute_results', string='First Session Result')
    first_session_result_bool= fields.Boolean(computed='compute_results', string='First Session Active')
    first_session_acquiered = fields.Selection(([('A', 'Aquired'),('NA', 'Not Acquired')]),string='First Session Acquired Credits',default='NA',required=True)
    first_session_note = fields.Text(string='First Session Notes')
    
    ## Second Session ##
    
    second_session_computed_result = fields.Float(computed='compute_results', string='Second Session Computed Result')
    second_session_computed_result_bool= fields.Boolean(string='Second Session Computed Active')
    second_session_deliberated_result = fields.Float(string='Second Session Deliberated Result')
    second_session_deliberated_result_bool= fields.Boolean(string='Second Session Deliberated Active')
    second_session_result= fields.Float(computed='compute_results', string='Second Session Result')
    second_session_result_bool= fields.Boolean(computed='compute_results', string='Second Session Active')
    second_session_acquiered = fields.Selection(([('A', 'Aquired'),('NA', 'Not Acquired')]),string='Second Session Acquired Credits',default='NA',required=True)
    second_session_note = fields.Text(string='Second Session Notes')
    
    ## Final ##
    
    final_result = fields.Float(compute='compute_results', string='Final Result')
    final_result_bool = fields.Boolean(compute='compute_results', string='Final Active')
    acquiered = fields.Selection(([('A', 'Aquired'),('NA', 'Not Acquired')]),string='Acquired Credits',default='NA',required=True)
    final_note = fields.Text(string='Final Notes')
    
    @api.depends('course_ids','total_weight','first_session_deliberated_result','second_session_deliberated_result')
    @api.multi
    def compute_results(self):
        for cg in self:
            ## Compute Weighted Average
            running_first_session_result = 0
            running_second_session_result = 0
            for ic in cg.course_ids:
                if ic.first_session_result_bool :
                    running_first_session_result += ic.first_session_result * ic.weight
                    cg.first_session_computed_result_bool = True
                if ic.second_session_result_bool :
                    running_second_session_result += ic.second_session_result * ic.weight
                    cg.second_session_computed_result_bool = True
            if cg.first_session_computed_result_bool :
                cg.first_session_computed_result = running_first_session_result / cg.total_weight
            if cg.second_session_computed_result_bool :
                cg.second_session_computed_result = running_second_session_result / cg.total_weight
            
            ## Compute Session Results
            if cg.first_session_deliberated_result_bool :
                cg.first_session_result = cg.first_session_deliberated_result
                cg.first_session_result_bool = True
            elif cg.first_session_computed_result_bool :
                cg.first_session_result = cg.first_session_computed_result
                cg.first_session_result_bool = True
            else :
                cg.first_session_result_bool = False
            
            if cg.second_session_deliberated_result_bool :
                cg.second_session_result = cg.second_session_deliberated_result
                cg.second_session_result_bool = True
            elif cg.second_session_computed_result_bool :
                cg.second_session_result = cg.second_session_computed_result
                cg.second_session_result_bool = True
            else :
                cg.second_session_result_bool = False
            
            ## Compute Final Results
            if cg.second_session_result_bool :
                cg.final_result = cg.second_session_result
                cg.final_result_bool = True
                cg.acquired = cg.second_session_acquiered
            elif cg.first_session_result_bool :
                cg.final_result = cg.first_session_result
                cg.final_result_bool = True
                cg.acquired = cg.first_session_acquiered
            else :
                cg.final_result_bool = False

class IndividualCourse(models.Model):
    '''Individual Course'''
    _inherit = 'school.individual_course'
    
    ## First Session ##
    
    first_session_result= fields.Float(string='First Session Result')
    first_session_result_bool= fields.Boolean(string='First Session Active')
    first_session_note = fields.Text(string='First Session Notes')
    
    ## Second Session ##
    
    second_session_result= fields.Float(string='Second Session Result')
    second_session_result_bool= fields.Boolean(string='Second Session Active')
    second_session_note = fields.Text(string='Second Session Notes')
    
    ## Final ##
    
    final_result = fields.Float(compute='compute_results', string='Final Result')
    final_result_bool = fields.Boolean(compute='compute_results', string='Final Active')
    final_note = fields.Text(string='Final Notes')
    
    @api.depends('first_session_result','second_session_result')
    @api.multi
    def compute_results(self):
        for ic in self:
            if ic.second_session_result_bool :
                ic.final_result = ic.second_session_result
                ic.final_result_bool = True
            elif ic.first_session_result_bool :
                ic.final_result = ic.first_session_result
                ic.final_result_bool = True
            else :
                ic.final_result_bool = False