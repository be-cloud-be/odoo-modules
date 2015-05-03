{
    'name': 'Property management',
    'version': '0.1',
    'license': 'GPL-3',
    'author': 'be-Cloud.be (Jerome Sonnet)',
    'website': '',
    'category': 'CRM',
    'depends': ['crm'],
    'init_xml': [],
    'update_xml': [
        'property_management_view.xml',
        #'security/ir.model.access.csv',
    ],
    'demo_xml': [],
    'description': '''
    This modules add a property management.
    ''',
    'active': False,
    'installable': True,
}
