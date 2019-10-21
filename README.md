# rqalpha参数优化模块

rqalpha自带的数据源在使用池化资源进行参数优化时会造成内存泄露，该插件解决了该问题并封装了参数优化方法

### 修改日志
20191019 
增加了修改回测起始时间的办法

## 安装方法
在Terminal中运行以下命令
```
$ pip install git+https://github.com/xingetouzi/rqalpha-mod-optimization.git
$ rqalpha mod install optimization
```
或者: 
```
$ git clone 
$ sh reinstall.sh
```

## rqalpha中关于外部参数传入的方案
在rqalpha中，如需从外部向策略中传入参数，可以设置如下项```config["extra"]["context_vars"]```：
```
config = {
    "extra": {
        "context_vars": {
                "SHORTPERIOD": short_period,
                "LONGPERIOD": long_period,
                ...
            },
            ...
        },
        ...
    }
    ...
```

这样参数就会被添加到context的对应项，下面是一个对应的策略示例：
```
from rqalpha.api import *
import talib

def init(context):
    context.PARAM_A = 20
    context.PARAM_B = 120
    print("Param value after init:")
    print(context.PARAM_A, context.PARAM_B)
    print("Param value in handle_bar:")

def handle_bar(context, bar_dict):
    print(context.PARAM_A, context.PARAM_B)


if __name__ == "__main__":
    import os
    from rqalpha import run

    para_a = 10
    para_b = 110
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
        },
    }
    run(config)
```

将以上代码保存到文件运行，得到以下输出:
```
Param value after init:
20 120
Param value in handle_bar:
10 110
10 110
...
```

## 调用Opimizer进行参数优化
1. 创建策略文件，按照上面介绍的方法定义要传入的外部参数，示例：
```
from rqalpha.api import *
import talib


def init(context):
    context.s1 = "000001.XSHE"
    
    ＃定义了两个外部参数SHORTPERIOD和LONGPERIOD
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
```

2. 创建优化入口脚本
```
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
        # 初始化传入基础配置，调用open函数设置要优化的策略文件，调用optimize传入要优化的参数开始优化
        print(result)
        print(result.sort_values(by=["sharpe"], ascending=False))
    except Exception as e:
        logging.exception(e)
        print("******POOL TERMINATE*******")
```
