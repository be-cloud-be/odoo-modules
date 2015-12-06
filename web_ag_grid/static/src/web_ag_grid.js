odoo.define('web_ag_grid.AgGridView', function (require) {
"use strict";
/*---------------------------------------------------------
 * OpenERP web_ag_grid
 *---------------------------------------------------------*/

var core = require('web.core');
var data = require('web.data');
var form_common = require('web.form_common');
var Model = require('web.DataModel');
var time = require('web.time');
var View = require('web.View');

var CompoundDomain = data.CompoundDomain;

var _t = core._t;
var _lt = core._lt;
var QWeb = core.qweb;

var AgGridView = View.extend({
    template: "AgGridView",
    display_name: _lt('AgGrid'),
    view_type: "ag_grid",
    searchview_hidden: true,
    icon: 'fa-th-list',
    
    init: function (parent, dataset, view_id, options) {
        this._super(parent);
        this.ready = $.Deferred();
        this.set_default_options(options);
        this.dataset = dataset;
        this.model = dataset.model;
        this.fields_view = {};
        this.view_id = view_id;
        this.view_type = 'ag-grid';
        this.color_map = {};
        this.range_start = null;
        this.range_stop = null;
        this.selected_filters = [];

        this.title = (this.options.action)? this.options.action.name : '';

        this.shown = $.Deferred();
    },

    view_loading: function (fv) {
        
        var columnDefs = [
            {headerName: "Make", field: "make"},
            {headerName: "Model", field: "model"},
            {headerName: "Price", field: "price"}
        ];
        
        var rowData = [
            {make: "Toyota", model: "Celica", price: 35000},
            {make: "Ford", model: "Mondeo", price: 32000},
            {make: "Porsche", model: "Boxter", price: 72000}
        ];
        
        var gridOptions = {
            columnDefs: columnDefs,
            rowData: rowData
        };

        this.$ag-grid = this.$(".o_ag_grid_widget");
        window.agGridGlobalFunc(this.$ag-grid, gridOptions);
    },
    
});

core.view_registry.add('ag_grid', AgGridView);

return AgGridView;

});