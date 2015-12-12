/*
 * Collection of Accounting Moves
 */
odoo.unleashed.module('account_ag_grid', function(aag, require, _, Backbone, base){

    var Move = aag.models('Move');

    var BaseCollection = base.collections('BaseCollection'),
        _super = BaseCollection.prototype;

    var Moves = BaseCollection.extend({

        // Odoo model name, allow auto-binding with JSON-RPC API
        model_name: 'account.move.line',

        model: Move,

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