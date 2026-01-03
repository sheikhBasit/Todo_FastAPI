import pytest
from sqlalchemy.orm import Session
from app.models.model import User, Group

def test_after_insert_event_listener(db: Session):
    # Create a new user
    new_user = User(username="testuser", email="testuser@example.com", password_hash="hashed_password")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Check if the default "Inbox" group was created
    inbox_group = db.query(Group).filter_by(user_id=new_user.id, name="Inbox").first()

    assert inbox_group is not None, "Default 'Inbox' group was not created."
    assert inbox_group.name == "Inbox", "Default group name is incorrect."
    assert inbox_group.user_id == new_user.id, "Default group user_id is incorrect."