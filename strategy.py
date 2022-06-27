# -*- coding: utf-8 -*-
import os
import json
import pandas as pd
import numpy as np

work_dir = os.path.dirname(os.path.dirname(__file__))
factor_path = os.path.join(work_dir, '因子预处理模块', '因子（已预处理）')
save_path = os.path.join(work_dir, 'backtest')
strategy_path = os.path.join(work_dir, 'strategy')
stocks_path = os.path.join(work_dir, 'stocks')

def run_single_strategy(config, start_date, end_date):
    '''
    运行单一策略
    '''
    start_date = pd.to_datetime(start_date, format='%Y%m%d')
    end_date = pd.to_datetime(end_date, format='%Y%m%d')
    # 读取股票池
    stocks_file_path = os.path.join(stocks_path, '%s.csv'%config['stocks'])
    stocks_df = pd.read_csv(stocks_file_path)
    # 读取股票池历史上所有的股票
    all_stocks = stocks_df.unstack().unique()
    # 读取在回测区间内的因子数据
    factors_files = [f for f in os.listdir(factor_path)]
    stock_wt = pd.DataFrame(index=all_stocks)
    for f in factors_files:
        factor_file_path = os.path.join(factor_path, f)
        factor_df = pd.read_csv(factor_file_path, encoding='gbk')
        factor_df = factor_df.set_index('code')
        date = pd.to_datetime(f.rstrip('.csv'))
        if (date >= start_date) and (date <= end_date):
            # 提取最近一起的股票池清单
            select_col = None
            for col_date in stocks_df.columns:
                if pd.to_datetime(col_date, format='%Y%m%d') <= date:
                    select_col = col_date
                else:
                    break
            stock_list = stocks_df[select_col]
            # print('股票池共有股票%d只'%(len(stock_list)), select_col)
            # 提取在股票池中的股票因子
            index = factor_df.index.intersection(stock_list)
            print('回测时间：%s，候选股票%d只'%(date.strftime('%Y-%m-%d'), index.size))
            # 计算因子加权得分
            factor_values = factor_df.loc[index, config['factor_weight_method']['factors']]
            if (config['factor_weight_method']['method_name'] == 'given weights'):
                factor_weights = np.array(config['factor_weight_method']['factor_weights'])
            else:
                # 其他因子加权方法待补充
                pass
            stock_values = (factor_values * factor_weights).sum(axis=1)
            # 将得分归一化到0~1
            stock_values = (stock_values - stock_values.min()) / (stock_values.max() - stock_values.min())
            # 从大到小排序后取前K只股票
            stock_values = stock_values.sort_values(ascending=False).head(config['stock_weight_method']['stock_nums'])
            # 给选出的股票赋权重
            if config['stock_weight_method']['method_name'] == 'by factors':
                stock_weights = stock_values / stock_values.sum()
                stock_wt.loc[stock_weights.index, date] = stock_weights
                # print(stock_weights.sort_values(ascending=False).head(n=10))
    stock_wt = stock_wt.dropna(how='all')
    stock_wt_path = os.path.join(save_path, '%s.csv'%(config['strategy_name']))
    stock_wt.to_csv(stock_wt_path)

def run(strategies, start_date, end_date, weights=None):
    '''
    运行多个策略
    '''
    stock_wt = []
    for st in strategies:
        strategy_file_path = os.path.join(strategy_path, '%s.json'%(st))
        with open(strategy_file_path, 'rb') as f:
            strategy_config = json.loads(f.read())
        print(strategy_config)
        run_single_strategy(strategy_config, start_date, end_date)
        strategy_wt_path = os.path.join(save_path, '%s.csv'%(strategy_config['strategy_name']))
        strategy_wt = pd.read_csv(strategy_wt_path, index_col=0)
        stock_wt.append(strategy_wt)
    if len(stock_wt) == 1:
        # 单策略
        stock_wt_path = os.path.join(save_path, 'stock_wt.csv')
        stock_wt[0].to_csv(stock_wt_path)
    else:
        if weights is None: # 默认平均
            weights = [1./len(stock_wt)] * len(stock_wt)
            pass
        elif isinstance(weights, list):
            pass
        else:
            pass
