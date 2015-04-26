
# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 be-cloud.be 
#                             
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsability of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

'''
This parser can be used to import CSV files produced by CBC-KBC web banking.
'''

from account_banking.parsers import models
from account_banking.parsers.convert import str2date

from tools.translate import _

import csv
import re

__all__ = ['parser']

class transaction_line(object):
    '''
    A auxiliary class to validate and coerce read values
    
    Numéro de compte    Nom rubrique    Nom    Devise    Numéro extrait    Date    Description    Date valeur    Montant    Solde
    '''
    attrnames = [
        'local_account', 'rubrique',  'entity', 'local_currency', 'statement_id', 'execution_date', 'message', 'effective_date',
        'transferred_amount', 'balance', 'remark',
    ]

    def __init__(self, values, subno):
        '''
        Initialize own dict with attributes and coerce values to right type
        '''
        if (len(self.attrnames) != len(values) and len(self.attrnames) != len(values)+1) :
            raise ValueError, \
                    _('Invalid transaction line: expected %d columns, found '
                      '%d') % (len(self.attrnames), len(values))
        ''' Strip all values except the blob '''
        for (key, val) in zip(self.attrnames, values):
            self.__dict__[key] = key == 'blob' and val or val.strip()
        # for lack of a standardized locale function to parse amounts
        self.local_account = self.local_account.zfill(10)
        self.balance = float(self.balance.replace(',', '.'))
        self.transferred_amount = float(self.transferred_amount.replace(',', '.'))
        self.execution_date = str2date(self.execution_date, '%d/%m/%Y')
        self.value_date = str2date(self.effective_date, '%d/%m/%Y')
        self.effective_date = str2date(self.effective_date, '%d/%m/%Y')
        self.id = str(subno).zfill(4)

class transaction(models.mem_bank_transaction):
    attrnames = ['local_account', 'local_currency', 'execution_date', 'effective_date', 'value_date',
        'transferred_amount', 'id'
                ]
    
    def __init__(self, line, *args, **kwargs):
        '''
        Initialize own dict with read values.
        '''
        super(transaction, self).__init__(*args, **kwargs)
        # Copy attributes from auxiliary class to self.
        for attr in self.attrnames:
            setattr(self, attr, getattr(line, attr))
        # Initialize other attributes
        self.transfer_type = 'UNKN'
        self.remote_account = ''
        self.remote_owner = ''
        self.reference = ''
        self.message = line.message.decode('iso-8859-1').encode('utf-8')
        self.currency = 'EUR'
        # Decompose structured messages
        self.parse_message(line)
        
    def parse_message(self,line):
        iban = re.search('BE\d{2} \d{4} \d{4} \d{4}', self.message)
        if iban:
            self.remote_account = iban.group(0)
            self.transfer_type = models.mem_bank_transaction.ORDER
        acnt_num = re.search('\d{3}-\d{7}-\d{2}', self.message)
        if acnt_num:
            self.remote_account = acnt_num.group(0)
            self.transfer_type = models.mem_bank_transaction.ORDER
        pass
        is_frais = re.search('DECOMPTE FRAIS', self.message)
        if is_frais:
            self.transfer_type = models.mem_bank_transaction.BANK_COSTS
    
class statement(models.mem_bank_statement):
    '''
    Implementation of bank_statement communication class of account_banking
    '''
    def __init__(self, t_line, *args, **kwargs):
        '''
        Set decent start values based on first transaction read
        '''
        super(statement, self).__init__(*args, **kwargs)
        self.id = t_line.statement_id
        self.local_account = t_line.local_account
        self.date = t_line.execution_date
        self.end_balance = self.start_balance = t_line.balance - t_line.transferred_amount
        self.import_transaction(t_line)

    def import_transaction(self, msg):
        '''
        Import a transaction and keep some house holding in the mean time.
        '''
        trans = transaction(msg)
        self.end_balance += trans.transferred_amount
        self.transactions.append(trans)

    def is_valid(self):
#        for attr in dir(self):
#            try:
#                print "self.%s = %s" % (attr, getattr(self, attr))
#            except:
#                pass    
        return 1

class parser(models.parser):
    code = 'CBC'
    country_code = 'BE'
    name = _('CBC-KBC (BE)')
    doc = _('''\
This parser can be used to import CSV files produced by CBC-KBC web banking.
''')

    def parse(self, cr, data):
        results = []
        stmnt = None
        subno = 0
        lines = data.splitlines()
        lines.pop(0)
        for line in lines:
            items = line.split(';')
            t_line = transaction_line(items, subno)
            if stmnt and stmnt.id == t_line.statement_id:
                stmnt.import_transaction(t_line)               
            else: 
                if stmnt:
                    results.append(stmnt)
                subno = 0
                stmnt = statement(t_line)
        if stmnt:
            results.append(stmnt)    
        return results
