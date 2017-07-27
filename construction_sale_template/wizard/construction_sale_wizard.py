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
from odoo.exceptions import UserError, ValidationError

import odoo.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)

class ConstructionSaleWizard(models.TransientModel):
    _name = "construction.sale_wizard"
    
    building_asset_id = fields.Many2one('construction.building_asset', string='Building Asset')
    partner_id = fields.Many2one('res.partner', string='Customer', related="building_asset_id.partner_id")
    
    date = fields.Date(string='Date', required=True, default=lambda self:fields.Date.from_string(fields.Date.today()))
    template_id = fields.Many2one('construction.sale_order_template', string="Template", required=True)
    total_untaxed = fields.Integer(string="Total Untaxed", required=True)
    
    @api.multi
    def action_confirm(self):
        self.ensure_one()
        lines = []  
        total = self.total_untaxed
        for line in self.template_id.sale_order_template_line_ids.filtered(lambda l: l.price_unit > 0) :
            lines.append(
                (0,0,{
                    'name': line.name, 
                    'product_id': line.product_id.id, 
                    'product_uom_qty': line.product_uom_qty, 
                    'product_uom': line.product_uom.id, 
                    'price_unit': line.price_unit,
                    'tax_id' : [(6, 0, [line.tax_id.ids])],
                }))
            total = total - line.product_uom_qty * line.price_unit
        for line in self.template_id.sale_order_template_line_ids.filtered(lambda l: l.percentage > 0) :
            lines.append(
                (0,0,{
                    'name': line.name, 
                    'product_id': line.product_id.id, 
                    'product_uom_qty': 1, 
                    'product_uom': line.product_uom.id, 
                    'price_unit': line.percentage * total / 100,
                    'tax_id' : [(6, 0, [line.tax_id.ids])],
                }))

        vals = {
            'partner_id' : self.partner_id.id,
            'building_asset_id' : self.building_asset_id.id,
            'date_order' : self.date,
            'order_line' : lines
        } 
            
        so = self.env['sale.order'].create(vals)
        
        return {
            'name': _('Sale Order'),
            'domain': [],
            'context': dict(self._context, active_ids=[so.id]),
            'res_id': so.id,
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
        }