odoo.define('account_ag_grid.widgets', function(require) {
"use strict";

var core = require('web.core');
var data = require('web.data');
var Dialog = require('web.Dialog');
var form_common = require('web.form_common');
var Widget = require('web.Widget');

var _t = core._t;
var QWeb = core.qweb;

var AgGrid = Widget.extend({
    // QWeb template to use when rendering the object
    template: "ag_grid",
    events: {
        // events binding example
        //'click .my-button': 'handle_click',
    },

    init: function(parent) {
        this._super(parent);
        // insert code to execute before rendering, for object
        // initialization
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
        
        window.agGridGlobalFunc(this.el, gridOptions);
    },
    
    start: function() {
        var sup = this._super();
        // post-rendering initialization code, at this point

    }
});

core.action_registry.add('account_move_line_aggrid_view', AgGrid);
/* This widget takes its parameters from the action context. They are :
     - statement_ids: list of bank statements to reconcile (if not passed, all unreconciled bank
            statement lines will be displayed)
     - notifications: list of {
            type: one of bootstrap alert types (success, info, warning, danger)
            message: the message to display,
            details: a dict containing 'name', 'model' and 'ids' used to call a window action
        }
*/

return {
    AgGrid: AgGrid
};

});