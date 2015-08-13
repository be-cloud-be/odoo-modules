from openerp.osv import fields, osv

class knowledge_config_settings(osv.osv_memory):
    _inherit = 'knowledge.config.settings'
    _columns = {
        'document_gdrive_upload_dir': fields.char('Google Drive Upload Directory',
            help='Directory where the files will be uploaded using the Google File Picker.'),
    }