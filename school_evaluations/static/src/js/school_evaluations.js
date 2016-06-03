odoo.define('school_evaluations.action_school_evaluations_main', function (require) {
"use strict";

var core = require('web.core');

var Widget = require('web.Widget');
var Dialog = require('web.Dialog');
var Model = require('web.DataModel');
var data = require('web.data');

var BlocEditor = require('school_evaluations.school_evaluations_bloc_editor');

var QWeb = core.qweb;
var _t = core._t;

var EvaluationConfigDialog = Dialog.extend({
    template: 'ConfigDialog',
    
    
});

var EvaluationsAction = Widget.extend({
    template: 'MainView',
    
    events: {
        "click .o_school_group_item": function (event) {
            event.preventDefault();
            var group_id = this.$(event.currentTarget).data('group-id');
            this.set_group(group_id);
        },
        "click .evaluation_config": function (event) {
            event.preventDefault();
            new EvaluationConfigDialog(this, {title : 'Evaluation Config'}).open();
        },
        "click .o_school_bloc_item": function (event) {
            event.preventDefault();
            this.$('.o_school_bloc_item.active').removeClass('active');
            this.$(event.currentTarget).addClass('active');
            var bloc_id = this.$(event.currentTarget).data('bloc-id');
            this.set_bloc(bloc_id);
        },
        "click .o_school_musique": function (event) {
            event.preventDefault();
            this.school_domain = 1;
            this.$('.o_school_theatre').removeClass('active');
            this.$(event.currentTarget).addClass('active');
            this.update_blocs();
        },
        "click .o_school_theatre": function (event) {
            event.preventDefault();
            this.school_domain = 2;
            this.$('.o_school_musique').removeClass('active');
            this.$(event.currentTarget).addClass('active');
            this.update_blocs();
        },
    },
    
    init: function(parent, title) {
        this._super.apply(this, arguments);
        this.title = title;
        this.context = new data.CompoundContext();
        this.school_domain = 1;
    },
    
    build_domain: function() {
        return new data.CompoundDomain([['source_bloc_domain_id','=',this.school_domain]]);
    },
    
    start: function() {
        var self = this;
        this.model = new Model('school.individual_bloc');

        this.update_blocs();

        this.evaluation_bloc_editor = new BlocEditor(this, {});
        this.evaluation_bloc_editor.appendTo(this.$('.o_evaluation_bloc_container'));
    
    },
    
    update_blocs: function() {
        var self = this;
        
        this.groups = [
            {   
                'id' : 0, 
                'title' : "Bloc 1",
                'blocs' : [],
            },
            { 
                'id' : 1, 
                'title' : "Bloc 2",
                'blocs' : [],
            },
            { 
                'id' : 2, 
                'title' : "Bloc 3",
                'blocs' : [],
            },
            
        ];
        var defs = [];
        for (var i=0, ii=3; i<ii; i++) {
            defs.push(this.model.query(['id','name','student_id','student_name','source_bloc_level','source_bloc_title','state']).context(this.context).order_by('student_name').filter(self.build_domain()).filter([['source_bloc_level', '=', i+1]]).all().then(
                function(data){
                    if(data.length > 0){
                        self.groups[data[0].source_bloc_level-1].blocs = data;
                    }
                }
            ));
        }
        $.when.apply($,defs).then(function(){
            self.render_sidebar();
        });  
    },
    
    render_sidebar: function () {
        var $sidebar = $(QWeb.render("SideBar", this));
        this.$(".sidebar").html($sidebar);
        this.$('.main_navbar').metisMenu();
    },
    
    set_group: function(group_id) {
        var self = this;
        if(this.groups[group_id]) {
            this.$(".sub_sidebar").hide();
            var $sidebar = $(QWeb.render("SubSideBar", this.groups[group_id]));
            this.$(".sub_sidebar").html($sidebar);
            this.$('.sub_navbar').metisMenu();
            
            var group = this.groups[group_id];
            var ids = [];
            for (var i=0, ii=group.blocs.length; i<ii; i++) {
                ids.push(group.blocs[i].id);
            }
            
            this.evaluation_bloc_editor.read_ids(ids).then(
                function(){
                    self.$(".sub_sidebar").show();
                } 
            );
            
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