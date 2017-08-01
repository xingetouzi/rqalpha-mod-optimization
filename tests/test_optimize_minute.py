# encoding: utf-8
import logging

from rqalpha_mod_optimization.optimizer import SimpleOptimizeApplication

params = {
    "SHORTPERIOD": range(3, 11, 2),
    "LONGPERIOD": range(30, 100, 5),
}

config = {
    "extra": {
        "log_level": "verbose",
    },
    "base": {
        "accounts": {"stock": 100000},
        "matching_type": "current_bar",
        "start_date": "2015-01-01",
        "end_date": "2016-01-01",
        "benchmark": "000001.XSHE",
        "frequency": "1m",
    },
    "mod": {
        "fxdayu_source": {
                    "enabled": True,
                    "source": "bundle",
                    "cache_length": 50000
        }
    }
}

if __name__ == "__main__":
    try:
        result = SimpleOptimizeApplication(config).open("strategy.py").optimize(params)
        print(result)
        print(result.sort_values(by=["sharpe"], ascending=False))
    except Exception as e:
        logging.exception(e)
        print("******POOL TERMINATE*******")
