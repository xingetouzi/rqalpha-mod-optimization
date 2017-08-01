# -*- coding: utf-8 -*-
# __author__ = "Morrison"
import os
from datetime import datetime
from itertools import product, chain

import pandas as pd
from rqalpha import run

from rqalpha_mod_optimization.parallel import run_parallel


class AbstractAnalyzer(object):
    def summary(self, tasks, results):
        raise NotImplementedError

    def analysis(self, task, result):
        raise NotImplementedError


class Optimizer(object):
    def __init__(self):
        self._tasks = []
        self._pre_backtest = []
        self._post_backtest = []

    def add_pre_backtest(self, func):
        self._pre_backtest.append(func)

    def add_post_backtest(self, func):
        self._post_backtest.append(func)

    def summit(self, *tasks):
        self._tasks.extend(tasks)

    def clear(self):
        self._tasks = []

    def optimize(self):
        return run_parallel(run_bt, self._tasks, self)


def run_bt(config, self, *args, **kwargs):
    for func in self._pre_backtest:
        config = func(config)
    run(config, *args, **kwargs)
    for func in self._post_backtest:
        config = func(config)


class SimpleOptimizeApplication(object):
    def __init__(self, config):
        self._optimizer = Optimizer()
        self._analyser = SummaryAnalyzer()
        self._base = self._init_config()
        if config:
            self.init(**config)

    @staticmethod
    def _init_config():
        return {
            "extra": {},
            "base": {},
            "mod": {
                "optimization": {
                    "enabled": True
                }
            },
        }

    @staticmethod
    def _union_config(config, extra):
        dct = {}
        for k in set(chain(config.keys(), extra.keys())):
            dct[k] = dict(config.get(k, {}), **extra.get(k, {}))
        return dct

    def open(self, filename):
        self._base["base"]["strategy_file"] = filename
        return self

    def init(self, **kwargs):
        self._base = self._union_config(self._base, kwargs)
        return self

    def optimize(self, params):
        keys = sorted(params.keys())
        ranges = [params[key] for key in keys]
        tasks = []
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        strategy_name = os.path.basename(self._base["base"]["strategy_file"]).replace(".py", "")
        result_root = os.path.join(".", "optimize-%s-%s" % (strategy_name, timestamp))
        try:
            os.makedirs(result_root)
        except OSError as e:
            if e.errno != os.errno.EEXIST:
                raise
        for para in product(*ranges):
            config = self._union_config(self._base, {"extra": {
                "context_vars": {k: v for k, v in zip(keys, para)},
            }})
            param_repr = [str(p) for p in para]
            config["mod"]["sys_analyser"] = {
                "enabled": True,
                "output_file": os.path.join(result_root, "-".join(["out"] + param_repr) + ".pkl")
            }
            tasks.append(config)
        self._optimizer.summit(*tasks)
        return self._analyser.analysis(tasks, self._optimizer.optimize())


class SummaryAnalyzer(object):
    @staticmethod
    def _analysis(args):
        config, result = args
        file_name = config["mod"]["sys_analyser"]["output_file"]
        result_dict = pd.read_pickle(file_name)
        summary = result_dict["summary"]
        result = {
            "annualized_returns": summary["annualized_returns"],
            "sharpe": summary["sharpe"],
            "max_drawdown": summary["max_drawdown"],
        }
        for k, v in zip(sorted(config["extra"]["context_vars"].keys()),
                        os.path.basename(file_name).split(".")[0].split("-")[1:]):
            result[k] = float(v)
        return result

    def analysis(self, tasks, results):
        results = run_parallel(self._analysis, list(zip(tasks, results)))
        return pd.DataFrame(results).set_index(list(tasks[0]["extra"]["context_vars"].keys()))


class GraphicAnalyzer(object):
    results = []
