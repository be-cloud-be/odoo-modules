odoo.define('school_evaluations.school_evaluations_bloc_editor', function (require) {
"use strict";

var config = require('web.config');
var core = require('web.core');
var data = require('web.data');
var session = require('web.session');

var Widget = require('web.Widget');
var Model = require('web.DataModel');

var QWeb = core.qweb;
var _t = core._t;

return Widget.extend({
    template: "BlocEditor",
    events: {
        "click .bloc_confirm": function (event) {
            event.preventDefault();
            var self = this;
            new Model(self.dataset.model).call("confirm",[self.datarecord.id,self.dataset.get_context()]).then(function(result) {
                self.next().then(function(){
                    self.parent.$('.o_school_bloc_item.active').removeClass('active');
                    self.parent.$("a[data-bloc-id='" + self.datarecord.id + "']").addClass('active');
                });
            });
        },
        
    },
    
    init: function(parent, title) {
        this._super.apply(this, arguments);
        this.title = title;
        this.parent = parent;
    },
    
    start: function() {
        this.dataset = new data.DataSet(this, 'school.individual_bloc', {});
        this.bloc = false;
    },
    
    read_ids: function(ids) {
        return this.dataset.read_slice(false,[['id', 'in', ids]]);
    },
    
    set_bloc_id: function(bloc_id) {
        var self = this;
        this.bloc_id = bloc_id;
        this.dataset.select_id(bloc_id)
        this.dataset.read_index().then(
            function(data){
                self.datarecord = data;
                self.bloc = data;
                self._read_bloc_data().done(
                    function(){
                        self.renderElement();
                    }  
                );
            }
        );
    },
    
    next: function() {
        var self = this;
        this.dataset.next();
        return this.dataset.read_index().then(
            function(data){
                self.datarecord = data;
                self.bloc = data;
                self._read_bloc_data().done(
                    function(){
                        self.renderElement();
                    }  
                );
            }
        );
    },
    
    _read_bloc_data: function(bloc){
        var self = this;
        var all_data_loaded = $.Deferred();
        
        var model_res_partner = new Model('res.partner');
        var model_individual_course_group = new Model('school.individual_course_group');
        var model_individual_course = new Model('school.individual_course');
        
        $.when(
            model_res_partner.query().filter([['id', '=', self.bloc.student_id[0]]]).all().then(
                function(student) {
                    self.student = student[0];
                    self.student_image = session.url('/web/image', {
                                                        model: 'res.partner',
                                                        id: self.student.id,
                                                        field: 'image',
                                                        unique: (self.datarecord.__last_update || '').replace(/[^0-9]/g, '')
                    });
                }    
            ),
            model_individual_course_group.query().filter([['id', 'in', self.bloc.course_group_ids]]).all().then(
                function(course_groups) {
                    self.course_groups = course_groups;
                    var defereds = [];
                    for (var i=0, ii=course_groups.length; i<ii; i++) {
                        var course_group = course_groups[i];
                        // TODO Load course details
                    }
                }
            )
        ).then(function(){all_data_loaded.resolve();});
        
        return all_data_loaded.promise();
    },
    
    
    /*render_form: function() {
        var self = this;
        self.dataset.read_index().then(
            function(data){
                var $form = $(QWeb.render("BlocForm", data));
                this.$(".o_school_evaluation_bloc_form").html($form);
                
                var model_individual_bloc = new Model('school.individual_bloc');
                self.view_form = model_individual_bloc.fields_view_get({
                    view_id : [],
                    view_type : 'form',
                    context : session.context,
                }).then(
                    function( view_form ){
                        var FormView = core.view_registry.get('form');
                        self.view_form = new FormView(self, self.dataset, view_form.id || false, {"initial_mode": "edit"});
                        self.view_form.load_record(data);
                        self.view_form.to_edit_mode();
                        
                        self.do_hide();
                        self.$('.o_school_evaluation_bloc_form').empty();
                        self.view_form.appendTo(self.$('.o_school_evaluation_bloc_form'));
                        self.view_form.on("form_view_loaded", self, function() {
                            self.view_form.do_show().then(function() {
                                self.do_show();
                        });
                        });
                    });
            }
        );
    },*/
    
});
});