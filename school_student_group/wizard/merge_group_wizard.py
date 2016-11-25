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

class MergeGroupWizard(models.TransientModel):
    _name = "school.student_group.merge.wizard"
    _description = "Merge Group Wizard"
    
    dst_group_id = fields.Many2one('school.student_group', string="Destination Group", required=True, ondelete='cascade')
    group_ids = fields.Many2many('school.student_group', 'merge_wizard_group_rel', 'merge_wizard_id', 'group_id', string='Groups', required=True, ondelete='cascade')
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(MergeGroupWizard, self).default_get(cr, uid, fields, context)
        if context.get('active_model') == 'school.student_group' and context.get('active_ids'):
            group_ids = context['active_ids']
            res['dst_group_id'] = group_ids[0]
            res['group_ids'] = group_ids
        return res
    
    @api.one
    def merge_groups(self):
        if self.dst_group_id.type == 'L':
            all_courses = self.dst_group_id.course_ids
            all_groups = []
            for group_id in self.group_ids:
                if group_id != self.dst_group_id:
                    if group_id.type == 'L':
                        all_courses |= group_id.course_ids
                        all_groups.append(group_id)
                    else:
                        raise UserError(_('Only LinkedCourse groups are mergeable for now.'))
            self.dst_group_id.course_ids = all_courses
            self.dst_group_id.update_linked_students()
            for group_id in all_groups:
                group_id.unlink()
        else:
            raise UserError(_('Only LinkedCourse groups are mergeable for now.'))