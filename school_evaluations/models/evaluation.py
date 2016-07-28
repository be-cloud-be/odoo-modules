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
    
    enable_exclusion_bool = fields.Boolean(string='Enable exclusion evaluation', default=True)
    
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
    
    enable_exclusion_bool = fields.Boolean(string='Enable exclusion evaluation', related="source_course_group_id.enable_exclusion_bool", readonly=True)
    
    ## First Session ##
    
    first_session_computed_result = fields.Float(compute='compute_average_results', string='First Session Computed Result', store=True, digits=(5, 2))
    first_session_computed_result_bool= fields.Boolean(compute='compute_average_results', string='First Session Computed Active', store=True)
    first_session_computed_exclusion_result_bool= fields.Boolean(compute='compute_average_results', string='First Session Exclusion Result', store=True)
    
    first_session_deliberated_result = fields.Char(string='First Session Deliberated Result',track_visibility='onchange')
    first_session_deliberated_result_bool= fields.Boolean(string='First Session Deliberated Active',track_visibility='onchange')
    
    first_session_result= fields.Float(compute='compute_first_session_results', string='First Session Result', store=True, digits=(5, 2))
    first_session_result_bool= fields.Boolean(compute='compute_first_session_results', string='First Session Active', store=True)
    first_session_acquiered = fields.Selection(([('A', 'Acquired'),('NA', 'Not Acquired')]), compute='compute_first_session_acquiered', string='First Session Acquired Credits',default='NA',store=True,required=True,track_visibility='onchange')
    first_session_note = fields.Text(string='First Session Notes')
    
    ## Second Session ##
    
    second_session_computed_result = fields.Float(compute='compute_average_results', string='Second Session Computed Result', store=True, digits=(5, 2))
    second_session_computed_result_bool= fields.Boolean(compute='compute_average_results', string='Second Session Computed Active', store=True)
    second_session_computed_exclusion_result_bool= fields.Boolean(compute='compute_average_results', string='Second Session Exclusion Result', store=True)
    
    second_session_deliberated_result = fields.Char(string='Second Session Deliberated Result', digits=(5, 2),track_visibility='onchange')
    second_session_deliberated_result_bool= fields.Boolean(string='Second Session Deliberated Active',track_visibility='onchange')
    
    second_session_result= fields.Float(compute='compute_second_session_results', string='Second Session Result', store=True, digits=(5, 2))
    second_session_result_bool= fields.Boolean(compute='compute_second_session_results', string='Second Session Active', store=True)
    second_session_acquiered = fields.Selection(([('A', 'Acquired'),('NA', 'Not Acquired')]), compute='compute_second_session_acquiered',string='Second Session Acquired Credits',default='NA',store=True,required=True,track_visibility='onchange')
    second_session_note = fields.Text(string='Second Session Notes')
    
    ## Final ##
    
    dispense =  fields.Boolean(compute='compute_final_results', string='Dispense',default=False,track_visibility='onchange', store=True)
    
    final_result = fields.Float(compute='compute_final_results', string='Final Result', store=True, digits=(5, 2),track_visibility='onchange')
    final_result_bool = fields.Boolean(compute='compute_final_results', string='Final Active')
    acquiered = fields.Selection(([('A', 'Acquiered'),('NA', 'Not Acquiered')]), compute='compute_final_results', string='Acquired Credits', store=True, track_visibility='onchange',default='NA')
    final_note = fields.Text(string='Final Notes')
    
    def _parse_result(self,input):
        f = float(input)
        if(f < 0 or f > 20):
            raise ValidationError("Evaluation shall be between 0 and 20")
        else:
            return f
    
    ## override so that courses with dispense and no deferred results are excluded from computation
    @api.one
    def _get_courses_total(self):
        _logger.debug('Trigger "_get_courses_total" on Course Group %s' % self.name)
        total_hours = 0.0
        total_credits = 0.0
        total_weight = 0.0
        for course in self.course_ids:
            total_hours += course.hours
            total_credits += course.credits
            total_weight += course.c_weight
        self.total_hours = total_hours
        self.total_credits = total_credits
        self.total_weight = total_weight
    
    @api.one
    def compute_average_results(self):
        _logger.debug('Trigger "compute_average_results" on Course Group %s' % self.name)
        ## Compute Weighted Average
        running_first_session_result = 0
        running_second_session_result = 0
        self.first_session_computed_result_bool = False
        self.first_session_computed_exclusion_result_bool = False
        self.second_session_computed_result_bool = False
        self.second_session_computed_exclusion_result_bool = False
        
        for ic in self.course_ids:
            # Compute First Session 
            if ic.first_session_result_bool :
                running_first_session_result += ic.first_session_result * ic.c_weight
                self.first_session_computed_result_bool = True
                if ic.first_session_result < 10 :
                    self.first_session_computed_exclusion_result_bool = True
                
            # Compute Second Session
            if ic.second_session_result_bool :
                running_second_session_result += ic.second_session_result * ic.c_weight
                self.second_session_computed_result_bool = True
                if ic.second_session_result < 10 :
                    self.second_session_computed_exclusion_result_bool = True
            elif ic.first_session_result_bool :
                # Use First session in computation of the second one if no second one
                running_second_session_result += ic.first_session_result * ic.c_weight
                if ic.first_session_result < 10 :
                    self.second_session_computed_exclusion_result_bool = True
                
        if self.first_session_computed_result_bool :
            if self.total_weight > 0:
                self.first_session_computed_result = running_first_session_result / self.total_weight
        if self.second_session_computed_result_bool :
            if self.total_weight > 0:
                self.second_session_computed_result = running_second_session_result / self.total_weight
    
    @api.depends('first_session_deliberated_result_bool','first_session_deliberated_result','first_session_computed_result_bool','first_session_computed_result')
    @api.one
    def compute_first_session_results(self):
        _logger.debug('Trigger "compute_first_session_results" on Course Group %s' % self.name)
        ## Compute Session Results
        if self.first_session_deliberated_result_bool :
            try:
                f = self._parse_result(self.first_session_deliberated_result)
            except ValueError:
                self.write('first_session_deliberated_result', None)
                raise UserError(_('Cannot decode %s, please encode a Float eg "12.00".' % self.first_session_deliberated_result))
            if (f < self.first_session_computed_result):
                raise ValidationError("Deliberated result must be above computed result, i.e. %s > %s." % (self.first_session_deliberated_result, self.first_session_computed_result))
            else:
                self.first_session_result = f
            self.first_session_result_bool = True
        elif self.first_session_computed_result_bool :
            self.first_session_result = self.first_session_computed_result
            self.first_session_result_bool = True
        else :
            self.first_session_result = 0
            self.first_session_result_bool = False
    
    @api.depends('first_session_result_bool','first_session_result')
    @api.one
    def compute_first_session_acquiered(self):
        _logger.debug('Trigger "compute_first_session_acquiered" on Course Group %s' % self.name)
        self.first_session_acquiered = 'NA'
        if self.enable_exclusion_bool :
            if self.first_session_result >= 10 and (not self.first_session_computed_exclusion_result_bool or self.first_session_deliberated_result_bool):
                self.first_session_acquiered = 'A'
        else:
            if self.first_session_result >= 10 : # cfr appel Ingisi 27-06 and (not self.first_session_computed_exclusion_result_bool or self.first_session_deliberated_result_bool):
                self.first_session_acquiered = 'A'

    @api.depends('second_session_deliberated_result_bool','second_session_deliberated_result','second_session_computed_result_bool','first_session_computed_result')
    @api.one
    def compute_second_session_results(self):
        _logger.debug('Trigger "compute_second_session_results" on Course Group %s' % self.name)
        if self.second_session_deliberated_result_bool :
            try:
                f = self._parse_result(self.second_session_deliberated_result)
            except ValueError:
                self.write('second_session_deliberated_result', None)
                raise UserError(_('Cannot decode %s, please encode a Float eg "12.00".' % self.second_session_deliberated_result))
            if (f < self.second_session_computed_result):
                raise ValidationError("Deliberated result must be above computed result, i.e. %s > %s." % (self.second_session_deliberated_result, self.second_session_computed_result))
            else:
                self.second_session_result = f
            self.second_session_result_bool = True
        elif self.second_session_computed_result_bool :
            self.second_session_result = self.second_session_computed_result
            self.second_session_result_bool = True
        else :
            self.second_session_result = 0
            self.second_session_result_bool = False

    @api.depends('second_session_result_bool','second_session_result')
    @api.one
    def compute_second_session_acquiered(self):
        _logger.debug('Trigger "compute_second_session_acquiered" on Course Group %s' % self.name)
        self.second_session_acquiered = self.first_session_acquiered
        if self.enable_exclusion_bool :
            if self.second_session_result >= 10 and (not self.second_session_computed_exclusion_result_bool or self.second_session_deliberated_result_bool):
                self.second_session_acquiered = 'A'
        else:    
            if self.second_session_result >= 10 : # and (not self.second_session_computed_exclusion_result_bool or self.second_session_deliberated_result_bool):
                self.second_session_acquiered = 'A'

    @api.depends('first_session_result',
                 'first_session_result_bool',
                 'first_session_acquiered',
                 'second_session_result',
                 'second_session_result_bool',
                 'second_session_acquiered',
                 'total_weight')
    @api.one
    def compute_final_results(self):
        _logger.debug('Trigger "compute_final_results" on Course Group %s' % self.name)
        ## Compute Final Results
        if self.second_session_result_bool :
            self.final_result = self.second_session_result
            self.acquiered = self.second_session_acquiered
            self.final_result_bool = True
        elif self.first_session_result_bool :
            self.final_result = self.first_session_result
            self.acquiered = self.first_session_acquiered
            self.final_result_bool = True
        elif self.total_weight == 0:  #TODO ici ça foire à la création d'un nouveau record ???
            self.dispense = True
            self.acquiered = 'A'
        else :
            self.acquiered = 'NA'
            self.final_result_bool = False
    
    @api.one
    def recompute_results(self):
        _logger.debug('Trigger "recompute_results" on Course Group %s' % self.name)
        self._get_courses_total()
        self.compute_average_results()
        self.compute_first_session_results()
        self.compute_second_session_results()
        self.compute_first_session_acquiered()
        self.compute_second_session_acquiered()
        self.compute_final_results()

class Course(models.Model):
    '''Course'''
    _inherit = 'school.course'
    
    type = fields.Selection(([('S', 'Simple'),('T', 'Triple'),('C', 'Complex')]), string='Type', default="S")

class IndividualCourse(models.Model):
    '''Individual Course'''
    _inherit = 'school.individual_course'
    
    ## Type and weight for average computation (ie 0 for dispenses) ##
    
    type = fields.Selection(([('S', 'Simple'),('T', 'Triple'),('C', 'Complex'),('D','Deferred')]),compute='compute_type', string='Type', store=True, default="S")
    c_weight =  fields.Float(compute='compute_weight', readonly=True, store=True)

    ## Evaluation ##
    
    ann_result= fields.Char(string='Annual Result',track_visibility='onchange')
    jan_result= fields.Char(string='January Result',track_visibility='onchange')
    jun_result= fields.Char(string='June Result',track_visibility='onchange')
    sept_result= fields.Char(string='September Result',track_visibility='onchange')
    
    ## First Session ##
    
    first_session_result= fields.Float(compute='compute_results', string='First Session Result', store=True, group_operator='avg')
    first_session_result_bool = fields.Boolean(compute='compute_results', string='First Session Active', store=True)
    first_session_note = fields.Text(string='First Session Notes')
    
    ## Second Session ##
    
    second_session_result= fields.Float(compute='compute_results', string='Second Session Result', store=True, group_operator='avg')
    second_session_result_bool = fields.Boolean(compute='compute_results', string='Second Session Active', store=True)
    second_session_note = fields.Text(string='Second Session Notes')

    @api.model
    def create(self, values):
        if not(values.get('type', False)) and values.get('source_course_id', False):
            course = self.env['school.course'].browse(values['source_course_id'])
            values['type'] = course.type or 'S'
        result = super(IndividualCourse, self).create(values)
        return result
    
    @api.one
    @api.depends('dispense','weight','jun_result')
    def compute_weight(self):
        _logger.debug('Trigger "compute_weight" on Course %s' % self.name)
        if self.dispense and not self.jun_result:
            self.c_weight = 0
        else:
            self.c_weight = self.weight
    
    @api.one
    @api.depends('dispense', 'source_course_id.type')
    def compute_type(self):
        _logger.debug('Trigger "compute_type" on Course %s' % self.name)
        if self.dispense :
            self.type = 'D'
        else:
            self.type = self.source_course_id.type
            
    def _parse_result(self,input):
        f = float(input)
        if(f < 0 or f > 20):
            raise ValidationError("Evaluation shall be between 0 and 20")
        else:
            return f
    
    @api.depends('type','ann_result','jan_result','jun_result','sept_result')
    @api.one
    def compute_results(self):
        _logger.debug('Trigger "compute_results" on Course %s' % self.name)
        if self.type == 'D' :
            if self.jun_result :
                try:
                    f = self._parse_result(self.jun_result)
                    self.first_session_result = f
                    self.first_session_result_bool = True
                except ValueError:
                    self.first_session_result = 0
                    self.first_session_result_bool = False
                    raise UserError(_('Cannot decode %s in June Result, please encode a Float eg "12.00".' % self.jun_result))
                    
        if self.type in ['S','D','T']:
            f = False
            if self.jan_result :
                try:
                    f = self._parse_result(self.jan_result)
                except ValueError:
                    self.first_session_result = 0
                    self.first_session_result_bool = False
                    raise UserError(_('Cannot decode %s in January Result, please encode a Float eg "12.00".' % self.jan_result))
            if self.jun_result :
                try:
                    f = self._parse_result(self.jun_result)
                except ValueError:
                    self.first_session_result = 0
                    self.first_session_result_bool = False
                    raise UserError(_('Cannot decode %s in June Result, please encode a Float eg "12.00".' % self.jun_result))
            if f :
                self.first_session_result = f
                self.first_session_result_bool = True
            if self.sept_result :
                try:
                    f = self._parse_result(self.sept_result)
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
                    ann = self._parse_result(self.ann_result)
                except ValueError:
                    raise UserError(_('Cannot decode %s in January Result, please encode a Float eg "12.00".' % self.ann_result))
            if self.jan_result :
                try:
                    jan = self._parse_result(self.jan_result)
                except ValueError:
                    raise UserError(_('Cannot decode %s in January Result, please encode a Float eg "12.00".' % self.jan_result))
            if self.jun_result :
                try:
                    jun = self._parse_result(self.jun_result)
                    if self.ann_result and self.jan_result :
                        self.first_session_result = ann * 0.5 + (jan * 0.5 + jun * 0.5) * 0.5
                        self.first_session_result_bool = True
                    elif self.ann_result :
                        self.first_session_result = ann * 0.5 + jun * 0.5
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
                    sept = self._parse_result(self.sept_result)
                    if self.ann_result :
                        self.second_session_result = ann * 0.5 + sept * 0.5
                        self.second_session_result_bool = True 
                    else:
                        self.first_session_result = 0
                        self.first_session_result_bool = False
                except ValueError:
                    self.second_session_result = 0
                    self.second_session_result_bool = False
                    raise UserError(_('Cannot decode %s in September Result, please encode a Float eg "12.00".' % self.sept_result))
        # Trigger CG recompute - TODO only if value actually changed ??
        self.course_group_id.recompute_results()


class IndividualBloc(models.Model):
    '''Individual Bloc'''
    _inherit = 'school.individual_bloc'

    state = fields.Selection([
            ('draft','Draft'),
            ('progress','In Progress'),
            ('postponed', 'Postponed'),
            ('awarded_first_session', 'Awarded in First Session'),
            ('awarded_second_session', 'Awarded in Second Session'),
            ('failed', 'Failed'),
        ], string='Status', index=True, default='draft',
        copy=False,
        help=" * The 'Draft' status is used when results are not confirmed yet.\n"
             " * The 'In Progress' status is used during the courses.\n"
             " * The 'Postponed' status is used when a second session is required.\n"
             " * The 'Awarded' status is used when the bloc is awarded in either first or second session.\n"
             " * The 'Failed' status is used during the bloc is definitively considered as failed.\n"
             ,track_visibility='onchange')
    
    @api.multi
    def set_to_draft(self, context):
        # TODO use a workflow to make sure only valid changes are used.
        return self.write({'state': 'draft'})
    
    @api.multi
    def set_to_progress(self, context):
        # TODO use a workflow to make sure only valid changes are used.
        return self.write({'state': 'progress'})
    
    @api.multi
    def set_to_postponed(self, decision=None, context=None):
        # TODO use a workflow to make sure only valid changes are used.
        if isinstance(decision, dict):
            context = decision
            decision = None
        return self.write({'state': 'postponed','decision' : decision})
    
    @api.multi
    def set_to_awarded_first_session(self, decision=None, context=None):
        # TODO use a workflow to make sure only valid changes are used.
        if isinstance(decision, dict):
            context = decision
            decision = None
        return self.write({'state': 'awarded_first_session','decision' : decision})
        
    @api.multi
    def set_to_awarded_second_session(self, decision=None, context=None):
        # TODO use a workflow to make sure only valid changes are used.
        if isinstance(decision, dict):
            context = decision
            decision = None
        return self.write({'state': 'awarded_second_session','decision' : decision})
    
    @api.multi
    def set_to_failed(self, decision=None, context=None):
        # TODO use a workflow to make sure only valid changes are used.
        if isinstance(decision, dict):
            context = decision
            decision = None
        return self.write({'state': 'failed','decision' : decision})
        
    total_acquiered_credits = fields.Integer(string="Acquiered Credits",compute="compute_credits", store=True)
    
    @api.depends('course_group_ids','course_group_ids.acquiered')
    @api.one
    def compute_credits(self):
        total = 0
        for icg in self.course_group_ids:
            if icg.acquiered == 'A':
                total += icg.total_credits
        self.total_acquiered_credits = total
        
    evaluation = fields.Float(string="Evaluation",compute="compute_evaluation")
    
    @api.depends('course_group_ids','course_group_ids.acquiered','course_group_ids.final_result')
    @api.one
    def compute_evaluation(self):
        total = 0
        total_weight = 0
        for icg in self.course_group_ids:
            if icg.acquiered == 'A' and icg.total_weight > 0 : # if total_weight == 0 means full dispense
                total += icg.final_result * icg.weight
                total_weight += icg.weight
        if total_weight > 0 :
            self.evaluation = total / total_weight
        else:
            self.evaluation = None
        
    decision = fields.Text(string="Decision",track_visibility='onchange')
        
    @api.onchange('source_bloc_id')
    @api.depends('course_group_ids')
    def assign_source_bloc(self):
        super(IndividualBloc, self).assign_source_bloc()
        for group in self.course_group_ids:
            group.recompute_results()
        
class IndividualProgram(models.Model):
    '''Individual Program'''
    _inherit='school.individual_program'
    
    state = fields.Selection([
            ('draft','Draft'),
            ('progress','In Progress'),
            ('awarded', 'Awarded'),
            ('abandonned', 'Abandonned'),
        ], string='Status', index=True, default='draft',copy=False,
        help=" * The 'Draft' status is used when results are not confirmed yet.\n"
             " * The 'In Progress' status is used during the cycle.\n"
             " * The 'Awarded' status is used when the cycle is awarded.\n"
             " * The 'Abandonned' status is used if a student leave the program.\n"
             ,track_visibility='onchange')
    
    @api.multi
    def set_to_draft(self, context):
        # TODO use a workflow to make sure only valid changes are used.
        return self.write({'state': 'draft'})
    
    @api.multi
    def set_to_progress(self, context):
        # TODO use a workflow to make sure only valid changes are used.
        return self.write({'state': 'progress'})
    
    @api.multi
    def set_to_awarded(self, context, grade=None, grade_year_id=None, grade_comments=None):
        # TODO use a workflow to make sure only valid changes are used.
        if(grade):
            self.write({'state': 'awarded',
                           'grade' : grade,
                           'grade_year_id' : grade_year_id,
                           'grade_comments' : grade_comments,})
        else:
            self.write({'state': 'awarded'})
        
    @api.multi
    def set_to_abandonned(self, context):
        # TODO use a workflow to make sure only valid changes are used.
        return self.write({'state': 'abandonned'})
    
    historical_bloc_1_eval = fields.Float(string="Hist Bloc 1 Eval")
    historical_bloc_1_credits = fields.Integer(string="Hist Bloc 1 ECTS")
    
    historical_bloc_2_eval = fields.Float(string="Hist Bloc 2 Eval")
    historical_bloc_2_credits = fields.Integer(string="Hist Bloc 2 ECTS")
    
    grade = fields.Selection([
            ('without','Without Grade'),
            ('satisfaction','Satisfaction'),
            ('distinction','Distinction'),
            ('second_class', 'Second Class Honor'),
            ('first_class', 'First Class Honor'),
        ],string="Grade")
    
    grade_year_id = fields.Many2one('school.year', string="Year")
    
    grade_comments = fields.Text(string="Grade Comments")
    
    evaluation = fields.Float(string="Evaluation",compute="compute_evaluation")
    
    @api.depends('bloc_ids','bloc_ids.evaluation','historical_bloc_1_eval','historical_bloc_2_eval')
    @api.one
    def compute_evaluation(self):
        total = 0
        count = 0
        for bloc in self.bloc_ids:
            total += bloc.evaluation
            count += 1
        if self.historical_bloc_1_eval > 0:
            total += self.historical_bloc_1_eval
            count += 1
        if self.historical_bloc_2_eval > 0:
            total += self.historical_bloc_2_eval
            count += 1
        self.evaluation = total/count
        # TODO : Implement computation based on UE as per the decret
        
    @api.depends('bloc_ids','bloc_ids.evaluation','historical_bloc_1_eval','historical_bloc_2_eval')
    @api.multi
    def compute_evaluation_details(self):
        self.ensure_one();
        ret = [0,0,0,0,0]
        if self.historical_bloc_1_eval > 0:
            ret[0] = self.historical_bloc_1_eval
        if self.historical_bloc_2_eval > 0:
            ret[1] = self.historical_bloc_2_eval
        for bloc in self.bloc_ids:
            ret[int(bloc.source_bloc_level)-1] = bloc.evaluation
        return {
            'bloc_evaluations' : ret
        }
        # TODO : Implement computation based on UE as per the decret