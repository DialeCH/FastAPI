from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter()
oauth2 = OAuth2PasswordBearer(tokenUrl="login")

# Entidad user
class User(BaseModel):
    username: str
    fullname: str
    email: str
    disabled: bool

class UserDB(User):
    password: str

users_db = {
    "mouredev": {
        "username": "mouredev",
        "fullname": "Brais Moure",
        "email": "braismoure@mourede.com",
        "disabled": False,
        "password": "123456"
    },
    "mouredev2": {
        "username": "mouredev2",
        "fullname": "Brais Moure 2",
        "email": "brais@dev.com",
        "disabled": True,
        "password": "qwerty"
    }
}

def search_user_db(username: str):
    if username in users_db:
        return UserDB(**users_db[username])
    return None

def search_user(username: str):
    if username in users_db:
        return User(**users_db[username])
    return None
    

async def current_user(token: str = Depends(oauth2)):
    user = search_user(token)
    if not user:
        raise HTTPException(status_code=401, 
                            detail="Invalid authentication credentials", 
                            headers={"WWW-Authenticate": "Bearer"})
    if user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user_db = users_db.get(form.username)
    if not user_db:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    user = search_user_db(form.username)
    if not form.password == user.password: # type: ignore
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    return {"access_token": user.username, "token_type": "bearer"} # type: ignore

@router.get("/users/me")
async def me(user: User = Depends(current_user)):
    return user