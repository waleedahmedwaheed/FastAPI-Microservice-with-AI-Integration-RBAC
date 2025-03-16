from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models import User, Profile
from auth import get_current_user
from oso_rbac import authorize
from sqlalchemy.future import select
from rag_pipeline import router as rag_router
from auth import router as auth_router
from pydantic import BaseModel
import logging

# ✅ Configure Logging
logging.basicConfig(
    filename="app.log",  # ✅ Log file for tracking errors & requests
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.DEBUG
)

# ✅ Initialize FastAPI Application
app = FastAPI(title="FastAPI Microservice with AI & RBAC")

# ✅ Include Authentication & AI Query Routes
app.include_router(auth_router, prefix="")
app.include_router(rag_router, prefix="/rag")

# ✅ Root Endpoint
@app.get("/")
async def root():
    return {"message": "FastAPI Microservice is running"}

# ✅ User Profile Routes
@app.get("/profile")
async def get_profile(
    user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    """
    🔹 Fetch user profile (protected by JWT authentication).
    - If the profile does not exist, it is created automatically.
    """
    try:
        result = await db.execute(select(Profile).where(Profile.user_id == user.id))
        profile = result.scalars().first()

        # ✅ Create profile if missing
        if profile is None:
            profile = Profile(user_id=user.id, bio="This is a new profile.")
            db.add(profile)
            await db.commit()
            await db.refresh(profile)

        # ✅ Authorization check after ensuring profile exists
        authorize(user, "read", profile)

        return profile

    except Exception as e:
        logging.error(f"❌ Profile Retrieval Error: {e}")  # ✅ Logging error
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# ✅ Update User Profile
class ProfileUpdate(BaseModel):
    bio: str  # ✅ Ensure request body contains "bio"

@app.put("/profile")
async def update_profile(
    request: ProfileUpdate, 
    user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    """
    🔹 Update the bio of the authenticated user's profile.
    - If profile does not exist, it is created automatically.
    """
    try:
        result = await db.execute(select(Profile).where(Profile.user_id == user.id))
        profile = result.scalars().first()

        # ✅ Create profile if it doesn't exist
        if profile is None:
            profile = Profile(user_id=user.id, bio=request.bio)
            db.add(profile)
        else:
            profile.bio = request.bio  # ✅ Update existing bio

        await db.commit()
        await db.refresh(profile)  # ✅ Ensure update is saved

        return {"message": "Profile updated successfully", "bio": profile.bio}

    except Exception as e:
        await db.rollback()  # ✅ Rollback transaction on failure
        logging.error(f"❌ Profile Update Error: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# ✅ Delete User Profile
@app.delete("/profile")
async def delete_profile(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    🔹 Delete the authenticated user's profile.
    - Ensures only profile owners can delete their profiles.
    """
    try:
        result = await db.execute(select(Profile).where(Profile.user_id == user.id))
        profile = result.scalars().first()

        if profile is None:
            raise HTTPException(status_code=404, detail="Profile not found")

        await db.delete(profile)
        await db.commit()

        return {"message": "Profile deleted successfully"}

    except Exception as e:
        logging.error(f"❌ Profile Deletion Error: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# ✅ Admin-Only Route with RBAC
@app.get("/admin")
async def get_admin_data(user: User = Depends(get_current_user)):
    """
    🔹 Admin-only route using Oso RBAC.
    - Requires "manage" permission on "admin-dashboard".
    """
    authorize(user, "manage", "admin-dashboard")

    return {"message": f"Welcome, {user.username}. You have admin access."}

# ✅ Fetch Any User's Profile (Admin or Profile Owner)
@app.get("/profile/{user_id}")
async def get_user_profile(
    user_id: int, 
    user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    """
    🔹 Fetch a user's profile (Only accessible by the profile owner or an admin).
    - Ensures security by restricting unauthorized access.
    """
    try:
        result = await db.execute(select(Profile).where(Profile.user_id == user_id))
        profile = result.scalars().first()

        if profile is None:
            raise HTTPException(status_code=404, detail="Profile not found")

        # ✅ Only allow access if the user is the owner or an admin
        if user.id != user_id and not user.is_admin:
            raise HTTPException(status_code=403, detail="Access denied")

        return profile

    except Exception as e:
        logging.error(f"❌ Error Fetching User Profile: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
