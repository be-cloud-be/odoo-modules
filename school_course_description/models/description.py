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

class CourseDocumentation(models.Model):
    '''CourseDocumentation'''
    _name = 'school.course_documentation'
    _description = 'Documentation about a course'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    
    state = fields.Selection([
            ('draft','Draft'),
            ('published', 'Published'),
            ('archived', 'Archived'),
        ], string='Status', index=True, readonly=True, default='draft',
        #track_visibility='onchange', TODO : is this useful for this case ?
        copy=False,
        help=" * The 'Draft' status is used when a new program is created and not published yet.\n"
             " * The 'Published' status is when a program is published and available for use.\n"
             " * The 'Archived' status is used when a program is obsolete and not publihed anymore.")
    
    course_id = fields.Many2one('school.course', string='Course')
    
    name = fields.Char(related='course_id.name')
    
    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'draft')]
    
    @api.one
    @api.constrains('state', 'course_id')
    def _check_uniqueness(self):
        num_active = self.env['school.course_documentation'].search_count([['course_id', '=', self.course_id.id],['state','=','published']])
        if num_active > 1:
            raise ValidationError("Only on documentation shall be published at a given time")
    
    @api.multi
    def unpublish(self):
        return self.write({'state': 'draft'})
    
    @api.multi
    def publish(self):
        current = self.env['school.course_documentation'].search([['course_id', '=', self.course_id.id],['state','=','published']])
        if current:
            current[0].write({'state': 'archived'})
        return self.write({'state': 'published'})
    
    @api.multi
    def archive(self):
        return self.write({'state': 'archived'})

    content = fields.Text(string="Content")
    method = fields.Text(string="Method")
    learning_outcomes = fields.Text(string="Learning outcomes")
    competencies = fields.Text(string="Competencies")
    evaluation_method = fields.Text(string="Evaluation method")
    staff_ids = fields.One2many("school.course_staff", 'doc_id', string='Staff', copy=True)
    language = fields.Text(string="Language")
    schedule = fields.Text(string="Schedule")
    rooms = fields.Text(string="Rooms")
    
class CourseStaff(models.Model):
    '''CourseStaff'''
    _name = 'school.course_staff'
    _description = 'Staff of a course'
    doc_id = fields.Many2one('school.course_documentation', string='Documentation')
    teacher_id = fields.Many2one('res.partner', string='Teacher', domain=[('teacher', '=', True)])
    role = fields.Char(string="Role")
    
class Course(models.Model):
    '''Course'''
    _inherit = 'school.course'
    
    documentation_id = fields.Many2one('school.course_documentation', string='Documentation', compute='compute_documentation_id')
    
    @api.one
    def compute_documentation_id(self):
        doc_ids = self.env['school.course_documentation'].search([['course_id', '=', self.id],['state','=','published']])
        if doc_ids :
            self.documentation_id = doc_ids[0]