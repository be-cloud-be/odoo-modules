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

class IndividualBloc(models.Model):
    '''Individual Bloc'''
    _inherit = 'school.individual_bloc'
    
    @api.multi
    def set_to_progress(self, context):
        for bloc in self:
            for icg in bloc.course_group_ids:
                if icg.dispense and not icg.is_dispense_approved:
                    raise UserError(_('Cannot set program on progress, %s dispense in %s is not approved.' % (icg.name, bloc.name)))
        return super(IndividualBloc, self).set_to_progress(context)

class IndividualCourseGroup(models.Model):
    '''Individual Course Group'''
    _inherit = ['school.individual_course_group']

    is_dispense_approved = fields.Boolean(string="Is Dispense Approved", default=False, track_visibility='onchange')
    dispense_approval_comment = fields.Text(string="Dispense Approval Comment")
    
    @api.model
    def _needaction_domain_get(self):
        return [('dispense', '=', True),('is_dispense_approved', '=', False)]