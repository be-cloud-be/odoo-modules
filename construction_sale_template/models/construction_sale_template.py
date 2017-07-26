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

class SaleOrderTemplate(models.Model):
    '''Sale Order Template'''
    _name = 'construction.sale_order_template'
    _description = 'Sale Order Template'
    
    name = fields.Char(string="Name")
    active = fields.Boolean(string="Active", default=True)
    
    company_id = fields.Many2one('res.company', string='Company', change_default=True,
        required=True, readonly=True,
        default=lambda self: self.env['res.company']._company_default_get('account.invoice'))
    
    sale_order_template_line_ids = fields.One2many('construction.sale_order_template.line','sale_order_template_id',string="Sale Order Template Lines")
    
    @api.multi
    def write(self, vals):
        res = super(SaleOrderTemplate, self).write(vals)
        for order in self:
            total = sum(order.sale_order_template_line_ids.mapped('percentage'))
            if total != 100 and total != 0 :
                raise ValidationError(_('Percentages of the lines must sum up to 100 (or 0).'))
        return res
    
class SaleOrderTemplateLine(models.Model):
    '''Sale Order Template Line'''
    _name = 'construction.sale_order_template.line'
    _description = 'Sale Order Template Line'
    
    _order = 'sale_order_template_id, layout_category_id, sequence, id'
    
    sale_order_template_id = fields.Many2one('construction.sale_order_template')
    name = fields.Text(string='Description', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    
    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)], change_default=True, ondelete='restrict', required=True)
    price_unit = fields.Float('Unit Price', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    
    product_uom_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True, default=1.0)
    product_uom = fields.Many2one('product.uom', string='Unit of Measure', required=True)
    
    layout_category_id = fields.Many2one('sale.layout_category', string='Section')
    layout_category_sequence = fields.Integer(related='layout_category_id.sequence', string='Layout Sequence', store=True)
    
    company_id = fields.Many2one(related='sale_order_template_id.company_id', string='Company', store=True, readonly=True)
    
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')
    
    tax_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    
    percentage = fields.Float(string="Percentage", help="Split of the total deduced of the line with a price, total should be 100%.")
    
    @api.constrains('percentage')
    def _check_dates(self):
        if self.filtered(lambda c: c.percentage < 0 or c.percentage > 100):
            raise ValidationError(_('Percentage must be between 0 and 100 and sum to 100.'))
    
    @api.multi
    @api.onchange('percentage')
    def _percentage_change(self):
        self.price_unit = 0
        
    @api.multi
    @api.onchange('price_unit')
    def _price_unit_change(self):
        self.percentage = 0
        
    @api.multi
    @api.onchange('product_id')
    def _product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}

        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = 1.0

        product = self.product_id.with_context(
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            uom=self.product_uom.id
        )

        name = product.name_get()[0][1]
        if product.description_sale:
            name += '\n' + product.description_sale
        vals['name'] = name
        
        self.update(vals)

        self._compute_tax_id()

        return {'domain': domain}
        
    @api.multi
    def _compute_tax_id(self):
        for line in self:
            line.tax_id = line.product_id.taxes_id.filtered(lambda r: not line.company_id or r.company_id == line.company_id)