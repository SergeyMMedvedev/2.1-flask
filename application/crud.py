from errors import ApiError
from models import User, Advert, ORM_MODEL_CLS
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


def get_item(
    session: Session, model_cls: ORM_MODEL_CLS, item_id: int | str
) -> User | Advert:
    item = session.query(model_cls).get(item_id)
    if item is None:
        raise ApiError(404, f"{model_cls.__name__.lower()} not found")
    return item


def create_item(
    session: Session, model_cls: ORM_MODEL_CLS, commit: bool = True, **params
) -> User | Advert:
    new_item = model_cls(**params)
    session.add(new_item)
    if commit:
        try:
            session.commit()
        except IntegrityError:
            raise ApiError(
                409, f"such {model_cls.__name__.lower()} already exists"
            )
    return new_item


def patch_item(
    session: Session, item: User | Advert, commit: bool = True, **params
) -> User | Advert:
    for field, value in params.items():
        setattr(item, field, value)
    session.add(item)
    if commit:
        try:
            session.commit()
        except IntegrityError:
            raise ApiError(409, "attr already exists")
    return item


def delete_item(session: Session, item: User | Advert, commit: bool = True):
    session.delete(item)
    if commit:
        session.commit()
