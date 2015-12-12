/*
 * Component View, display the Dashboard,
 * see MarionnetteJS documentation for more details:
 * http://marionettejs.com/docs/v2.4.3/marionette.compositeview.html
 */
odoo.unleashed.module('account_ag_grid', function(aag, require, _, Backbone, base){

    var MoveModel = aag.models('Move');

    var ItemView = Backbone.Marionette.ItemView,
        _super = ItemView.prototype;

    var DashboardView = ItemView.extend({
        
        template: 'AccountingDashboard.AgGrid',

        events: {
            //'click .remove-todo': 'removeTodo'
        },

        /* Keep a reference to the collection */
        initialize: function(options){
            _super.initialize.apply(this, options);

            var columnDefs = [
                {headerName: '', field: 'account', width: 450, cellRenderer: {renderer: 'group'}},
                {headerName: "Credit", field: "credit", width: 150, cellRenderer: this.currencyRenderer},
                {headerName: "Debit", field: "debit", width: 150, cellRenderer: this.currencyRenderer},
                {headerName: "Balance", field: "balance", width: 150, cellRenderer: this.currencyRenderer},
            ];
            
            var gridOptions = {
                columnDefs: columnDefs,
                datasource: this.collection,
                groupKeys: ['type','account'],
                groupDefaultExpanded: false,
                enableColResize: true,
                groupSuppressAutoColumn: true,
                icons: {
                    groupExpanded: '<i class="fa fa-minus-square-o"/>',
                    groupContracted: '<i class="fa fa-plus-square-o"/>'
                },
                groupAggFields: ['credit','tcredit','debit','tdebit','balance','tbalance'],
            };
                    
            this.gridOptions = gridOptions;
            this.trigger('ag_grid_view_loaded');
        },

        render: function(){
            window.agGridGlobalFunc(this.$el.get(0), this.gridOptions);
        },

        /**
         * when user click on delete button,
         * remove to-do model from collection
         * and refresh the view.
         **/
        /*removeTodo: function(e){
            e.preventDefault();
            var self = this;
            this.model.destroy().then(function() {
                // reload the collection, refresh the layout
                self.collection.load();
            })
        },*/

        /**
         * define data passed to the template
         */
        /*serializeData: function(){

            // make a call to super
            var data = _super.serializeData.apply(this, arguments);

            // change priority number into a label and a specific class name
            var priorities = [
                { label: 'high', cls: 'danger' },
                { label: 'medium', cls: 'warning' },
                { label: 'low', cls: 'success' }
            ];

            data.priority = $.isNumeric(data.priority)
                ? parseInt(data.priority)
                : data.priority;

            if(data.priority && data.priority >= 0 && priorities.length >= data.priority){
                data.priority = priorities[data.priority-1];
            }

            return data;
        }*/

    });

    aag.views('Dashboard', DashboardView);
});