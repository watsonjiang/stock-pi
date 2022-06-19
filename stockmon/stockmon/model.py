from typing import Callable

from sqlalchemy import Column, Integer, String, DateTime, func, FLOAT, create_engine, select
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class CompanyInfoEntity(Base):
    """ 公司信息
    """
    __tablename__ = 't_company_info'

    code = Column(String, primary_key=True)
    name = Column(String)


class SelectedCompanyEntity(Base):
    """ 选中公司信息
    """
    __tablename__ = 't_select_company'

    code = Column(Integer, primary_key=True)
    order = Column(Integer)  # 在列表中的排序, 0开始


class HqHistoryEntity(Base):
    """行情历史
    """
    __tablename__ = 't_hq_hist'

    id = Column(Integer, primary_key=True)
    code = Column(String)
    price = Column(FLOAT)
    volume = Column(FLOAT)
    create_time = Column(DateTime, server_default=func.now())
    update_time = Column(DateTime, server_default=func.now(), server_onupdate=func.now())


def init_engine(db_url):
    """an Engine, which the Session will use for connection
    resources
    """
    engine = create_engine(db_url)
    create_all_tables(engine)
    return engine


def create_all_tables(db_engine):
    """建表
    """
    Base.metadata.create_all(db_engine)


class StockDao:
    """
    股票数据访问接口
    """

    def __init__(self, db_engine):
        self.db_engine = db_engine

    def save_company(self, comp: CompanyInfoEntity):
        """保存公司信息. 如果存在,更新
        """
        with sessionmaker(self.db_engine)() as session:
            session.merge(comp)
            session.commit()

    def get_company_by_code(self, code: str) -> CompanyInfoEntity:
        """返回code对应的公司信息
        """
        st = select(CompanyInfoEntity).where(CompanyInfoEntity.code == code)
        with sessionmaker(self.db_engine)() as session:
            return session.scalars(st).first()

    def iter_selected_company(self, consumer: Callable[[CompanyInfoEntity], None]):
        """遍历选中的公司
        """
        st1 = select(SelectedCompanyEntity).order_by(SelectedCompanyEntity.order)
        with sessionmaker(self.db_engine)() as session:
            for s_comp in session.scalars(st1):
                comp = self.getCompany_by_code(s_comp.code)
                consumer(comp)

    def iter_all_company(self, consumer: Callable[[CompanyInfoEntity], None]):
        """遍历所有公司
        """
        st = select(CompanyInfoEntity)
        with sessionmaker(self.db_engine)() as session:
            for company in session.scalars(st):
                consumer(company)

    def get_price(self, code):
        """
        获取最新的价格
        """
        return self.codes[code]
