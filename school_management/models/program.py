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
    
    student_id = fields.Many2one('res.partner', string='Student', domain="[('student', '=', '1')]")
    bloc_ids = fields.One2many('school.individual_bloc', 'individual_program_id', string="Individual Blocs")
    
class IndividualBloc(models.Model):
    '''Individual Bloc'''
    _name='school_individual_bloc'
    _description='Individual Bloc'
    
    individual_program_id = fields.Many2one('school.individual_program', string='Individual Program')
    course_group_ids = fields.One2many('school.individual_course_group', string="Individual Course Groups")
    
    