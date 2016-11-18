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

import csv
import hashlib
import logging
import io
from dateutil import parser

_logger = logging.getLogger(__name__)

class AccountBankStatementImport(models.TransientModel):
    _inherit = "account.bank.statement.import"
    
    attrnames  = [
        'local_account', 'rubrique',  'entity', 'local_currency', 'statement_id', 'execution_date', 'message', 'value_date',
        'transferred_amount', 'balance', 'debit', 'credit', 'bicc_c', 'counterparty', 'counterparty_addr', 'struct_com', 'remark',
    ]
    
    def utf_8_encoder(self,unicode_csv_data):
        for line in unicode_csv_data:
            yield line.encode('utf-8')
    
    def _parse_file(self,data_file):
        
        currency = None
        account = None
        statements = []
        
        try:
            rows = data_file.splitlines()
            rows.pop(0) # skip header
            row = rows.pop(0)
            statement = {
                'id' : None,
                'transactions' : [],
            }
            while (len(rows) > 0) :
                values = row.split(';')
                _logger.debug("KBC Parser dealing with value")
                _logger.debug(values)
                if (len(self.attrnames) != len(values) and len(self.attrnames) != len(values)+1) :
                    _logger.debug("Wrong number of columns, continue")
                    row = rows.pop(0)
                    continue
                
                transaction = {}
                ''' Strip all values except the blob '''
                for (key, val) in zip(self.attrnames, values):
                    transaction[key] = val

                transaction['balance'] = float(transaction['balance'].replace(',', '.'))
                transaction['transferred_amount'] = float(transaction['transferred_amount'].replace(',', '.'))
                transaction['execution_date'] = parser.parse(transaction['execution_date'], dayfirst=True, yearfirst=False)
                transaction['value_date'] = parser.parse(transaction['value_date'], dayfirst=True, yearfirst=False)
                
                if statement['id'] != transaction['statement_id']:
                    # create new statement
                    statement = {
                        'id' : transaction['statement_id'],
                        'name' : transaction['local_account'] + "-" + transaction['statement_id'],
                        'balance_start': transaction['balance'] - transaction['transferred_amount'],
                        'balance_end_real': transaction['balance'],
                        'date': transaction['execution_date'],
                        'transactions' : [],
                        'partner_name' : transaction['counterparty'],
                    }
                    statements.append(statement)
                    currency = transaction['local_currency']
                    account = transaction['local_account']
                else :
                    statement['balance_end_real'] = transaction['balance']

                st_line = {
                    'date' : transaction['execution_date'],    
                    'amount' : transaction['transferred_amount'],
                    'name' : transaction['message'],
                    'unique_import_id' : hashlib.sha1(buffer(str(transaction))).hexdigest(),
                }
                if st_line['amount'] != 0 :
                    _logger.debug("Got it add line")
                    _logger.debug(st_line)
                    statement['transactions'].append(st_line)
                
                row = rows.pop(0)
                
        except Exception, e:
            _logger.exception(e)
            _logger.debug("Statement file was not recognized as a CBC file, trying next parser", exc_info=True)
            return super(AccountBankStatementImport, self)._parse_file(data_file)
        
        finally :
            if (len(statements) > 0) :
                return currency, account, statements
            else :
                _logger.debug("No statement found, trying next parser", exc_info=True)
                return super(AccountBankStatementImport, self)._parse_file(data_file)