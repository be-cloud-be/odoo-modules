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
              	name = doc[google.picker.Document.NAME];
              	url = doc[google.picker.Document.EMBEDDABLE_URL] || doc[google.picker.Document.URL];
	            var self = this;
	            var model = new openerp.web.Model("ir.attachment.add_gdrive");
	            model.call('action_add_gdrive',[name,url],{context: this.context}).then(function (result) {
	            	if(self.view.ViewManager.views[self.view.ViewManager.active_view]){
	            	    self.view.ViewManager.views[self.view.ViewManager.active_view]).controller.reload();
	            	} else {
	            	    self.view.ViewManager.active_view.controller.reload();
	            	} // TODO Check why this API changed in saas-6 ??
			    });
            }
        },
        on_gdrive_doc: function() {
        	if(!pickerApiLoaded) {ypo // || !oauthToken) {
          	  onApiLoad();
            }
        	var self = this;
            var view = self.getParent();
            var ids = ( view.fields_view.type != "form" )? view.groups.get_selection().ids : [ view.datarecord.id ];
            if (pickerApiLoaded) { // && oauthToken) {
              var picker = new google.picker.PickerBuilder().
                  addView(google.picker.ViewId.RECENTLY_PICKED).
              	  addView(google.picker.ViewId.DOCS).
              	  addView(new google.picker.DocsUploadView().setParent('0B-bLy40Prl36fkRpLTJELXUydU0ybkU0MVZQZ3kybXVqSzJDYVg4T2paeEwwR25RMWM0RTQ')). //TODO set as a parameter
                  setOAuthToken(oauthToken).
                  setLocale('fr').
                  setCallback(this.pickerCallback).
                  build();
              picker.context = new openerp.web.CompoundContext(this.session.user_context, {
                      'active_ids': ids,
                      'active_id': [ids[0]],
                      'active_model': view.dataset.model,
                  });
              picker.view = view;
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
