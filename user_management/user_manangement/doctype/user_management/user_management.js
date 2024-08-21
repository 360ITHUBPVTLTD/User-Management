// Copyright (c) 2024, Pankaj and contributors
// For license information, please see license.txt

frappe.ui.form.on("User Management", {
	refresh(frm) {
        frm.fields_dict['role'].get_query = function(doc) {
            return {
                filters: {
                    "custom_custom_role": 1
                }
            };
        };
	},
});
