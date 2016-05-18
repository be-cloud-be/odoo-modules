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
    
        
    },
    
    init: function(parent, title) {
        this._super.apply(this, arguments);
        this.title = title;
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
                self.bloc = data;
                self.renderElement();
            }
        );
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