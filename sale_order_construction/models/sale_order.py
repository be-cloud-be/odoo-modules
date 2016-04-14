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

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    '''Sale Order'''
    _inherit = 'sale.order'
    
    chantier_id = fields.Many2one('sale_order_construction.chantier', string='Chantier', ondelete='set null')
    
    @api.multi
    def _prepare_invoice(self):
        """
        Add chantier adress to invoice
        """
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals['chantier_id'] = self.chantier_id
        return invoice_vals
    
class Invoice(models.Model):
    '''Invoice'''
    _inherit = 'account.invoice'
    
    chantier_id = fields.Many2one('sale_order_construction.chantier', string='Chantier', ondelete='set null')
    
class Chantier(models.Model):
    '''Chantier'''
    _name = 'sale_order_construction.chantier'
    _description = 'Chantier'
    
    name = fields.Char(string='Nom du projet')
    address_id = fields.Many2one('res.partner', string='Addresse du chantier', domain="[('type', '=', 'delivery')]")
    notes = fields.Text(string='Notes')