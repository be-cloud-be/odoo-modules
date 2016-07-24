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
    
    init_bloc_id = fields.Many2one('school.individual_bloc', string="Initial Bloc", required=True, readonly=True)
    
    student_name = fields.Char('Student', related="init_bloc_id.student_name", readonly=True)
    
    init_source_bloc_name = fields.Char(string="Initial Source Bloc", readonly=True, related="init_bloc_id.source_bloc_name")
    
    new_bloc_id = fields.Many2one('school.individual_bloc', string="New Bloc")
    
    new_bloc_name = fields.Char(string="New Source Bloc", readonly=True, related="new_bloc_id.source_bloc_name")
    
    course_group_ids = fields.One2many('school.individual_course_group', related='new_bloc_id.course_group_ids', string='Courses Groups')
    
    anticipated_course_group_ids = fields.Many2many('school.course_group', 'anticipated_course_group_wizard_rel', 'course_group_id', 'wizard_id', string='Anticipated Course')
    
    @api.model
    def default_get(self, fields):
        import wdb
        wdb.set_trace()
        res = super(RegisterNext, self).default_get(fields)
        init_bloc_id = self.env['school.individual_bloc'].browse(res.get('init_bloc_id'))
        ## We go the real logic to create the new program
        new_bloc_source_id = self.env['school.bloc'].search([('program_id', '=', init_bloc_id.source_bloc_id.program_id.id),('level','=',int(init_bloc_id.source_bloc_id.level)+1)])
        if new_bloc_source_id:
            program = self.env['school.individual_bloc'].create({'year_id':init_bloc_id.year_id.next.id,'student_id': init_bloc_id.student_id.id,'bloc_source_id':new_bloc_source_id[0].id,'program_id':init_bloc_id.program_id.id})
            res['new_bloc_id'] = program.id
        return res

class RegisterNextLine(models.TransientModel):   
    _name = 'school.individual_course_group_proxy'
    
    wizard_id = fields.Many2one('school.register_next_wizard')
    
    name = fields.Char('Name')
    total_credits = fields.Integer('Total Credits')
    total_hours = fields.Integer('Total Hours')
    final_result = fields.Float(string='Final Result', digits=(5, 2))
    acquiered = fields.Selection(([('A', 'Acquiered'),('NA', 'Not Acquiered')]), string='Acquired Credits')