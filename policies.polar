# Define roles (Fixed by removing explicit type annotation)
has_role(_user, "admin", _resource) if _user.is_admin;
has_role(_user, "user", _resource) if true;

# Users can only access their own profile
allow(user, "read", profile) if profile.user_id = user.id;

# Admins can access all profiles
allow(user, "read", profile) if has_role(user, "admin", profile);
