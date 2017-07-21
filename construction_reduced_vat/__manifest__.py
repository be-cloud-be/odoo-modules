# -*- encoding: utf-8 -*-
# see LICENSE file

{
    'name': 'Construction Projects',
    'version': '0.1',
    'category': 'Sales',
    'description': """
    Manage construction projects
    """,
    "author": "be-cloud.be (Jerome Sonnet)",
    "website": "http://www.be-cloud.be",
    'depends': ['sale','crm','project'],
    'init_xml': [],
    'data': [
        'views/construction_view.xml',
        'security/ir.model.access.csv',
        
    ],
    'installable': True,
    'active': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: