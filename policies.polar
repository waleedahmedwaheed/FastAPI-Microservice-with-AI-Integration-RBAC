# Define roles for users
has_role(user, "admin", _resource) if user.is_admin;
has_role(user, "user", _resource) if not user.is_admin;

# Users can only access their own profile
allow(user, "read", profile) if profile.user_id = user.id;

# Admins can access all profiles
allow(user, "read", profile) if has_role(user, "admin", profile);

# Admins can manage users (delete, update, view all)
allow(user, "manage", resource) if has_role(user, "admin", resource);
