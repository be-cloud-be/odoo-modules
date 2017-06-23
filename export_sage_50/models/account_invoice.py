# -*- encoding: utf-8 -*-
# Subject to license. See LICENSE file for full copyright and licensing details.

from openerp import api, fields, models, tools, _
from openerp.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    is_exported_to_sage_50 = fields.Boolean('Is Exported to Sage 50', default=False)

class AccountTax(models.Model):
    _inherit = 'account.tax'

    sage_50_code = fields.Char(string="Sage Export Code")    

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    
    @api.multi
    def get_taxes_values(self):
        tax_grouped = {}
        line = self
        price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
        taxes = line.invoice_line_tax_ids.compute_all(price_unit, self.invoice_id.currency_id, line.quantity, line.product_id, self.invoice_id.partner_id)['taxes']
        for tax in taxes:
            val = self._prepare_tax_line_vals(tax)
            key = self.env['account.tax'].browse(tax['id']).get_grouping_key(val)

            if key not in tax_grouped:
                tax_grouped[key] = val
            else:
                tax_grouped[key]['amount'] += val['amount']
                tax_grouped[key]['base'] += val['base']
        return tax_grouped
        
    def _prepare_tax_line_vals(self, tax):
        """ Prepare values to create an account.invoice.tax line
        The line parameter is an account.invoice.line, and the
        tax parameter is the output of account.tax.compute_all().
        """
        vals = {
            'invoice_id': self.invoice_id.id,
            'name': tax['name'],
            'tax_id': tax['id'],
            'amount': tax['amount'],
            'base': tax['base'],
            'manual': False,
            'sequence': tax['sequence'],
            'account_analytic_id': tax['analytic'] and self.account_analytic_id.id or False,
            'account_id': self.invoice_id.type in ('out_invoice', 'in_invoice') and (tax['account_id'] or self.account_id.id) or (tax['refund_account_id'] or self.account_id.id),
        }

        # If the taxes generate moves on the same financial account as the invoice line,
        # propagate the analytic account from the invoice line to the tax line.
        # This is necessary in situations were (part of) the taxes cannot be reclaimed,
        # to ensure the tax move is allocated to the proper analytic account.
        if not vals.get('account_analytic_id') and self.account_analytic_id and vals['account_id'] == self.account_id.id:
            vals['account_analytic_id'] = self.account_analytic_id.id

        return vals