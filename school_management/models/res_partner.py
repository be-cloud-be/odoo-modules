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
import threading

import openerp
from openerp import tools, api, fields, models, _
from openerp.exceptions import UserError
from openerp.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

class Partner(models.Model):
    '''Partner'''
    _inherit = 'res.partner'
    
    student = fields.Boolean("Student",default=False)
    teacher = fields.Boolean("Teacher",default=False)
    employee = fields.Boolean("Employee",default=False)
    
    initials = fields.Char('Initials')
    sex = fields.Selection([('m', 'Male'),('f', 'Female')])
    birthdate = fields.Date(string="Birthdate")
    birthplace = fields.Char('Birthplace')
    phone2 = fields.Char('Phone2')
    title = fields.Selection([('Mr', 'Monsieur'),('Mme', 'Madame'),('Mlle', 'Mademoiselle')])
    marial_status = fields.Selection([('M', 'Maried'),('S', 'Single')])
    registration_date = fields.Date('Registration Date')
    email_personnel = fields.Char('Email personnel')
    
    minerval_ids = fields.One2many('school.minerval', 'student_id', string='Minerval')
    has_paid_current_minerval = fields.Boolean(compute='_has_paid_current_minerval',string="Has paid current minerval", store=True)
    student_current_program_id = fields.Many2one('school.individual_bloc', compute='_get_student_current_program_id', string='Program', store=True)
    student_current_program_name = fields.Char(related='student_current_program_id.source_bloc_name', string='Current Program', store=True)
    
    student_program_ids = fields.One2many('school.individual_bloc', 'student_id', string="Programs")
    
    teacher_current_course_ids = fields.One2many('school.individual_course_proxy', compute='_get_teacher_current_individual_course_ids', string="Current Courses")
    
    @api.one
    def _get_teacher_current_individual_course_ids(self):
        self.teacher_current_course_ids = self.env['school.individual_course_proxy'].search([['year_id', '=', self.env.user.current_year_id.id], ['teacher_id', '=', self.id]])

    @api.one
    @api.depends('minerval_ids')
    def _has_paid_current_minerval(self):
        res = self.env['school.minerval'].search([['year_id', '=', self.env.user.current_year_id.id], ['student_id', '=', self.id]])
        self.has_paid_current_minerval = len(res) > 0
        
    @api.one
    @api.depends('has_paid_current_minerval')
    def pay_current_minerval(self):
        if not self.has_paid_current_minerval:
            self.env['school.minerval'].create({'student_id': self.id,'year_id': self.env.user.current_year_id.id})
        
    @api.one
    @api.depends('student_program_ids')
    def _get_student_current_program_id(self):
        for program in self.student_program_ids:
            if program.year_id == self.env.user.current_year_id:
                self.student_current_program_id = program
    
    @api.one
    def _get_teacher_current_course_session_ids(self):
        res = self.env['school.course_session'].search([['year_id', '=', self.env.user.current_year_id.id], ['teacher_id', '=', self.id]])
        self.teacher_current_assigment_ids = res
    
    # TODO : This is not working but don't know why
    @api.model
    def _get_default_image(self, is_company, colorize=False):
        _logger.info("YES WE ARE HERE")
        if getattr(threading.currentThread(), 'testing', False) or self.env.context.get('install_mode'):
            return False

        if self.env.context.get('partner_type') == 'invoice':
            img_path = openerp.modules.get_module_resource('school_management', 'static/src/img', 'home-icon.png')
            with open(img_path, 'rb') as f:
                image = f.read()
            return tools.image_resize_image_big(image.encode('base64'))
        else:
            return super(Partner, self)._get_default_image(is_company, colorize)
        
class Minerval(models.Model):
    '''Minerval'''
    _name = 'school.minerval'
    
    year_id = fields.Many2one('school.year', string='Year', readonly=True)
    student_id = fields.Many2one('res.partner', string='Student', domain="[('student', '=', '1')]", readonly=True)
    payment_date = fields.Date(string='Payment Date',default=fields.Date.context_today)