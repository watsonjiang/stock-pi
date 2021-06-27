# 数据库模型
from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.sqltypes import DateTime, FLOAT, Integer, String

Base = declarative_base()

class CompanyInfo(Base):
    ''' 公司信息
    '''
    __tablename__ = 't_company_info'

    id = Column(Integer, primary_key=True)
    stock_no = Column(String)
    name = Column(String)
    create_time = Column(DateTime, server_default=func.now())
    update_time = Column(DateTime, server_default=func.now(), server_onupdate=func.now())

class HqHistory(Base):
    '''行情历史
    '''
    __tablename__ = 't_hq_hist'

    id = Column(Integer, primary_key=True)
    stock_no = Column(String)
    price = Column(FLOAT)
    create_time = Column(DateTime, server_default=func.now())
    update_time = Column(DateTime, server_default=func.now(), server_onupdate=func.now())

def init(db_url):
    # an Engine, which the Session will use for connection
    # resources
    engine = create_engine(db_url)
    create_all_tables(engine)
    return engine

def create_all_tables(db_engine):
    '''建表
    '''
    Base.metadata.create_all(db_engine)