odoo.define('school_evaluations.action_school_evaluations_main', function (require) {
"use strict";

var core = require('web.core');

var Widget = require('web.Widget');
var Dialog = require('web.Dialog');
var Model = require('web.DataModel');
var data = require('web.data');
var session = require('web.session');

var BlocEditor = require('school_evaluations.school_evaluations_bloc_editor');

var QWeb = core.qweb;
var _t = core._t;

var EvaluationConfigDialog = Dialog.extend({
    template: 'ConfigDialog',
    
    events: {
        'change .o_school_year_select': function (event) {
            event.preventDefault();
            self.parent.year_id = parseInt(this.$(event.currentTarget).find(":selected").attr('value'))
            self.parent.year_name = this.$(event.currentTarget).find(":selected").text();
        },
        "click .o_school_first_session": function (event) {
            event.preventDefault();
            this.parent.school_session = 1;
            this.$('.o_school_second_session').removeClass('active');
            this.$(event.currentTarget).addClass('active');
        },
        "click .o_school_second_session": function (event) {
            event.preventDefault();
            this.parent.school_session = 2;
            this.$('.o_school_first_session').removeClass('active');
            this.$(event.currentTarget).addClass('active');
        },
    },
    
    init: function(parent, title) {
        self = this;
        this._super.apply(this, arguments);
        self.parent = parent;
        self.school_session = parent.school_session;
    },
    
    start: function() {
        var self = this;
        var tmp = this._super.apply(this, arguments);
        var defs = [];
        self.$school_year_select = this.$('select.o_school_year_select');
        defs.push(new Model('school.year').query(['id','name']).all().then(
                        function(years) {
                            years.map(function(year){
                                var o = new Option(year.name,year.id);
                                if (year.id == self.parent.year_id) {
                                    $(o).attr('selected',true);
                                }
                                self.$school_year_select.append(o);
                            });
                        }
                    ));
        return $.when(tmp, defs);
    },
    
    close: function () {
        this._super();
        if(this.parent.school_session == 1) {
            this.parent.$('h2.o_school_deliberation_title').text("Délibération Première Session " + this.parent.year_name);
        } else {
            this.parent.$('h2.o_school_deliberation_title').text("Délibération Seconde Session " + this.parent.year_name);
        }
        this.parent.update_blocs();
    },
    
});

var EvaluationsAction = Widget.extend({
    template: 'MainView',
    
    events: {
        "click .o_school_group_item": function (event) {
            event.preventDefault();
            var self = this;
            this.$('.o_school_group_item.active').removeClass('active');
            this.$(event.currentTarget).addClass('active');
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
        this.school_session = new Date().getMonth() < 7 ? 1 : 2;
        this.parent = parent;
        this.parent.webclient.$el.find('#oe_main_menu_navbar').addClass('o_hidden');
    },
    
    start: function() {
        var self = this;
        return new Model("res.users").call("read", [session.uid, ['id','name','current_year_id']]).then(
                    function(user) {
                        self.user = user;
                        self.year_id = self.user.current_year_id[0];
                        self.year_name = self.user.current_year_id[1];
                        if(self.school_session == 1) {
                            self.$('h2.o_school_deliberation_title').text("Délibération Première Session " + self.year_name);
                        } else {
                            self.$('h2.o_school_deliberation_title').text("Délibération Seconde Session " + self.year_name);
                        }
                }).then(
                    function() {
                        self.model = new Model('school.individual_bloc');
                        self.update_blocs();
        
                        self.evaluation_bloc_editor = new BlocEditor(self, {});
                        self.evaluation_bloc_editor.appendTo(self.$('.o_evaluation_bloc_container'));
                });
    },

    build_domain: function() {
        var domain = new data.CompoundDomain([['exclude_from_deliberation','=',false],['source_bloc_domain_id','=',this.school_domain],['year_id','=',this.year_id]]);
        if(this.school_session == 1) {
            domain.add(['state','in',['progress','postponed','awarded_first_session']]);
        } else {
            domain.add(['state','in',['postponed','awarded_second_session','failed']]);
        }
        return domain;
    },
    
    update_blocs: function() {
        var self = this;
        
        this.groups = [
            {   
                'id' : 0, 
                'title' : "Bloc 1",
                'blocs' : [],
                'school_session' : this.school_session,
            },
            { 
                'id' : 1, 
                'title' : "Bloc 2",
                'blocs' : [],
                'school_session' : this.school_session,
            },
            { 
                'id' : 2, 
                'title' : "Bloc 3",
                'blocs' : [],
                'school_session' : this.school_session,
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