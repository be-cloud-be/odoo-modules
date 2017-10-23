# -*- encoding: utf-8 -*-
# see LICENSE file

{
    'name': 'Construction Sale Order Template',
    'version': '0.1',
    'category': 'Sales',
    'description': """
    Create template of Sale Order which build Sale Orders using percentages.
    """,
    "author": "be-cloud.be (Jerome Sonnet)",
    "website": "http://www.be-cloud.be",
    'depends': ['construction','sale'],
    'init_xml': [],
    'data': [
        'views/construction_sale_template_view.xml',
        'wizard/construction_sale_wizard.xml',
        'security/ir.model.access.csv',
    ],
    'installable': False,
    'active': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: