# from market_maker.states import *

def get_last_price():
    mylist = range(38940, 39070, 5)
    for i in mylist:
        yield i * 0.1


# def get_price(side):
#     if side == OrderSide.buy:
#         # уменьшить цену
#         return get_last_price() // 5 * 5
#     elif side == OrderSide.sell:
#         # увелитить цену
#         return self.get_last_price() // 5 * 5
#     else:
#         return False


def get_price():

    mygenerator = get_last_price() # создаём генератор

    for i in mygenerator:
        print('------')
        print('{:.2f}'.format((i//5*5 - 5 )))
        print('{:.2f}'.format(i))
        print('{:.2f}'.format(i // 5 * 5 + 5))
        print((i // 5 * 5 + 5) - (i//5*5 - 5))

get_price()