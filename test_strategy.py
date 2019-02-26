
import unittest
import uuid
from unittest.mock import patch
from market_maker.settings import settings
from market_maker.custom_strategy import CustomOrderManager
from market_maker.states import *
from market_maker.utils import log

logger = log.setup_custom_logger('test')

class MockExchangeInterface:
    ticker = {'last': 3786.0, 'buy': 3785, 'sell': 3787.0, 'mid': 3787.0}
    position = {'avgEntryPrice': 0,
                'avgCostPrice': 0,
                'currentQty': 10,
                }
    orders = []

    def remove_filled_orders(self):
        MockExchangeInterface.orders = list(
            filter(lambda o: o['ordStatus'] != OrderStates.filled,
                   MockExchangeInterface.orders))


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
            order['leavesQty'] = settings.ORDER_SIZE
            MockExchangeInterface.orders.append(order)

        return MockExchangeInterface.orders


    def cancel_bulk_orders(self, orders):
        pass
        # print('cancel')
        print(orders)




    def order_by_clOrdID(self, cl_ord_id):
        return [o for o in MockExchangeInterface.orders if o['clOrdID'] == cl_ord_id]

    def change_order_status(self, order_id):
        for order in MockExchangeInterface.orders:
            if order['clOrdID'] == order_id:
                order['ordStatus'] = OrderStates.filled
                MockExchangeInterface.position['currentQty'] += settings.ORDER_SIZE
                MockExchangeInterface.position['avgEntryPrice'] = \
                    (MockExchangeInterface.position['avgEntryPrice'] + order['price']) / 2

                logger.info('Orders {} change status to {}'.format(
                    order['clOrdID'], OrderStates.filled
                ))
        return MockExchangeInterface.orders


class MockCustomOrderManager:
    def place_orders(self):
        logger.info("-----")
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

        buy_orders = self.orders[OrderSide.buy]
        sell_orders = self.orders[OrderSide.sell]

        self.converge_orders(buy_orders, sell_orders)
        self.print_active_order()



    def print_active_order(self):
        logger.info("-----")
        logger.info("Active %d orders:" %
                    (len(self.orders[settings.REVERSE_SIDE]) +
                     len(self.orders[settings.GRID_SIDE])))

        if len(self.orders[settings.REVERSE_SIDE]) > 0:
            for order in reversed(self.orders[settings.REVERSE_SIDE]):
                logger.info(
                    f"{order['side']}, {order['orderQty']} @ {order['price']}, "
                    f"Status: {order.get('ordStatus', 'noStatus')}")

        if len(self.orders[settings.GRID_SIDE]) > 0:
            for order in reversed(self.orders[settings.GRID_SIDE]):
                logger.info(
                    f"{order['side']}, {order['orderQty']} @ {order['price']}, "
                    f"Status: {order.get('ordStatus', 'noStatus')}")


@patch('market_maker.custom_strategy.CustomOrderManager.print_active_order',
       new=MockCustomOrderManager.print_active_order)
@patch('market_maker.custom_strategy.CustomOrderManager.place_orders',
       new=MockCustomOrderManager.place_orders)
@patch('market_maker.custom_strategy.ExchangeInterface.get_ticker',
       new=MockExchangeInterface.get_ticker)
@patch('market_maker.custom_strategy.ExchangeInterface.get_orders',
       new=MockExchangeInterface.get_orders)
@patch('market_maker.custom_strategy.ExchangeInterface.get_position',
       new=MockExchangeInterface.get_position)
@patch('market_maker.custom_strategy.ExchangeInterface.create_bulk_orders',
       new=MockExchangeInterface.create_bulk_orders)
@patch('market_maker.custom_strategy.ExchangeInterface.cancel_bulk_orders',
       new=MockExchangeInterface.cancel_bulk_orders)
@patch('market_maker.custom_strategy.ExchangeInterface.order_by_clOrdID',
       new=MockExchangeInterface.order_by_clOrdID)


class TestScarlettSubprocess(unittest.TestCase):
    def test_first_level(self):

        order_manager = CustomOrderManager()

        #Start Positions
        mock_exchange = MockExchangeInterface()
        mock_exchange.set_position('currentQty', 0)
        mock_exchange.set_position('avgEntryPrice', 4000)
        mock_exchange.set_ticker('last', 4000.0)

        order_manager.place_orders()

        orders = order_manager.exchange.get_orders()
        order_id = orders[0].get('clOrdID')
        mock_exchange.change_order_status(order_id)

        order_manager.place_orders()
        print(mock_exchange.orders)
        mock_exchange.remove_filled_orders()
        # order_manager.exchange.remove_filled_orders()
        # order_manager.place_orders()
        # order_manager.place_orders()
        # print(order_manager.orders)
        print(mock_exchange.orders)







if __name__ == "__main__":
    unittest.main()


