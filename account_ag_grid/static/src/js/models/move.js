/*
 * Model for an Accounting Move
 */
odoo.unleashed.module('account_ag_grid', function(aag, require, _, Backbone, base){
    
    var BaseModel = base.models('BaseModel'),
        _super = BaseModel.prototype;
    
    var Move = BaseModel.extend({
        // OpenERP model name, allow auto-binding with JSON-RPC API
        model_name: 'account.move.line'
    });

    aag.models('Move', Move);
});