# encoding: UTF-8

from strategyEngine import *
from backtestingEngine import *
from Test_Model2 import RB_R_L_G_M_Strategy



# 回测脚本    
if __name__ == '__main__':
    symbol = 'TA605'
    
    # 创建回测引擎
    be = BacktestingEngine()
    
    # 创建策略引擎对象
    se = StrategyEngine(be.eventEngine, be, backtesting=True)
    be.setStrategyEngine(se)
    
    # 初始化回测引擎
    be.connectMongo()
    be.loadDataHistory(symbol, "2015/2/5", "2015/4/5")
    
    #创建策略
    setting={}
    setting["LinearReglength"]=25 #线性回归通道线参数
    setting["smoothlength"]=4  #平滑参数
    setting["MACD_fastlength"]=12   
    setting["MACD_slowlength"]=26
    setting["MACD_XAverage_Length"]=9
    setting["RSI_length"]=14 #RSI指标参数
    setting["ROC_length"]=5 #ROC指标的参数 
    setting["StopLoss_N1"]=3 #移动止损参数1
    setting["StopLoss_N2"]=2 #移动止损参数2
    setting["StopLoss_N3"]=50 #移动止损参数3
    setting["Gallery_LN1"]=1 #内层通道参数
    setting["Gallery_LN2"]=2 #外层通道参数
    setting["ATRlength"]=10 #ATR参数  
    setting['fastAlpha'] = 0.2
    setting['slowAlpha'] = 0.05
#     setting['startDate'] = datetime(year=2015, month=5, day=20)
    se.createStrategy(u"线性回归线通道策略","TA605",RB_R_L_G_M_Strategy,setting)
    
    # 启动所有策略
    se.startAll()
    
    # 开始回测
    be.startBacktesting()
    

