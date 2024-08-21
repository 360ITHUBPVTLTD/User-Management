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
			
		




@frappe.whitelist()
def user_to_user():
	# Sync core user data to User Management
	core_users = frappe.get_all("User", fields=["name", "email", "full_name", "first_name", "last_name",
												"middle_name", "gender", "enabled", "birth_date", 
												"send_welcome_email", "mobile_no", "new_password"])

	for core_user in core_users:
		if core_user.first_name in ["Guest", "Administrator", "Account", "Pankaj"]:
			continue

		# Fetching role profiles for the current user
		role_profiles = frappe.get_all("User Role Profile", filters={"parent": core_user.name},
									fields=["role_profile"])
		role_profile_names = [role["role_profile"] for role in role_profiles]
		
		lsa_user = frappe.get_all("User Management", filters={"email": core_user.email}, fields=["name"])
		
		if any(core_user.email == user_info['name'] for user_info in lsa_user):
			continue
		elif lsa_user:
			# Update existing User Management
			existing_lsa_user = frappe.get_doc("User Management", lsa_user[0].name)
			existing_lsa_user.update({
				"full_name": core_user.full_name,
				"first_name": core_user.first_name,
				"last_name": core_user.last_name,
				"middle_name": core_user.middle_name,
				"gender": core_user.gender,
				"enabled": core_user.enabled,
				"date_of_birth": core_user.birth_date,
				"send_welcome_email": core_user.send_welcome_email,
				"mobile_no": core_user.mobile_no,
				"role": [{"role_profile": role_profile} for role_profile in role_profile_names]
			})
			existing_lsa_user.save()
		else:
			# Create a new User Management if it doesn't exist
			new_lsa_user = frappe.new_doc("User Management")
			new_lsa_user.update({
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
				"password": "NULL",
				"role": [{"role_profile": role_profile} for role_profile in role_profile_names]
			})
			new_lsa_user.insert()
			new_lsa_user.submit()
	return {"status": "Users Synced"}

