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

    is_choice_course_group = fields.Boolean(string="Is Choice Course Group", default=False)
    
    total_credits_to_select = fields.Integer(string='Total Credits to Select')
    total_hours_to_select = fields.Integer(string='Total Hours to Select')
    total_weight_to_select = fields.Integer(string='Total Weight to Select')

    @api.depends('title','level','speciality_id.name', 'is_choice_course_group')
    @api.multi
    def compute_name(self):
        for course_g in self:
            if course_g.is_choice_course_group :
                if course_g.level:
                    course_g.name = _("%s (Choice) - %s - %s") % (course_g.title, course_g.speciality_id.name, course_g.level)
                else:
                    course_g.name = _("%s (Choice) - %s") % (course_g.title, course_g.speciality_id.name)
            else :
                if course_g.level:
                    course_g.name = "%s - %s - %s" % (course_g.title, course_g.speciality_id.name, course_g.level)
                else:
                    course_g.name = "%s - %s" % (course_g.title, course_g.speciality_id.name)
            
    @api.one
    @api.depends('course_ids','is_choice_course_group','total_credits_to_select','total_hours_to_select','total_weight_to_select')
    def _get_courses_total(self):
        if self.is_choice_course_group:
            self.total_hours = self.total_hours_to_select
            self.total_credits = self.total_credits_to_select
            self.total_weight = self.total_weight_to_select
        else:
            super(CourseGroup, self)._get_courses_total()
            
class IndividualBloc(models.Model):
    '''Individual Bloc'''
    _inherit = 'school.individual_bloc'

    @api.multi
    def set_to_progress(self, context):
        import wdb
        wdb.set_trace()
        for bloc in self:
            for icg in bloc.course_group_ids:
                if icg.source_course_group_id.is_choice_course_group:
                    if icg.source_course_group_id.total_credits_to_select != icg.total_credits:    
                        raise UserError(_('Cannot set program on progress, choice for %s are not set in %s.' % (icg.name, bloc.name)))
                    if icg.source_course_group_id.total_hours_to_select != icg.total_hours:    
                        raise UserError(_('Cannot set program on progress, choice for %s are not set in %s.' % (icg.name, bloc.name)))
        return super(IndividualBloc, self).set_to_progress(context)