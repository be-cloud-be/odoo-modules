//////////////////////////////////////////////////////////////////////////////
//    OpenERP, Open Source Management Solution    
//    
//    Author: Jerome Sonnet <jerome.sonnet@be-cloud.be>
//
//    This program is free software: you can redistribute it and/or modify
//    it under the terms of the GNU General Public License as published by
//    the Free Software Foundation, either version 3 of the License, or
//    (at your option) any later version.
//
//    This program is distributed in the hope that it will be useful,
//    but WITHOUT ANY WARRANTY; without even the implied warranty of
//    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//    GNU General Public License for more details.
//
//    You should have received a copy of the GNU General Public License
//    along with this program.  If not, see <http://www.gnu.org/licenses/>.
//
/////////////////////////////////////////////////////////////////////////////

odoo.define('school_course_description.editor', function(require) {
    "use strict";

    var core = require('web.core');
    var Model = require('web.Model');
    var Dialog = require('web.Dialog');
    var website = require('website.website');
    
    var _t = core._t;
    
    $('.text_editor').summernote();
    
    $('.school_editor_save').on('click', function (event) {
        if (!event.isDefaultPrevented() && !$(this).is(".disabled")) {
            var doc_id = $('.course_doc_editor').data('doc-id');
            var content = $("#content").code();
            var method = $("#method").code();
            var learning_outcomes = $("#learning-outcomes").code();
            var competencies = $("#competencies").code();
            var evaluation_method = $("#evaluation-method").code();
            var language = $("#language").code();
            var schedule = $("#schedule").code();
            var rooms = $("#rooms").code();
            new Model('school.course_documentation').call('write', [doc_id,{
                'content' : content,
                'method' : method,
                'learning_outcomes' : learning_outcomes,
                'competencies' : competencies,
                'evaluation_method' : evaluation_method,
                //'staff_ids' = fields.One2many("school.course_staff", 'doc_id', string='Staff')
                'language' : language,
                'schedule' : schedule,
                'rooms' : rooms
            }]).then(function(result){
                if(result){
                    Dialog.alert(self, _t("You changes are saved, they are to be reviewed before being published."), {
                        title: _t('Changes saved'),
                    });
                }
            })
        }
    });

});