frappe.listview_settings['User Management'] = {
    onload: function(listview) {
		listview.page.add_inner_button("Sync Users", () => {

			frappe.call({
				method: 'user_management.user_manangement.doctype.user_management.user_management.user_to_user',
				args: {},
				callback: function(response) {
					if (response.message) {

                        frappe.msgprint(response.message.status);
                        console.log("refreshed from core user")
                        // frappe.ui.toolbar.clear_cache();
                        window.location.reload();
						
					} else {
						frappe.msgprint("Error after callback");
					}
				},
				error: function(error) {
					console.error('Error fetching data from backend:', error);
				}
			});
			
		});
		
	}
};