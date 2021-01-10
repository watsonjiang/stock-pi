import logging, sys
from stockpi import PriceMon

STOCK_LIST = ['sh600580']

def init_logging():
    logging.basicConfig(stream=sys.stdout,
                level=logging.DEBUG,
                format="%(asctime)s %(levelname)-8s %(message)s"

def main():
    pricemon = PriceMon(STOCK_LIST)
    pricemon.mon()

if __name__ == "__main__":
    main()