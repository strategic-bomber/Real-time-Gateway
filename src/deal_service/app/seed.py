from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Deal, DealField, Participant


def seed_database(db: Session):
    deal_id = "deal-001"

    existing_deal = db.get(Deal, deal_id)

    if existing_deal:
        print("Demo deal already exists")
        return

    deal = Deal(id=deal_id)

    fields = [
        DealField(
            name="brand",
            value="Toyota",
        ),
        DealField(
            name="model",
            value="Camry",
        ),
        DealField(
            name="year",
            value="2020",
        ),
        DealField(
            name="horsePower",
            value="150",
        ),
        DealField(
            name="engineVolume",
            value="2.0",
        ),
        DealField(
            name="paintColor",
            value="Синий",
        ),
        DealField(
            name="mileage",
            value="75000",
        ),
        DealField(
            name="vin",
            value="JTNB11HK303123456",
        ),
        DealField(
            name="ownerName",
            value="Михаил Иванов",
        ),
        DealField(
            name="price",
            value="2500000",
        ),
    ]

    deal.fields = fields

    participants = [
        Participant(
            user_id="client-001",
            role="client",
        ),
        Participant(
            user_id="manager-001",
            role="manager",
        ),
    ]

    deal.participants = participants

    db.add(deal)
    db.commit()

    print("Demo deal created")


def main():
    db = SessionLocal()

    try:
        seed_database(db)
    finally:
        db.close()

            
if __name__ == "__main__":
    main()