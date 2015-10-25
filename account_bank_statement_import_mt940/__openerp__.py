# -*- encoding: utf-8 -*-
{
    'name': 'Import MT940 Bank Statement',
    'category' : 'Accounting & Finance',
    'version': '0.1',
    'author': 'be-cloud.be (Jerome Sonnet)',
    'description' : """
Module to import MT940 bank statements.
======================================

This module allows you to import MT940 files in Odoo: they are parsed and stored in human readable format in
Accounting \ Bank and Cash \ Bank Statements.

    """,
    'data': ['account_bank_statement_import_mt940_view.xml'],
    'depends': ['account_bank_statement_import'],
    'demo': [],
    'auto_install': True,
    'installable': True,
}
