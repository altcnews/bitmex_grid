import uuid

from market_maker.settings import settings
from market_maker.states import *
from market_maker.utils import log

logger = log.setup_custom_logger(f'{uuid.uuid4()}')

class MockExchangeInterface:
    ticker = {'last': 3786.0, 'buy': 3785, 'sell': 3787.0, 'mid': 3787.0}
    position = {'avgEntryPrice': 0,
                'avgCostPrice': 0,
                'currentQty': 0,
                }
    orders = []

    def remove_filled_orders(self):
        MockExchangeInterface.orders = list(
            filter(lambda o: o['ordStatus'] != OrderStates.filled,
                   MockExchangeInterface.orders))
        print(MockExchangeInterface.orders)
        return MockExchangeInterface.orders


    def set_ticker(self, key, valye):
        MockExchangeInterface.ticker[key] = valye
        MockExchangeInterface.ticker['buy'] = valye - 1
        MockExchangeInterface.ticker['sell'] = valye - 1
        MockExchangeInterface.ticker['mid'] = key

    def get_ticker(self):
        return MockExchangeInterface.ticker

    def get_orders(self):
        return list(filter(lambda o: o.get('ordStatus') != OrderStates.filled,
                   MockExchangeInterface.orders))

    def get_position(self, symbol=None):
        return MockExchangeInterface.position

    def set_position(self, key, valye):
        MockExchangeInterface.position[key] = valye

    def create_bulk_orders(self, orders):
        for order in orders:
            order['ordStatus'] = OrderStates.new
            order['clOrdID'] = f'{uuid.uuid4()}'
            order['orderID'] = f'{uuid.uuid4()}'
            order['cumQty'] = 0
            order['leavesQty'] = settings.ORDER_SIZE
            MockExchangeInterface.orders.append(order)

        return MockExchangeInterface.orders

    def amend_bulk_orders(self, orders):
        self.cancel_bulk_orders(orders)
        self.create_bulk_orders(orders)
        return MockExchangeInterface.orders

    def cancel_bulk_orders(self, orders):
        cancel_orders = [order['orderID'] for order in orders]
        MockExchangeInterface.orders = \
            list(filter(lambda o: o.get('orderID') not in cancel_orders,
                   MockExchangeInterface.orders))
        return MockExchangeInterface.orders

    def order_by_clOrdID(self, cl_ord_id):
        return [o for o in MockExchangeInterface.orders if o['clOrdID'] == cl_ord_id]

    def change_order_status(self, order_id):
        for order in MockExchangeInterface.orders:
            if order['clOrdID'] == order_id:
                order['ordStatus'] = OrderStates.filled
                ratio = -1 if order['side'] == OrderSide.sell else 1
                MockExchangeInterface.position['avgEntryPrice'] = 111

                MockExchangeInterface.position['currentQty'] += settings.ORDER_SIZE * ratio

                logger.info('{} {} @ {} - {} - change status to {}'.format(
                    order['side'],
                    order['orderQty'],
                    order['price'],
                    order['clOrdID'],
                    OrderStates.filled
                ))
        return MockExchangeInterface.orders


class MockCustomOrderManager:
    def place_orders(self):
        if len(self.orders[settings.GRID_SIDE]) == 0 \
                and len(self.orders[settings.REVERSE_SIDE]) == 0:
            self.prepare_orders()

        self.grid_update()
        self.reverse_update()

        buy_orders = self.orders[OrderSide.buy]
        sell_orders = self.orders[OrderSide.sell]

        self.converge_orders(buy_orders, sell_orders)

        self.fill_cl_ord_id()
        self.print_active_order()

    def print_active_order(self, info_head="-----"):
        logger.info(info_head)
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

    def print_current_log(self):
        self.log_message = []

        self.log_message.append(
        str('Last price: {}.'.format(
            self.exchange.get_ticker()['last']
        )))
        self.log_message.append(
        str('Current Price: {}. Current Qty: {}.'.format(
            self.exchange.get_position()['avgEntryPrice'],
            self.exchange.get_position()['currentQty']
        )))

        self.log_message.append(
            str("Active %d orders:" %
                    (len(self.orders[settings.REVERSE_SIDE]) +
                     len(self.orders[settings.GRID_SIDE]))))

        if len(self.orders[settings.REVERSE_SIDE]) > 0:
            for order in reversed(self.orders[settings.REVERSE_SIDE]):
                self.log_message.append(
                    str(
                    f"{order['side']}, {order['orderQty']} @ {order['price']}, "
                    f"Status: {order.get('ordStatus', 'noStatus')}, clOrdID: {order.get('clOrdID')}"))

        if len(self.orders[settings.GRID_SIDE]) > 0:
            for order in reversed(self.orders[settings.GRID_SIDE]):
                self.log_message.append(
                    str(
                    f"{order['side']}, {order['orderQty']} @ {order['price']}, "
                    f"Status: {order.get('ordStatus', 'noStatus')}, clOrdID: {order.get('clOrdID')}"))

        if self.log_message != self.history_log_message:
            self.history_log_message = self.log_message
            for i in self.log_message:
                logger.info(i)

