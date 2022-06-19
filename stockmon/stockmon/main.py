import asyncio

from quamash import QEventLoop

from stockmon.app import StockMonApplication
from stockmon.views.systray import SysTrayView


def main():
    app = StockMonApplication.instance()
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    #load system tray
    SysTrayView()
    with loop:
        loop.run_forever()

if __name__ == '__main__':
    main()
