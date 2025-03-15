from oso import Oso
from models import User, Profile

oso = Oso()

# Register models with Oso before loading policies
oso.register_class(User)
oso.register_class(Profile)

# Load Oso policies
oso.load_files(["policies.polar"])

def authorize(user: User, action: str, resource: object):
    if not oso.is_allowed(user, action, resource):
        raise HTTPException(status_code=403, detail="Access denied")
