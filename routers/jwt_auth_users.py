from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta

ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 1
SECRET_KEY = "mysecretkey"

router = APIRouter()

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

crypt = CryptContext(schemes=["bcrypt"])

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
        "password": "$2a$12$eh3KoI59mx/w3oOtoX/DLOy1b0B0G0eDPaU/8c55rspP3D.3Z8A7e"
    },
    "mouredev2": {
        "username": "mouredev2",
        "fullname": "Brais Moure 2",
        "email": "brais@dev.com",
        "disabled": True,
        "password": "$2a$12$CdGwdNOU6/IvRvge8koysO/4/bXcQlzfljU8Kcm6BhiTTnH/FZMRK"
    }
}

# hashed = crypt.hash("123456")
# print(hashed)

def search_user_db(username: str):
    if username in users_db:
        return UserDB(**users_db[username])
    return None

def search_user(username: str):
    if username in users_db:
        return User(**users_db[username])
    return None

async def auth_user(token: str = Depends(oauth2)):

    exception = HTTPException(status_code=401, 
                              detail="Invalid authentication credentials",
                                headers={"WWW-Authenticate": "Bearer"})

    try:
        username = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM]).get("sub")
        if username is None:
            raise exception

    except JWTError:
        raise exception
    
    return search_user(username)
       


async def current_user(user: User = Depends(auth_user)):
    if user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user = search_user_db(form.username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    if not crypt.verify(form.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = {"sub": user.username, 
                    "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION)}
    
    return {"access_token": jwt.encode(access_token, key=SECRET_KEY, algorithm=ALGORITHM), "token_type": "bearer"}


router.get("/users/me")
async def me(user: User = Depends(current_user)):
    return user