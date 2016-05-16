odoo.define('school_evaluations.action_school_evaluations_main', function (require) {
"use strict";

var core = require('web.core');

var Widget = require('web.Widget');
var Model = require('web.DataModel');

var QWeb = core.qweb;
var _t = core._t;
 
var EvaluationsAction = Widget.extend({
    template: 'MainView',
    
    init: function(parent, title) {
        this._super.apply(this, arguments);
        var self = this;
        this.title = title;
        
        this.programs = [];
        
        var Programs = new Model('school.program');
        
        Programs.call('get_data_for_evaluation_widget').then(function(data) {
            self.programs = data;
            self.render_sidebar();
        });
        
    },
    
    render_sidebar: function () {
        var $sidebar = $(QWeb.render("SideBar", {
            programs: this.programs,
        }));
        this.$(".sidebar").html($sidebar.contents());
        this.$('.sidebar').metisMenu();
    },
    
});
   
core.action_registry.add('school_evaluations.main', EvaluationsAction);

});