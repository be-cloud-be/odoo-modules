{
    'name': 'Membership team management',
    'version': '0.1',
    'license': 'GPL-3',
    'author': 'be-Cloud.be (Jerome Sonnet)',
    'website': '',
    'category': 'Association',
    'depends': ['membership'],
    'init_xml': [],
    'update_xml': [
        'membership_team_management_view.xml',
        #'security/ir.model.access.csv',
    ],
    'demo_xml': [],
    'description': '''
This modules add a management of member being assigned to a team.
    ''',
    'active': False,
    'installable': True,
}
