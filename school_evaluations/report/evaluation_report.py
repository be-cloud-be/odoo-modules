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
import time

from openerp import api, fields, models, tools, _
from openerp.exceptions import MissingError
from openerp.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

class ReportEvaluationByTeacherWizard(models.TransientModel):
    _name = "school_evaluations.report_evaluation_by_teacher"
    _description = "Evaluations by Teacher Report"

    year_id = fields.Many2one('school.year', string='Year', default=lambda self: safe_eval(self.env['ir.config_parameter'].get_param('school.current_year_id','1')))
    teacher_id = fields.Many2one('res.partner', string='Teacher')
    display_results = fields.Boolean(string='Display Current Results')
    message = fields.Text(string="Message")
    
    @api.multi
    def print_report(self, data):
        self.ensure_one()
        data['year_id'] = self.year_id.id
        data['message'] = self.message
        data['display_results'] = self.display_results
        if self.teacher_id:
            data['teacher_ids'] = [self.teacher_id.id] 
        else:
            context = dict(self._context or {})
            data['teacher_ids'] = data.get('active_ids')
        return self.env['report'].get_action(self, 'school_evaluations.report_evaluation_by_teacher_content', data=data)
    

class ReportEvaluationByTeacher(models.AbstractModel):
    _name = 'report.school_evaluations.report_evaluation_by_teacher_content'
    
    @api.multi
    def render_html(self, data):
        res_data = []
        current_year_id = safe_eval(self.env['ir.config_parameter'].get_param('school.current_year_id','1'))
        if data['teacher_ids']:
            teacher_ids = self.env['res.partner'].browse(data['teacher_ids'])
        else:
            teacher_ids = self.env['school.individual_course_proxy'].search([['year_id', '=', data['year_id'] or current_year_id]]).mapped('teacher_id').sorted(key=lambda r: r.name)
        ids = []
        for teacher_id in teacher_ids:
            source_course_ids = self.env['school.individual_course_proxy'].search([['year_id', '=', data['year_id'] or current_year_id], ['teacher_id', '=', teacher_id.id]]).mapped('source_course_id').sorted(key=lambda r: r.name)
            courses = []
            for source_course_id in source_course_ids:
                individual_courses_ids = self.env['school.individual_course'].search([['year_id', '=', data['year_id'] or current_year_id], ['teacher_id', '=', teacher_id.id], ['source_course_id', '=', source_course_id.id]]).sorted(key=lambda r: r.student_id.name)
                courses.append({
                    'course':source_course_id,
                    'individual_courses':individual_courses_ids,
                })
            res_data.append({
                'teacher_id':teacher_id,
                'courses':courses,
                })
            ids.append(teacher_id.id)
        docargs = {
            'doc_ids': ids,
            'doc_model': self.env['res.partner'],
            'data': res_data,
            'time': time,
            'message': data['message'],
            'display_results':data['display_results'],
        }
        return self.env['report'].render('school_evaluations.report_evaluation_by_teacher_content', docargs)