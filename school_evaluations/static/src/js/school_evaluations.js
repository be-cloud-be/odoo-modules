odoo.define('school_evaluations.action_school_evaluations_main', function (require) {
"use strict";

var core = require('web.core');

var Widget = require('web.Widget');
var Model = require('web.DataModel');

var BlocEditor = require('school_evaluations.school_evaluations_bloc_editor');

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
        "click .o_school_bloc_item": function (event) {
            event.preventDefault();
            this.$('.o_school_bloc_item.active').removeClass('active');
            this.$(event.currentTarget).addClass('active');
            var bloc_id = this.$(event.currentTarget).data('bloc-id');
            this.set_bloc(bloc_id);
        },
    },
    
    init: function(parent, title) {
        this._super.apply(this, arguments);
        this.title = title;
    },
    
    start: function() {
        var self = this;
        
        var IndividualBloc = new Model('school.individual_bloc');
        
        IndividualBloc.call('get_data_for_evaluation_widget').then(function(data) {
            self.$el.extend( true, self, data )
            self.render_sidebar();
        });
        
        this.evaluation_bloc_editor = new BlocEditor(this, {});
        
        this.evaluation_bloc_editor.appendTo(this.$('.o_evaluation_bloc_container'));
        
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
            
            var group = this.groups[group_id];
            var ids = [];
            for (var i=0, ii=group.blocs.length; i<ii; i++) {
                ids.push(group.blocs[i].id);
            }
            
            this.evaluation_bloc_editor.read_ids(ids);
            
        } else {
            this.$(".sub_sidebar").empty();
        }
    },
    
    set_bloc: function(bloc_id) {
        this.evaluation_bloc_editor.set_bloc_id(bloc_id);
    },
    
});
   
core.action_registry.add('school_evaluations.main', EvaluationsAction);

});