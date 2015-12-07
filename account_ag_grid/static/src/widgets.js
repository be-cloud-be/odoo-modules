odoo.define('web_calendar.widgets', function(require) {
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
    template: "AgGrid",
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
        
        window.agGridGlobalFunc(this, gridOptions);
    },
    
    start: function() {
        var sup = this._super();
        // post-rendering initialization code, at this point

    }
});

return {
    AgGrid: AgGrid
};

});