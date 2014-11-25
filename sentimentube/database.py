#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
import os
cwdir = os.path.join(os.path.dirname(__file__), "data", "project.db")
engine = sqlalchemy.create_engine("sqlite:///{}".format(cwdir), echo=False)
db_session = sqlalchemy.orm.scoped_session(sqlalchemy.orm.sessionmaker(
                                           autocommit=False, autoflush=False,
                                           bind=engine))
base = declarative_base()


def init_db():
    import models
    base.metadata.create_all(bind=engine)
#init_db()
