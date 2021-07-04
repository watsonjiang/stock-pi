import logging, sys
from stockpi import PriceMon

STOCK_LIST = ['sh600580', 'sh600316', 'sz002603', 'sz000568']

def init_logging():
    logging.basicConfig(stream=sys.stdout,
                level=logging.DEBUG,
                format="%(asctime)s %(levelname)-8s %(message)s")

def main():
    pricemon = PriceMon(STOCK_LIST, 'sqlite:///stock_db.sqlite3')
    pricemon.mon()

if __name__ == "__main__":
    init_logging()
    main()