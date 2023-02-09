import traceback
from time import sleep

from sqlalchemy import create_engine, Column, Integer, String, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from utils import status
from config.secret_config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
from config.system_config import MAX_ATTEMPT_NUMBER
from utils.log import log


class DataBase:
    def __init__(self):
        d = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        log(d)
        self.__engine = create_engine(d, echo=False)

        attempt_number = 0
        while True:
            try:
                self.__engine.connect()
                break
            except Exception as e:
                log(f"Engine connect exception: {e}")
                traceback.print_exc()
                attempt_number += 1
                if attempt_number == MAX_ATTEMPT_NUMBER:
                    raise e
                sleep(5)
                log("------------ Try again")

        Base = declarative_base()

        class User(Base):
            __tablename__ = "user"

            id = Column(Integer, primary_key=True)
            status = Column(String, nullable=False, default=status.EMPTY)

            def __repr__(self):
                return f"<{self.id}: {self.status}>"

        self.User = User

        class WaitDeclaration(Base):
            __tablename__ = "wait_declaration"

            id = Column(Integer, primary_key=True)
            user = Column(Integer, nullable=False)
            text = Column(String, nullable=False)
            content_source = Column(String, nullable=False)

            def __repr__(self):
                return f"<{self.id} to {self.user}\nTEXT: {self.text}>"

        self.WaitDeclaration = WaitDeclaration

        Base.metadata.create_all(self.__engine)

        self.Session = sessionmaker(bind=self.__engine)

    def __del__(self):
        self.__engine.dispose()

    def get_user_by_id(self, user_id):
        session = self.Session()
        result = session.query(self.User).filter_by(id=user_id)
        if result.first() is not None:
            return result.one(), session

        new_user = self.User(id=user_id)
        session.add(new_user)
        session.commit()
        log(f"Insert new user {new_user}")
        return new_user, session

    def add_wait_declaration(self, user, text, content_source):
        session = self.Session()
        new_wait_declaration = self.WaitDeclaration(user=user, text=text, content_source=content_source)
        session.add(new_wait_declaration)
        session.commit()
        session.close()

    def get_all_wait_declaration_for_user(self, user_id):
        session = self.Session()
        wait_declaration = session.query(self.WaitDeclaration).filter_by(user=user_id)
        declaration_with_content_source = []
        for declaration in wait_declaration.all():
            declaration_with_content_source.append([declaration.text, declaration.content_source])
        wait_declaration.delete()
        session.commit()
        session.close()
        return declaration_with_content_source

    def get_user_with_wait_declaration(self):
        session = self.Session()
        user_with_wait_declaration = session.query(self.WaitDeclaration.user,
                                                   func.count(self.WaitDeclaration.user)).group_by(
            self.WaitDeclaration.user).all()
        user_with_wait_declaration_str = []
        for user in user_with_wait_declaration:
            user_with_wait_declaration_str.append(f"@id{user[0]}  {user[1]}")
        session.commit()
        session.close()
        return user_with_wait_declaration_str
