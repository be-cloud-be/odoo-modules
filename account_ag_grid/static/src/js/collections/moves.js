/*
 * Collection of Accounting Moves
 */
odoo.unleashed.module('account_ag_grid', function(aag, require, _, Backbone, base){

    var Move = aag.models('Move');

    var PagerCollection = base.collections('Pager'),
        _super = PagerCollection.prototype;

    var Moves = PagerCollection.extend({

        // Odoo model name, allow auto-binding with JSON-RPC API
        model_name: 'account.move.line',

        model: Move,

        initialize: function(options){
            _super.initialize.apply(this, options);
            this.disable();
            this.limit = '';
        },

        getRows : function (params) {
            var rowData = [];
            this.models.forEach(function(model) {
                var line = model.attributes;
                rowData.push(
                    {
                        'type' : line.user_type_id[1],
                        'account' : line.account_id[1],
                        'credit' : line.credit,
                        'debit' : line.debit,
                        'balance' : line.balance,
                    }
                );
            });
            params.successCallback(rowData);
        },

    });

    aag.collections('Moves', Moves);
});