{
    'name': 'Accounting Dashboard using AG Grid',
    'version': '0.1',
    'license': 'GPL-3',
    'author': 'be-Cloud.be (Jerome Sonnet)',
    'website': '',
    'category': 'Accounting',
    'depends': ['web_ag_grid','account_accountant','web_unleashed_extra'],
    'data': [
        # view
        'view/account_ag_grid_view.xml',

        # menu
        'menu/account_ag_grid.xml',

         # JS/CSS Assets files
        'assets/account_ag_grid.xml',
    ],
    'description': '''
        This modules add a ag-grid view on account move line.
    ''',
    'active': True,
    'installable': True,
    'qweb' : [
        'static/src/templates/*.xml',
    ],
    'demo': [],
    'application': False,
    'installable': True,
    'active': False,
}
