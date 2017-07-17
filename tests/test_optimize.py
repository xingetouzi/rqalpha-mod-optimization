# encoding: utf-8
import logging
import os
from collections import OrderedDict

from rqalpha_mod_optimization.utils import run_dask_multiprocess

RESULT_PATH = os.path.join(os.path.dirname(__file__), "results")
try:
    os.makedirs(RESULT_PATH)
except OSError as e:
    if e.errno != os.errno.EEXIST:
        raise

tasks1 = []

for short_period in range(3, 20, 2):
    for long_period in range(30, 180, 5):
        context_vars = OrderedDict([
            ("SHORTPERIOD", short_period),
            ("LONGPERIOD", long_period),
        ])
        config = {
            "extra": {
                "context_vars": context_vars,
                "log_level": "error",
            },
            "base": {
                "securities": "stock",
                "matching_type": "current_bar",
                "start_date": "2014-01-01",
                "end_date": "2016-01-01",
                "stock_starting_cash": 100000,
                "benchmark": "000001.XSHE",
                "frequency": "1d",
                "strategy_file": os.path.join(os.path.dirname(os.path.abspath(__file__)), "strategy.py"),
                "data_bundle_path": r"E:\Users\BurdenBear\.rqalpha\bundle",
            },
            "mod": {
                # "sys_progress": {
                #     "enabled": True,
                #     "show": True,
                # },
                "sys_analyser": {
                    "enabled": True,
                    "output_file": os.path.join(RESULT_PATH, "-".join(["out"] +
                                                                      [str(v) for v in context_vars.values()]) + ".pkl"
                                                )
                },
                "optimization": {
                    "enabled": True
                },
            },
        }

        tasks1.append(config)

if __name__ == "__main__":
    # gc.set_debug(gc.DEBUG_LEAK)
    try:
        result = run_dask_multiprocess(tasks1)
        print(result)
        print(result.sort_values(by=["sharpe"], ascending=False))
    except Exception as e:
        logging.exception(e)
        print("******POOL TERMINATE*******")
