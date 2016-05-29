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
from openerp.exceptions import UserError

_logger = logging.getLogger(__name__)

class IndividualCourseGroup(models.Model):
    '''Individual Course Group'''
    _inherit = 'school.individual_course_group'
    
    state = fields.Selection([
            ('draft','Draft'),
            ('progress','In Progress'),
            ('finish', 'Awarded'),
        ], string='Status', index=True, readonly=True, default='draft',
        #track_visibility='onchange', TODO : is this useful for this case ?
        copy=False,
        help=" * The 'Draft' status is used when results are not confirmed yet.\n"
             " * The 'Confirmed' status is when restults are confirmed.")
    
    ## First Session ##
    
    first_session_computed_result = fields.Float(compute='compute_results', string='First Session Computed Result', store=True, digits=(5, 2))
    first_session_computed_result_bool= fields.Boolean(compute='compute_results', string='First Session Computed Active', store=True)
    first_session_deliberated_result = fields.Char(string='First Session Deliberated Result')
    first_session_deliberated_result_bool= fields.Boolean(string='First Session Deliberated Active')
    first_session_result= fields.Float(compute='compute_results', string='First Session Result', store=True, digits=(5, 2))
    first_session_result_bool= fields.Boolean(compute='compute_results', string='First Session Active', store=True)
    first_session_acquiered = fields.Selection(([('A', 'Acquired'),('NA', 'Not Acquired')]),string='First Session Acquired Credits',default='NA',required=True)
    first_session_note = fields.Text(string='First Session Notes')
    
    ## Second Session ##
    
    second_session_computed_result = fields.Float(compute='compute_results', string='Second Session Computed Result', store=True, digits=(5, 2))
    second_session_computed_result_bool= fields.Boolean(compute='compute_results', string='Second Session Computed Active', store=True)
    second_session_deliberated_result = fields.Char(string='Second Session Deliberated Result', digits=(5, 2))
    second_session_deliberated_result_bool= fields.Boolean(string='Second Session Deliberated Active')
    second_session_result= fields.Float(compute='compute_results', string='Second Session Result', store=True, digits=(5, 2))
    second_session_result_bool= fields.Boolean(compute='compute_results', string='Second Session Active', store=True)
    second_session_acquiered = fields.Selection(([('A', 'Acquired'),('NA', 'Not Acquired')]),string='Second Session Acquired Credits',default='NA',required=True)
    second_session_note = fields.Text(string='Second Session Notes')
    
    ## Final ##
    
    final_result = fields.Float(compute='compute_results', string='Final Result', store=True, digits=(5, 2))
    final_result_bool = fields.Boolean(compute='compute_results', string='Final Active')
    acquiered = fields.Selection(([('A', 'Acquiered'),('NA', 'Not Acquiered')]), compute='compute_results', string='Acquired Credits', store=True)
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
            if self.total_weight > 0:
                self.first_session_computed_result = running_first_session_result / self.total_weight
        if self.second_session_computed_result_bool :
            if self.total_weight > 0:
                self.second_session_computed_result = running_second_session_result / self.total_weight
        
        ## Compute Session Results
        if self.first_session_deliberated_result :
            try:
                f = float(self.first_session_deliberated_result)
                self.first_session_result = f
                self.first_session_result_bool = True
            except ValueError:
                self.write('first_session_deliberated_result', None)
                raise UserError(_('Cannot decode %s, please encode a Float eg "12.00".' % self.first_session_deliberated_result))
        elif self.first_session_computed_result_bool :
            self.first_session_result = self.first_session_computed_result
            self.first_session_result_bool = True
        else :
            self.first_session_result_bool = False
        
        if self.second_session_deliberated_result_bool :
            try:
                f = float(self.second_session_deliberated_result)
                self.second_session_result = f
                self.second_session_result_bool = True
            except ValueError:
                self.write('second_session_deliberated_result', None)
                raise UserError(_('Cannot decode %s, please encode a Float eg "12.00".' % self.second_session_deliberated_result))
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
        

class Course(models.Model):
    '''Course'''
    _inherit = 'school.course'
    
    type = fields.Selection(([('S', 'Simple'),('T', 'Triple'),('C', 'Complex')]), string='Type')

class IndividualCourse(models.Model):
    '''Individual Course'''
    _inherit = 'school.individual_course'
    
    type = fields.Selection(([('S', 'Simple'),('T', 'Triple'),('C', 'Complex'),('D','Deferral')]), string='Type', required=True, default="S")
    
    @api.model
    def create(self, values):
        if not(values.get('type', False)) and values.get('source_course_id', False):
            course = self.env['school.course'].browse(values['source_course_id'])
            values['type'] = course.type or 'S'
        result = super(IndividualCourse, self).create(values)
        return result
    
    @api.one
    def write(self, vals):
        if self.type == 'S':
            vals['ann_result'] = False
            vals['jan_result'] = False
        elif self.type == 'T':
            vals['ann_result'] = False
        res = super(IndividualCourse, self).write(vals)
        self.course_group_id.compute_results()
        return res
    
    @api.onchange('type')
    @api.depends('ann_result','jan_result','jun_result','sept_result')
    def onchange_type(self):
        self.ann_result = False
        self.jan_result = False
        self.jun_result = False
        self.sept_result = False

    ## Annual Evaluation ##
    
    ann_result= fields.Char(string='Annual Result')
    
    ## January Evaluation ##
    
    jan_result= fields.Char(string='January Result')
    
    ## June Evaluation ##
    
    jun_result= fields.Char(string='June Result')
    
    ## September Evaluation ##
    
    sept_result= fields.Char(string='September Result')
    
    ## First Session ##
    
    first_session_result= fields.Float(compute='compute_results', string='First Session Result', store=True)
    first_session_result_bool = fields.Boolean(compute='compute_results', string='First Session Active', store=True)
    first_session_note = fields.Text(string='First Session Notes')
    
    ## Second Session ##
    
    second_session_result= fields.Float(compute='compute_results', string='Second Session Result', store=True)
    second_session_result_bool = fields.Boolean(compute='compute_results', string='Second Session Active', store=True)
    second_session_note = fields.Text(string='Second Session Notes')
    
    @api.depends('ann_result','jan_result','jun_result','sept_result')
    @api.one
    def compute_results(self):
        if self.type in ['S','D','T']:
            if self.jan_result :
                try:
                    f = float(self.jan_result)
                    self.first_session_result = f
                    self.first_session_result_bool = True
                except ValueError:
                    self.first_session_result = 0
                    self.first_session_result_bool = False
                    raise UserError(_('Cannot decode %s in January Result, please encode a Float eg "12.00".' % self.jan_result))
            if self.jun_result :
                try:
                    f = float(self.jun_result)
                    self.first_session_result = f
                    self.first_session_result_bool = True
                except ValueError:
                    self.first_session_result = 0
                    self.first_session_result_bool = False
                    raise UserError(_('Cannot decode %s in June Result, please encode a Float eg "12.00".' % self.jun_result))
            if self.sept_result :
                try:
                    f = float(self.sept_result)
                    self.second_session_result = f
                    self.second_session_result_bool = True 
                except ValueError:
                    self.second_session_result = 0
                    self.second_session_result_bool = False
                    raise UserError(_('Cannot decode %s in September Result, please encode a Float eg "12.00".' % self.sept_result))
        if self.type in ['C']:
            ann = None
            jan = None
            if self.ann_result :
                try:
                    ann = float(self.ann_result)
                except ValueError:
                    raise UserError(_('Cannot decode %s in January Result, please encode a Float eg "12.00".' % self.ann_result))
            if self.jan_result :
                try:
                    jan = float(self.jan_result)
                except ValueError:
                    raise UserError(_('Cannot decode %s in January Result, please encode a Float eg "12.00".' % self.jan_result))
            if self.jun_result :
                try:
                    jun = float(self.jun_result)
                    if ann and jan and jun :
                        self.first_session_result = ann * 0.5 + (jan * 0.5 + jun * 0.5) * 0.5
                        self.first_session_result_bool = True
                    else:
                        self.first_session_result = 0
                        self.first_session_result_bool = False
                except ValueError:
                    self.first_session_result = 0
                    self.first_session_result_bool = False
                    raise UserError(_('Cannot decode %s in June Result, please encode a Float eg "12.00".' % self.jun_result))
            if self.sept_result :
                try:
                    sept = float(self.sept_result)
                    if ann and sept :
                        self.second_session_result = ann * 0.5 + sept * 0.5
                        self.second_session_result_bool = True 
                    else:
                        self.first_session_result = 0
                        self.first_session_result_bool = False
                except ValueError:
                    self.second_session_result = 0
                    self.second_session_result_bool = False
                    raise UserError(_('Cannot decode %s in September Result, please encode a Float eg "12.00".' % self.sept_result))
        
    

class IndividualBloc(models.Model):
    '''Individual Bloc'''
    _inherit = 'school.individual_bloc'
    
    state = fields.Selection([
            ('draft','Draft'),
            ('progress','In Progress'),
            ('postponed', 'Postponed'),
            ('awarded', 'Awarded'),
            ('failed', 'Failed'),
        ], string='Status', index=True, readonly=True, default='draft',
        #track_visibility='onchange', TODO : is this useful for this case ?
        copy=False,
        help=" * The 'Draft' status is used when results are not confirmed yet.\n"
             " * The 'In Progress' status is used during the courses.\n"
             " * The 'Postponed' status is used when a second session is required.\n"
             " * The 'Awarded' status is used when the bloc is awarded.\n"
             " * The 'Failed' status is used during the bloc is definitively considered as failed.\n"
             )
    
    @api.multi
    def set_state(self, state):
        # TODO use a workflow to make sure only valid changes are used.
        return self.write({'state': state})
    
    totat_acquiered_credits = fields.Integer(string="Acquiered Credits",compute="compute_credits", store=True)
    
    @api.depends('course_group_ids','course_group_ids.acquiered')
    @api.one
    def compute_credits(self):
        total = 0
        for icg in self.course_group_ids:
            if icg.acquiered == 'A':
                total += icg.total_credits
        self.totat_acquiered_credits = total