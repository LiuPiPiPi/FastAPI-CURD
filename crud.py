from sqlalchemy.orm import Session

"""
Session manages persistence operations for ORM-mapped objects.
Let's just refer to it as a database session for simplicity
"""

from models import Friend


def create_friend(db:Session, first_name, last_name, age):
    """
    function to create a friend model object
    """
    # create friend instance
    new_friend = Friend(first_name=first_name, last_name=last_name, age=age)
    #place object in the database session
    db.add(new_friend)
    #commit your instance to the database
    db.commit()
    #reefresh the attributes of the given instance
    db.refresh(new_friend)
    return new_friend

def get_friend(db:Session, id:int):
    """
    get the first record with a given id, if no such record exists, will return null
    """
    db_friend = db.query(Friend).filter(Friend.id==id).first()
    return db_friend

def list_friends(db:Session):
    """
    Return a list of all existing Friend records
    """
    all_friends = db.query(Friend).all()
    return all_friends


def update_friend(db:Session, id:int, first_name: str, last_name: str, age:int):
    """
    Update a Friend object's attributes
    """
    db_friend = get_friend(db=db, id=id)
    db_friend.first_name = first_name
    db_friend.last_name = last_name
    db_friend.age = age

    db.commit()
    db.refresh(db_friend) #refresh the attribute of the given instance
    return db_friend

def delete_friend(db:Session, id:int):
    """
    Delete a Friend object
    """
    db_friend = get_friend(db=db, id=id)
    db.delete(db_friend)
    db.commit() #save changes to db