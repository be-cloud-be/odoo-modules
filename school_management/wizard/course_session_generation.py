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

_logger = logging.getLogger(__name__)

class CourseSessionGeneration(models.TransientModel):
    _name = "school.course_session.generate"
    _description = "Course Session Generation"
    
    year_id = fields.Many2one('school.year', string="Year")

    @api.one
    @api.depends('year_id')
    def generate_assigments(self):
        self.env.cr.execute("SELECT school_bloc.id, school_course.id from school_program, school_bloc, school_course_group, school_course WHERE school_program.year_id = %s AND school_program.id = school_bloc.program_id AND school_bloc.id = school_course_group.bloc_id AND school_course_group.id =  school_course.course_group_id" % (self.year_id.id))
        
        res = self.env.cr.fetchall()
        for (bloc_id,course_id) in res:
            try:
                _logger.info('Create course session %s - %s',bloc_id,course_id)
                self.env['school.course_session'].create({'bloc_id':bloc_id, "course_id":course_id})
            except Exception as e:
                _logger.info(_('Error during creation of course session %s' % e))
                pass
                #TODO : detect missing course_session and insert them
            