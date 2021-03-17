import argparse
from contextlib import contextmanager

import random

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey, Table, Text
from sqlalchemy.engine.url import URL
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


import hasher
import settings


@contextmanager
def session_scope(cls):
    session = cls()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


Base = declarative_base()


class Proverb(Base):
    __tablename__ = "proverb"
    id = Column(Integer, autoincrement=True, primary_key=True)
    hash = Column(String(256), index=True)

    proverb = Column(Text)
    meaning = Column(Text)
    examples = Column(Text)

    @classmethod
    def from_items(cls, proverb, meaning, examples=None):
        return cls(
            hash=hasher.compute_hash(proverb),
            proverb=proverb,
            meaning=meaning,
            examples=examples,
        )

    def __repr__(self):
        return f"Proverb(hash={self.hash},id={self.id},proverb={self.proverb},meaning={self.meaning})"


class ProverbData:
    def __init__(
        self,
        id,
        hash,
        proverb,
        meaning,
        examples,
    ):
        self._id = id
        self._hash = hash
        self._proverb = proverb
        self._meaning = meaning
        self._examples = examples

    def __repr__(self):
        return f"ProverbData(id={self._id},hash={self._hash},proverb={self._proverb},meaning={self._meaning})"

    @classmethod
    def from_model(cls, model):
        return cls(
            id=model.id,
            hash=model.hash,
            proverb=model.proverb,
            meaning=model.meaning,
            examples=model.examples,
        )

    @property
    def id(self):
        return self._id

    @property
    def hash(self):
        return self._hash

    @property
    def proverb(self):
        return self._proverb

    @property
    def meaning(self):
        return self._meaning


class DatabaseManager:
    def __init__(self, config=None):
        if not config:
            config = {
                "drivername": settings.DB_DRIVER,
                "database": settings.DB_NAME,
            }
        self._engine = create_engine(URL(**config))

    def create(self):
        Base.metadata.create_all(bind=self._engine)

    def remove(self):
        Base.metadata.drop_all(bind=self._engine)

    def session(self):
        return session_scope(sessionmaker(self._engine))


class DataManager:
    def __init__(self, db):
        self._db = db
        self._last_index = self._get_last_index()

    def _get_last_index(self):
        with self._db.session() as session:
            p = session.query(Proverb).order_by(Proverb.id.desc()).first()
            if p:
                return p.id
            else:
                return 0

    def add(self, proverbs):
        with self._db.session() as session:
            for p in proverbs:
                session.add(p)

    def get(self, id=None, hash=None):
        with self._db.session() as session:
            if id:
                p = session.query(Proverb).filter(Proverb.id == id).first()
            elif hash:
                p = session.query(Proverb).filter(Proverb.hash == hash).first()

            return ProverbData.from_model(p) if p else None

    def get_random(self):
        id = random.randint(1, self._last_index)
        return self.get(id)

    def show(self):
        with self._db.session() as session:
            for p in session.query(Proverb):
                print(p)


def make_proverbs(filename):
    def make_p(line):
        pos = line.find(":")
        return Proverb.from_items(
            proverb=line[:pos].strip(),
            meaning=line[pos + 1 :].strip(),
        )

    with open(filename) as f:
        return [make_p(line) for line in f]


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--upgrade",
        help="Drop database then create new one and populate with content from the specified file",
    )

    parser.add_argument(
        "-f",
        "--file",
        help="file containing the list of proverbs to be stored in database",
    )

    parser.add_argument(
        "--dry-run",
        help="make proverbs from file but do not store them intro database",
    )

    parser.add_argument(
        "-g",
        "--get",
        help="get proverb from database by the specified id",
    )

    parser.add_argument(
        "-r",
        "--random",
        help="get random proverb from database",
        action="store_true",
    )

    args = parser.parse_args()

    dbmgr = DatabaseManager()

    if args.upgrade:
        dbmgr.remove()
        dbmgr.create()

        datamgr = DataManager(dbmgr)
        proverbs = make_proverbs(args.upgrade)
        datamgr.add(proverbs)
        datamgr.show()

    # if args.file:

    #     proverbs = make_proverbs(args.file)
    #     if args.dry_run:
    #         for p in proverbs:
    #             print(p)
    #     else:
    #         m.add(make_proverbs(args.file))
    #         m.show()

    # if args.get:
    #     print(m.get(id=args.get))

    # if args.random:
    #     print(m.get_random())


if __name__ == "__main__":
    main()
