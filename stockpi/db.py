# 数据库模型
import functools
import logging

from sqlalchemy import Column, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.sqltypes import DateTime, FLOAT, Integer, String

STOCK_DB = 'sqlite+aiosqlite:///stock_pi.sqlite3'
LOGGER = logging.getLogger(__name__)

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


_db_engine = None


async def db_init(db_url=None):
    # an Engine, which the Session will use for connection
    # resources
    global _db_engine
    _db_engine = create_async_engine(db_url if db_url else STOCK_DB)
    await _create_all_tables(_db_engine)


async def _create_all_tables(db_engine):
    """建表
    """
    async with db_engine.begin() as conn:
        # await conn.run_async(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def _with_session(c):
    async_session = sessionmaker(_db_engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as sess:
        return await c(sess)


def db_create_hq_subscriber():
    async def _on_hq_info(hq_info):
        """保存hq信息
        """
        await _with_session(functools.partial(_save_hq_info, hq_info=hq_info))

    return _on_hq_info


async def _save_hq_info(sess, hq_info):
    await _update_company_info(sess, hq_info)
    await _append_hq_hist(sess, hq_info)


async def _update_company_info(sess, hq_info):
    async with sess.begin():
        comp = (await sess.execute(
            select(CompanyInfo).where(CompanyInfo.stock_no == hq_info.stock_no))).scalar_one_or_none()
        if comp:
            comp.name = hq_info.name
        else:
            comp = CompanyInfo(stock_no=hq_info.stock_no, name=hq_info.name)
            sess.add(comp)


async def _append_hq_hist(sess, hq_info):
    async with sess.begin():
        hist = HqHistory(stock_no=hq_info.stock_no, price=hq_info.price)
        sess.add(hist)


async def db_get_company(stock_no):
    async def _get_company_by_stock_no(sess):
        return (await sess.execute(select(CompanyInfo).where(CompanyInfo.stock_no == stock_no))).scalar_one_or_none()

    return await _with_session(_get_company_by_stock_no)


async def db_get_hq_hist(stock_no):
    async def _get_hq_hist_by_stock_no(sess):
        return (await sess.execute(select(HqHistory).where(HqHistory.stock_no == stock_no))).scalars()

    return await _with_session(_get_hq_hist_by_stock_no)
