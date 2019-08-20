import math
from decimal import Decimal, getcontext, ROUND_DOWN, ROUND_UP
from sympy import Symbol, solve

from .misc import create_logger
from .config import UPBIT_DECIMAL_PRECISION, CALC_DECIMAL_PRECISION

logger = create_logger("calculator")

getcontext().prec = CALC_DECIMAL_PRECISION

def dec2float(value: Decimal):
    # 계산된 decimal 값을 float으로 변경합니다.
    precision = 0

    def _chk_dp():
        cnt = 0
        for s in str_value:
            if s == "0": cnt += 1
            else: return cnt

    int_value = int(value)

    if int_value == 0: # 0.000xxx 값인 경우 정수값을 유지할 필요가 없습니다.
        str_value = str(value)[2:]
        precision += (UPBIT_DECIMAL_PRECISION - _chk_dp())
    else:
        precision += (len(str(int_value)) + UPBIT_DECIMAL_PRECISION)

    getcontext().prec = precision
    value_float = float(value + Decimal(0)) # type: float
    getcontext().prec = CALC_DECIMAL_PRECISION
    return value_float



# for support KRW trading
# https://docs.upbit.com/docs/market-info-trade-price-detail
# KRW마켓에서 매도 시에도 반영됩니다. (거래 테스트함)
# def get_transactionable_balance(balance: Decimal):
#     return 0

## -> 호가에 반영된다는 의미임. : 테스트 완료. balance에는 정수 단위부터(1원) 사용 가능하다.


def solve_equation(equation):
    return Decimal(str(solve(equation)[0]))


def truncate(value: Decimal):
    return math.trunc(value)


def vt_buy_all(balance, fee, ask_prices: list, ask_amounts: list, isKRW=True):

    amount = Decimal(0)
    is_finished = 0

    def set_buy_amount(ask_price: Decimal, ask_amount: Decimal):
        global balance, amount

        sym_amount = Symbol('sym_amount')
        equation = (sym_amount * ask_price) * fee - balance
        _amount = solve_equation(equation)

        if _amount > ask_amount: # 현재의 거래가 완벽히 끝나지 않고 부분채결이 됨.
            tbanalce = Decimal((ask_amount * ask_price) * fee) # 현재 호가에서 드는 가격 (최대)
            balance -= truncate(tbanalce) if isKRW else tbanalce
            amount += ask_amount # 현재 호가에서 구매 가능한 갯수 - 현재 호가 전체!
            return False

        else:
            balance -= truncate(balance) if isKRW else balance
            amount += _amount
            return True

    for i in range(0, len(ask_prices)):
        _ask_price = ask_prices[i]
        _ask_amount = ask_amounts[i]

        if set_buy_amount(ask_price=_ask_price, ask_amount=_ask_amount):
            is_finished += 1
            break

    if not bool(is_finished):
        logger.critical("vt_buy_all: 최대 호가로 거래를 종결할 수 없음.")
        raise Exception("최대 호가로 거래를 종결할 수 없음.")

    balance = truncate(balance)
    return balance, amount



def vt_sell_all(amount, fee, bid_prices, bid_amounts, isKRW=True):

    balance = Decimal(0)
    is_finished = 0

    def set_sell_balance(bid_price: Decimal, bid_amount: Decimal):
        global balance, amount

        is_continue = 0
        _amount = Decimal(0)
        if amount > bid_amount:
            is_continue += 1
            _amount += bid_amount
        else:
            _amount += amount

        contract_balance = _amount * bid_price
        fee_balance = contract_balance * fee
        _balance = contract_balance - fee_balance # 실제 입금되는 금액은 다음과 같다.

        balance += truncate(_balance) if isKRW else _balance
        amount -= _amount
        return not bool(is_continue)

    for i in range(0, len(bid_prices)):
        _bid_price = bid_prices[i]
        _bid_amount = bid_amounts[i]

        if set_sell_balance(bid_price=_bid_price, bid_amount=_bid_amount):
            is_finished += 1
            break

    if not bool(is_finished):
        logger.critical("vt_sell_all: 최대 호가로 거래를 종결할 수 없음.")
        raise Exception("Error - 최대 호가로 거래를 종결할 수 없습니다.")

    balance = math.trunc(balance) if isKRW else balance
    return balance, amount # 거래화폐가 KRW 단위등으로 남는 경우가 있으므로 거래후 amount까지 남겨놓아야 한다.




