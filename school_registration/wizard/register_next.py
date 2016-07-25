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
from openerp.exceptions import MissingError
from openerp.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

class RegisterNext(models.TransientModel):
    _name = "school.register_next_wizard"
    _description = "Register Next Wizard"
    
    state = fields.Selection([('awarded', 'awarded'),('failed', 'failed'),('rework', 'rework'),('anticipate', 'anticipate'),('confirm','confirm')]) 
    
    init_bloc_id = fields.Many2one('school.individual_bloc', string="Initial Bloc", required=True, readonly=True)
    
    yeard_id = fields.Many2one('school.year', related="init_bloc_id.year_id", readonly=True)
    student_id = fields.Many2one('res.partner', related="init_bloc_id.student_id", readonly=True)
    init_source_bloc_name = fields.Char(string="Initial Source Bloc", readonly=True, related="init_bloc_id.source_bloc_name")
    
    new_bloc_id = fields.Many2one('school.individual_bloc', string="New Bloc", readonly=True)
    new_bloc_name = fields.Char(string="New Source Bloc", readonly=True, related="new_bloc_id.source_bloc_name")
    
    course_group_ids = fields.One2many('school.individual_course_group', related='new_bloc_id.course_group_ids', string='Courses Groups')
    
    rework_course_group_ids = fields.Many2many('school.course_group', 'rework_course_group_wizard_rel', 'course_group_id', 'wizard_id', string='Rework Course')
    
    anticipated_course_group_ids = fields.Many2many('school.course_group', 'anticipated_course_group_wizard_rel', 'course_group_id', 'wizard_id', string='Anticipated Course')
    
    total_credits = fields.Integer(compute='_get_courses_total', string='Credits')
    total_hours = fields.Integer(compute='_get_courses_total', string='Hours')
    
    @api.one
    @api.depends('course_group_ids')
    def _get_courses_total(self):
        total_hours = 0.0
        total_credits = 0.0
        for course_group in self.course_group_ids:
            total_hours += course_group.total_hours
            total_credits += course_group.total_credits
        for course_group in self.rework_course_group_ids:
            total_hours += course_group.total_hours
            total_credits += course_group.total_credits
        for course_group in self.anticipated_course_group_ids:
            total_hours += course_group.total_hours
            total_credits += course_group.total_credits
        self.total_hours = total_hours
        self.total_credits = total_credits

    @api.model
    def default_get(self, fields):
        res = super(RegisterNext, self).default_get(fields)
        init_bloc_id = self.env['school.individual_bloc'].browse(res.get('init_bloc_id'))
        if init_bloc_id.state == 'failed':
            res['state'] = 'failed'
            new_bloc_source_id = self.env['school.bloc'].search([('program_id', '=', self.init_bloc_id.source_bloc_id.program_id.id),('level','=',int(self.init_bloc_id.source_bloc_id.level)+1)])
        else:
            res['state'] = 'awarded'
            new_bloc_source_id = self.env['school.bloc'].search([('program_id', '=', self.init_bloc_id.source_bloc_id.program_id.id),('level','=',int(self.init_bloc_id.source_bloc_id.level)+1)])
        new_bloc_source_id = self.env['school.bloc'].search([('program_id', '=', init_bloc_id.source_bloc_id.program_id.id),('level','=',int(init_bloc_id.source_bloc_id.level)+1)])
        if new_bloc_source_id:
            program = self.env['school.individual_bloc'].create({'year_id':init_bloc_id.year_id.next.id,'student_id': init_bloc_id.student_id.id,'source_bloc_id':new_bloc_source_id[0].id,'program_id':init_bloc_id.program_id.id})
            program.assign_source_bloc()
            res['new_bloc_id'] = program.id
        return res

    @api.onchange('state')
    @api.one
    def onchange_state(self):
        # Rework look into previous bloc for not acquiered CG
        if self.state == 'rework':
            for group in self.init_bloc_id.course_group_ids:
                if not group.acquiered:
                    self.rework_course_group_ids.push(group.clone())
            return
        # Confirm merge all into the new bloc for review
        if self.state == 'confirm':
            self.new_bloc_id.course_group_ids.append(self.rework_course_group_ids)
            self.new_bloc_id.course_group_ids.append(self.anticipated_course_group_ids)
            
    @api.one
    def oncancel(self):
        self.new_bloc_id.unlink()
        return {'type': 'ir.actions.act_window_close'}
    
            
class RegisterNextLine(models.TransientModel):   
    _name = 'school.individual_course_group_proxy'
    
    wizard_id = fields.Many2one('school.register_next_wizard')
    
    name = fields.Char('Name')
    total_credits = fields.Integer('Total Credits')
    total_hours = fields.Integer('Total Hours')
    final_result = fields.Float(string='Final Result', digits=(5, 2))
    acquiered = fields.Selection(([('A', 'Acquiered'),('NA', 'Not Acquiered')]), string='Acquired Credits')