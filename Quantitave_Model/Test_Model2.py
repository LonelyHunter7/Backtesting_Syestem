# encoding: UTF-8

#首先引入系统模块
import sys
sys.path.append(r"E:\MAIZIPYTHON\Quantitave_Strategy_Model\vn.strategy\strategydemo")
from datetime import datetime,timedelta,time
from time import sleep 
import numpy as np
import pandas as pd
from pandas import Series,DataFrame

#引入第三方模块
import sip
from PyQt4 import QtCore
import talib
import numpy as np
from pandas import Series,DataFrame

#引入自己写的模块
from demoEngine import MainEngine
from backtestingEngine import *
from strategyEngine import *

########################################################################
class RB_R_L_G_M_Strategy(StrategyTemplate):
    """线性回归通道模型"""
    def __init__(self,name,symbol,engine):
        """Constructor"""
        super(RB_R_L_G_M_Strategy,self).__init__(name,symbol,engine)
        self.be=BacktestingEngine()
        
        """策略的相关设置"""
        self.fastAlpha = 0.2    # 快速EMA的参数
        self.slowAlpha = 0.05   # 慢速EMA的参数
        self.fastEMA = 0        # 快速EMA的数值
        self.slowEMA = 0        # 慢速EMA的数值
        #指标名设置，具体的值在策略方法中进行计算
        self.ATR=0  #ATR指标
        self.midline=0 #通道中线
        self.upperband1=0 #通道上内层线
        self.lowerband1=0 #通道下内层线
        self.upperband2=0 #通道上外层线
        self.lowerband2=0 #通道下外层
        self.RSI_Average=0 #RSI指标
        self.ROC_Value=0 #ROC指标，这里指的是5日简单均线的ROC指标
        self.ma5=0 #5日简单平均线
        self.ma20=0 #20日简单平均线
        
        #策略需要用到的参数，也可以在外部进行设置
        self.LinearReglength=0 #线性回归线
        self.smoothlength=0 #平滑参数
        self.MACD_fastlength=0 
        self.MACD_slowlength=0
        self.MACD_XAverage_Length=0
        self.RSI_length=0
        self.ROC_length=0
        self.StopLoss_N1=0 #移动止损参数1
        self.StopLoss_N2=0 #移动止损参数2
        self.StopLoss_N3=0 #移动止损参数3
        self.Gallery_LN1=0 #内层通道参数
        self.Gallery_LN2=0 #外层通道参数
        self.ATRlength=0 #ATR参数

        #最新一根tick数据的缓存
        self.currentTick=0 
        
        #K线数据的缓存
        self.barOpen=0
        self.barHigh=0
        self.barLow=0
        self.barClose=0
        self.Volume=0
        self.barTime=None
        
        #保存K线数据的李彪
        self.listOpen=[]
        self.listHigh=[]
        self.listLow=[]
        self.listClose=[]
        self.listVolume=[]
        self.listTime=[]
        
        #账户仓位
        self.pos=0
        
        self.var=0
        self.countGet=0
        
        self.five_minute_bar=DataFrame(np.arange(1440).reshape((6,240)),
                                  columns=range(240),
                                  index=["barOpen","barHigh","barLow","barClose","barVolume","barTime"])
        
        #初始化是否完成
        self.initCompleted=False
        
        #读取历史数据的开始日期
        self.startdata=0
        
    #----------------------------------------------------------------------
    def loadSetting(self,setting):
        """读取参数"""
        try:
           self.LinearReglength=setting["LinearReglength"]  #线性回归通道线参数
           self.smoothlength=setting["smoothlength"] #平滑参数
           self.MACD_fastlength=setting["MACD_fastlength"] 
           self.MACD_slowlength=setting["MACD_slowlength"]
           self.MACD_XAverage_Length=setting["MACD_XAverage_Length"]
           self.RSI_length=setting["RSI_length"] #RSI指标参数
           self.ROC_length=setting["ROC_length"]
           self.StopLoss_N1=setting["StopLoss_N1"] #移动止损参数1
           self.StopLoss_N2=setting["StopLoss_N2"] #移动止损参数2
           self.StopLoss_N3=setting["StopLoss_N3"] #移动止损参数3
           self.Gallery_LN1=setting["Gallery_LN1"] #内层通道参数
           self.Gallery_LN2=setting["Gallery_LN2"] #外层通道参数
           self.ATRlength=setting["ATRlength"] #ATR参数
           setting['fastAlpha'] = 0.2
           setting['slowAlpha'] = 0.05
           self.engine.writeLog(self.name+u"读取参数成功")
        except KeyError:
            self.engine.writeLog(self.name+u"读取参数错误，检查读取参数设置")
            
        try:
            self.initStrategy(setting["startData"])
        except KeyError:
            self.initStrategy()    
            
    #----------------------------------------------------------------------
    def initStrategy(self,startData=None):
        """初始化策略"""
        self.initCompleted=True
        self.engine.writeLog(self.name+u"初始化完成")
#         td=timedelta(days=3) #建立三天的时间间隔
#          
#         if startData:
#             cx=self.engine.loadTick(self.symbol,startData-td)
#         else:
#             today=datetime.today().replace(hour=0,minute=0,second=0,microsecond=0)
#             cx=self.engine.loadTick(self.symbol,today-td)
#             
#         if cx:
#             tick=Tick(self.symbol)
#             
#             for data in cx:
#                 #tick的各项数据
#                 tick = Tick(data['InstrumentID'])
#             
#                 tick.openPrice = data['OpenPrice']
#                 tick.highPrice = data['HighestPrice']
#                 tick.lowPrice = data['LowestPrice']
#                 tick.lastPrice = data['LastPrice']
#                 
#                 tick.volume = data['Volume']
#                 tick.openInterest = data['OpenInterest']
#                 
#                 tick.upperLimit = data['UpperLimitPrice']
#                 tick.lowerLimit = data['LowerLimitPrice']
#                 
#                 tick.time = data['UpdateTime']
#                 tick.ms = data['UpdateMillisec']
#                 
#                 tick.bidPrice1 = data['BidPrice1']
#                 tick.bidPrice2 = data['BidPrice2']
#                 tick.bidPrice3 = data['BidPrice3']
#                 tick.bidPrice4 = data['BidPrice4']
#                 tick.bidPrice5 = data['BidPrice5']
#                 
#                 tick.askPrice1 = data['AskPrice1']
#                 tick.askPrice2 = data['AskPrice2']
#                 tick.askPrice3 = data['AskPrice3']
#                 tick.askPrice4 = data['AskPrice4']
#                 tick.askPrice5 = data['AskPrice5']   
#                 
#                 tick.bidVolume1 = data['BidVolume1']
#                 tick.bidVolume2 = data['BidVolume2']
#                 tick.bidVolume3 = data['BidVolume3']
#                 tick.bidVolume4 = data['BidVolume4']
#                 tick.bidVolume5 = data['BidVolume5']
#                 
#                 tick.askVolume1 = data['AskVolume1']
#                 tick.askVolume2 = data['AskVolume2']
#                 tick.askVolume3 = data['AskVolume3']
#                 tick.askVolume4 = data['AskVolume4']
#                 tick.askVolume5 = data['AskVolume5']   
#                 
#                 self.onTick(tick)
            
                
            
                
    #----------------------------------------------------------------------    
    def onTick(self,tick):
        """行情更新的相关处理，
                                这里的重点是用tick数据合成5分钟的bar数据"""
        
        td=timedelta(minutes=5)       
        self.currentTick=tick
        ticktime=datetime.strptime(tick.time,"%Y/%m/%d %H:%M:%S")

        #检查是否是接收第一笔tick
        if self.barOpen == 0:
            # 初始化新的K线数据
            self.barOpen = tick.openPrice
            self.barHigh = tick.highPrice
            self.barLow = tick.lowPrice
            self.barClose = tick.lastPrice
            self.barVolume = tick.volume
            self.barTime = ticktime
        else:
             # 如果是当前一分钟内的数据
            if ticktime-self.barTime <=td:
                 # 汇总TICK生成K线   
                self.barHigh = max(self.barHigh, tick.lastPrice)
                self.barLow = min(self.barLow, tick.lastPrice)
                self.barClose = tick.lastPrice
                self.barVolume = self.barVolume + tick.volume
                self.barTime = ticktime                
            # 如果是新一分钟的数据
            else:
                # 首先推送K线数据
                self.onBar(self.barOpen, self.barHigh, self.barLow, self.barClose, 
                           self.barVolume, self.barTime)
                   
                # 初始化新的K线数据
                self.barOpen = tick.openPrice
                self.barHigh = tick.highPrice
                self.barLow = tick.lowPrice
                self.barClose = tick.lastPrice
                self.barVolume = tick.volume
                self.barTime = ticktime                
    #----------------------------------------------------------------------        
    def onTrade(self,trade):
        """更新账户仓位"""
        if trade.direction==DIRECTION_BUY:
            self.pos +=trade.volume
#             print(self.name+str(self.pos))
        else:
            self.pos -=trade.volume
#             print(self.name+str(self.pos))
        
        log=self.name+u'当前仓位：'+str(self.pos)
        self.engine.writeLog(u"更新仓位完成")
        
    #----------------------------------------------------------------------          
    def onOrder(self,orderRef):
        """报单更新""" 
        
        pass
 
    #----------------------------------------------------------------------     
    def onStopOrder(self,so):
        """停止单更新"""
        
        pass
    
    #----------------------------------------------------------------------   
    def onBar(self,o,h,l,c,volume,time):
        """K线数据更新的处理，策略中最核心的一步，前面所有的步骤都是为了这一步做准备"""
        #保存K线数据到K线列表中
#         print(c)
        self.listOpen.append(o)
        self.listHigh.append(h)
        self.listLow.append(l)
        self.listClose.append(c)
        self.listVolume.append(volume)
        self.listTime.append(time) 
        
        """具体的策略"""
        #首先进行一下格式转换，把list转换为talib需要的array数组格式
        self.listClose=[float(x) for x in self.listClose]
        open=np.array(self.listOpen)
        high=np.array(self.listHigh)
        low=np.array(self.listLow)
        close=np.array(self.listClose)
#         print(close)
        

        
        #获取合约的最小价格跳动
#         contract=self.engine.mainEngine.selectInstrument(self.symbol)
#         priceTick=contract["PriceTick"]
        
        #进场信号
        """进场信号是利用到通道的穿越，包括通道里层线和通道外层线的穿越，
                                这个模型策略非常简单，后期可以以这个为蓝本，发展出更多的模型"""
                                
        #进场信号相关计算
        if self.fastEMA:
            self.fastEMA = c*self.fastAlpha + self.fastEMA*(1-self.fastAlpha)
            self.slowEMA = c*self.slowAlpha + self.slowEMA*(1-self.slowAlpha)
        else:
            self.fastEMA = c
            self.slowEMA = c
        self.ma5=talib.MA(close,timeperiod=5)
        self.ma20=talib.MA(close,timeperiod=20)
             
        if self.initCompleted:      # 首先检查是否是实盘运行还是数据预处理阶段
            # 快速EMA在慢速EMA上方，做多
            if  self.currentTick.lastPrice> self.ma5[-1] and self.ma5[-1] > self.ma20[-1]:
                # 如果当前手头无仓位，则直接做多
                if self.pos == 0:
                    # 涨停价买入开仓
                    self.buy(self.currentTick.lastPrice, 1,self.currentTick.time)
#                     print(self.name+u":进场信号，买入开仓一手")
                    print(self.currentTick.time)
                # 手头有空仓，则先平空，再开多
                elif self.pos < 0:
                    self.cover(self.currentTick.lastPrice, 1,self.currentTick.time)
#                     print(self.name+u":平仓信号，买入平仓一手")
#                     print(self.currentTick.time)
                    self.buy(self.currentTick.lastPrice, 1,self.currentTick.time)
#                     print(self.name+u":进场信号，买入开仓一手(平仓后)")
#                     print(self.currentTick.time)
             
            # 反之，做空
            elif self.currentTick.lastPrice < self.ma5[-1] and self.ma5[-1] < self.ma20[-1]:
                if self.pos == 0: 
                    self.short(self.currentTick.lastPrice, 1,self.currentTick.time)
#                     print(self.currentTick.time)
#                     print(self.name+u":进场信号一，卖出开仓一手")
                elif self.pos > 0:
                    self.sell(self.currentTick.lastPrice, 1,self.currentTick.time)
#                     print(self.currentTick.time)
#                     print(self.name+u":平仓信号一，卖出平仓一手")
                    self.short(self.currentTick.lastPrice, 1,self.currentTick.time)
#                     print(self.currentTick.time)
#                     print(self.name+u":进场信号一，卖出开仓一手(平仓后)")
             
            # 记录日志
#             log= self.name + u'，K线时间：' + str(time) + '\n' + \
#             u'，当前价格：' + str(self.currentTick.lastPrice) + u'，5日平均线：' + str(self.ma5)
#             print(log)
        

    #----------------------------------------------------------------------       
    def strToTime(self, t, ms):
        """从字符串时间转化为time格式的时间"""
        hh, mm, ss = t.split(':')
        tt = time(int(hh), int(mm), int(ss), microsecond=ms)
        return tt

########################################################################
def print_Log(event):
    log=event.dict_["log"]
    print(str(datetime.now())+u","+log)
    
########################################################################
# def main():
#     """在CMD中演示策略"""
#     #创建pyqt应用对象
#     app = QtCore.QCoreApplication(sys.argv)
# 
#     #引入主策略
#     me=MainEngine()
#     
#     #注册打印日志事件监听函数到相关事件上去
#     me.ee.register(EVENT_LOG,print_Log)
#     
#     #登陆
#     userid = '044025'
#     password = 'e67726802'
#     brokerid = '9999'
#     mdAddress = 'tcp://180.168.146.187:10011'
#     tdAddress = 'tcp://180.168.146.187:10001'
#     
#     me.login(userid, password, brokerid, mdAddress, tdAddress)
#     
#     #阻塞10秒，用于读取合约等
#     sleep(5)
#     
#     #创建策略引擎
#     se=StrategyEngine(me.ee,me)
#     
#     #创建策略
#     setting={}
#     setting["LinearReglength"]=25 #线性回归通道线参数
#     setting["smoothlength"]=4  #平滑参数
#     setting["MACD_fastlength"]=12   
#     setting["MACD_slowlength"]=26
#     setting["MACD_XAverage_Length"]=9
#     setting["RSI_length"]=14 #RSI指标参数
#     setting["ROC_length"]=5 #ROC指标的参数 
#     setting["StopLoss_N1"]=3 #移动止损参数1
#     setting["StopLoss_N2"]=2 #移动止损参数2
#     setting["StopLoss_N3"]=50 #移动止损参数3
#     setting["Gallery_LN1"]=1 #内层通道参数
#     setting["Gallery_LN2"]=2 #外层通道参数
#     setting["ATRlength"]=10 #ATR参数  
#     se.createStrategy(u"线性回归线通道策略","TA605",RB_R_L_G_M_Strategy,setting)
#     
#     #开始所有策略
#     se.startAll()
#     
#     #让策略连续运行
#     sys.exit(app.exec_())
# 
# ########################################################################
# if __name__=="__main__":
#     main()    

