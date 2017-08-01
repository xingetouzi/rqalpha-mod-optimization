# encoding: utf-8
import logging
import os

from rqalpha_mod_optimization.optimizer import SimpleOptimizeApplication
from rqalpha_mod_optimization.parallel import set_parallel_method, ParallelMethod

params = {
    "SHORTPERIOD": range(3, 20, 2),
    "LONGPERIOD": range(30, 50, 5),
}

config = {
    "extra": {
        "log_level": "verbose",
    },
    "base": {
        "accounts": {"stock": 100000},
        "matching_type": "current_bar",
        "start_date": "2014-01-01",
        "end_date": "2016-01-01",
        "benchmark": "000001.XSHE",
        "frequency": "1d",
        "strategy_file": os.path.join(os.path.dirname(os.path.abspath(__file__)), "strategy.py")
    }
}

if __name__ == "__main__":
    try:
        set_parallel_method(ParallelMethod.DASK)
        result = SimpleOptimizeApplication(config).open("strategy.py").optimize(params)
        print(result)
        print(result.sort_values(by=["sharpe"], ascending=False))
    except Exception as e:
        logging.exception(e)
        print("******POOL TERMINATE*******")
