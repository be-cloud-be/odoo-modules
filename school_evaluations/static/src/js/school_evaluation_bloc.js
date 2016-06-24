odoo.define('school_evaluations.school_evaluations_bloc_editor', function (require) {
"use strict";

var config = require('web.config');
var form_common = require('web.form_common');
var core = require('web.core');
var data = require('web.data');
var session = require('web.session');

var Widget = require('web.Widget');
var Model = require('web.DataModel');
var Dialog = require('web.Dialog');

var QWeb = core.qweb;
var _t = core._t;

var DetailEvalDialog = Dialog.extend({
    template: 'DetailEvalDialog',
    
    events: {
        'change #grade-list': 'changeGrade',
        'change #grade-comment-list': 'changeGradeComment',
    },
    
    init: function(parent, options) {
        this._super.apply(this, arguments);
        this.title = options.title;
        this.program = options.program;
        this.parent = parent;
        this.messages = [
            '',
            'Pertinence et singularité du travail artistique',
            'Qualité particulière du travail artistique',
            'Participation active et régulière aux activités d’enseignement',
            'Caractère accidentel des échecs',
            'Echecs limités en qualité et quantité',
            'Pourcentage global et importance relative des échecs',
            'Progrès réalisés d’une session à l’autre',
            'La réussite des activités de remédiation'
        ];
    },
    
    changeGrade: function() {
        var self = this;
        var grade = this.$('#grade-list').val()
        new Model('school.individual_program').call('write', [self.program.id,{'grade':grade}]).then(function(result){
            self.program.grade = grade;
        })
    },
    
    changeGradeComment: function() {
        var self = this;
        var mess_idx = parseInt(this.$('#grade-comment-list').val());
        var message = this.messages[mess_idx];
        new Model('school.individual_program').call('write', [self.program.id,{'grade_comments':message}]).then(function(result){
            self.program.grade_comments = message;
        })
    },
    
});

var DetailResultDialog = Dialog.extend({
    template: 'DetailResultDialog',
    
    init: function(parent, options) {
        this._super.apply(this, arguments);
        this.title = options.title;
        this.course_group = options.course_group;
        this.parent = parent;
    },
    
});

return Widget.extend({
    template: "BlocEditor",
    events: {
        "click .bloc_award": function (event) {
            event.preventDefault();
            var self = this;
            new Model(self.dataset.model).call("set_to_awarded",[self.datarecord.id,self.dataset.get_context()]).then(function(result) {
                self.parent.$(".o_school_bloc_item.active i").removeClass('fa-user');
                self.parent.$(".o_school_bloc_item.active i").addClass('fa-check');
                self.bloc.state = "awarded";
                self.next().then(function(){
                    self.parent.$('.o_school_bloc_item.active').removeClass('active');
                    self.parent.$("a[data-bloc-id='" + self.datarecord.id + "']").addClass('active');
                });
            });
        },

        "click .bloc_postpone": function (event) {
            event.preventDefault();
            var self = this;
            new Model(self.dataset.model).call("set_to_postponed",[self.datarecord.id,self.dataset.get_context()]).then(function(result) {
                self.parent.$(".o_school_bloc_item.active i").removeClass('fa-user');
                self.parent.$(".o_school_bloc_item.active i").addClass('fa-check');
                self.bloc.state = "postponed";
                self.next().then(function(){
                    self.parent.$('.o_school_bloc_item.active').removeClass('active');
                    self.parent.$("a[data-bloc-id='" + self.datarecord.id + "']").addClass('active');
                });
            });
        },

        "click .bloc_failed": function (event) {
            event.preventDefault();
            var self = this;
            new Model(self.dataset.model).call("set_to_failed",[self.datarecord.id,self.dataset.get_context()]).then(function(result) {
                self.parent.$(".o_school_bloc_item.active i").removeClass('fa-user');
                self.parent.$(".o_school_bloc_item.active i").addClass('fa-check');
                self.bloc.state = "failed";
                self.next().then(function(){
                    self.parent.$('.o_school_bloc_item.active').removeClass('active');
                    self.parent.$("a[data-bloc-id='" + self.datarecord.id + "']").addClass('active');
                });
            });
        },
        
        "click .o_school_eval_details": function (event) {
            var self = this;
            event.preventDefault();
            new DetailEvalDialog(this, {title : _t('Detailed Evaluation'), program : self.program}).open();
        },
        
        "click .o_school_edit_icg": function (event) {
            var self = this;
            event.preventDefault();
            var id = this.$(event.currentTarget).data('cg-id');
            var res_id = parseInt(id).toString() == id ? parseInt(id) : id;
            new DetailResultDialog(this, {title : _t('Detailed Results'), course_group : self.course_groups[self.course_group_id_map[res_id]]}).open();
            /*var dialog = new form_common.FormViewDialog(this, {
                res_model: 'school.individual_course_group',
                res_id: parseInt(id).toString() == id ? parseInt(id) : id,
                context: this.dataset.get_context(),
                title: _t("Edit Course Group"),
                view_id: false,
                readonly: true,
                buttons: [
                    {text: _t("Edit"), classes: 'btn-primary oe_school_edit_cgi_button', close: false, click: function() {
                        this.view_form.to_edit_mode();
                        dialog.$footer.children('.oe_school_edit_cgi_button').hide();
                        dialog.$footer.children('.oe_school_save_cgi_button').show();
                    }},
                    {text: _t("Save"), classes: 'btn-primary oe_school_save_cgi_button', close: true, click: function() {
                        this.view_form.save()
                    }},
                    {text: _t("Close"), close: true}
                ]
            }).open();
            dialog.$footer.children('.oe_school_save_cgi_button').hide(); //TODO how to hide a button ??
            dialog.on('closed', self, function () {
                self.update();
            });*/
        },
        
    },
    
    init: function(parent, title) {
        this._super.apply(this, arguments);
        this.title = title;
        this.parent = parent;
    },
    
    start: function() {
        this.dataset = new data.DataSet(this, 'school.individual_bloc', new data.CompoundContext());
        this.bloc = false;
    },
    
    read_ids: function(ids) {
        var self = this;
        return this.dataset.read_ids(ids,[]).then(function (results) {
                self.records = results;
                self.record_idx = 0;
                self.datarecord = self.records[self.record_idx];
            });
    },
    
    set_bloc_id: function(bloc_id) {
        var self = this;
        this.bloc_id = bloc_id;
        for (var i=0, ii=self.records.length; i<ii; i++) {
            if(this.records[i].id == bloc_id){
                this.record_idx = i;
                this.datarecord = this.records[this.record_idx];
                return self.update();
            }
        }
    },
    
    next: function() {
        var self = this;
        if(this.record_idx < this.records.length-2){
            this.record_idx += 1;
            this.datarecord = this.records[this.record_idx];
            return self.update();
        }
    },
    
    update: function() {
        var self = this;
        self.bloc = this.datarecord;
        return self._read_bloc_data().done(
            function(){
                self.renderElement();
            }  
        );
    },
    
    _update_evaluation_messages: function() {
        var self = this;
        switch(self.bloc.source_bloc_level) {
            case "1" :
                if(self.bloc.total_acquiered_credits >= 60) {
                    self.bloc_result = {
                        'message' : _t("60 crédits ECTS acquis ou valorisés, autorisé(e) à poursuivre son parcours sans restriction."),
                        'class' : "success",
                        'button_text' : _t("Réussite"),
                        'next_action' : "award",
                    };
                }
                /*else if(self.bloc.total_acquiered_credits >= 45) {
                    self.bloc_result = {
                        'message' : _t("Au moins 45 crédits ECTS acquis ou valorisés, autorisé(e) à poursuivre son parcours tout en finalisant ses crédits résiduels."),
                        'class' : "warning",
                        'button_text' : _t("Réussite"),
                        'next_action' : "postpone",
                    };
                } 
                else if(self.bloc.total_acquiered_credits >= 30) {
                    self.bloc_result = {
                        'message' : _t("Au moins 30 crédits ECTS acquis ou valorisés, impossibilité de poursuivre son parcours mais autorisé à compléter, avec l'accord du jury, son programme annuel."),
                        'class' : "warning",
                        'button_text' : _t("Ajourné"),
                        'next_action' : "postpone",
                    };
                } 
                else {
                    self.bloc_result = {
                        'message' : _t("Moins de 30 crédits ECTS acquis ou valorisés, impossibilité de poursuivre son parcours et pas de possibilité de compléter son programme annuel."),
                        'class' : "danger",
                        'button_text' : _t("Ajourné"),
                        'next_action' : "postpone",
                    };
                }*/
                else {
                    self.bloc_result = {
                        'message' : _t("Moins de 60 crédits ECTS acquis ou valorisés, les crédits non-acquis sont à présenter en seconde session."),
                        'class' : "danger",
                        'button_text' : _t("Ajourné"),
                        'next_action' : "postpone",
                    };
                }
                break;
            case "2" :
                if(self.bloc.total_acquiered_credits >= 60) {
                    self.bloc_result = {
                        'message' : _t("60 crédits ECTS acquis ou valorisés, autorisé(e) à poursuivre son parcours sans restriction."),
                        'class' : "success",
                        'button_text' : _t("Réussite"),
                        'next_action' : "award",
                    };
                }
                else {
                    self.bloc_result = {
                        'message' : _t("Moins de 60 crédits ECTS acquis ou valorisés, les crédits non-acquis sont à présenter en seconde session."),
                        'class' : "danger",
                        'button_text' : _t("Ajourné"),
                        'next_action' : "postpone",
                    };
                }
                break;
            case "3" :
                if(self.bloc.total_acquiered_credits >= 60) {
                    self.bloc_result = {
                        'message' : _t("180 crédits ECTS acquis ou valorisés, le jury confère le grade académique de Bachelier avec "),
                        'class' : "success",
                        'button_text' : _t("Réussite"),
                        'next_action' : "award",
                    };
                    if(self.program.evaluation >= 18){
                        self.bloc_result.grade_text = _t("First Class Honor");
                        self.bloc_result.grade = 'first_class';
                    } else if (self.program.evaluation >= 16){
                        self.bloc_result.grade_text = _t("Second Class Honor");
                        self.bloc_result.grade = 'second_class';
                    } else if (self.program.evaluation >= 14){
                        self.bloc_result.grade_text = _t("Distinction");
                        self.bloc_result.grade = 'distinction';
                    } else if (self.program.evaluation >= 12){
                        self.bloc_result.grade_text = _t("Satisfaction");
                        self.bloc_result.grade = 'satisfaction';
                    } else {
                        self.bloc_result.grade_text = _t("Without Grade");
                        self.bloc_result.grade = 'without';
                    };
                }
                /*
                else if(self.bloc.total_acquiered_credits >= 45) {
                    self.bloc_result = {
                        'message' : _t("Au moins 165 crédits ECTS acquis ou valorisés, autorisation d'accéder au programme de Master tout en finalisant ses crédits résiduels."),
                        'class' : "warning",
                        'button_text' : _t("Ajourné"),
                        'next_action' : "postpone",
                    };
                } 
                else {
                    self.bloc_result = {
                        'message' : _t("Moins de 165 crédits ECTS acquis ou valorisés, pas de possibilité d'accéder au programme de Master."),
                        'class' : "danger",
                        'button_text' : _t("Ajourné"),
                        'next_action' : "postpone",
                    };
                }*/
                else {
                    self.bloc_result = {
                        'message' : _t("Moins de 60 crédits ECTS acquis ou valorisés, les crédits non-acquis sont à présenter en seconde session."),
                        'class' : "danger",
                        'button_text' : _t("Ajourné"),
                        'next_action' : "postpone",
                    };
                }
                break;
        }
    },
    
    _read_bloc_data: function(){
        var self = this;
        
        self.student_image = session.url('/web/image', {
            model: 'res.partner',
            id: self.bloc.student_id[0],
            field: 'image_medium',
            unique: (self.datarecord.__last_update || '').replace(/[^0-9]/g, '')
        });
        
        return new Model('school.individual_course_group').query(['id','name','title','course_ids','acquiered','first_session_computed_result','final_result','total_credits','total_weight','first_session_deliberated_result_bool']).filter([['id', 'in', self.bloc.course_group_ids]]).all().then(
            function(course_groups) {
                self.course_groups = course_groups;
                var all_course_ids = [];
                self.course_group_id_map = {}
                for (var i=0, ii=self.course_groups.length; i<ii; i++) {
                    all_course_ids = all_course_ids.concat(self.course_groups[i].course_ids);
                    self.course_group_id_map[self.course_groups[i].id] = i;
                    self.course_groups[i].courses = [];
                }
                
                return new Model('school.individual_course').query().filter([['id', 'in', all_course_ids]]).all().then(
                    function(courses) {
                        for (var i=0, ii=courses.length; i<ii; i++) {
                            var course = courses[i];
                            self.course_groups[self.course_group_id_map[course.course_group_id[0]]].courses.push(course);
                        }
                });
            }
        ).done(
                new Model('school.individual_program').query().filter([['id','=',self.bloc.program_id[0]]]).all().then(
                function(program) {
                    if (program) {
                        self.program = program[0];
                        switch (self.program.grade) {
                          case "without":
                            self.program.grade_text = "Sans grade";
                            break;
                          case "satisfaction":
                            self.program.grade_text = "Satisfaction";
                            break;
                          case "distinction":
                            self.program.grade_text = "Distinction";
                            break;
                          case "second_class":
                            self.program.grade_text = "la Grande Distinction";
                            break;
                          case "first_class":
                            self.program.grade_text = "la Plus Grande Distinction";
                            break;
                        };
                        new Model('school.individual_program').call('compute_evaluation_details', [self.program.id]).then(function(results){
                            self.program.evaluation_details = results;
                        })
                    }
                    self._update_evaluation_messages();
                }
            )
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