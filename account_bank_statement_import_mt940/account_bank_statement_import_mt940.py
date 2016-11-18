# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2015 be-cloud.be
#                       Jerome Sonnet <jerome.sonnet@be-cloud.be>
#
#    Thanks to Alexis Yushin <AYUSHIN@thy.com> for sharing code/ideas
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


from openerp import api, fields, models, _
from openerp.exceptions import UserError
import mt940
import hashlib
import logging
import StringIO

_logger = logging.getLogger(__name__)

class AccountBankStatementImport(models.TransientModel):
    _inherit = "account.bank.statement.import"
    
    def _parse_file(self,data_file):
        
        currency = None
        account = None
        statements = []
        
        try:
            transactions = mt940.parse(StringIO.StringIO(data_file))
            # if no statements found
            if not transactions:
                _logger.debug("Statement file was not recognized as an MT940 file, trying next parser", exc_info=True)
                return super(AccountBankStatementImport, self)._parse_file(data_file)
            
            statement = {
                'name' : transactions.data['account_identification'] + "-" + transactions.data['statement_number'] + "-" + transactions.data['sequence_number'],
                'balance_start': transactions.data['final_opening_balance'].amount.amount,
                'balance_end_real': transactions.data['final_closing_balance'].amount.amount,
                'date': transactions.data['final_opening_balance'].date,
                'transactions' : [],
            }
            
            currency = transactions.data['final_opening_balance'].amount.currency
            account = transactions.data['account_identification'].split('/')[1]
            
            # we iterate through each transaction
            for t in transactions:
                st_line = {
                    'date' : t.data.get('entry_date') or t.data.get('date'),    
                    'amount' : t.data['amount'].amount,
                    'ref' : t.data.get('bank_reference') or t.data.get('extra_details'),
                    'name' : t.data['transaction_details'],
                    'unique_import_id' : hashlib.sha1(buffer(str(t.data))).hexdigest(),
                }
                if st_line['amount'] != 0 :
                    statement['transactions'].append(st_line)
            if len(statement['transactions']) > 0 :
                return currency, account, [statement]
            return None, None, None
                    
        except Exception, e:
            _logger.exception(e)
            _logger.debug("Statement file was not recognized as a MT940 file, trying next parser", exc_info=True)
            return super(AccountBankStatementImport, self)._parse_file(data_file)