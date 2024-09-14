from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from backend.config.db import  engine
from backend.models.tables import Order, Payment, User
import stripe
import os

from backend.security import get_current_active_user

stripe.api_key=os.getenv('STRIPE_API_KEY')

router=APIRouter()

@router.post("/payments/")
async def create_payment(payment_data: Payment, current_user: User = Depends(get_current_active_user)):
    if current_user.role != "simple_user":
        raise HTTPException(status_code=403, detail="You are not authorized to create a payment")

    with Session(engine) as session:
        order = session.exec(select(Order).where(Order.id == payment_data.order_id)).first()
        if not order or order.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Order not found or access denied")

    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=int(payment_data.amount * 100),  
            currency=payment_data.currency,  
            receipt_email=current_user.email,
            metadata={"order_id": payment_data.order_id, "user_id": current_user.id}
        )

        with Session(engine) as session:
            payment = Payment(
                user_id=current_user.id,
                order_id=payment_data.order_id,
                amount=payment_data.amount,
                currency=payment_data.currency,
                payment_status=payment_data.payment_status,  
                payment_method=payment_data.payment_method,
                payment_date=datetime.now(),
                stripe_payment_intent_id=payment_intent.id
                
            )
            session.add(payment)
            session.commit()
            session.refresh(payment)

        return {
            "status": 200,
            "message": "Payment created successfully",
            "payment_intent": payment_intent
        }

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=f"Stripe error: {e.user_message}")

@router.get("/payment/{payment_id}")
async def get_payment_by_id(payment_id: int):
    with Session(engine) as session:
        payment = session.exec(select(Payment).where(Payment.id == payment_id)).first()
        if not payment:
            return {"status": 404, "Message": "Payment not found"}
        return {"status": 200, "Payment": payment}
    
    
@router.post("/payment/{payment_id}/refund")
async def refund_payment(payment_id: int, user: User = Depends(get_current_active_user)):
    if user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions to process a refund")

    with Session(engine) as session:
        db_payment = session.exec(select(Payment).where(Payment.id == payment_id)).first()

        if not db_payment:
            raise HTTPException(status_code=404, detail="Payment not found")

        if db_payment.payment_status != "completed":
            raise HTTPException(status_code=400, detail="Payment is not eligible for a refund")

        try:
            # Retrieve the PaymentIntent from Stripe
            payment_intent = stripe.PaymentIntent.retrieve(db_payment.stripe_payment_intent_id)
            
            # Ensure the PaymentIntent has a successful charge
            charges = stripe.Charge.list(payment_intent=db_payment.stripe_payment_intent_id)
            if not charges.data or charges.data[0].status != 'succeeded':
                raise HTTPException(status_code=400, detail="No successful charge to refund")

            # Create the refund
            refund = stripe.Refund.create(payment_intent=db_payment.stripe_payment_intent_id)
            
            # Update the payment status
            db_payment.payment_status = "refunded"
            session.add(db_payment)
            session.commit()
            session.refresh(db_payment)

            return {"message": "Refund processed successfully", "refund_id": refund.id}

        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=f"Stripe error: {e.user_message}")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")