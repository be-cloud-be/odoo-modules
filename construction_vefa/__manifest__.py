# -*- encoding: utf-8 -*-
# see LICENSE file

{
    'name': 'Construction VEFA',
    'version': '0.1',
    'category': 'Sales',
    'description': """
    Manage 'Vente en etat futur d achèvement' au Luxembourg.
    """,
    "author": "be-cloud.be (Jerome Sonnet)",
    "website": "http://www.be-cloud.be",
    'depends': ['construction','sale'],
    'init_xml': [],
    'data': [
        'views/construction_vefa_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'active': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: