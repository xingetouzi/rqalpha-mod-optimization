# encoding: utf-8
import logging
import os

from rqalpha_mod_optimization.utils import run_dask_multiprocess

RESULT_PATH = os.path.join(os.path.dirname(__file__), "results")
os.makedirs(RESULT_PATH, exist_ok=True)

tasks1 = []

for short_period in range(3, 20, 2):
    for long_period in range(30, 180, 5):
        config = {
            "extra": {
                "context_vars": {
                    "SHORTPERIOD": short_period,
                    "LONGPERIOD": long_period,
                },
                "log_level": "error",
            },
            "base": {
                "securities": "stock",
                "matching_type": "current_bar",
                "start_date": "2015-01-01",
                "end_date": "2016-01-01",
                "stock_starting_cash": 100000,
                "benchmark": "000001.XSHE",
                "frequency": "1d",
                "strategy_file": "strategy.py",
                "data_bundle_path": r"E:\Users\BurdenBear\.rqalpha\bundle",
            },
            "mod": {
                # "sys_progress": {
                #     "enabled": True,
                #     "show": True,
                # },
                "sys_analyser": {
                    "enabled": True,
                    "output_file": os.path.join(RESULT_PATH, "out-{short_period}-{long_period}.pkl".format(
                        short_period=short_period,
                        long_period=long_period,
                    ))
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
        print(run_dask_multiprocess(tasks1))
        print(run_dask_multiprocess(tasks1))
    except Exception as e:
        logging.exception(e)
        print("******POOL TERMINATE*******")
