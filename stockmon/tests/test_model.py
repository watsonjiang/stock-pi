from unittest import TestCase

from stockmon import model
from stockmon.model import StockDao, CompanyInfoEntity


class TestModel(TestCase):

    def test_save_company(self):
        """测试添加公司信息
        """
        db_engine = model.init_engine("sqlite:///stock_db.sqlite3")
        stock_dao = StockDao(db_engine)
        comp = CompanyInfoEntity(code='600580', name='卧龙电驱')
        stock_dao.save_company(comp)
        stock_dao.iter_all_company(lambda c: print(c.code, c.name))

