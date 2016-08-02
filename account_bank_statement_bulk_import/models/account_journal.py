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

<<<<<<< HEAD
from odoo import tools

from odoo import api, fields, models, _
from odoo.exceptions import UserError
=======
from openerp import api, fields, models, _
from openerp.exceptions import UserError
>>>>>>> merge

_logger = logging.getLogger(__name__)

class AccountJournal(models.Model):
    _inherit = "account.journal"

    @api.multi
<<<<<<< HEAD
    @api.depends('parent_id', 'parent_id.report_name')
    def _get_report_name(self):
        '''Returns the name of the Root Account which correspond to the 
            Report Name.'''
        for report in self:
            name = report.name
            if report.parent_id:
                name = report.parent_id.report_name
            report.report_name = name

    report_name = fields.Char(string="Report Name" ,compute="_get_report_name")
    
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.depends('debit', 'credit')
    def _store_reversed_balance(self):
        for line in self:
            line.reversed_balance = line.credit - line.debit
            
    reversed_balance = fields.Monetary(string="Reversed Balance", compute='_store_reversed_balance', currency_field='company_currency_id', store=True, default=0.0, help="Technical field holding the credit - debit in order to open meaningful graph views from reports using reversed sign balance")
    
class TaxBaseReport(models.Model):
    _name = "account.tax.base.report"
    _auto = False
    
    date = fields.Date(string="Date")
    name = fields.Char(string="Name")
    tax_name = fields.Char(string="Tax Name")
    move_id = fields.Many2one('account.move', string='Account Move')
    partner_id = fields.Many2one('res.partner', 'Partner')
    untaxed_amount = fields.Float(string="Untaxed Amount",digits=(10, 2))
    
    def init(self, cr):
        """ School Student main report """
        tools.drop_view_if_exists(cr, 'account_tax_base_report')
        cr.execute(""" CREATE VIEW account_tax_base_report AS (
                        select CONCAT('hr',hr_expense.id) id, hr_expense.date, hr_expense.name, hr_expense.account_move_id as move_id, hr_expense.employee_id as partner_id, account_tax.name as tax_name, untaxed_amount 
                        from hr_expense, expense_tax, account_tax
                        where hr_expense.id = expense_tax.expense_id and account_tax.id = expense_tax.tax_id
                        union all
                        select CONCAT('in',account_invoice_line.id) id, account_invoice.date, account_invoice_line.name, account_invoice.move_id, account_invoice.partner_id, account_tax.name, account_invoice_line.price_subtotal_signed
                        from account_invoice, account_invoice_line, account_invoice_line_tax, account_tax 
                        where account_invoice.id = account_invoice_line.invoice_id and account_invoice_line.id = account_invoice_line_tax.invoice_line_id and account_tax.id = account_invoice_line_tax.tax_id
                        )""")
=======
    def bulk_import_statement(self):
        """return action to bulk import bank/cash statements. This button should be called only on journals with type =='bank'"""
        model = 'account.bank.statement'
        action_name = 'action_account_bank_statement_bulk_import'
        ir_model_obj = self.pool['ir.model.data']
        model, action_id = ir_model_obj.get_object_reference(self._cr, self._uid, 'account_bank_statement_bulk_import', action_name)
        action = self.pool[model].read(self._cr, self._uid, action_id, context=self.env.context)
        # Note: this drops action['context'], which is a dict stored as a string, which is not easy to update
        action.update({'context': (u"{'journal_id': " + str(self.id) + u"}")})
        return action
>>>>>>> merge
