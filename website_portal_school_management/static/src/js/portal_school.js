odoo.define('school_evaluations.action_school_portal_main', function (require) {
    
    "use strict";

    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var Model = require('web.Model');
    var session = require('web.session');
    var Widget = require('web.Widget');
    
    var _t = core._t;
    var QWeb = core.qweb;
    
    $(document).ready(function () {
        session.rpc("/web/session/get_session_info", {}).then(function(result) {
            var Users = new Model('res.users');
            Users.call('has_group', ['school_management.group_teacher']).then(function(has_group){
                if(has_group){
                    $("#oe_main_menu_navbar").remove();
                }
            })
        }); 
    });
});