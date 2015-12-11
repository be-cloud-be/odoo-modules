odoo.define('web_ag_grid.AgGridView', function (require) {
"use strict";

var core = require('web.core');
var formats = require('web.formats');
var Model = require('web.Model');
var session = require('web.session');
var View = require('web.View');
var Pager = require('web.Pager');

var QWeb = core.qweb;

var _t = core._t;
var _lt = core._lt;

var AgGridView = View.extend({

    display_name: _lt('AgGrid'),
    view_type: "ag_grid",
    //searchview_hidden: true,
    icon: 'fa-th-list',
    className: "o_ag_grid_view",

    init: function (parent, dataset, view_id, options) {
        this._super(parent, dataset, view_id, options);
        // qweb setup
        this.qweb = new QWeb2.Engine();
        this.qweb.debug = session.debug;
        this.qweb.default_dict = _.clone(QWeb.default_dict);

        this.model = this.dataset.model;
        this.grouped = undefined;
        this.group_by_field = undefined;
        this.default_group_by = undefined;
    },

    view_loading: function(fvg) {
        this.$el.addClass(fvg.arch.attrs.class);
        this.fields_view = fvg;
        this.default_group_by = fvg.arch.attrs.default_group_by;

        this.fields_keys = _.keys(this.fields_view.fields);

        // add qweb templates
        for (var i=0, ii=this.fields_view.arch.children.length; i < ii; i++) {
            
        }
        
        var super_render = this._super;
        var self = this;
        
        var columnDefs = [
            {headerName: "Account", field: "account"},
            {headerName: "Credit", field: "credit"},
            {headerName: "Debit", field: "debit"},
            {headerName: "Balance", field: "balance"},
        ];
        
        var gridOptions = {
            columnDefs: columnDefs,
            datasource: this,
            groupKeys = ['account'],
        };
                
        this.gridOptions = gridOptions;
        this.trigger('ag_grid_view_loaded');
    },


    getRows: function(params) {
        
        var AccountLines = new Model('account.move.line');
        
        AccountLines.query(['account_id','debit','credit']).all().then(
            function (lines) {
                var rowData = [];
                lines.forEach(function(line) {
                    rowData.push(
                        {
                            'account' : line.account_id[1],
                            'credit' : line.credit,
                            'debit' : line.debit,
                            'balance' : line.debit-line.credit,
                        }
                    );
                });
            params.successCallback(rowData);
        });
    },


    render_pager: function($node, options) {
        var self = this;
        this.pager = new Pager(this, this.dataset.size(), 1, 1000, options);
        this.pager.appendTo($node);
        this.pager.on('pager_changed', this, function (state) {
            var limit_changed = (self.limit !== state.limit);

            self.limit = state.limit;
            self.load_records(state.current_min - 1)
                .then(function (data) {
                    self.data = data;

                    // Reset the scroll position to the top on page changed only
                    if (!limit_changed) {
                        self.scrollTop = 0;
                        self.trigger_up('scrollTo', {offset: 0});
                    }
                })
                .done(this.proxy('render'));
        });
        this.update_pager();
    },

    update_pager: function() {
        this.pager.do_hide();
    },

    do_search: function(domain, context, group_by) {
        this.search_domain = domain;
        this.search_context = context;
        this.group_by_field = group_by[0] || this.default_group_by;
        this.grouped = group_by.length || this.default_group_by;

        var field = this.fields_view.fields[this.group_by_field];
        
        this.render();
        this.render_pager();
    },

    render: function() {
        console.log("render_pager");
        this.$el.empty();
        window.agGridGlobalFunc(this.$el.get(0), this.gridOptions);
    },
    
});

core.view_registry.add('ag_grid', AgGridView);

return AgGridView;

});