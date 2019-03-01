import sys
import unittest
from unittest.mock import patch
from market_maker.utils.mock import MockCustomOrderManager, MockExchangeInterface
from market_maker.custom_strategy import CustomOrderManager
from market_maker.states import *
from market_maker.settings import settings



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
@patch('market_maker.custom_strategy.ExchangeInterface.amend_bulk_orders',
       new=MockExchangeInterface.amend_bulk_orders)
@patch('market_maker.custom_strategy.ExchangeInterface.order_by_clOrdID',
       new=MockExchangeInterface.order_by_clOrdID)


class TestScarlettSubprocess(unittest.TestCase):
    # def test_first_level(self):
    #     order_manager = CustomOrderManager()
    #
    #     #Start Positions
    #     mock_exchange = MockExchangeInterface()
    #
    #     last = 4000
    #     mock_exchange.set_ticker('last', last)
    #     order_manager.place_orders()
    #
    #     buy_orders = order_manager.orders[OrderSide.buy]
    #     sell_orders = order_manager.orders[OrderSide.sell]
    #     buy_orders_price = [o['price'] for o in buy_orders]
    #     sell_orders_price = [o['price'] for o in sell_orders]
    #
    #     reference_buy_orders_price = [last - settings.ORDER_STEP]
    #     reference_sell_orders_price = []
    #
    #     assert reference_buy_orders_price == buy_orders_price
    #     assert reference_sell_orders_price == sell_orders_price


    # def test_fill_grid(self):
    #     order_manager = CustomOrderManager()
    #
    #     # Start Positions
    #     mock_exchange = MockExchangeInterface()
    #
    #     last = 4000
    #     mock_exchange.set_ticker('last', last)
    #     order_manager.place_orders()
    #
    #     filled_depht = 3
    #     reference_sell_orders_price = []
    #     for _ in range(filled_depht):
    #         exchange_orders = order_manager.exchange.get_orders()
    #         buy_exchange_orders = \
    #             list(filter(lambda o: o['side'] == OrderSide.buy, exchange_orders))
    #
    #         order_id = buy_exchange_orders[-1].get('clOrdID')
    #         order_price = buy_exchange_orders[-1].get('price')
    #         mock_exchange.change_order_status(order_id)
    #
    #         order_manager.place_orders()
    #         mock_exchange.remove_filled_orders()
    #
    #         reference_buy_orders_price = [order_price - settings.ORDER_STEP]
    #         reference_sell_orders_price.append(order_price + settings.ORDER_SPREAD)
    #
    #     buy_orders = order_manager.orders[OrderSide.buy]
    #     sell_orders = order_manager.orders[OrderSide.sell]
    #     buy_orders_price = [o['price'] for o in buy_orders]
    #     sell_orders_price = [o['price'] for o in sell_orders]
    #
    #     assert reference_buy_orders_price == buy_orders_price
    #     assert reference_sell_orders_price == sell_orders_price


    # def test_fill_reverse(self):
    #     order_manager = CustomOrderManager()
    #
    #     # Start Positions
    #     mock_exchange = MockExchangeInterface()
    #
    #     last = 4000
    #     mock_exchange.set_ticker('last', last)
    #     order_manager.place_orders()
    #
    #     reference_buy_orders_price = [last - settings.ORDER_STEP]
    #     reference_sell_orders_price = []
    #
    #     filled_depht = 2
    #     reference_sell_orders_price = []
    #     for _ in range(filled_depht):
    #         exchange_orders = order_manager.exchange.get_orders()
    #         buy_exchange_orders = \
    #             list(filter(lambda o: o['side'] == OrderSide.buy, exchange_orders))
    #
    #         order_id = buy_exchange_orders[-1].get('clOrdID')
    #         order_price = buy_exchange_orders[-1].get('price')
    #         mock_exchange.change_order_status(order_id)
    #
    #         order_manager.place_orders()
    #         mock_exchange.remove_filled_orders()
    #
    #         reference_buy_orders_price = [order_price - settings.ORDER_STEP]
    #         reference_sell_orders_price.append(order_price + settings.ORDER_SPREAD)
    #
    #     reverse_depht = 1
    #     for _ in range(reverse_depht):
    #         exchange_orders = order_manager.exchange.get_orders()
    #         sell_exchange_orders = \
    #             list(filter(lambda o: o['side'] == OrderSide.sell, exchange_orders))
    #
    #         order_id = sell_exchange_orders[-1].get('clOrdID')
    #         order_price = sell_exchange_orders[-1].get('price')
    #         mock_exchange.change_order_status(order_id)
    #
    #         order_manager.place_orders()
    #         mock_exchange.remove_filled_orders()
    #
    #         reference_buy_orders_price = [order_price - settings.ORDER_SPREAD]
    #         reference_sell_orders_price.pop()
    #
    #     buy_orders = order_manager.orders[OrderSide.buy]
    #     sell_orders = order_manager.orders[OrderSide.sell]
    #     buy_orders_price = [o['price'] for o in buy_orders]
    #     sell_orders_price = [o['price'] for o in sell_orders]
    #
    #     order_manager.place_orders()
    #     order_manager.place_orders()
    #
    #     print(reference_buy_orders_price)
    #     print(buy_orders_price)
    #
    #     assert reference_buy_orders_price == buy_orders_price
    #     assert reference_sell_orders_price == sell_orders_price



    # def test_last_price_over_order_price(self):
    #     order_manager = CustomOrderManager()
    #
    #     # Start Positions
    #     mock_exchange = MockExchangeInterface()
    #
    #     last = 3800
    #     mock_exchange.set_ticker('last', last)
    #     mock_exchange.set_position('avgEntryPrice', 3818.1055)
    #     mock_exchange.set_position('currentQty', 30)
    #     order_manager.place_orders()
    #
    #     buy_orders = order_manager.orders[OrderSide.buy]
    #     sell_orders = order_manager.orders[OrderSide.sell]
    #     buy_orders_price = [o['price'] for o in buy_orders]
    #     sell_orders_price = [o['price'] for o in sell_orders]
    #     #
    #     # print(buy_orders_price)
    #     # print(sell_orders_price)
    #
    #     assert buy_orders_price == [3799]
    #     assert sell_orders_price ==[3821, 3820, 3819]
    #
    #     #---------------------
    #     exchange_orders = order_manager.exchange.get_orders()
    #     sell_exchange_orders = \
    #         list(filter(lambda o: o['side'] == OrderSide.sell, exchange_orders))
    #
    #     order_id = sell_exchange_orders[-1].get('clOrdID')
    #     mock_exchange.change_order_status(order_id)
    #
    #     order_manager.place_orders()
    #     mock_exchange.remove_filled_orders()
    #
    #     buy_orders = order_manager.orders[OrderSide.buy]
    #     sell_orders = order_manager.orders[OrderSide.sell]
    #     buy_orders_price = [o['price'] for o in buy_orders]
    #     sell_orders_price = [o['price'] for o in sell_orders]
    #     #
    #     # print(buy_orders_price)
    #     # print(sell_orders_price)
    #
    #     assert buy_orders_price == [3800]
    #     assert sell_orders_price ==[3821, 3820]
    #
    #     # ---------------------
    #     exchange_orders = order_manager.exchange.get_orders()
    #     sell_exchange_orders = \
    #         list(filter(lambda o: o['side'] == OrderSide.sell, exchange_orders))
    #
    #     order_id = sell_exchange_orders[-1].get('clOrdID')
    #     mock_exchange.change_order_status(order_id)
    #
    #     order_manager.place_orders()
    #     mock_exchange.remove_filled_orders()
    #
    #     buy_orders = order_manager.orders[OrderSide.buy]
    #     sell_orders = order_manager.orders[OrderSide.sell]
    #     buy_orders_price = [o['price'] for o in buy_orders]
    #     sell_orders_price = [o['price'] for o in sell_orders]
    #
    #     assert buy_orders_price == [3801]
    #     assert sell_orders_price ==[3821]
    #
    #     # ---------------------
    #     exchange_orders = order_manager.exchange.get_orders()
    #     sell_exchange_orders = \
    #         list(filter(lambda o: o['side'] == OrderSide.sell, exchange_orders))
    #
    #     order_id = sell_exchange_orders[-1].get('clOrdID')
    #     mock_exchange.change_order_status(order_id)
    #
    #     order_manager.place_orders()
    #     mock_exchange.remove_filled_orders()
    #
    #     buy_orders = order_manager.orders[OrderSide.buy]
    #     sell_orders = order_manager.orders[OrderSide.sell]
    #     buy_orders_price = [o['price'] for o in buy_orders]
    #     sell_orders_price = [o['price'] for o in sell_orders]
    #
    #     assert buy_orders_price == []
    #     assert sell_orders_price==[]
    #
    #     # ---------------------
    #     order_manager.place_orders()
    #     buy_orders = order_manager.orders[OrderSide.buy]
    #     sell_orders = order_manager.orders[OrderSide.sell]
    #     buy_orders_price = [o['price'] for o in buy_orders]
    #     sell_orders_price = [o['price'] for o in sell_orders]
    #
    #     assert buy_orders_price == [3799]
    #     assert sell_orders_price ==[]

    def test_last_price_over_order_price(self):
        order_manager = CustomOrderManager()

        # Start Positions
        mock_exchange = MockExchangeInterface()

        last = 3810
        mock_exchange.set_ticker('last', last)
        mock_exchange.set_position('avgEntryPrice', 3814)
        mock_exchange.set_position('currentQty', 10)
        order_manager.place_orders()

        buy_orders = order_manager.orders[OrderSide.buy]
        sell_orders = order_manager.orders[OrderSide.sell]
        buy_orders_price = [o['price'] for o in buy_orders]
        sell_orders_price = [o['price'] for o in sell_orders]

        print(buy_orders_price)
        print(sell_orders_price)

        assert buy_orders_price == [3819]
        assert sell_orders_price ==[3821]



if __name__ == "__main__":
    unittest.main()


