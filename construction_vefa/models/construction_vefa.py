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

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class BuildingAsset(models.Model):
    '''Building Asset'''
    _inherit = 'construction.building_asset'
    
    is_vefa =fields.Boolean(string="Is VEFA", default=False)
    
    vefa_bank_account_id = fields.Many2one('res.partner.bank', string="VEFA Bank Account", ondelete='restrict', copy=False)
    vefa_bank_acc_number = fields.Char(related='vefa_bank_account_id.acc_number')
    vefa_bank_id = fields.Many2one('res.bank', related='vefa_bank_account_id.bank_id')

class SaleOrder(models.Model):
    '''Sale Order'''
    _inherit = "sale.order"
    
    is_vefa = fields.Boolean(string="Is VEFA")
    is_asset_vefa = fields.Boolean(related="building_asset_id.is_vefa")
    
    @api.onchange('building_asset_id')
    def update_building_asset_id(self):
        self.is_vefa = self.building_asset_id.is_vefa
    
    @api.multi
    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals['is_vefa'] = self.is_vefa
        return invoice_vals

class Invoice(models.Model):
    '''Invoice'''
    _inherit = 'account.invoice'
    
    is_vefa =fields.Boolean(string="Is VEFA")
    is_asset_vefa = fields.Boolean(related="building_asset_id.is_vefa")