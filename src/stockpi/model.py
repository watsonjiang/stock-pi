# 数据库模型
from sqlite3 import dbapi2
from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker 
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql.sqltypes import DateTime, FLOAT, Integer, String

Base = declarative_base()

class CompanyInfo(Base):
    ''' 公司信息
    '''
    __tablename__ = 't_company_info'

    id = Column(Integer, primary_key=True)
    stock_no = Column(String)
    name = Column(String)
    create_time = Column(DateTime, server_default=dbapi2.func.now())
    update_time = Column(DateTime, server_default=dbapi2.func.now(), server_onupdate=dbapi2.func.now())

class HqHistory(Base):
    '''行情历史
    '''
    __tablename__ = 't_hq_hist'

    id = Column(Integer, primary_key=True)
    stock_no = Column(String)
    price = Column(FLOAT)
    create_time = Column(DateTime, server_default=dbapi2.func.now())
    update_time = Column(DateTime, server_default=dbapi2.func.now(), server_onupdate=dbapi2.func.now())

def init_session_maker(db_url):
    # an Engine, which the Session will use for connection
    # resources
    engine = create_engine(db_url)

    # a sessionmaker(), also in the same scope as the engine
    return sessionmaker(engine)
 