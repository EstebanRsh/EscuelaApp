from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.modelo import Career, InputCareer, get_db

career = APIRouter()


@career.get("/career/all")
def get_careers(db: Session = Depends(get_db)):
    return db.query(Career).all()


@career.post("/career/add")
def add_career(ca: InputCareer, db: Session = Depends(get_db)):
    try:
        newCareer = Career(ca.name)
        db.add(newCareer)
        db.commit()
        res = f"carrera {ca.name} guardada correctamente!"
        print(res)
        return res
    except Exception as ex:
        db.rollback()
        print("Error al agregar career --> ", ex)
