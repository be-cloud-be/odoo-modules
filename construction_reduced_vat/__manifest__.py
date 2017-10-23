# -*- encoding: utf-8 -*-
# see LICENSE file

{
    'name': 'Construction VAT reduced',
    'version': '0.1',
    'category': 'Sales',
    'description': """
    Manage reduced VAT as applied in Luxembourg.
    """,
    "author": "be-cloud.be (Jerome Sonnet)",
    "website": "http://www.be-cloud.be",
    'depends': ['construction'],
    'init_xml': [],
    'data': [
        'views/construction_reduced_vat_view.xml',
        'security/ir.model.access.csv',
        'report/construction_reduced_vat_report.xml',
    ],
    'installable': False,
    'active': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: