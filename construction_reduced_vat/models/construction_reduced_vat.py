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

class ReducedVATAgreement(models.Model):
    '''Reduced VAT Agreement'''
    _name = 'construction.reduced_vat_agreement'
    _description = 'Reduced VAT Agreement'
    
    state = fields.Selection([
            ('draft', 'Draft'),
            ('requested', 'Requested'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('archived', 'Archived'),
        ], string='State', required=True, help="", default="draft")
        
    @api.multi
    def action_request(self):
        if self.filtered(lambda inv: inv.state != 'draft'):
            raise UserError(_("Agreement must be a draft in order to set it to requested."))
        return self.write({'state': 'requested'})
    
    @api.multi
    def action_approve(self):
        if self.filtered(lambda inv: inv.state != 'draft' and inv.state != 'requested'):
            raise UserError(_("Agreement must be a draft or requested in order to set it to approved."))
        return self.write({'state': 'approved'})
        
    @api.multi
    def action_reject(self):
        if self.filtered(lambda inv: inv.state != 'requested'):
            raise UserError(_("Agreement must be a requested in order to set it to rejected."))
        return self.write({'state': 'rejected'})
        
    @api.multi
    def action_draft(self):
        return self.write({'state': 'draft','active':True})
        
    @api.multi
    def action_archive(self):
        return self.write({'state': 'arvhived','active':False})
        
    active = fields.Boolean(default=True)
    
    agreement_code = fields.Char(string='Agreement Code',help='Agreement Code given by the administration', readonly=True, states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one('res.partner', string='Customer', readonly=True, states={'draft': [('readonly', False)]}, required=True)
    
    name = fields.Char(compute='_compute_name', store=True)
    
    @api.one
    @api.depends('agreement_code','partner_id.name')
    def _compute_name(self):
       self.name = "%s - %s" % (self.agreement_code, self.partner_id.name)
    
    agreement_total_amount = fields.Monetary(string="Agreement Total Amount", currency_field='company_currency_id', track_visibility='onchange')
    invoice_ids = fields.One2many('account.invoice','reduced_vat_agreement_id',string="Invoices")
    agreement_remaining_amount = fields.Monetary(string="Agreement Remaining Amount", compute="_compute_remaining_amount", currency_field='company_currency_id', store=True)
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True)
    company_id = fields.Many2one('res.company', string='Company', change_default=True,
        required=True, readonly=True, states={'draft': [('readonly', False)]},
        default=lambda self: self.env['res.company']._company_default_get('account.invoice'))
    
    @api.one
    @api.depends('agreement_total_amount','invoice_ids.amount_untaxed')
    def _compute_remaining_amount(self):
        used_amount = sum(invoice.amount_untaxed for invoice in self.invoice_ids)
        self.agreement_remaining_amount = self.agreement_total_amount - used_amount
    
class Invoice(models.Model):
    '''Invoice'''
    _inherit = 'account.invoice'
    
    reduced_vat_agreement_id = fields.Many2one('construction.reduced_vat_agreement', string='Reduced VAT Agreement', readonly=True, states={'draft': [('readonly', False)]})