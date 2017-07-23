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

from odoo import tools
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class ReducedVATAgreementReport(models.Model):
    '''Reduced VAT Agreement Report'''
    _name = 'construction.reduced_vat_agreement_report'
    _description = 'Reduced VAT Agreement Report'
    
    _auto = False
    _rec_name = 'agreement_code'
    
    agreement_code = fields.Char(string='Agreement Code',readonly=True)
    matricule = fields.Char(string="Matricule",readonly=True)
    zip = fields.Char(string="Zip Code",readonly=True)
    date = fields.Date(string="Date",readonly=True)
    number = fields.Char(string="Number",readonly=True)
    amount_untaxed = fields.Monetary(string='Untaxed Amount',readonly=True, currency_field='company_currency_id')
    amount_tax = fields.Monetary(string='Tax Amount',readonly=True, currency_field='company_currency_id')
    
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    
    last_quarter = fields.Boolean('Last Quarter')
    current_quarter = fields.Boolean('Current Quarter')
    
    @api.model_cr
    def init(self):
        # self._table = construction_reduced_vat_agreement_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            SELECT inv.id, agg.agreement_code, cust.matricule, s_addr.zip, inv.date_invoice as date, inv.move_name as number, inv.amount_untaxed, inv.amount_tax, inv.company_id
            FROM account_invoice inv, res_partner cust, construction_reduced_vat_agreement agg, construction_building_asset ba, construction_building_site bs, res_partner s_addr
            WHERE inv.partner_id = cust.id AND inv.reduced_vat_agreement_id = agg.id AND inv.building_asset_id = ba.id AND ba.site_id = bs.id AND bs.address_id = s_addr.id
        )""" % (self._table))