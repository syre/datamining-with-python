#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Handling the database connection """
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
import os


CWDIR = os.path.join(os.path.dirname(__file__), "data", "project.db")
ENGINE = sqlalchemy.create_engine("sqlite:///{}".format(CWDIR), echo=False)
DB_SESSION = sqlalchemy.orm.scoped_session(sqlalchemy.orm.sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=ENGINE))
BASE = declarative_base()


def init_db():
    """
    Creates the database and its tables
    """
    import models  # pylint: disable=unused-variable
    BASE.metadata.create_all(bind=ENGINE)
init_db()
