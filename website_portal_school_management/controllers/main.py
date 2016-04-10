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

from openerp import http
from openerp.http import request
from openerp import tools
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class website_portal_school_management(http.Controller):
    @http.route(['/my/info'], type='http', auth='user', website=True)
    def details(self, redirect=None, **post):
        user = request.env['res.users'].browse(request.uid)
        year = request.env['school.year'].browse(1) #TODO set this as global parameter
        _logger.info('HERHEEHREHREH')
        _logger.info(year)
        _logger.info(user)
        bloc = request.env['school.individual_bloc'].search([('year_id','=',year.id),('student_id','=',user.partner_id.id)])
        _logger.info(bloc)
        values = {
            'user': user,
            'yead': year,
            'bloc': bloc,
        }
        return request.website.render("website_portal_school_management.information", values)
        
    @http.route(['/program'], type='http', auth='public', website=True)
    def program(self, redirect=None, **post):
        programs = request.env['school.program'].sudo().search([('state', '=', 'published')],order="domain_id, name ASC")
        values = {
            'programs': programs,
        }
        return request.website.render("website_portal_school_management.program", values)
        
    @http.route(['/program/<model("school.program"):program>'], type='http', auth='public', website=True)
    def program_details(self, program, redirect=None, **post):
        values = {
            'program': program,
        }
        return request.website.render("website_portal_school_management.program_details", values)