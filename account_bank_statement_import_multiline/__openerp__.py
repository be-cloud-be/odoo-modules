# -*- encoding: utf-8 -*-
{
    'name': 'Import Multiline Bank Statement',
    'category' : 'Accounting & Finance',
    'version': '0.1',
    'author': 'be-cloud.be (Jerome Sonnet)',
    'description' : """
Module to import Multiline bank statements.
======================================

This module allows you to import the machine readable Multiline Files in Odoo: they are parsed and stored in human readable format in
Accounting \ Bank and Cash \ Bank Statements.

Bank Statements may be generated containing a subset of the Multiline information (only those transaction lines that are required for the
creation of the Financial Accounting records). 
    
    """,
    'data': ['account_bank_statement_import_multiline_view.xml'],
    'depends': ['account_bank_statement_import'],
    'demo': [],
    'auto_install': True,
    'installable': True,
}
