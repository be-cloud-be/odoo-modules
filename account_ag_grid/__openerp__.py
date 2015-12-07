{
    'name': 'Account ag-grid',
    'version': '0.1',
    'license': 'GPL-3',
    'author': 'be-Cloud.be (Jerome Sonnet)',
    'website': '',
    'category': 'Accounting',
    'depends': ['web','account_accountant'],
    'init_xml': [],
    'data': [
        'account_ag_grid_view.xml',
    ],
    'demo_xml': [],
    'description': '''
        This modules add a ag-grid view on account move line.
    ''',
    'active': True,
    'installable': True,
    'web':True,
    'css': [
        'static/lib/ag-grid/ag-grid.min.css',
    ],
    'js': [
        'static/lib/ag-grid/ag-grid.min.js',
        'static/src/js/widgets.js',
    ],
    'qweb': [
        'static/src/xml/account_ag_grid.xml',
    ],
}
