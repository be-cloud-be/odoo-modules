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

class AccountJournal(models.Model):
    _inherit = "account.journal"

    @api.multi
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