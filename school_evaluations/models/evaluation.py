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
    
    first_session_computed_result = fields.Float(computed='compute_results', string='First Session Computed Result', store=True, digits=(5, 2))
    first_session_computed_result_bool= fields.Boolean(computed='compute_results', string='First Session Computed Active', store=True)
    first_session_deliberated_result = fields.Float(string='First Session Deliberated Result', digits=(5, 2))
    first_session_deliberated_result_bool= fields.Boolean(string='First Session Deliberated Active')
    first_session_result= fields.Float(computed='compute_results', string='First Session Result', store=True, digits=(5, 2))
    first_session_result_bool= fields.Boolean(computed='compute_results', string='First Session Active', store=True)
    first_session_acquiered = fields.Selection(([('A', 'Aquired'),('NA', 'Not Acquired')]),string='First Session Acquired Credits',default='NA',required=True)
    first_session_note = fields.Text(string='First Session Notes')
    
    ## Second Session ##
    
    second_session_computed_result = fields.Float(computed='compute_results', string='Second Session Computed Result', store=True, digits=(5, 2))
    second_session_computed_result_bool= fields.Boolean(computed='compute_results', string='Second Session Computed Active', store=True)
    second_session_deliberated_result = fields.Float(string='Second Session Deliberated Result', digits=(5, 2))
    second_session_deliberated_result_bool= fields.Boolean(string='Second Session Deliberated Active')
    second_session_result= fields.Float(computed='compute_results', string='Second Session Result', store=True, digits=(5, 2))
    second_session_result_bool= fields.Boolean(computed='compute_results', string='Second Session Active', store=True)
    second_session_acquiered = fields.Selection(([('A', 'Aquired'),('NA', 'Not Acquired')]),string='Second Session Acquired Credits',default='NA',required=True)
    second_session_note = fields.Text(string='Second Session Notes')
    
    ## Final ##
    
    final_result = fields.Float(compute='compute_results', string='Final Result', store=True, digits=(5, 2))
    final_result_bool = fields.Boolean(compute='compute_results', string='Final Active')
    acquiered = fields.Selection(([('A', 'Aquiered'),('NA', 'Not Acquiered')]), compute='compute_results', string='Acquired Credits',required=True, store=True)
    final_note = fields.Text(string='Final Notes')
    
    @api.depends('course_ids',
                 'first_session_deliberated_result_bool',
                 'first_session_deliberated_result',
                 'first_session_acquiered',
                 'second_session_deliberated_result_bool',
                 'second_session_deliberated_result',
                 'second_session_acquiered')
    @api.one
    def compute_results(self):
        ## Compute Weighted Average
        running_first_session_result = 0
        running_second_session_result = 0
        self.first_session_computed_result_bool = False
        self.second_session_computed_result_bool = False
        for ic in self.course_ids:
            if ic.first_session_result_bool :
                running_first_session_result += ic.first_session_result * ic.weight
                self.first_session_computed_result_bool = True
            if ic.second_session_result_bool :
                running_second_session_result += ic.second_session_result * ic.weight
                self.second_session_computed_result_bool = True
            # In case there is a result for first session and not second one while a second exists
            elif ic.first_session_result_bool : 
                running_second_session_result += ic.first_session_result * ic.weight
        if self.first_session_computed_result_bool :
            self.first_session_computed_result = running_first_session_result / self.total_weight
        if self.second_session_computed_result_bool :
            self.second_session_computed_result = running_second_session_result / self.total_weight
        
        ## Compute Session Results
        if self.first_session_deliberated_result_bool :
            self.first_session_result = self.first_session_deliberated_result
            self.first_session_result_bool = True
        elif self.first_session_computed_result_bool :
            self.first_session_result = self.first_session_computed_result
            self.first_session_result_bool = True
        else :
            self.first_session_result_bool = False
        
        if self.second_session_deliberated_result_bool :
            self.second_session_result = self.second_session_deliberated_result
            self.second_session_result_bool = True
        elif self.second_session_computed_result_bool :
            self.second_session_result = self.second_session_computed_result
            self.second_session_result_bool = True
        else :
            self.second_session_result_bool = False
        
        ## Compute Final Results
        if self.second_session_result_bool :
            self.final_result = self.second_session_result
            self.acquiered = self.second_session_acquiered
            self.final_result_bool = True
        elif self.first_session_result_bool :
            self.final_result = self.first_session_result
            self.acquiered = self.first_session_acquiered
            self.final_result_bool = True
        else :
            self.acquiered = 'NA'
            self.final_result_bool = False
        

class IndividualCourse(models.Model):
    '''Individual Course'''
    _inherit = 'school.individual_course'
    
    type = fields.Selection(([('S', 'Simple'),('T', 'Triple'),('C', 'Complex')]), string='Type',required=True)
    
    ## Annual Evaluation ##
    
    annual_result= fields.Float(string='Annual Result', digits=(5, 2))
    annual_result_bool= fields.Boolean(string='Annual Active')
    annual_note = fields.Text(string='Annual Notes')
    
    ## January Evaluation ##
    
    jan_result= fields.Float(string='January Result', digits=(5, 2))
    jan_result_bool= fields.Boolean(string='January Active')
    jan_note = fields.Text(string='January Notes')
    
    ## First Session ##
    
    first_session_result= fields.Float(string='First Session Result', digits=(5, 2))
    first_session_result_bool= fields.Boolean(string='First Session Active')
    first_session_note = fields.Text(string='First Session Notes')
    
    ## Second Session ##
    
    second_session_result= fields.Float(string='Second Session Result', digits=(5, 2))
    second_session_result_bool= fields.Boolean(string='Second Session Active')
    second_session_note = fields.Text(string='Second Session Notes')
    
    ## Final ##
    
    final_result = fields.Float(compute='compute_results', string='Final Result', digits=(5, 2))
    final_result_bool = fields.Boolean(compute='compute_results', string='Final Active')
    final_note = fields.Text(string='Final Notes')
    
    @api.depends('first_session_result','second_session_result','first_session_result_bool','second_session_result_bool')
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
                
class IndividualBloc(models.Model):
    '''Individual Bloc'''
    _inherit = 'school.individual_bloc'
    
    state = fields.Selection([
            ('draft','Draft'),
            ('confirmed', 'Confirmed'),
        ], string='Status', index=True, readonly=True, default='draft',
        #track_visibility='onchange', TODO : is this useful for this case ?
        copy=False,
        help=" * The 'Draft' status is used when results are not confirmed yet.\n"
             " * The 'Confirmed' status is when restults are confirmed.")
    
    @api.multi
    def set_to_draft(self):
        return self.write({'state': 'draft'})
    
    @api.multi
    def confirm(self):
        return self.write({'state': 'confirmed'})
    
    totat_acquiered_credits = fields.Integer(string="Acquiered Credits",compute="compute_credits", store=True)
    
    @api.depends('course_group_ids')
    @api.one
    def compute_credits(self):
        total = 0
        for icg in self.course_group_ids:
            if icg.acquiered == 'A':
                total += icg.total_credits
        self.totat_acquiered_credits = total
    
    @api.model
    def get_data_for_evaluation_widget(self):
        """ Returns the data required to display an evaluation widget """
        ret =   {
            "res_company" :
                {
                    "name" : self.env.user.company_id.name
                    },
            "groups" : [
                        {   
                            'id' : 0, 
                            'title' : "Bloc 1",
                            'blocs' : self.get_blocs_for_evaluation_widget(level=1),
                        },
                        { 
                            'id' : 1, 
                            'title' : "Bloc 2",
                            'blocs' : self.get_blocs_for_evaluation_widget(level=2),
                        },
                        { 
                            'id' : 2, 
                            'title' : "Bloc 3",
                            'blocs' : self.get_blocs_for_evaluation_widget(level=3),
                        },
            ],
        }
        return ret

    def get_blocs_for_evaluation_widget(self, level):
        """ Returns the data required by the evaluation widget to display a bloc """
        ret = []
        bloc_ids = self.env['school.individual_bloc'].search([('source_bloc_level','=',level)])
        for bloc in bloc_ids:
            ret.append({
                'id' : bloc.id,
                'name': bloc.name,
                'student': bloc.student_id.name,
            })
        return ret