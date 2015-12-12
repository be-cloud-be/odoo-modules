/*
 * Module initialization, ready function is called when OpenERP framework is ready
 */
odoo.unleashed.module('account_ag_grid', function(aag, require, _, Backbone, base) {

    // make a reference to view registry
    var core = require('web.core');
    var UnleashedView = base.views('Unleashed');

    /**
     * object instantiated by OpenERP when the "todo" view is called
     */
    var AAGView = UnleashedView.extend({

        template: "AccountingDashboard",
        view_type: "account_ag_grid",
        display_name: "Accounting Dashboard",
        icon: "fa fa-tasks",
        accesskey: "D",

        /**
         * executed when the View is started
         */
        start: function(){

            var PagerView = base.views('Pager'),
                DashboardView = account_ag_grid.views('Dashboard'),
                MovesCollection = account_ag_grid.collections('Moves');

            // create MVC components
            this.collection = new MovesCollection();
            this.view = new DashboardView({
                collection: this.collection
            });
            this.pager = new PagerView({
                collection: this.collection
            });

            return this._super();
        },

        /**
         * apply search from OpenERP search widget
         **/
        do_search: function(domain, context, groupby){

            var self = this;

            var loaded = this.collection.load({
                filter: domain, context: context, persistent: true
            });

            loaded.then(function(){

                // show the main view & pager view
                self.panel.body.show(self.view);
                self.panel.pager.show(self.pager);

                // update application state
                self.state.trigger("change");
            });
        },
    });

     // standard way to add a view in Odoo
    core.view_registry.add('account_ag_grid', AAGView);
});