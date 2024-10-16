# -*- coding: utf-8 -*-
import os
import pandas as pd
import warnings
from single_factor_test import *

warnings.filterwarnings('ignore')  #将运行中的警告信息设置为“忽略”，从而不在控制台显示

#工作目录，存放代码和因子基本信息
work_dir = os.path.dirname(os.path.dirname(__file__))
#经过预处理后的因子截面数据存放目录
factor_path = os.path.join(work_dir, '因子预处理模块', '因子（已预处理）')
#测试结果图表存放目录
sf_test_save_path = os.path.join(work_dir, '单因子检验')
# 股票池目录
stocks_path = os.path.join(work_dir, 'stocks')

def main():
    stocks = '沪深300'
    start_date, end_date = '20120101', '202205031'
    factors = input("请输入待进行检验的因子（以,分隔），'a'为全部因子：")
    if factors == 'a':
        factors = get_factor_names()
    else:
        factors = factors.split(',')

    stock_pool = None
    if stocks != '':
        # 读取股票池
        stocks_file_path = os.path.join(stocks_path, '%s.csv'%(stocks))
        stocks_df = pd.read_csv(stocks_file_path)
        stock_pool = stocks_df.unstack().unique()

    # T检验与IC检验
    # single_factor_test(factors)
    # 分层检验
    layer_division_backtest(factors, start_date, end_date, stock_pool)

if __name__ == '__main__':
    main()
