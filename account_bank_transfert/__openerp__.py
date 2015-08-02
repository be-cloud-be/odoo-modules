# -*- encoding: utf-8 -*-
{
    'name': 'Bank Transfert Voucher Management',
    'category' : 'Accounting & Finance',
    'version': '0.1',
    'author': 'be-cloud.be (Jerome Sonnet)',
    'description' : """
Module to create bank transfer voucher.
=======================================

    """,
    'data': ['account_bank_transfert_view.xml',
            'security/ir.model.access.csv',],
    'depends': ['account','account_voucher'],
    'demo': [],
    'auto_install': True,
    'installable': True,
}
