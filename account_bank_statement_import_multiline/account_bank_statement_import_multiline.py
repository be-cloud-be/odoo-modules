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

    @api.one
    def _get_hide_journal_field(self):
        return self.env.context and 'journal_id' in self.env.context or False

    journal_id = fields.Many2one('account.journal', string='Journal', help='Accounting journal related to the bank statement you\'re importing. It has be be manually chosen for statement formats which doesn\'t allow automatic journal detection (QIF for example).',
                                 default=_get_hide_journal_field)
    hide_journal_field = fields.Boolean('Hide the journal field in the view')

    @api.multi
    def import_file(self):
        """ Process the file chosen in the wizard, create bank statement(s) and go to reconciliation. """

        # Fix data charset and other small things
        data_file = self.with_context(active_id=self.ids[0]).data_file
        data = base64.b64decode(data_file)
        encoding = chardet.detect(data)
        data.decode(encoding['encoding'])
        # REMOVE BOM if present because it depends of the platform use to access multiline.
        if data[:3] == codecs.BOM_UTF8:
            data = data[3:]
        self.data_file = base64.b64encode(data)

        return super(AccountBankStatementImport, self).import_file()

    def _check_csv(self,file):
        try:
            dict = unicodecsv.DictReader(file, delimiter=';', quotechar='"',encoding="iso-8859-1")
        except:
            return False
        return dict

    def _parse_file(self,data_file):
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
                    if (currency , account_num ,statement_id) in all_statements:
                        all_statements[currency , account_num ,statement_id]['transactions'].append(vals_line)
                    else:
                        all_statements[currency , account_num ,statement_id] = {
                            'name': line['Account'] + '-' + line['Statement number'],
                            'balance_start': float(line['Opening balance'].replace(',','.')),
                            'balance_end_real': float(line['Closing balance'].replace(',','.')),
                            'transactions' : [vals_line],
                        }
        except Exception, e:
            raise UserError(_("The following problem occurred during import. The file might not be valid.\n\n %s" % e.message))
        return all_statements
