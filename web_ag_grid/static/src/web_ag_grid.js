odoo.define('web_ag_grid.AgGridView', function (require) {
"use strict";

var core = require('web.core');
var formats = require('web.formats');
var Model = require('web.Model');
var session = require('web.session');
var KanbanView = require('web_kanban.KanbanView');

var QWeb = core.qweb;

var _t = core._t;
var _lt = core._lt;

var AgGridView = KanbanView.extend({

    display_name: _lt('AgGrid'),
    view_type: "ag_grid",
    searchview_hidden: true,
    icon: 'fa-th-list',

    render: function() {
        var super_render = this._super;
        var self = this;

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


        super_render.call(self);
        window.agGridGlobalFunc(this.$el.empty().get(0), gridOptions);
    },
    
});

core.view_registry.add('ag_grid', AgGridView);

return AgGridView;

});