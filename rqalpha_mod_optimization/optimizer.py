# -*- coding: utf-8 -*-
# __author__ = "Morrison"
import os
from datetime import datetime
from itertools import product, chain

import pandas as pd
from rqalpha import run

from rqalpha_mod_optimization.parallel import run_parallel, set_parallel_method


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

    def optimize(self, *args, **kwargs):
        return run_parallel(run_bt, self._tasks, self, *args, **kwargs)

    def set_parallel_method(self, method):
        set_parallel_method(method)


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

    def optimize(self, params, *args, **kwargs):
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
            param_repr = [str(p).replace(".", "#") for p in para]
            config["mod"]["sys_analyser"] = {
                "enabled": True,
                "output_file": os.path.join(result_root, "-".join(["out"] + param_repr) + ".pkl")
            }
            tasks.append(config)
        self._optimizer.summit(*tasks)
        return self._analyser.analysis(tasks, self._optimizer.optimize(*args, **kwargs))


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
            result[k] = float(v.replace("#", "."))
        return result

    def analysis(self, tasks, results):
        results = run_parallel(self._analysis, list(zip(tasks, results)))
        return pd.DataFrame(results).set_index(list(tasks[0]["extra"]["context_vars"].keys()))


class GraphicAnalyzer(object):
    results = []


class DateOptimizeApplication(SimpleOptimizeApplication):

    def __init__(self, config):
        SimpleOptimizeApplication.__init__(self, config)
        self._analyser = DateSummaryAnalyzer()

    # 加入不同的日期的优化
    def optimize(self, params, dates, *args, **kwargs):
        keys = sorted(params.keys())
        ranges = [params[key] for key in keys]

        dkeys = (dates.keys())
        dranges = [dates[key] for key in dkeys]

        tasks = []
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        strategy_name = os.path.basename(self._base["base"]["strategy_file"]).replace(".py", "")
        result_root = os.path.join(os.path.abspath("."), "optimize-%s-%s" % (strategy_name, timestamp))
        try:
            os.makedirs(result_root)
        except OSError as e:
            if e.errno != os.errno.EEXIST:
                raise
        for para in product(*ranges):
            for da in product(*dranges):
                config = self._union_config(self._base, {"extra": {
                    "context_vars": {k: v for k, v in zip(keys, para)},
                }})
                # 如果起始日期大于结束日期，则不加入
                if (da[0] > da[2]):
                    continue
                if (da[1] >= da[3]):
                    continue
                start_date = "%d-%d-01" %(da[0],da[1])
                end_date = "%d-%d-20" %(da[2],da[3])
                config2 = self._union_config(config, {"base": {
                    "start_date": start_date,
                    "end_date": end_date
                }})
                param_repr = [str(p).replace(".", "#") for p in para]
                start = start_date.replace("-","_")
                end = end_date.replace("-","_")

                config2["mod"]["sys_analyser"] = {
                    "enabled": True,
                    "output_file": os.path.join(result_root, "_".join([start + "_" + end] + param_repr) + ".pkl"),
                    "plot_save_file": os.path.join(result_root, "_".join([start + "_" + end] + param_repr) + ".png")
                }
                tasks.append(config2)

        # 如果debug，则只打印。
        debug = bool(kwargs.get("debug",0))
        if (debug):
            with open("optimizer_debug.txt", "w", encoding='utf-8') as f:
                s = str(tasks)
                f.write(s)
                f.close()
            return pd.DataFrame()

        self._optimizer.summit(*tasks)
        return self._analyser.analysis(tasks, self._optimizer.optimize(*args, **kwargs))


class DateSummaryAnalyzer(SummaryAnalyzer):
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

        params = os.path.basename(file_name).split(".")[0].split("_")
        for k, v in zip(sorted(config["extra"]["context_vars"].keys()),
                        params[6:]):
            result[k] = float(v.replace("#", "."))
        dates = ['start_year', 'start_month', 'start_day', 'end_year', 'end_month', 'end_day']
        for k, v in zip(dates, params[0:6]):
            result[k] = v
        return result

    def analysis(self, tasks, results):
        results = run_parallel(self._analysis, list(zip(tasks, results)))
        return pd.DataFrame(results)
