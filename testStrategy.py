# encoding: UTF-8

# 首先写系统内置模块
import sys 
from datetime import datetime,timedelta,time
from time import sleep

# 首先写系统内置模块
import sip
import PyQt4

# 然后是自己编写的模块
from demoEngine import MainEngine
from strategyEngine import *


########################################################################
class SimpleEmaStrategy(StrategyTemplate):
    """简单ema均线策略"""

    def __init__(self,name,symbol,engine):
        """constructor""""
        super(SimpleEmaStrategy,self).__init__(self,name,symbol,engine)
        
        #策略的外部参数设置
        self.fastAlpha=0.2 #快线ema的参数
        self.slowAlpha0.05 #慢线ema的参数
        
        #最新的tick数据值(市场最新成交价)
        self.currenttick=0
        
        #K线数据的缓存
        self.barOpen=0
        self.barHigh=0
        self.barLow=0
        self.barClose=0
        self.volume=0
        self.barTime=None
        
        #存储K线数据的列表对象
        self.listOpen=[]
        self.listHigh=[]
        self.listLow=[]
        self.listClose=[]
        self.listVolume=[]
        self.listTime=[]
        
        #ema均线
        self.emafast=0 #ema快线
        self.emaslow=0 #ema慢线
        
        #持仓
        self.pos=0 
        
        #报单列表
        self.listOrder=[] #报单列表
        self.listStopOrder=[] #停止单列表
        
        #是否完成初始化
        self.initCompleted = False
        
        #在初始化时读取历史数据的时期，可以在外部设置
        self.startData=None
        
    #----------------------------------------------------------------------
    def loadSetting(self,setting):
        """读取参数设置"""
        try:
            self.fastAlpha=setting["fastAlpha"]
            self.slowAlpha=setting["slowAlpha"]
            self.engine.writelog(self.name+u"读取参数成功")
        except KeyError:
            self.engine.writelog(self.name+u"读取参数失败，请检查参数设置是否正确")
            
        try:
            self.initStrategy(setting["startData"])
        except KeyError:
            self.initStrategy()
            
    #----------------------------------------------------------------------
    def initStrategy(self,startData=None):
        """初始化"""
        td=timedelta(days=3) #生成一个三天的时间间隔
                    
        if startData:
            cx=self.engine.loadTick(self.symbol,startData-td)
        else:
            today=datetime.today().replace(hour=0,minute=0,second=0,micsecond=0) #将小时以后的时间表示全部设置为0 
            cx=self.engine.loadTick(self.symbol,today-3)
            
        if cx: #如果TICK数据的列表存在
            tick=Tick(self.symbol)
            for data in cx:
            
                #ohlc
                tick.openPrice=data["OpenPrice"]
                tick.highPrice=data["HighestPrice"]
                tick.lowPrice=data["LowestPrice"]
                tick.lastPrice=data["LastPrice"]
                
                tick.volume=data["Volume"]
                tick.openIntrest=["OpenIntrest"]
                
                tick.upperLimit=data["UpperLimit"]
                tick.lowerLimit=data["LowerLimit"]
                
                tick.time=data["Updatetime"]
                tick.ms=data["Update"]
        
                tick.bidPrice1=data["BidPrice1"]
                tick.bidPrice2=data["BidPrice2"]
                tick.bidPrice3=data["BidPrice3"]
                tick.bidPrice4=data["BidPrice4"]
                tick.bidPrice5=data["BidPrice5"]
                
                tick.askPrice1=data["AskPrice1"]
                tick.askPrice2=data["AskPrice2"]
                tick.askPrice3=data["AskPrice3"]
                tick.askPrice4=data["AskPrice4"]
                tick.askPrice5=data["AskPrice5"]
                
                tick.bidVolume1=data["BidVolume1"]
                tick.bidVolume2=data["BidVolume2"]
                tick.bidVolume3=data["BidVolume3"]
                tick.bidVolume4=data["BidVolume4"]
                tick.bidVolume5=data["BidVolume5"]
 
                tick.askVolume1=data["AskVolume1"]
                tick.askVolume2=data["AskVolume2"]
                tick.askVolume3=data["AskVolume3"]
                tick.askVolume4=data["AskVolume4"]
                tick.askVolume5=data["AskVolume5"]
                
                self.onTick(tick)
            
            self.initCompleted=True
            
            self.engine.writeLog(self.name+u"初始化完成")
            
    #---------------------------------------------------------------------- 
    def onTick(self,tick):
        """行情更新的相关处理"""
        #将最新一根tick数据存入到缓存中
        self.currenttick=tick
        
        #把tick数据中的时间数据格式转换为datetime的数据格式，方便进行比较
        ticktime=datetime.strtotime(tick.time,tick.ms)
        
        #检查是否是接收第一笔tick，如果是
        if self.barOpen==0:
            self.barOpen=tick.lastPrice
            self.barHigh=tick.lastPrice
            self.barLow=tick.lastPrice
            self.barClose=tick.lastPrice
            self.barVolume=tick.volume
            self.barTime=ticktime 
        
        else:
            #如果当前传入的tick数据的一分钟时间和当前bar数据的一分钟时间相同
            if ticktime.minute==self.bartime.minute:
                self.barHigh=max(self.barHigh,tick.lastPrice)
                self.barLow=min(self.barLow,tick.lastPrice)
                self.barClose=tick.lastPrice
                self.barVolume +=tick.volume
                self.barTime=ticktime
                
            else:
                #首先推送数据给onBar
                self.onBar(self.barOpen,self.barHigh,self.barLow,
                           self.barClose,self.Volume,self.bartime)
            
                #对新的一根bar进行赋值    
                self.barOpen=tick.lastPrice
                self.barHigh=tick.lastPrice
                self.barLow=tick.lastPrice
                self.barClose=tick.lastPrice
                self.barvolume=tick.volume
                self.barTime=ticktime 

    #---------------------------------------------------------------------- 
    def onTrade(self,trade):
        """成交更新的相关处理"""
        if trade.direction==DIRECTION_BUY:
            self.pos +=trade.volume
        else:
            self.pos -=trade.volume         
        
        log=self.name+u"当前持仓:"+str(self.pos)
        self.engine.writeLog(log)
       
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
        self.listOpen.append(o)
        self.listHigh.append(h)
        self.listLow.append(l)
        self.listClose.append(c)
        self.listVolume.append(volume)
        self.listTime.append(time)
        
        #计算ema
        if self.fastEma !=0:
            self.fastEma=c*self.fastAlpha+self.fastEma*(1-self.fastAlpha)
            self.slowEma=c*self.slowAlpha+self.slowEma*(1-self.slowAlpha)
        else:
            self.fastEma=c
            self.slowEma=c
            
        #交易逻辑
        if self.initCompleted: #检查初始化是否已经完成
            if self.fastEma >=self.slowEma:
                #快线在慢线之上
                if self.pos==0: 
                    #如果无仓位，那么直接开多仓
                    self.buy(self.currentTick.upperLimit,1)
                if self.pos<0:
                    #如果是空仓，先平仓，再开仓
                    self.cover(self.currentTick.upperLimit,1)
                    self.buy(self.currentTick.upperLimit,1)
                
                if self.pos==0
                    self.short(self.currentTick.lowerLimit,1)
                if self.pos>0
                    self.sell(self.currentTick.lowerLimit,1)
                    self.short(self.currentTick.lowerLimit,1)
 
         log = self.name + u'，K线时间：' + str(time) + '\n' + \
                u'，快速EMA：' + str(self.fastEMA) + u'，慢速EMA：' + \
                str(self.slowEMA)
            self.engine.writeLog(log)
 
 
    def strToTime(self, t, ms):
        """从字符串时间转化为time格式的时间"""
        hh, mm, ss = t.split(':')
        tt = time(int(hh), int(mm), int(ss), microsecond=ms)
        return tt
########################################################################
def print_log(event):
    """打印日志"""
    log=event.dict_["log"]
    print(str(dateime.now()),u",",log)
    
########################################################################
def main:
    """演示策略，也可以说是完成策略的函数"""
    #新建一个Pyqt4对象，用于处理相关事件
    app=PyQt4.QcoreApplication(sys.argv)
    
    #创建主引擎
    me=MainEngine()
    
    #向事件驱动引擎中注册打印日志的事件驱动函数
    me.ee.register(EVENT_LOG,Print_log)
    
    #输入登陆信息
    userid=" "
    password=" "
    brokerid=" "
    mdaddress=" "
    tdaddress=" "
    
    #登陆
    me.login(userid,password,brokerid,mdaddress,tdaddress)
    
    #阻塞10s，用于获取合约等，也可以视情自己调整
    sleep(5)
    
    #创建策略引擎
    se=strategyEngine(me,ee,me)
    
    #创建策略
    setting={}
    setting["fastAlpha"]=0.2
    setting["slowAlpha"]=0.05
    strategyEngine().createStrategy(u"ema策略","TA1601",SimpleEmaStrategy,setting)
    
    #运行所有策略
    se.startAll()
    
    #让程序连续运行
    sys.exit(app.exec())
    
######################################################################## 
if __name__="__main__"
    main()        
          