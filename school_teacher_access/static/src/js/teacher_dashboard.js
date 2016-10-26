odoo.define('school_teacher_access.school_teacher_dashboard', function (require) {
"use strict";

var core = require('web.core');
var formats = require('web.formats');
var Model = require('web.Model');
var session = require('web.session');
var KanbanView = require('web_kanban.KanbanView');

var QWeb = core.qweb;

var _t = core._t;
var _lt = core._lt;

var SchoolTeacherDashboardView = KanbanView.extend({
    display_name: _lt('Dashboard'),
    icon: 'fa-dashboard',
    view_type: "school_teacher_dashboard",
    searchview_hidden: true,

    fetch_data: function() {
        var self = this;
        return new Model("res.partner").query().filter([["user_ids", "=",session.uid]]).all()
    },
	
    render: function() {
        var super_render = this._super;
        var self = this;

        return this.fetch_data().then(function(result){
            
            var teacher_dashboard = QWeb.render('school_teacher_access.TeacherDashboard', {
                widget: self,
                teacher: result[0],
            });
            
            super_render.call(self);
            $(teacher_dashboard).prependTo(self.$el);
        });
    },

});

core.view_registry.add('school_teacher_dashboard', SchoolTeacherDashboardView);

return SchoolTeacherDashboardView

});