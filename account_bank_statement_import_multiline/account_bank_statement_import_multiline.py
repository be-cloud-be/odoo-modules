# -*- coding: utf-8 -*-
# Author be-cloud (Jerome Sonnet)
# Somme code from OFX importer

import logging
import StringIO
import unicodecsv
import chardet
import codecs
import dateutil.parser
import base64
import hashlib

from openerp import api, fields, models, _
from openerp.exceptions import UserError

_logger = logging.getLogger(__name__)

class AccountBankStatementImport(models.TransientModel):
    _inherit = "account.bank.statement.import"

    def _check_csv(self,file):
        try:
            dict = unicodecsv.DictReader(file, delimiter=';', quotechar='"',encoding="iso-8859-1")
        except:
            return False
        return dict

    def _parse_file(self,data_file):
        
        import wdb
        wdb.set_trace()
        
        # decode Charset and remove BOM if needed
        encoding = chardet.detect(data_file)
        data_file.decode(encoding['encoding'])
        if data_file[:3] == codecs.BOM_UTF8:
            data_file = data_file[3:]
        
        csv = self._check_csv(StringIO.StringIO(data_file))
        if not csv:
            return super(AccountBankStatementImport, self)._parse_file(data_file)
        all_statements = {}
        try:
            for line in csv:
                if not line['Bank reference'] is None:
                    currency = line['Statement currency']
                    account_num = line['Account']
                    statement_id = line['Statement number']
                    m = hashlib.sha512()
                    m.update(str(line))
                    vals_line = {
                        'date': dateutil.parser.parse(line['Entry date'], dayfirst=True, fuzzy=True).date(),
                        'name': line['Counterparty name']+line['Transaction motivation'],
                        'ref': line['Account'] + '-' + line['Statement number']+'-'+line['Bank reference'],
                        'amount': float(line['Transaction amount'].replace(',','.')),
                        'unique_import_id': m.hexdigest(),
                        #'bank_account_id': bank_account_id,
                        #'partner_id': partner_id,
                    }
                    if (currency , account_num ) in all_statements:
                        account_statements = all_statements[currency , account_num ]
                        processed = False
                        for statement in account_statements :
                            if statement.name == line['Account'] + '-' + line['Statement number']:
                                # There is already a statement with this number add the transaction
                                statement['transactions'].append(vals_line)
                                processed = True
                                break
                        if not processed :
                            # There is no statement with this number, create one with this transaction
                            statement = {
                                'name': line['Account'] + '-' + line['Statement number'],
                                'balance_start': float(line['Opening balance'].replace(',','.')),
                                'balance_end_real': float(line['Closing balance'].replace(',','.')),
                                'transactions' : [vals_line],
                            }
                            account_statements.append(statement)
                    else:
                        statement = {
                                'name': line['Account'] + '-' + line['Statement number'],
                                'balance_start': float(line['Opening balance'].replace(',','.')),
                                'balance_end_real': float(line['Closing balance'].replace(',','.')),
                                'transactions' : [vals_line],
                        }
                        all_statements[currency , account_num ] = [statement]
                        
        except Exception, e:
            raise UserError(_("The following problem occurred during import. The file might not be valid.\n\n %s" % e.message))
        return currency, account_num, all_statements
