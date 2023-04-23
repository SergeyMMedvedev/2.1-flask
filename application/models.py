import uuid
from typing import Type

import config
from cachetools import cached
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    create_engine,
    func,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy_utils import EmailType, UUIDType

Base = declarative_base()


class User(Base):
    __tablename__ = "ads_users"

    id = Column(Integer, primary_key=True)
    email = Column(EmailType, unique=True, index=True)
    password = Column(String(60), nullable=False)
    registration_time = Column(DateTime, server_default=func.now())


class Token(Base):
    __tablename__ = "tokens"

    id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    creation_time = Column(DateTime, server_default=func.now())
    user_id = Column(Integer, ForeignKey("ads_users.id", ondelete="CASCADE"))
    user = relationship("User", lazy="joined")


class Advert(Base):
    __tablename__ = "adverts"

    id = Column(Integer, primary_key=True)
    title = Column(String(40), unique=True, index=True)
    description = Column(String(120))
    creation_time = Column(DateTime, server_default=func.now())
    owner_id = Column(Integer, ForeignKey("ads_users.id", ondelete="CASCADE"))
    owner = relationship("User", lazy="joined")

    def __str__(self):
        return (f"title: {self.title}, "
                f"description: {self.description}, "
                f"creation_time: {self.creation_time}, "
                f"user_id: {self.user_id}, ")


@cached({})
def get_engine():
    return create_engine(config.PG_DSN)


@cached({})
def get_session_maker():
    return sessionmaker(bind=get_engine())


def init_db():
    Base.metadata.create_all(bind=get_engine())


def close_db():
    get_engine().dispose()


ORM_MODEL_CLS = Type[User] | Type[Advert]
