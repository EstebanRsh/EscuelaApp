from fastapi import APIRouter, Query, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from models.modelo import Payment, InputPayment, User, get_db, InputPaginatedRequest
from auth.security import Security
from sqlalchemy.orm import joinedload
from typing import Optional
import traceback

payment = APIRouter()


@payment.get("/payment/all/detailled")
def get_payments(db: Session = Depends(get_db)):
    allPayments = db.query(Payment).all()
    paymentsDetailled = []
    for pay in allPayments:
        result = {
            "id_pago": pay.id,
            "monto": pay.amount,
            "afecha de pago": pay.created_at,
            "mes_pagado": pay.affected_month,
            "alumno": f"{pay.user.userdetail.first_name} {pay.user.userdetail.last_name}",
            "carrera afectada": pay.career.name,
        }
        paymentsDetailled.append(result)
    return paymentsDetailled
    ##return session.query(Payment).options(joinedload(Payment.user)).userdetail


"""
@payment.get("/payment/paginated")
def get_payments_paginated(
    limit: int = Query(20, gt=0, le=100),
    last_seen_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    try:
        query = (
            db.query(Payment)
            .options(
                joinedload(Payment.user).joinedload(User.userdetail),
                joinedload(Payment.career),
            )
            .order_by(Payment.id)
        )

        if last_seen_id is not None:
            query = query.filter(Payment.id > last_seen_id)

        payments_page = query.limit(limit).all()

        payments_detailed = []
        for pay in payments_page:
            result = {
                "id_pago": pay.id,
                "monto": pay.amount,
                "afecha de pago": (
                    pay.created_at.isoformat() if pay.created_at else None
                ),
                "mes_pagado": (
                    pay.affected_month.isoformat() if pay.affected_month else None
                ),
                "alumno": (
                    f"{pay.user.userdetail.first_name} {pay.user.userdetail.last_name}"
                    if pay.user and pay.user.userdetail
                    else "Dato no disponible"
                ),
                "carrera afectada": (
                    pay.career.name if pay.career else "Dato no disponible"
                ),
            }
            payments_detailed.append(result)
            next_cursor = None
        if payments_detailed and len(payments_detailed) == limit:
            next_cursor = payments_detailed[-1]["id_pago"]

        return JSONResponse(
            status_code=200,
            content={"payments": payments_detailed, "next_cursor": next_cursor},
        )
    except Exception as ex:
        traceback.print_exc()
        return JSONResponse(
            status_code=500, content={"message": "Error interno al procesar los pagos"}
        )
"""


@payment.post("/payment/paginated")
def get_payments_paginated(
    req: Request,
    body: InputPaginatedRequest,
    db: Session = Depends(get_db),
):
    try:
        # 1. Añadimos la verificación de seguridad
        has_access = Security.verify_token(req.headers)
        if "iat" not in has_access:
            return JSONResponse(status_code=401, content=has_access)

        # 2. Obtenemos los parámetros desde el body
        limit = body.limit
        last_seen_id = body.last_seen_id

        # 3. La lógica de la consulta es la que ya tenías
        query = (
            db.query(Payment)
            .options(
                joinedload(Payment.user).joinedload(User.userdetail),
                joinedload(Payment.career),
            )
            .order_by(Payment.id)
        )

        if last_seen_id is not None:
            query = query.filter(Payment.id > last_seen_id)

        payments_page = query.limit(limit).all()

        payments_detailed = []
        for pay in payments_page:
            result = {
                "id_pago": pay.id,
                "monto": pay.amount,
                "fecha_pago": pay.created_at.isoformat() if pay.created_at else None,
                "mes_pagado": (
                    pay.affected_month.isoformat() if pay.affected_month else None
                ),
                "alumno": (
                    f"{pay.user.userdetail.first_name} {pay.user.userdetail.last_name}"
                    if pay.user and pay.user.userdetail
                    else "Dato no disponible"
                ),
                "carrera_afectada": (
                    pay.career.name if pay.career else "Dato no disponible"
                ),
            }
            payments_detailed.append(result)

        next_cursor = None
        if payments_detailed and len(payments_detailed) == limit:
            next_cursor = payments_detailed[-1]["id_pago"]

        return JSONResponse(
            status_code=200,
            content={"payments": payments_detailed, "next_cursor": next_cursor},
        )
    except Exception as ex:
        traceback.print_exc()
        return JSONResponse(
            status_code=500, content={"message": "Error interno al procesar los pagos"}
        )


@payment.get("/payment/user/{_username}")
def payament_user(_username: str, db: Session = Depends(get_db)):
    userEncontrado = db.query(User).filter(User.username == _username).first()
    if not userEncontrado:
        return "Usuario no encontrado!"

    arraySalida = []
    payments = userEncontrado.payments
    for pay in payments:
        payment_detail = {
            "id": pay.id,
            "amount": pay.amount,
            "fecha_pago": pay.created_at,
            "usuario": f"{pay.user.userdetail.first_name} {pay.user.userdetail.last_name}",
            "carrera": pay.career.name,
            "mes_afectado": pay.affected_month,
        }
        arraySalida.append(payment_detail)
    return arraySalida


@payment.post("/payment/add")
def add_payment(pay: InputPayment, db: Session = Depends(get_db)):
    try:
        newPayment = Payment(pay.id_career, pay.id_user, pay.amount, pay.affected_month)
        db.add(newPayment)
        db.commit()
        db.refresh(newPayment)
        res = f"Pago para el alumno {newPayment.user.userdetail.first_name} {newPayment.user.userdetail.last_name}, aguardado!"
        print(res)
        return res
    except Exception as ex:
        db.rollback()
        print("Error al guardar un pago --> ", ex)
