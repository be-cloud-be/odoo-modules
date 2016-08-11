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

from openerp import api, fields, models, tools, _
from openerp.exceptions import UserError

_logger = logging.getLogger(__name__)

class IndividualBloc(models.Model):
    '''Individual Bloc'''
    _inherit = 'school.individual_bloc'
    
    @api.onchange('course_group_ids')
    def on_change_course_group_ids(self):
        self.ensure_one()
        res = {}
        current_scg_ids = self.course_group_ids.mapped('source_course_group_id')
        for cg in self.course_group_ids:
            scg = cg.source_course_group_id
            # Check pre-requisits
            for prereq in scg.pre_requisit_course_ids:
                icg_acq = self.env['school.individual_course_group'].search([('student_id','=',self.student_id.id),('source_course_group_id','=',prereq.id),('acquiered','=',True)])
                if len(icg_acq) == 0 :
                    res = {'warning': {
                        'title': _('Warning'),
                        'message': _("PreRequisit for course group %s is not matched" % prereq.name)
                    }}
            # Check co-requisits
            for coreq in scg.co_requisit_course_ids:
                if not coreq.id in current_scg_ids.ids :
                    res = {'warning': {
                        'title': _('Warning'),
                        'message': _("CoRequisit for course group %s is not matched" % coreq.name)
                    }}
        if res:
            return res