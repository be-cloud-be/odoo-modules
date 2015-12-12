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
        },

        getRows : function (params) {
            var AccountLines = new Model('account.move.line');
        
            AccountLines.query(['user_type_id','account_id','debit','credit']).all().then(
                function (lines) {
                    var rowData = [];
                    lines.forEach(function(line) {
                        rowData.push(
                            {
                                'type' : line.user_type_id[1],
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

    });

    aag.collections('Moves', Moves);
});