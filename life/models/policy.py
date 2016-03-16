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

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil.relativedelta import relativedelta
from datetime import datetime,date

_logger = logging.getLogger(__name__)

class Policy(models.Model):
    '''Policy'''
    _name = 'life.policy'
    _description = 'Policy'

    number = fields.Integer(string="Policy Number")
    policy_holder_id = fields.Many2one('res.partner',string='Policy Holder')
    name = fields.Char(string="Name",compute='_compute_name')

    life_type = fields.Selection([('pure', 'Pure endowment')],string = "Life Type")
    life_number = fields.Integer(string="Life Policy Number", related="number")
    death_type = fields.Selection([('oneterm', 'One-year term insurance')],string = "Death Type")
    death_number = fields.Integer(string="Death Policy Number")

    term_year = fields.Integer(string="Term Year",compute="compTermYear")

    @api.one
    @api.depends('policy_holder_id','number')
    def _compute_name(self):
        self.name = "%s - %s" % (self.policy_holder_id.name,self.number)
        
    @api.one
    @api.depends('policy_holder_id.retirement_date')
    def compTermYear(self):
        self.term_year = datetime.strptime(self.policy_holder_id.retirement_date, DEFAULT_SERVER_DATE_FORMAT).year()