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
from openerp import api, fields, models, _
from openerp.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _compute_count_attachments(self):
        attachment_data = self.env['ir.attachment'].read_group([('res_model', '=', 'account.invoice'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for invoice in self:
            invoice.attachment_count = attachment.get(invoice.id, 0)

    attachment_count = fields.Integer(string="Attachment Count" ,compute="_compute_count_attachments")
    
    @api.one
    @api.depends('payment_move_line_ids.amount_residual')
    def _compute_last_payment_date(self):
        self.last_payment_date = None
        if self.payment_move_line_ids:
            for payment in self.payment_move_line_ids:
                if payment.date > self.last_payment_date:
                    self.last_payment_date = payment.date
    # TODO : use analytic query ??
                
    last_payment_date = fields.Date(string="Last Payment Date" ,compute="_compute_last_payment_date")