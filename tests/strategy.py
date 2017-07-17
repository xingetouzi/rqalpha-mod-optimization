from rqalpha.api import *
import talib


def init(context):
    context.s1 = "000001.XSHE"

    context.SHORTPERIOD = 20
    context.LONGPERIOD = 120


def handle_bar(context, bar_dict):
    prices = history_bars(context.s1, context.LONGPERIOD + 1, '1d', 'close')
    # print(prices)
    short_avg = talib.SMA(prices, context.SHORTPERIOD)
    long_avg = talib.SMA(prices, context.LONGPERIOD)

    cur_position = context.portfolio.positions[context.s1].quantity
    shares = context.portfolio.cash / bar_dict[context.s1].close

    if short_avg[-1] < long_avg[-1] and short_avg[-2] > long_avg[-2] and cur_position > 0:
        order_target_value(context.s1, 0)

    if short_avg[-1] > long_avg[-1] and short_avg[-2] < long_avg[-2]:
        order_shares(context.s1, shares)


if __name__ == "__main__":
    import os
    from rqalpha import run


    def get_file_root_relative_path(path):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), path)


    long_period = 50
    short_period = 5
    config = {
        "extra": {
            "context_vars": {
                "SHORTPERIOD": short_period,
                "LONGPERIOD": long_period,
            },
            "log_level": "debug",
        },
        "base": {
            "securities": "stock",
            "matching_type": "current_bar",
            "start_date": "2015-01-01",
            "end_date": "2016-01-01",
            "stock_starting_cash": 100000,
            "benchmark": "000001.XSHE",
            "frequency": "1d",
            "strategy_file": __file__,
            "data_bundle_path": r"E:\Users\BurdenBear\.rqalpha\bundle",
        },
        "mod": {
            # "sys_progress": {
            #     "enabled": True,
            #     "show": True,
            # },
            "sys_analyser": {
                "enabled": True,
                "output_file": get_file_root_relative_path("results/out-{short_period}-{long_period}.pkl".format(
                    short_period=short_period,
                    long_period=long_period,
                ))
            },
            "optimization": {
                "enabled": True
            },
        },
    }
    run(config)
