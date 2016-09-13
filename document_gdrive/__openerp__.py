# -*- coding: utf-8 -*-
# Copyright 2015 be-cloud.be Jerome Sonnet <jerome.sonnet@be-cloud.be>
# Copyright 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Google Drive Attachment',
<<<<<<< HEAD
    'version': '10.0.1.0.0',
=======
    'version': '9.0.1.0.0',
>>>>>>> [FIX] used new_api for 9.0 branch
    'category': 'Tools',
    'description': """
Module that allows to attach a Google Drive Document.
    """,
    'author': "be-cloud.be (Jerome Sonnet),Sodexis",
    'website': 'http://www.be-cloud.be',
    'license': 'AGPL-3',
    'depends': [
        'base_setup', 'google_account', 'document',
    ],
    'data': [
        'views/res_config.xml',
        'views/document_gdrive_view.xml',
    ],
    'qweb': [
        'static/src/xml/gdrive.xml',
    ],
    "installable": True,
}
