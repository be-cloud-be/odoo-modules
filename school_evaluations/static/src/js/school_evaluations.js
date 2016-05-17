odoo.define('school_evaluations.action_school_evaluations_main', function (require) {
"use strict";

var core = require('web.core');

var Widget = require('web.Widget');
var Model = require('web.DataModel');

var QWeb = core.qweb;
var _t = core._t;
 
var EvaluationsAction = Widget.extend({
    template: 'MainView',
    
    events: {
        "click .o_school_group_item": function (event) {
            event.preventDefault();
            var group_id = this.$(event.currentTarget).data('group-id');
            this.set_group(group_id);
        },
    },
    
    init: function(parent, title) {
        this._super.apply(this, arguments);
        var self = this;
        this.title = title;

        var IndividualBloc = new Model('school.individual_bloc');
        
        IndividualBloc.call('get_data_for_evaluation_widget').then(function(data) {
            self.$el.extend( true, self, data )
            self.render_sidebar();
        });
        
    },
    
    render_sidebar: function () {
        var $sidebar = $(QWeb.render("SideBar", this));
        this.$(".sidebar").html($sidebar);
        this.$('.main_navbar').metisMenu();
    },
    
    set_group: function(group_id) {
        if(this.groups[group_id]) {
            var $sidebar = $(QWeb.render("SubSideBar", this.groups[group_id]));
            this.$(".sub_sidebar").html($sidebar);
            this.$('.sub_navbar').metisMenu();
        } else {
            this.$(".sub_sidebar").empty();
        }
    },
    
});
   
core.action_registry.add('school_evaluations.main', EvaluationsAction);

});