import concurrent.futures
import multiprocessing
import os

import dask.multiprocessing
import pandas as pd
from dask import delayed, compute
from rqalpha import run


def run_multiprocess(tasks):
    results = []
    while tasks:
        errors = []
        with concurrent.futures.ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
            futures = [executor.submit(run_bt, task) for task in tasks]
            concurrent.futures.wait(futures)
            for task, futures in zip(tasks, futures):
                try:
                    results.append(futures.result())
                except Exception as e:
                    errors.append(task)
        tasks = errors
    return pd.DataFrame(results)


def run_raw_multiprocess(tasks):
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count(), maxtasksperchild=1)
    results = pool.map(run_bt, tasks)
    return pd.DataFrame(results).set_index(list(tasks[0]["extra"]["context_vars"].keys()))


def run_dask_multiprocess(tasks):
    all_delayed = [delayed(run_bt)(task) for task in tasks]
    results = list(compute(*all_delayed, get=dask.multiprocessing.get))
    return pd.DataFrame(results).set_index(list(tasks[0]["extra"]["context_vars"].keys()))


def run_synchronize(tasks):
    results = []
    for task in tasks:
        results.append(run_bt(task))
    return pd.DataFrame(results).set_index(list(tasks[0]["extra"]["context_vars"].keys()))


def run_bt(config):
    run(config)
    file_name = config["mod"]["sys_analyser"]["output_file"]
    result_dict = pd.read_pickle(file_name)
    summary = result_dict["summary"]
    result = {
        "annualized_returns": summary["annualized_returns"],
        "sharpe": summary["sharpe"],
        "max_drawdown": summary["max_drawdown"],
    }
    for k, v in zip(config["extra"]["context_vars"].keys(), os.path.basename(file_name).split(".")[0].split("-")[1:]):
        result[k] = float(v)
        # print("Before %s " % str(gc.get_count()))
        # gc.collect()
        # print("After %s " % str(gc.get_count()))
    return result


class Singleton(type):
    SINGLETON_ENABLED = True

    def __init__(cls, *args, **kwargs):
        cls._instance = None
        super(Singleton, cls).__init__(*args, **kwargs)

    def __call__(cls, *args, **kwargs):
        if cls.SINGLETON_ENABLED:
            if cls._instance is None:
                cls._instance = super(Singleton, cls).__call__(*args, **kwargs)
                return cls._instance
            else:
                return cls._instance
        else:
            return super(Singleton, cls).__call__(*args, **kwargs)
