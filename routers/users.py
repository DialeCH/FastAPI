from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/user", tags=["users"], responses={404: {"message": "Not found"}})


# Entidad user
class User(BaseModel):
    id: int
    name: str
    surname: str
    url: str
    age: int

users_list = [
                User(id=1, name="Brais", surname="Moure", url="https://moure.dev", age=35),
                User(id=2, name="Moure", surname="Dev", url="https://mouredev.com", age=35),
                User(id=3, name="Haakon", surname="Dahlberg", url="https://haakon.com", age=33),
            ]
 

@router.get("/usersjson")
async def usersjson():
    return [
        {"name": "Brais", "surname": "Moure", "url": "https://moure.dev", "age": 35},
        {"name": "Moure", "surname": "Dev", "url": "https://mouredev.com", "age": 35},
        {"name": "Haakon", "surname": "Dahlberg", "url": "https://haakon.com", "age": 33},
    ]

@router.get("/list")
async def users():
    return users_list


#Path
@router.get("/{id}")
async def user(id: int):
    return search_user(id)
    
#Query
@router.get("/")
async def get_user(id: int):
    return search_user(id)

@router.post("/", response_model=User, status_code=201)
async def create_user(user: User):
    if type(search_user(user.id)) == User:
        raise HTTPException(status_code=404, detail="User already exists")
    else:
        users_list.append(user)
        return user

@router.put("/")
async def update_user(user: User):

    found = False

    for index, saved_user in enumerate(users_list):
        if saved_user.id == user.id:
            users_list[index] = user
            found = True
            return saved_user
        return users_list[index]
        
    if not found:
        return {"error": "User not actualized"}
    


@router.delete("/{id}")
async def delete_user(id: int):
    found = False

    for index, saved_user in enumerate(users_list):
        if saved_user.id == id:
            del users_list[index]
            found = True
            return {"message": "User deleted"}

    if not found:
        return {"error": "User not deleted"}

def search_user(id: int):
    users = filter(lambda user: user.id == id, users_list)
    try:
        return list(users)[0]
    except IndexError:
        return {"error": "User not found"}
    
