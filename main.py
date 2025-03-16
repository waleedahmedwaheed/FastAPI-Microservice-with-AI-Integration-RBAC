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


logging.basicConfig(
    filename="app.log",  # Log file
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.DEBUG
)

app = FastAPI(title="FastAPI Microservice")

# ✅ Secure Routes
app.include_router(auth_router, prefix="")  
app.include_router(rag_router, prefix="/rag")



@app.get("/")
async def root():
    return {"message": "FastAPI Microservice is running"}
    
     
# @app.get("/profile")
# async def get_profile(
    # user: User = Depends(get_current_user), 
    # db: AsyncSession = Depends(get_db)
# ):
    # """Fetch user profile (protected by JWT authentication)"""
    # try:
        # # ✅ Ensure the database session is properly awaited
        # async with db as session:
            # result = await session.execute(select(Profile).where(Profile.user_id == user.id))
            # profile = result.scalars().first()

            # # ✅ Fix: Create profile **before** calling authorize()
            # if profile is None:
                # profile = Profile(user_id=user.id, bio="This is a new profile.")
                # session.add(profile)
                # await session.commit()
                # await session.refresh(profile)

            # # ✅ Now authorize() will not fail on missing profile
            # authorize(user, "read", profile)

        # return profile

    # except Exception as e:
        # raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/profile")
async def get_profile(
    user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    """Fetch user profile (protected by JWT authentication)"""
    try:
        # ✅ Fetch profile correctly
        result = await db.execute(select(Profile).where(Profile.user_id == user.id))
        profile = result.scalars().first()

        # ✅ Create profile **before** calling authorize()
        if profile is None:
            profile = Profile(user_id=user.id, bio="This is a new profile.")
            db.add(profile)
            await db.commit()
            await db.refresh(profile)

        # ✅ Ensure authorization happens after profile creation
        authorize(user, "read", profile)

        return profile

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


# ✅ Update User Profile
class ProfileUpdate(BaseModel):
    bio: str
    
# @app.put("/profile")
# async def update_profile(
    # profile_data: ProfileUpdate,  # ✅ Accept JSON request body
    # user: User = Depends(get_current_user), 
    # db: AsyncSession = Depends(get_db)
# ):
    # """Update user profile (protected by JWT authentication)"""
    # try:
        # result = await db.execute(select(Profile).where(Profile.user_id == user.id))
        # profile = result.scalars().first()

        # if profile is None:
            # raise HTTPException(status_code=404, detail="Profile not found")

        # profile.bio = profile_data.bio  # ✅ Update bio from request body
        # await db.commit()
        # await db.refresh(profile)

        # return {"message": "Profile updated successfully", "bio": profile.bio}

    # except Exception as e:
        # raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.put("/profile")
async def update_profile(request: ProfileUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """✅ Update the profile bio of the authenticated user"""
    try:
        # Fetch existing profile
        result = await db.execute(select(Profile).where(Profile.user_id == user.id))
        profile = result.scalars().first()

        # ✅ If no profile exists, create one
        if profile is None:
            profile = Profile(user_id=user.id, bio=request.bio)
            db.add(profile)
        else:
            profile.bio = request.bio  # ✅ Update bio field

        await db.commit()
        await db.refresh(profile)  # ✅ Ensure update is saved

        return {"message": "Profile updated successfully", "bio": profile.bio}
    
    except Exception as e:
        await db.rollback()  # ✅ Rollback transaction on failure
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


# ✅ Delete User Profile 
@app.delete("/profile")
async def delete_profile(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Delete user profile (protected by JWT authentication)"""
    try:
        result = await db.execute(select(Profile).where(Profile.user_id == user.id))
        profile = result.scalars().first()

        if profile is None:
            raise HTTPException(status_code=404, detail="Profile not found")

        await db.delete(profile)
        await db.commit()

        return {"message": "Profile deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.get("/admin")
async def get_admin_data(user: User = Depends(get_current_user)):
    """Admin-only route"""
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")

    return {"message": f"Welcome, {user.username}. You have admin access."}

@app.get("/profile/{user_id}")
async def get_user_profile(
    user_id: int, 
    user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    """Fetch a user's profile (only accessible by owner or admin)"""
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
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    

 

  