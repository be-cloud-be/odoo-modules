{
    'name': 'Real estate management',
    'version': '0.1',
    'license': 'GPL-3',
    'author': 'be-Cloud.be (Jerome Sonnet)',
    'website': '',
    'category': 'CRM',
    'depends': ['crm','sale'],
    'init_xml': [],
    'update_xml': [
        'realestate_view.xml',
        'security/realestate_security.xml',
        'security/ir.model.access.csv',
    ],
    'demo_xml': [],
    'description': '''
    This modules add a real estate management.
    ''',
    'active': False,
    'installable': True,
}
