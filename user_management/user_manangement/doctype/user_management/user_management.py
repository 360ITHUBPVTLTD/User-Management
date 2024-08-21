# Copyright (c) 2024, Pankaj and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class UserManagement(Document):
	def on_submit(self):
		existing_core_user = frappe.get_all("User", filters={"email": self.email})
		role_profile_names = [role_profile.role_profile for role_profile in self.role]

		if not existing_core_user:
			# Create a new core user if it doesn't exist
			core_user = frappe.get_doc({
				"doctype": "User",
				"email": self.email,
				# "full_name": self.full_name,
				"first_name": self.first_name,
				"last_name": self.last_name,
				"middle_name": self.middle_name,
				"gender": self.gender,
				"enabled": self.enabled,
				"birth_date": self.date_of_birth,
				"send_welcome_email": self.send_welcome_email,
				"mobile_no": self.mobile_no,
				"new_password": self.password,
				"module_profile": "No Module",
			})

			# Add each role profile to the core user's role_profiles field
			for role_profile in role_profile_names:
				core_user.append("role_profiles", {
					"role_profile": role_profile
				})
				
			core_user.insert()


		return

	def before_save(self):
		name_list=[self.first_name,self.middle_name,self.last_name]
		name_list = [value for value in name_list if value is not None]
		self.full_name=" ".join(name_list)

	def before_update_after_submit(self):
		# Extract role profile names from UserRoleProfile objects
		role_profile_names = [role_profile.role_profile for role_profile in self.role]
		frappe.logger().info(f"Role Profiles: {role_profile_names}")

		# Update core user information on User Management update
		core_users = frappe.get_all("User", filters={"email": self.email}, fields=["name"])
		frappe.logger().info(f"Core Users: {core_users}")

		if core_users:
			core_user = frappe.get_doc("User", core_users[0].name)
			frappe.logger().info(f"Core User before update: {core_user.as_dict()}")

			core_user.update({
				"full_name": self.full_name,
				"first_name": self.first_name,
				"last_name": self.last_name,
				"middle_name": self.middle_name,
				"gender": self.gender,
				"enabled": self.enabled,
				"birth_date": self.date_of_birth,
				"send_welcome_email": self.send_welcome_email,
				"mobile_no": self.mobile_no
			})

			# Update password if not "NULL"
			frappe.logger().info(f"Password Update: {self.password}")
			if self.password != "NULL":
				core_user.new_password = self.password

			# Assign role profiles to the core user
			core_user.set("role_profiles", [])
			for role_profile_name in role_profile_names:
				core_user.append("role_profiles", {
					"role_profile": role_profile_name
				})
			frappe.logger().info(f"Assigned Role Profiles: {core_user.role_profiles}")

			

			core_user.save()
			frappe.logger().info(f"Core User saved: {core_user.name}")



	def on_cancel(self):
		# Handle user deletion
		user = frappe.get_all("User", filters={"email": self.email})
			# pass  # Uncomment the next line if you want to delete the associated core user
		frappe.delete_doc("User", user[0].name)
			
		




# @frappe.whitelist()
# def user_to_user():
# 	# Sync core user data to User Management
# 	core_users = frappe.get_all("User", fields=["name", "email", "full_name", "first_name", "last_name",
# 												"middle_name", "gender", "enabled", "birth_date", 
# 												"send_welcome_email", "mobile_no", "new_password"])

# 	for core_user in core_users:
# 		if core_user.first_name in ["Guest", "Administrator", "Account", "Pankaj"]:
# 			continue

# 		# Fetching role profiles for the current user
# 		role_profiles = frappe.get_all("User Role Profile", filters={"parent": core_user.name},
# 									fields=["role_profile"])
# 		role_profile_names = [role["role_profile"] for role in role_profiles]
		
# 		user_management = frappe.get_all("User Management", filters={"email": core_user.email}, fields=["name"])
		
# 		if any(core_user.email == user_info['name'] for user_info in user_management):
# 			continue
# 		elif user_management:
# 			# Update existing User Management
# 			existing_user_management = frappe.get_doc("User Management", user_management[0].name)
# 			existing_user_management.update({
# 				"full_name": core_user.full_name,
# 				"first_name": core_user.first_name,
# 				"last_name": core_user.last_name,
# 				"middle_name": core_user.middle_name,
# 				"gender": core_user.gender,
# 				"enabled": core_user.enabled,
# 				"date_of_birth": core_user.birth_date,
# 				"send_welcome_email": core_user.send_welcome_email,
# 				"mobile_no": core_user.mobile_no,
# 				"role": [{"role_profile": role_profile} for role_profile in role_profile_names]
# 			})
# 			existing_user_management.save()
# 		else:
# 			# Create a new User Management if it doesn't exist
# 			new_user_management = frappe.new_doc("User Management")
# 			new_user_management.update({
# 				"email": core_user.email,
# 				"full_name": core_user.full_name,
# 				"first_name": core_user.first_name,
# 				"last_name": core_user.last_name,
# 				"middle_name": core_user.middle_name,
# 				"gender": core_user.gender,
# 				"enabled": core_user.enabled,
# 				"date_of_birth": core_user.birth_date,
# 				"send_welcome_email": core_user.send_welcome_email,
# 				"mobile_no": core_user.mobile_no,
# 				"password": "NULL",
# 				"role": [{"role_profile": role_profile} for role_profile in role_profile_names]
# 			})
# 			new_user_management.insert()
# 			new_user_management.submit()
# 	return {"status": "Users Synced"}




@frappe.whitelist()
def user_to_user():
    # Fetch all core user data
    core_users = frappe.get_all("User", fields=["name", "email", "full_name", "first_name", "last_name",
                                                "middle_name", "gender", "enabled", "birth_date", 
                                                "send_welcome_email", "mobile_no"])

    for core_user in core_users:
        # Skip specific users
        if core_user.first_name in ["Guest", "Administrator", "Account", "Pankaj"]:
            continue

        # Fetch role profiles for the current user
        role_profiles = frappe.get_all("User Role Profile", filters={"parent": core_user.name},
                                       fields=["role_profile"])
        role_profile_names = [role["role_profile"] for role in role_profiles]

        # Check if the user already exists in User Management
        user_management = frappe.get_all("User Management", filters={"email": core_user.email}, fields=["name"])

        if user_management:
            # Update existing User Management record
            existing_user_management = frappe.get_doc("User Management", user_management[0].name)

            # Clear existing roles
            existing_user_management.set('role', [])

            # Add new roles without duplication
            for role_profile in role_profile_names:
                if not any(r.role_profile == role_profile for r in existing_user_management.role):
                    existing_user_management.append('role', {"role_profile": role_profile})

            # Update other fields
            existing_user_management.update({
                "full_name": core_user.full_name,
                "first_name": core_user.first_name,
                "last_name": core_user.last_name,
                "middle_name": core_user.middle_name,
                "gender": core_user.gender,
                "enabled": core_user.enabled,
                "date_of_birth": core_user.birth_date,
                "send_welcome_email": core_user.send_welcome_email,
                "mobile_no": core_user.mobile_no,
            })

            # Save the updated document
            existing_user_management.save()
            frappe.db.commit()

        else:
            # Create a new User Management record
            new_user_management = frappe.new_doc("User Management")
            new_user_management.update({
                "email": core_user.email,
                "full_name": core_user.full_name,
                "first_name": core_user.first_name,
                "last_name": core_user.last_name,
                "middle_name": core_user.middle_name,
                "gender": core_user.gender,
                "enabled": core_user.enabled,
                "date_of_birth": core_user.birth_date,
                "send_welcome_email": core_user.send_welcome_email,
                "mobile_no": core_user.mobile_no,
                "password": "NULL",  # or you can set it to core_user.new_password if needed
                "role": [{"role_profile": role_profile} for role_profile in role_profile_names]
            })
            new_user_management.insert()
            new_user_management.submit()

    return {"status": "Users Synced"}
