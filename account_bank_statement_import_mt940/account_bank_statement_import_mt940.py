# -*- coding: utf-8 -*-
# Author be-cloud (Jerome Sonnet)
# Some code from Alexey kostjantynovytsj Yushin <AYUSHIN@thy.com>

from openerp import api, fields, models, _
from openerp.exceptions import UserError
import mt940

_logger = logging.getLogger(__name__)

class AccountBankStatementImport(models.TransientModel):
    _inherit = "account.bank.statement.import"
    
    def _parse_file(self,data_file):
        
        currency = None
        account = None
        statements = []
        
        try:
            transactions = mt940.parse(data_file)
            # if no statements found
            if not transactions:
                _logger.debug("Statement file was not recognized as an MT940 file, trying next parser", exc_info=True)
                return super(AccountBankStatementImport, self)._parse_file(data_file)
            
            statement = {
                'name' : transactions.transaction_reference,
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
                    'date' = t.data['entry_date'],    
                    'amount' = t.data['amount'].amount,
                    'name' = t.data['bank_reference'] || t.data['extra_details'],
                    'note' = t.data['transaction_details'],
                }
                statement['transactions'].append(st_line)
            
            return currency, account, statement
                    
        except Exception, e:
            raise UserError(_("The following problem occurred during import. The file might not be valid.\n\n %s" % e.message))