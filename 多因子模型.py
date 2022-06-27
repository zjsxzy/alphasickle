# -*- coding: utf-8 -*-
import os
import pandas as pd
from index_enhance import get_market_data, plot_net_value
from single_factor_test import Backtest_stock
from strategy import run

def main():
    # 常量
    work_dir = os.path.dirname(os.path.dirname(__file__))
    save_path = os.path.join(work_dir, 'backtest')
    # 回测参数
    benchmark = '000300.SH'
    start_date, end_date = '20110101', '20220531'
    strategies = ['gpe-roe-profitg']
    # 根据已计算的历史因子得到历史股票权重
    # 进行回测的每个月必须有组合权重数据
    run(strategies, start_date, end_date)

    #接下来为回测做准备
    stock_wt = pd.read_csv(os.path.join(save_path, 'stock_wt.csv'), index_col=0)
    stock_wt.columns = pd.to_datetime(stock_wt.columns)
    all_codes = stock_wt.index
    market_data = get_market_data(use_pctchg=False)
    benchmarkdata = market_data.loc[benchmark, start_date:end_date].T #基准指数日涨跌幅
    market_data = market_data.loc[all_codes, start_date:end_date] #组合所有股票的日涨跌幅
    #根据优化得到的各月末截面期HS300成分股股票权重,进行回测
    bt = Backtest_stock(market_data=market_data, 
                        start_date=start_date, 
                        end_date=end_date, 
                        benchmarkdata=benchmarkdata, 
                        stock_weights=stock_wt, 
                        use_pctchg=False)
    bt.run_backtest()
    print('回测结束, 进行回测结果分析...')
    summary_yearly = bt.summary_yearly() #回测统计
    summary_yearly.to_csv(os.path.join(save_path, f'回测统计_{start_date}至{end_date}.csv'), encoding='gbk')
    bt.portfolio_record.to_csv(os.path.join(save_path, f'回测净值_{start_date}至{end_date}.csv'), encoding='gbk')
    bt.position_record.to_csv(os.path.join(save_path, f'各期持仓_{start_date}至{end_date}.csv'), encoding='gbk')
    plot_net_value(bt.portfolio_record, benchmark, '多因子模型', save_path, start_date, end_date)

if __name__ == "__main__":
    main()