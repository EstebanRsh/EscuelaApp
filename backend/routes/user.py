from fastapi import APIRouter, Request, Query, Depends
from fastapi.responses import JSONResponse
from models.modelo import (
    get_db,
    User,
    UserDetail,
    PivoteUserCareer,
    InputUser,
    InputLogin,
    InputUserAddCareer,
    InputPaginatedRequest,
)
from sqlalchemy.orm import Session, joinedload
from auth.security import Security
from typing import Optional

user = APIRouter()


@user.get("/")
### funcion helloUer documentacion
def helloUser():
    return "Hello User!!!"


@user.get("/users/all")
### funcion helloUer documentacion
def getAllUsers(req: Request, db: Session = Depends(get_db)):
    try:
        has_access = Security.verify_token(req.headers)
        if "iat" in has_access:
            usersWithDetail = db.query(User).options(joinedload(User.userdetail)).all()
            usuarios_con_detalle = []
            for user in usersWithDetail:
                user_con_detalle = {
                    "id": user.id,
                    "username": user.username,
                    "password": user.password,
                    "first_name": user.userdetail.first_name,
                    "last_name": user.userdetail.last_name,
                    "dni": user.userdetail.dni,
                    "type": user.userdetail.type,
                    "email": user.userdetail.email,
                }
                usuarios_con_detalle.append(user_con_detalle)
            return JSONResponse(status_code=200, content=usuarios_con_detalle)
        else:
            return JSONResponse(status_code=401, content=has_access)
    except Exception as ex:
        print("Error ---->> ", ex)
        return {"message": "Error al obtener los usuarios"}


"""
@user.get("/users/paginated")
### funcion helloUer documentacion
def getUsersPaginated(
    req: Request,
    limit: int = Query(20, gt=0, le=100),
    last_seen_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    try:
        has_access = Security.verify_token(req.headers)
        if "iat" in has_access:
            query = (
                db.query(User).options(joinedload(User.userdetail)).order_by(User.id)
            )

            if last_seen_id is not None:
                query = query.filter(User.id > last_seen_id)

            usersWithDetail = query.limit(limit).all()

            usuarios_con_detalle = []
            for user in usersWithDetail:
                user_con_detalle = {
                    "id": user.id,
                    "username": user.username,
                    "password": user.password,
                    "first_name": user.userdetail.first_name,
                    "last_name": user.userdetail.last_name,
                    "dni": user.userdetail.dni,
                    "type": user.userdetail.type,
                    "email": user.userdetail.email,
                }
                usuarios_con_detalle.append(user_con_detalle)

            next_cursor = (
                usuarios_con_detalle[-1]["id"]
                if len(usuarios_con_detalle) == limit
                else None
            )

            return JSONResponse(
                status_code=200,
                content={"users": usuarios_con_detalle, "next_cursor": next_cursor},
            )
        else:
            return JSONResponse(status_code=401, content=has_access)
    except Exception as ex:
        print("Error al obtener página de usuarios---->> ", ex)
        return {"message": "Error al obtener página de usuarios"}
"""


@user.post("/users/paginated")
### funcion helloUer documentacion
async def get_Users_Paginated(
    req: Request,
    body: InputPaginatedRequest,
    db: Session = Depends(get_db),
):
    try:
        has_access = Security.verify_token(req.headers)
        if "iat" not in has_access:
            return JSONResponse(status_code=401, content=has_access)

        limit = body.limit
        last_seen_id = body.last_seen_id
        query = db.query(User).options(joinedload(User.userdetail)).order_by(User.id)
        if last_seen_id is not None:
            query = query.filter(User.id > last_seen_id)
        users_with_detail = query.limit(limit).all()

        usuarios_con_detalle = []
        for user in users_with_detail:
            user_con_detalle = {
                "id": user.id,
                "username": user.username,
                "password": user.password,
                "first_name": user.userdetail.first_name,
                "last_name": user.userdetail.last_name,
                "dni": user.userdetail.dni,
                "type": user.userdetail.type,
                "email": user.userdetail.email,
            }
            usuarios_con_detalle.append(user_con_detalle)
        next_cursor = (
            usuarios_con_detalle[-1]["id"]
            if len(usuarios_con_detalle) == limit
            else None
        )
        return JSONResponse(
            status_code=200,
            content={"users": usuarios_con_detalle, "next_cursor": next_cursor},
        )

    except Exception as ex:
        print("Error al obtener página de usuarios---->> ", ex)
        return {"message": "Error al obtener página de usuarios"}


@user.get("/users/{us}/{pw}")
### funcion helloUer documentacion
def loginUser(us: str, pw: str, db: Session = Depends(get_db)):
    usu = db.query(User).filter(User.username == us).first()
    if usu is None:
        return "Usuario no encontrado!"
    if usu.password == pw:
        return "Usuario logueado con éxito!"
    else:
        return "Contraseña incorrecta!"


@user.post("/users/add")
def create_user(us: InputUser, db: Session = Depends(get_db)):
    try:
        newUser = User(us.username, us.password)
        newUserDetail = UserDetail(us.firstname, us.lastname, us.dni, us.type, us.email)
        newUser.userdetail = newUserDetail
        db.add(newUser)
        db.commit()
        return "Usuario creado con éxito!"
    except Exception as ex:
        db.rollback()
        print("Error ---->> ", ex)


@user.post("/users/login")
def login_user(us: InputLogin, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.username == us.username).first()
        if user and user.password == us.password:
            tkn = Security.generate_token(user)
            if not tkn:
                return {"message": "Error en la generación del token!"}
            else:
                res = {
                    "status": "success",
                    "token": tkn,
                    "user": user.userdetail,
                    "estado_del_tiempo": "llueve",
                    "message": "User logged in successfully!",
                }

                print(res)
                return res
        else:
            res = {"message": "Invalid username or password"}
            print(res)
            return res
    except Exception as ex:
        print("Error ---->> ", ex)


## Inscribir un alumno a una carrera
@user.post("/user/addcareer")
def addCareer(ins: InputUserAddCareer, db: Session = Depends(get_db)):
    try:
        newInsc = PivoteUserCareer(ins.id_user, ins.id_career)
        db.add(newInsc)
        db.commit()
        res = f"{newInsc.user.userdetail.first_name} {newInsc.user.userdetail.last_name} fue inscripto correctamente a {newInsc.career.name}"
        print(res)
        return res
    except Exception as ex:
        db.rollback()
        print("Error al inscribir al alumno:", ex)
        import traceback

        traceback.print_exc()


@user.get("/user/career/{_username}")
def get_career_user(_username: str, db: Session = Depends(get_db)):
    try:
        userEncontrado = db.query(User).filter(User.username == _username).first()
        arraySalida = []
        if userEncontrado:
            pivoteusercareer = userEncontrado.pivoteusercareer
            for pivote in pivoteusercareer:
                career_detail = {
                    "usuario": f"{pivote.user.userdetail.first_name} {pivote.user.userdetail.last_name}",
                    "carrera": pivote.career.name,
                }
                arraySalida.append(career_detail)
            return arraySalida
        else:
            return "Usuario no encontrado!"
    except Exception as ex:
        db.rollback()
        print("Error al traer usuario y/o pagos")
