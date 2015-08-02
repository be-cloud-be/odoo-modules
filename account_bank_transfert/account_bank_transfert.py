# -*- coding: utf-8 -*-
# Author be-cloud (Jerome Sonnet)

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp

class account_bank_transfert(models.Model):
    _name = "account.bank_transfert"
    _inherit = ['mail.thread']
    _description = "Bank Transfert"
    
    _track = {
        'type': {
        },
        'state': {
            'account.mt_transfert_paid': lambda self, cr, uid, obj, ctx=None: obj.state == 'paid',
            'account.mt_transfert_confirmed': lambda self, cr, uid, obj, ctx=None: obj.state == 'confirmed',
        },
    }
    
    
    @api.model
    def _default_journal(self):
        #inv_type = self._context.get('type', 'out_invoice')
        #inv_types = inv_type if isinstance(inv_type, list) else [inv_type]
        #company_id = self._context.get('company_id', self.env.user.company_id.id)
        #domain = [
        #    ('type', 'in', filter(None, map(TYPE2JOURNAL.get, inv_types))),
        #    ('company_id', '=', company_id),
        #]
        #return self.env['account.journal'].search(domain, limit=1)
        return None

    @api.model
    def _default_currency(self):
        journal = self._default_journal()
        if journal:
            return journal.currency or journal.company_id.currency_id
        return None
    
    number = fields.Char(related='move_id.name', store=True, readonly=True, copy=False)
    
    sent = fields.Boolean(readonly=True, default=False, copy=False,
        help="It indicates that the transfert has been sent.")
    
    trade_date = fields.Date(string='Trade Date',
        readonly=True, states={'draft': [('readonly', False)]}, index=True,
        help="The date of the transfert.", copy=False)
    
    value_date = fields.Date(string='Due Date',
        readonly=True, states={'draft': [('readonly', False)]}, index=True, copy=False,
        help="Will be set to D+2 as a default")
    
    period_id = fields.Many2one('account.period', string='Force Period',
        domain=[('state', '!=', 'done')], copy=False,
        help="Keep empty to use the period of the trade date.",
        readonly=True, states={'draft': [('readonly', False)]})
        
    move_id = fields.Many2one('account.move', string='Journal Entry',
        readonly=True, index=True, ondelete='restrict', copy=False,
        help="Link to the automatically generated Journal Items.")
    
    currency_id = fields.Many2one('res.currency', string='Currency',
        required=True, readonly=True, states={'draft': [('readonly', False)]},
        default=_default_currency, track_visibility='always')
        
    journal_id = fields.Many2one('account.journal', string='Journal',
        required=True, readonly=True, states={'draft': [('readonly', False)]},
        default=_default_journal,
        domain="[('company_id', '=', company_id)]")
    
    company_id = fields.Many2one('res.company', string='Company', change_default=True,
        required=True, readonly=True, states={'draft': [('readonly', False)]},
        default=lambda self: self.env['res.company']._company_default_get('account.bank_transfert'))
    
    state = fields.Selection([
            ('draft','Draft'),
            ('confirmed','Confirmed'),
            ('paid','Paid'),
            ('cancel','Cancelled'),
        ], string='Status', index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False,
        help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Transfert.\n"
             " * The 'Confirmed' status is used when user confirm a Transfert,a transfert number is generated. Its in open status till user executes the transfert.\n"
             " * The 'Paid' status is set automatically when the transfert is executed.\n"
             " * The 'Cancelled' status is used when user cancel a transfert.")
             
    from_account_id = fields.Many2one('res.partner.bank', string='From Bank Account',
        help='Bank Account Number from which the transfert will be done. Must be a company bank account number.',
        readonly=True, states={'draft': [('readonly', False)]})
        
    to_account_id = fields.Many2one('res.partner.bank', string='To Bank Account',
        help='Bank Account Number from which the transfert will be done. Must be a company bank account number.',
        readonly=True, states={'draft': [('readonly', False)]})

    amount = fields.Float(string='Amount which will be transfered.', digits=dp.get_precision('Account'),
        readonly=True, states={'draft': [('readonly', False)]}, default=0.0)

    note = fields.Text(string='Notes')
    
    _sql_constraints = [
        ('number_uniq', 'unique(number, company_id)',
            'Transfert Number must be unique per Company!'),
    ]