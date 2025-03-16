from oso import Oso
from fastapi import HTTPException
from models import User, Profile

# ✅ Initialize Oso (RBAC Policy Engine)
oso = Oso()

# ✅ Register Models with Oso Before Loading Policies
# This allows Oso to enforce permissions based on model attributes
oso.register_class(User)
oso.register_class(Profile)

# ✅ Load Oso RBAC Policies from File (Ensure 'policies.polar' exists)
try:
    oso.load_files(["policies.polar"])
    print("✅ Oso RBAC Policies Loaded Successfully")
except Exception as e:
    print(f"❌ Error loading Oso policies: {str(e)}")  # ✅ Debugging
    raise RuntimeError("Failed to load Oso policies.")

def authorize(user: User, action: str, resource: object):
    """
    🔹 Authorize user actions using Oso RBAC.
    - user: The authenticated user object
    - action: The action the user wants to perform (e.g., "read", "update", "delete")
    - resource: The resource object the user is trying to access
    - Raises HTTPException(403) if access is denied.
    """
    try:
        if not oso.is_allowed(user, action, resource):
            print(f"❌ Access Denied: {user.username} attempted '{action}' on {resource}")  # ✅ Debugging
            raise HTTPException(status_code=403, detail="Access denied")
        
        print(f"✅ Access Granted: {user.username} performed '{action}' on {resource}")  # ✅ Debugging
    
    except Exception as e:
        print(f"❌ Authorization Error: {str(e)}")  # ✅ Debugging
        raise HTTPException(status_code=500, detail="Authorization service error")
