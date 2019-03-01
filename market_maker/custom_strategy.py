import sys
from copy import deepcopy

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
        execution = self.exchange.order_by_clOrdID(cl_ord_id)
        if cl_ord_id and len(execution) > 0:
            return execution[-1].get('ordStatus') == OrderStates.filled
        else:
            return False

    def get_last_price(self):
        return self.exchange.get_ticker()['last'] // 1

    def get_price(self, side, price=None):
        ratio = -1 if side == OrderSide.buy else 1
        if price is None:
            price = self.get_last_price()
        return min(price, self.get_last_price()) + settings.ORDER_STEP * ratio \
            if side == OrderSide.buy \
            else max(price, self.get_last_price()) + settings.ORDER_SPREAD * ratio

    def change_order(self, side, price=None):
        order = {"price": price, "orderQty": settings.ORDER_SIZE, "side": side}
        self.orders[side] = [order]

    def add_order(self, side, price=None):
        order = {"price": self.get_price(side, price),
                 "orderQty": settings.ORDER_SIZE, "side": side}
        self.orders[side].append(order)

    def orders_to_history(self):
        history_orders = {'Sell': [], 'Buy': []}
        buy_orders = [{'price': o['price'],
                       'orderQty': o['orderQty'],
                       'side': o['side']} for o in self.orders['Buy']]
        sell_orders = [{'price': o['price'],
                        'orderQty': o['orderQty'],
                        'side': o['side']} for o in self.orders['Sell']]
        for order in buy_orders:
            history_orders['Buy'].append(order)
        for order in sell_orders:
            history_orders['Sell'].append(order)
        return history_orders

    def grid_update(self):
        history_orders = self.orders_to_history()
        self.history_orders.append(history_orders)
        # self.history_orders.append(deepcopy(self.orders))
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
            print('order')
            print(order)
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
                logger.info(
                    f"{order['side']}, {order['orderQty']} @ {order['price']}, Status: {order.get('ordStatus', 'noStatus')}")

        if len(self.orders[settings.GRID_SIDE]) > 0:
            for order in reversed(self.orders[settings.GRID_SIDE]):
                logger.info(
                    f"{order['side']}, {order['orderQty']} @ {order['price']}, Status: {order.get('ordStatus', 'noStatus')}")

    def prepare_orders(self):
        self.orders[settings.REVERSE_SIDE] = [order for order in
                                              self.exchange.get_orders()
                                              if order['side'] == settings.REVERSE_SIDE]
        self.orders[settings.GRID_SIDE] = [order for order in
                                           self.exchange.get_orders()
                                           if order['side'] == settings.GRID_SIDE]
        current_qty = self.exchange.get_position()['currentQty']
        if current_qty != 0:
            # TODO проверка на кратность позиции
            reverse_orders_count = current_qty // settings.ORDER_SIZE
            reverse_prices = [self.get_last_price()]
            ratio = 1 if settings.REVERSE_SIDE == OrderSide.sell else -1

            for i in range(1, reverse_orders_count):
                reverse_prices.append(reverse_prices[-1] + settings.ORDER_STEP * ratio)
            reverse_prices.reverse()

            for price in reverse_prices:
                history_orders = self.orders_to_history()
                self.history_orders.append(history_orders)
                self.change_order(settings.GRID_SIDE, price - settings.ORDER_STEP * ratio)
                self.add_order(settings.REVERSE_SIDE, price)

        if self.orders[settings.GRID_SIDE] == []:
            self.add_order(settings.GRID_SIDE)


    """A sample order manager for implementing your own custom strategy"""

    def place_orders(self):
        logger.info('Last price: {}.'.format(
            self.exchange.get_ticker()['last']
        ))
        logger.info('Current Price: {}. Current Qty: {}.'.format(
            self.exchange.get_position()['avgEntryPrice'],
            self.exchange.get_position()['currentQty']
        ))

        if len(self.orders[settings.GRID_SIDE]) == 0 \
                and len(self.orders[settings.REVERSE_SIDE]) == 0:
            self.prepare_orders()

        self.grid_update()
        self.reverse_update()

        buy_orders = self.orders[OrderSide.buy]
        sell_orders = self.orders[OrderSide.sell]

        self.converge_orders(buy_orders, sell_orders)
        self.print_active_order()

    def print_active_order(self):
        logger.info("Active %d orders:" %
                    (len(self.orders[settings.REVERSE_SIDE]) +
                     len(self.orders[settings.GRID_SIDE])))

        if len(self.orders[settings.REVERSE_SIDE]) > 0:
            for order in reversed(self.orders[settings.REVERSE_SIDE]):
                logger.info(
                    f"{order['side']}, {order['orderQty']} @ {order['price']}, "
                    f"Status: {order.get('ordStatus', 'noStatus')}, clOrdID: {order.get('clOrdID')}")

        if len(self.orders[settings.GRID_SIDE]) > 0:
            for order in reversed(self.orders[settings.GRID_SIDE]):
                logger.info(
                    f"{order['side']}, {order['orderQty']} @ {order['price']}, "
                    f"Status: {order.get('ordStatus', 'noStatus')}, clOrdID: {order.get('clOrdID')}")

    def converge_orders(self, buy_orders, sell_orders):
        """Converge the orders we currently have in the book with what we want to be in the book.
           This involves amending any open orders and creating new ones if any have filled completely.
           We start from the closest orders outward."""

        to_create = []
        to_cancel = []
        buys_matched = 0
        sells_matched = 0
        existing_orders = self.exchange.get_orders()

        for order in existing_orders:
            try:
                if order['side'] == 'Buy':
                    desired_order = buy_orders[buys_matched]
                    buys_matched += 1
                else:
                    desired_order = sell_orders[sells_matched]
                    sells_matched += 1

                # Found an existing order. Do we need to amend it?
                if desired_order['price'] != order['price']:
                    to_cancel.append(order)
                    to_create.append(desired_order)
            except IndexError:
                # Will throw if there isn't a desired order to match. In that case, cancel it.
                to_cancel.append(order)

        while buys_matched < len(buy_orders):
            to_create.append(buy_orders[buys_matched])
            buys_matched += 1

        while sells_matched < len(sell_orders):
            to_create.append(sell_orders[sells_matched])
            sells_matched += 1

        # Could happen if we exceed a delta limit
        if len(to_cancel) > 0:
            logger.info("Canceling %d orders:" % (len(to_cancel)))
            for order in reversed(to_cancel):
                logger.info("%4s %d @ %d" % (
                order['side'], order['orderQty'], order['price']))
            self.exchange.cancel_bulk_orders(to_cancel)

        if len(to_create) > 0:
            logger.info("Creating %d orders:" % (len(to_create)))
            for order in reversed(to_create):
                logger.info("%4s %d @ %d" % (
                order['side'], order['orderQty'], order['price']))
            self.exchange.create_bulk_orders(to_create)


def run() -> None:
    order_manager = CustomOrderManager()

    # Try/except just keeps ctrl-c from printing an ugly stacktrace
    try:
        order_manager.run_loop()
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
