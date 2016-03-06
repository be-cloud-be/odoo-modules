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
from openerp.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

class Partner(models.Model):
    '''Partner'''
    _inherit = 'res.partner'
    
    grade_id = fields.Many2one("life.grade",string="Grade")
    pay_grid_id = fields.Many2one("life.pay_grid",string="Pay Grid")
    
    career_history_ids = fields.One2many('life.career_history', 'partner_id', string="Career History")
    
class CareerHistory(models.Model):
    '''Career History'''
    _name = 'life.career_history'
    _description = 'Career History'
    
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    grade_id = fields.Many2one("life.grade",string="Grade")
    pay_grid_id = fields.Many2one("life.pay_grid",string="Pay Grid")
    function = fields.Char(string="Job Position")
    
    partner_id = fields.Many2one('res.partner', required=True, string='Partner')
    
class Grade(models.Model):
    '''Grade'''
    _name = 'life.grade'
    _description = 'Grade'
    
    name = fields.Char(string="Name")
    
class PayGrid(models.Model):
    '''Pay Grid'''
    _name = 'life.pay_grid'
    _description = 'Pay Grid'
    
    name = fields.Char(string="Name")