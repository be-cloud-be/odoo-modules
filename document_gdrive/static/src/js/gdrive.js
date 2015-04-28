openerp.document_gdrive = function(instance, m) {
    var _t = instance.web._t,
        QWeb = instance.web.qweb;

    instance.web.Sidebar.include({
        redraw: function() {
            var self = this;
            this._super.apply(this, arguments);
            self.$el.find('.oe_sidebar_add_attachment').after(QWeb.render('AddGDriveDocumentItem', {widget: self}))
            self.$el.find('.oe_sidebar_add_gdrive').on('click', function (e) {
                self.on_gdrive_doc();
            });
        },
        pickerCallback: function(data) {
        	var url = 'nothing';
            if (data[google.picker.Response.ACTION] == google.picker.Action.PICKED) {
              var doc = data[google.picker.Response.DOCUMENTS][0];
              url = doc[google.picker.Document.URL];
	            var self = this;
	            var model = new openerp.web.Model("ir.attachment.add_gdrive");
	            model.call('action_add_gdrive',["",url],{context: this.context}).then(function (result) {
	            	alert(url);
			    });
            }
        },
        on_gdrive_doc: function() {
        	if(!pickerApiLoaded || !oauthToken) {
          	  onApiLoad();
            }
        	var self = this;
            var view = self.getParent();
            var ids = ( view.fields_view.type != "form" )? view.groups.get_selection().ids : [ view.datarecord.id ];
            if (pickerApiLoaded && oauthToken) {
              var picker = new google.picker.PickerBuilder().
                  addView(google.picker.ViewId.DOCS).
                  setOAuthToken(oauthToken).
                  setCallback(this.pickerCallback).
                  build();
              picker.context = new openerp.web.CompoundContext(this.session.user_context, {
                      'active_ids': ids,
                      'active_id': [ids[0]],
                      'active_model': view.dataset.model,
                  });
              picker.setVisible(true);
            }
        },
    });

    instance.web.ActionManager = instance.web.ActionManager.extend({
        ir_actions_act_close_wizard_and_reload_view: function (action, options) {
            if (!this.dialog) {
                options.on_close();
            }
            this.dialog_stop();
            this.inner_widget.views[this.inner_widget.active_view].controller.reload();
            return $.when();
        },
    });

};
