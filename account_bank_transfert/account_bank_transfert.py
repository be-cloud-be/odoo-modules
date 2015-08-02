# -*- coding: utf-8 -*-
# Author be-cloud (Jerome Sonnet)

import datetime
from dateutil.relativedelta import relativedelta

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp import tools
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

    journal_entry_id = fields.Many2one('account.move', string='Journal Entry', copy=False)

    note = fields.Text(string='Notes')
    
    _sql_constraints = [
        ('number_uniq', 'unique(number, company_id)',
            'Transfert Number must be unique per Company!'),
    ]
    
    @api.multi
    def onchange_trade_date_transfert(self, trade_date):
        if not trade_date:
            trade_date = fields.Date.context_today(self)
        datetime_today = datetime.datetime.strptime(trade_date, tools.DEFAULT_SERVER_DATE_FORMAT)
        value_date = str((datetime_today + relativedelta(days=+2)).strftime(tools.DEFAULT_SERVER_DATE_FORMAT))
        return {'value': {'value_date': value_date}}
    
    @api.multi
    def action_date_assign(self):
        for tr in self:
            res = tr.onchange_trade_date_transfert(tr.date_invoice)
            if res and res.get('value'):
                tr.write(res['value'])
        return True
        
    @api.model
    def _prepare_move(self):
        """Prepare the dict of values to create the move from a
           statement line. This method may be overridden to implement custom
           move generation (making sure to call super() to establish
           a clean extension chain).
           :param browse_record st_line: account.bank.statement.line record to
                  create the move from.
           :param char st_line_number: will be used as the name of the generated account move
           :return: dict of value to create() the account.move
        """
        return {
            'journal_id': self.journal_id.id,
            'period_id': self.period_id.id,
            'company_id': self.company_id.id,
            'date': self.trade_date,
            'name': None,
            'ref': None,
        }
        
    @api.multi
    def action_move_create(self):
        """ Creates transfert related analytics and financial move lines """
        am_obj = self.env['account.move']
        aml_obj = self.env['account.move.line']
        
        for tr in self:
            if not tr.from_account_id.journal_id.default_debit_account_id:
                raise except_orm(_('Error!'), _('Please define an internal transfert account on the journal related to the origin account.'))
            if not tr.to_account_id.journal_id.default_debit_account_id:
                raise except_orm(_('Error!'), _('Please define an internal transfert account on the journal related to the destination account.'))
            if not tr.from_account_id.journal_id.sequence_id:
                raise except_orm(_('Error!'), _('Please define sequence on the journal related to the origin account.'))
            if not tr.to_account_id.journal_id.sequence_id:
                raise except_orm(_('Error!'), _('Please define sequence on the journal related to the destination account.'))
            if tr.move_id:
                continue
            
            move_vals = bs_obj._prepare_move(tr)
            move_id = am_obj.create(move_vals)
            
            from_line = {
                'journal_id': tr.from_account_id.journal_id,
                'period_id': tr.period_id.id,
                'name': _('change') + ': ' + (tr.name or '/'),
                'account_id': tr.from_account_id.journal_id.default_debit_account_id.id,
                'move_id': move_id,
                'partner_id': tr.company_id,
                'currency_id': tr.currency_id,
                'amount_currency': tr.amount,
                'quantity': tr.amount,
                'credit': 0,
                'debit': tr.amount,
                'date': tr.trade_date,
                'counterpart_move_line_id': mv_line.id,
            }
            aml_obj.create(from_line)
            
            from_line_counterpart = {
                'journal_id': tr.from_account_id.journal_id,
                'period_id': tr.period_id.id,
                'name': _('change') + ': ' + (st_line.name or '/'),
                'account_id': tr.from_account_id.journal_id.internal_account_id.id,
                'move_id': move_id,
                'amount_currency': tr.amount,
                'partner_id': tr.company_id,
                'currency_id': tr.currency_id,
                'quantity': tr.amount,
                'debit': tr.amount,
                'credit': 0,
                'date': tr.trade_date,
            }
            aml_obj.create(from_line_counterpart)
            
            to_line = {
                'journal_id': tr.to_account_id.journal_id,
                'period_id': tr.period_id.id,
                'name': _('change') + ': ' + (tr.name or '/'),
                'account_id': tr.from_account_id.journal_id.internal_account_id.id,
                'move_id': move_id,
                'partner_id': tr.company_id,
                'currency_id': tr.currency_id,
                'amount_currency': tr.amount,
                'quantity': tr.amount,
                'credit': 0,
                'debit': tr.amount,
                'date': tr.trade_date,
                'counterpart_move_line_id': mv_line.id,
            }
            aml_obj.create(to_line)
            
            to_line_counterpart = {
                'journal_id': tr.to_account_id.journal_id,
                'period_id': tr.period_id.id,
                'name': _('change') + ': ' + (st_line.name or '/'),
                'account_id': tr.from_account_id.journal_id.default_debit_account_id.id,
                'move_id': move_id,
                'amount_currency': tr.amount,
                'partner_id': tr.company_id,
                'currency_id': tr.currency_id,
                'quantity': tr.amount,
                'debit': tr.amount,
                'credit': 0,
                'date': tr.trade_date,
            }
            aml_obj.create(to_line_counterpart)
        
            self.write({'journal_entry_id': move_id})
        
    @api.multi
    def action_cancel(self):
        moves = self.env['account.move']
        for inv in self:
            if inv.move_id:
                moves += inv.move_id
            if inv.payment_ids:
                for move_line in inv.payment_ids:
                    if move_line.reconcile_partial_id.line_partial_ids:
                        raise except_orm(_('Error!'), _('You cannot cancel a transfert which is partially paid. You need to unreconcile related payment entries first.'))

        # First, set the invoices as cancelled and detach the move ids
        self.write({'state': 'cancel', 'move_id': False})
        if moves:
            # second, invalidate the move(s)
            moves.button_cancel()
            # delete the move this invoice was pointing to
            # Note that the corresponding move_lines and move_reconciles
            # will be automatically deleted too
            moves.unlink()
        self._log_event(-1.0, 'Cancel Transfert')
        return True
