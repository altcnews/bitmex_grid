import sys

from market_maker.market_maker import OrderManager, ExchangeInterface
from market_maker.settings import settings
from market_maker.utils import log
from market_maker.states import *

#
# Helpers
#
logger = log.setup_custom_logger('customer')


class CustomOrderManager(OrderManager):

    def __init__(self):
        self.history_orders = []
        self.orders = {}
        self.orders[OrderSide.sell] = []
        self.orders[OrderSide.buy] = []
        super().__init__()


    def order_is_filled(self, order):
        cl_ord_id = order.get('clOrdID', False)
        if cl_ord_id:
            _order = self.exchange.order_by_clOrdID(cl_ord_id)[0]
            return _order.get('ordStatus') == OrderStates.filled
        else:
            return False


    def get_last_price(self):
        return self.exchange.get_ticker()['last'] // 1


    def get_price(self, side, price=None):
        ratio = -1 if side == OrderSide.buy else 1
        if price is None:
            price = self.get_last_price()
        return price + settings.ORDER_STEP * ratio


    def add_order(self, side, price=None):
        order = {"price": self.get_price(side, price), "orderQty": settings.ORDER_SIZE, "side": side}
        self.orders[side].append(order)


    def grid_update(self):
        self.history_orders.append(self.orders)
        order = self.orders[settings.GRID_SIDE].pop()

        if self.order_is_filled(order):
            self.add_order(settings.GRID_SIDE, order['price'])
            self.add_order(settings.REVERSE_SIDE, order['price'])
        else:
            self.orders[settings.GRID_SIDE].append(order)
            self.history_orders.pop()


    def reverse_update(self):
        if len(self.orders[settings.REVERSE_SIDE]) > 0:
            order = self.orders[settings.REVERSE_SIDE].pop()
            if self.order_is_filled(order):
                self.orders = self.history_orders.pop()
            else:
                self.orders[settings.REVERSE_SIDE].append(order)


    def print_active_order(self):
        logger.info("-----")
        logger.info("Active %d orders:" %
                    (len(self.orders[settings.REVERSE_SIDE]) +
                     len(self.orders[settings.GRID_SIDE])))

        if len(self.orders[settings.REVERSE_SIDE]) > 0:
            for order in reversed(self.orders[settings.REVERSE_SIDE]):
                logger.info(f"{order['side']}, {order['orderQty']} @ {order['price']}, Status: {order.get('ordStatus', 'noStatus')}")

        if len(self.orders[settings.GRID_SIDE]) > 0:
            for order in reversed(self.orders[settings.GRID_SIDE]):
                logger.info(f"{order['side']}, {order['orderQty']} @ {order['price']}, Status: {order.get('ordStatus', 'noStatus')}")


    def prepare_orders(self):
        self.orders[settings.REVERSE_SIDE] = [order for order in
                                              self.exchange.get_orders()
                                              if order['side'] == settings.REVERSE_SIDE]
        self.orders[settings.GRID_SIDE] = [order for order in
                                              self.exchange.get_orders()
                                              if order['side'] == settings.GRID_SIDE]
        current_qty = self.exchange.get_position()['currentQty']
        if current_qty != 0:
            while current_qty/settings.ORDER_SIZE != len(self.orders[settings.REVERSE_SIDE]):
                position_price = int(self.exchange.get_position()['avgEntryPrice'])
                self.add_order(settings.REVERSE_SIDE, position_price)

        if self.orders[settings.GRID_SIDE] == []:
            self.add_order(settings.GRID_SIDE)




    """A sample order manager for implementing your own custom strategy"""

    def place_orders(self) -> None:
        # implement your custom strategy here

        buy_orders = self.orders[OrderSide.buy]
        sell_orders = self.orders[OrderSide.sell]


        self.converge_orders(buy_orders, sell_orders)


def run() -> None:
    order_manager = CustomOrderManager()

    # Try/except just keeps ctrl-c from printing an ugly stacktrace
    try:
        order_manager.run_loop()
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
