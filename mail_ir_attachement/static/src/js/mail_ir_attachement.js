//////////////////////////////////////////////////////////////////////////////
//    OpenERP, Open Source Management Solution    
//    Copyright (c) 2010-2012 Elico Corp. All Rights Reserved.
//
//    Author: Jerome Sonnet <jerome.sonnet@be-cloud.be>
//
//    This program is free software: you can redistribute it and/or modify
//    it under the terms of the GNU General Public License as published by
//    the Free Software Foundation, either version 3 of the License, or
//    (at your option) any later version.
//
//    This program is distributed in the hope that it will be useful,
//    but WITHOUT ANY WARRANTY; without even the implied warranty of
//    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//    GNU General Public License for more details.
//
//    You should have received a copy of the GNU General Public License
//    along with this program.  If not, see <http://www.gnu.org/licenses/>.
//
/////////////////////////////////////////////////////////////////////////////:

odoo.define('mail_ir_attachement.composer', function (require) {
	"use strict";
	
	var core = require('web.core');
	var Widget = require('web.Widget');
	var Model = require('web.Model');
	
	var _t = core._t;
	var QWeb = core.qweb;
	
	var composer = require('mail.composer');

	composer.BasicComposer.include({

		events: _.defaults({
	        'click .o_composer_button_add_ir_attachment': 'on_add_ir_attachment',
	    }, composer.BasicComposer.prototype.events),

		start: function () {
			this.$('.o_composer_buttons').append('<button tabindex="6" class="btn btn-sm btn-icon fa fa-file-text o_composer_button_add_ir_attachment" type="button"/>')
			return this._super();
		},
		
	});
});