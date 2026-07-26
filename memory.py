from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    role = Column(String, nullable=False)  # "user" or "assistant"
    message = Column(String, nullable=False)


Base.metadata.create_all(engine)


def save_message(user_id: int, role: str, message: str) -> None:
    db = SessionLocal()
    try:
        db.add(ChatMessage(user_id=user_id, role=role, message=message))
        db.commit()
    finally:
        db.close()


def get_chat_history(user_id: int, limit: int = 20):
    """Return the most recent `limit` messages for a user, oldest first."""
    db = SessionLocal()
    try:
        rows = (
            db.query(ChatMessage)
            .filter(ChatMessage.user_id == user_id)
            .order_by(ChatMessage.id.desc())
            .limit(limit)
            .all()
        )
        return list(reversed(rows))
    finally:
        db.close()


def format_history(user_id: int, limit: int = 20) -> str:
    history = get_chat_history(user_id, limit)
    if not history:
        return "(no previous messages)"
    return "\n".join(f"{row.role}: {row.message}" for row in history)


def delete_chat_history(user_id: int) -> None:
    db = SessionLocal()
    try:
        db.query(ChatMessage).filter(ChatMessage.user_id == user_id).delete()
        db.commit()
    finally:
        db.close()
