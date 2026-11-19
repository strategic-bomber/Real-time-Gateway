from sqlalchemy import Column, Integer, String, ForeignKey, Text, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()

class Deal(Base):
    __tablename__ = 'deals'
    id = Column(String, primary_key=True)  # dealId
    status = Column(String, default='draft') # draft, buyout_completed, in_stock
    revision = Column(Integer, default=1)

class DealMember(Base):
    __tablename__ = 'deal_members'
    id = Column(Integer, primary_key=True, autoincrement=True)
    deal_id = Column(String, ForeignKey('deals.id'))
    user_id = Column(String)
    role = Column(String)  # 'client' or 'manager'

class DealField(Base):
    __tablename__ = 'deal_fields'
    id = Column(Integer, primary_key=True, autoincrement=True)
    deal_id = Column(String, ForeignKey('deals.id'))
    field_name = Column(String)  # e.g., horsePower, engineVolume, paintColour
    value = Column(String, nullable=True)
    status = Column(String, default='pending') # pending, approved, needs_correction
    version = Column(Integer, default=1)

class Message(Base):
    __tablename__ = 'messages'
    id = Column(String, primary_key=True)
    deal_id = Column(String, ForeignKey('deals.id'))
    sender_role = Column(String) # 'client', 'manager', 'system'
    text = Column(Text)
    
class Attachment(Base):
    __tablename__ = 'attachments'
    id = Column(String, primary_key=True)
    message_id = Column(String, ForeignKey('messages.id'))
    file_name = Column(String)
    file_path = Column(String)

# DB Setup
engine = create_engine("sqlite:///./deal_data.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)