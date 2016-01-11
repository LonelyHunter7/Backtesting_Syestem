# encoding: UTF-8
from _collections import deque
  
  
# Input:LinearReglength(25),smoothlength(3),fastlength(12),slowlength(26),MACDlength(9),
# rlength(12),roclength(2),wlength(14),length(7),N1(3),N2(2),N3(50),LN1(1),LN2(2),atrlength(10);
#    
# vars:minpoint(0),midline(0),upperband1(0),lowerband1(0),upperband2(0),lowerband2(0),ATR(0),mvalue(0),rvalue(0),blongstoped(false),
# bshortstoped(false),rocvalue(0),var1(false),var0(0),var2(0),var3(0),ma5(0),var4(false),var5(false),
# HiAfterEntry(0), LoAfterEntry(0), Stopline(0),ma20(0),flagb(0),flags(0);
#    
# if currentbar>=1 then
# begin
# {entry signal} 
# ATR=AvgTrueRange(atrlength);
# minpoint=MinMove*PriceScale;
# midline=LinearRegValue( C,LinearReglength, 0 ) ;
# upperband1=midline+LN1*ATR;
# lowerband1=midline-LN1*ATR;
# upperband2=midline+LN2*ATR; 
# lowerband2=midline-LN2*ATR;
# var2 = MACD( Close, fastlength, slowlength ) ; 
# var3 = XAverage( var2, MACDLength ) ;
# mvalue = var2 - var3 ; 
# rvalue=Average(RSI(c,14),5); 
# ma5=Average(c,5);
# ma20=XAverage(c,20);
#    
# condition1=c crosses over (upperband1) and c-o>=25*minpoint;
# condition2=close crosses over (upperband2) and c-o>=25*minpoint;
# condition3=c crosses under (lowerband1) and o-c>=25*minpoint; 
# condition4=close crosses under (lowerband2) and o-c>=25*minpoint; 
#    
# if marketposition<>1 and condition2 and ma5>=Average(c,10)  then
# begin
# buy("buy1") 1 share next bar at Open;
# flagb=1;
# end; 
#    
# if marketposition<>1  and mvalue>0  and condition1 then 
# begin  
# buy("buy2") 1 share next bar at Open;
# flagb=2;
# end; 
#    
#    
# if marketposition<>-1 and condition4 and ma5<=Average(c,10) then
# begin
# sellshort("sellshort1") 1 share next bar at Open;
# flags=1;
# end;  
#    
#    
# if marketposition<>-1 and  mvalue<0 and condition3  then
# begin
# sellshort("sellshort2") 1 share next bar at Open;
# flags=2;
# end; 
#    
# {exit signal}
# rocvalue=RateOfChange(Average(C,5) ,roclength);
# if marketposition=1 and rocvalue<=-1  and c<ma5 then 
# begin
# sell("sell1") 1 share next bar at market;
# flagb=0;
# end;
#    
# if marketposition=-1 and rocvalue>=1  and c>ma5 then 
# begin
# buytocover("BT1") 1 share next bar at market;
# flags=0; 
# end;
#    
#      
# if marketposition=1 and C crosses under ma20 and ma20<ma20[3] then 
# begin
# sell("sell2") 1 share next bar at market; 
# flagb=0;
# end;
#       
# if marketposition=-1 and C crosses over ma20 and ma20>ma20[3] then 
# begin
# buytocover("BT2") 1 share next bar at market;
# flags=0;
# end;
#  
#    
# {again entry}
# value10=barssinceentry(1); 
# If (MarketPosition=0 and  marketposition(1)=1 and  c>=highd(value10) and RateOfChange(c,2)>0  
# and  value10<=10)then 
#   begin
#     buy("buy3") 1 share next bar at o;
#     flagb=3;      
#   end;
#      
#   If (MarketPosition=0 and marketposition(1)=-1 and  c<=lowd(value10) and RateOfChange(c,2)<0 and  
#   value10<=10)then
#   begin 
#  sellshort("sellshort3") 1 share next bar at o; 
#  flags=3; 
# end;
#       
#  {stoploss}   
#  setstoploss(500);
#   If (barssinceentry = 0) then
#     HiAfterEntry = High; 
#   If (BarsSinceEntry >= 1) then
#     HiAfterEntry = Maxlist(HiAfterEntry,High); 
#   If (BarsSinceEntry = 0) then 
#     LoAfterEntry = Low; 
#   If (BarsSinceEntry >= 1) then
#     LoAfterEntry = minlist(LoAfterEntry,Low); 
#     
#   if (BarssinceEntry > 0 and MarketPosition = 1 and 
#   (HiAfterEntry>=entryprice*1.02 and HiAfterEntry<entryprice*1.1)) then 
#   begin
#    setstopcontract;
#    setpercenttrailing(entryprice*0.02*bigpointvalue,70);
#     StopLine = HiAfterEntry-N1*ATR;
#     If c<= StopLine then 
#     begin
#       Sell("stopb1")  1 share this bar at c;
#         flagb=0; 
#    end;
#    end;
#       
#   if (BarssinceEntry > 0 and MarketPosition = 1 and HiAfterEntry>=entryprice*1.1) then 
#   begin
#   setstopcontract;
#    setpercenttrailing(entryprice*0.1*bigpointvalue,50);
#     StopLine = HiAfterEntry-N2*ATR;
#     If c<= StopLine then 
#     begin
#       Sell("stopb3") 1 share this bar at c;
#       flagb=0;  
#    end;
#    end;
#       
#      if (BarssinceEntry > 0 and MarketPosition = 1 and HiAfterEntry<entryprice*1.02) then 
#   begin
#     StopLine = entryprice-N3*minpoint;
#     If c crosses under StopLine then 
#     begin
#       Sell("stopb2") 1 share this bar at c;
#       flagb=0; 
#    end;
#    end;
#       
#    If (BarsSinceEntry > 0 and MarketPosition = -1 and 
#    LoAfterEntry>=entryprice*0.9 and LoAfterEntry<entryprice*0.98) then  
#   begin
#     setstopcontract;
#    setpercenttrailing(entryprice*0.02*bigpointvalue,70);
#     StopLine = LoAfterEntry+N1*ATR;
#     If c>= StopLine then begin 
#       BuyToCover("stops1") 1 share this bar at c;
#       flags=0; 
#       end;
#       end;
#          
#    If (BarsSinceEntry > 0 and MarketPosition = -1 and LoAfterEntry<=entryprice*0.9) then  
#   begin
#   setstopcontract;
#    setpercenttrailing(entryprice*0.1*bigpointvalue,50);
#     StopLine = LoAfterEntry+N2*ATR; 
#     If c>= StopLine then begin 
#       BuyToCover("stops3") 1 share this bar at c;
#       flags=0; 
#       end;
#       End;
#          
#             
#    If (BarsSinceEntry > 0 and MarketPosition = -1 and LoAfterEntry>=entryprice*0.98) then  
#   begin
#     StopLine = entryprice+N3*minpoint;
#     If c crosses over StopLine then begin 
#       BuyToCover("stops2") 1 share this bar at c;
#       flags=0; 
#       end;
#       End;
#       end;
#  
 
 
# from pymongo import MongoClient
# import shelve
# # client=MongoClient()
# # tickdb=client["TickDB"]
# # collection=tickdb.mycol
# # collection.insert({"music":"love"})
# # post_id=
# # print(collection)
# "Date","Time","Open","High","Low","Close","TotalVolume"
#  
# f=shelve.open("result.vn")
# listtrade=f["listTrade"]
# print(listtrade)
# 
# 
# 
#  if self.barOpen==0:
#             self.barOpen=tick.openPrice 
#             self.barHigh=tick.highPrice
#             self.barLow=tick.lowPrice
#             self.barClose=tick.lastPrice
#             self.barVolume=tick.volume
#             self.barTime=ticktime
#             
#             
#             
#             
#    def onTick(self,tick):
#         """行情更新的相关处理，
#                                 这里的重点是用tick数据合成5分钟的bar数据"""
#         #将最新一根tick数据存入到缓存中
#         self.currenttick=tick
#         
#         #把tick数据中的时间数据格式转换为datetime的数据格式，方便进行比较
#         ticktime = self.strToTime(tick.time, tick.ms)
#         self.countGet=0
#         five_minute_bar=DataFrame(np.arange(30.).reshape((6,5)),
#                                   columns=["first_minute","2rd_minute","3th_minute","4th_minute","5th_minute"],
#                                   index=["barOpen","barHigh","barLow","barClose","barVolume","barTime"])
#         #检查是否是接收第一笔tick，如果是
#         if self.barOpen==0:
#             self.barOpen=tick.lastPrice
#             self.barHigh=tick.lastPrice
#             self.barLow=tick.lastPrice
#             self.barClose=tick.lastPrice
#             self.barVolume=tick.volume
#             self.barTime=ticktime 
#         
#         else:
#             #如果当前传入的tick数据的一分钟时间和当前bar数据的一分钟时间相同
#             while self.countGet <=5:
#                 
#                 if ticktime.minute==self.barTime.minute:
#                     self.barHigh=max(self.barHigh,tick.lastPrice)
#                     self.barLow=min(self.barLow,tick.lastPrice)
#                     self.barClose=tick.lastPrice
#                     self.barVolume +=tick.volume
#                     self.barTime=ticktime
#                     
#                 else:
#                     self.countGet +=1
#                     obj=series([self.barOpen,self.barHigh,self.barLow,self.barClose,self.barVolume,self.barTime],
#                                index=["barOpen","barHigh","barLow","barClose","barVolume","barTime"])
#                     five_minute_bar[self.counGet-1]=obj
#                     #对新的一根bar进行赋值
#                     self.barOpen=tick.lastPrice
#                     self.barHigh=tick.lastPrice
#                     self.barLow=tick.lastPrice
#                     self.barClose=tick.lastPrice
#                     self.barVolume=tick.volume
#                     self.barTime=ticktime
#                 
#             if self.countGet>5:
#                 self.barOpen=five_minute_bar["first_minute"]["barOpen"]
#                 self.barHigh=five_minute_bar.ix["barHigh"].max()
#                 self.barLow=five_minute_bar.ix["barLow"].min()
#                 self.barClose=five_minute_bar["5th_minute"]["barClose"]
#                 self.barVolume=five_minute_bar.ix["barVolume"].sum()
#                 self.barTime=five_minute_bar["5th_minute"]["barTime"]
#                 #首先推送数据给onBar
#                 self.onBar(self.barOpen,self.barHigh,self.barLow,
#                            self.barClose,self.Volume,self.barTime)
#             
#                 self.countGet=0 
#                            

# from pymongo import MongoClient
# from pymongo import errors
# from datetime import datetime
# time=datetime(2015,5,1)
# 
# 
# 
# #         except ConnectionFailure:
# #             self.writeLog(u'回测引擎连接MongoDB失败') 
#             #----------------------------------------------------------------------
# class test(object):
#     def __init__(self):
#         print("开始测试")
# 
#     def connectMongo(self):
#         """连接MongoDB数据库"""
#         
#         self.__mongoConnection = MongoClient()
#         self.__mongoConnected = True
#         self.__mongoTickDB = self.__mongoConnection['TickDB']
#         print(u'回测引擎连接MongoDB成功')
# #         except ConnectionFailure:
# #             self.writeLog(u'回测引擎连接MongoDB失败') 
#             
#     #----------------------------------------------------------------------
#     def loadDataHistory(self, symbol, startDate, endDate):
#         """载入历史TICK数据"""
#         if self.__mongoConnected:
#             collection = self.__mongoTickDB[symbol]
#             self.symbol=symbol
#             # 如果输入了读取TICK的最后日期
#             if endDate:
#                 cx = collection.find({'Date':{'$gte':startDate, '$lte':endDate}})
#             elif startDate:
#                 cx = collection.find({'Date':{'$gte':startDate}})
#             else:
#                 cx = collection.find()
#                 
#             # 将TICK数据读入内存
#             self.listDataHistory = [data for data in cx]
#             print(self.listDataHistory)
#             
#             print(u'历史TICK数据载入完成')
#         else:
#             print(u'MongoDB未连接，请检查')
#             
# 
# if __name__=="__main__":
#     date="2015/1/5"
#     time="11:00:00"
#     x=date+u" "+time
#     print(x)
# #     mongo=test()
# #     mongo.connectMongo()
# #     mongo.loadDataHistory("TA605", "2015/1/5", "2015/2/5")


# # import shelve
# # f=shelve.open("result.vn")
# # listTrade=f['listTrade']
# # print(listTrade)
# # f.close()
# import pandas as pd
# from pandas import Series,DataFrame
# import csv
# import re 
# results=[]
# data_dict={}
# r=[]
# # frame=DataFrame()
# # print(frame)
# with open("E:/result.csv") as f:
#     reader=csv.reader(f)
#     for line in reader:
#         lines=eval(line[0])
#         
#         InstrumentID=lines["InstrumentID"]
#         Direction=lines["Direction"] 
#         OffsetFlag=lines["OffsetFlag"]
#         TradeID=lines["TradeID"]
#         Price=lines["Price"] 
#         OrderRef=lines["OrderRef"]
#         Volume=lines['Volume']
#         results=[InstrumentID,Direction,OffsetFlag,TradeID,Price,OrderRef,Volume]
#         data_dict[OrderRef]=results
# #     print(data_dict)
#     
#     frame=DataFrame(data_dict).T
#     states=["InstrumentID","Direction","OffsetFlag","TradeID","Price","OrderRef",'Volume']
#     frame.columns=states
#     indexs=frame.index
#     for data in indexs:
#         data=int(data)
#         r.append(data)
#     frame.index=r
#     frame_results=frame.sort_index()
#     print(frame_results)
# #         lines=Series(line)
# #         dataframe[lines]
# #         print(lines)
# #         print(results)
# # rr="rr"
# # ss="sss"
# # list=[rr,ss,999]
# # print(list)
# # x={"ss":"xx","rr":"mm"}
# # y=x["ss"]
# # print(y)
# 
# # x={'InstrumentID': 'TA605', 'Direction': '1', 'OffsetFlag': '0', 'TradeID': '16', 'Price': 4698, 'OrderRef': '17', 'Volume': 1}
# # print(x['InstrumentID'])

# import talib
# import numpy as np
# # real_data = [float(x) for x in [135.01, 133.0, 134.0, 131.0, 133.0, 131.0]]
# real_data = [135, 133, 134, 131, 133, 131]
# np_real_data = np.array(real_data)
# np_out = talib.SMA(np_real_data,3)
# print(np_out)


# tick=range(50)
# # print(range(50))
# def onTick(tick):
#     list_barclose=[]
#     barclose=0
#     countGet=0
#     for data in tick: 
#         if len(list_barclose)<=5:
#             list_barclose.append(data)
#         else:
#             x=max(list_barclose)
#             print(x)
#             list_barclose=[]
#     
# 
# 
# onTick(tick)           
# from pandas import DataFrame,Series
# import numpy as np
# five_minute_bar=DataFrame(np.arange(30.).reshape((6,5)),
#                           columns=["first_minute","2rd_minute","3th_minute","4th_minute","5th_minute"],
#                           index=["barOpen","barHigh","barLow","barClose","barVolume","barTime"])  
# # print(five_minute_bar) 
# obj=Series([5,10,2,3,4,1],index=["barOpen","barHigh","barLow","barClose","barVolume","barTime"])
# print(five_minute_bar.icol(0)["barHigh"])  
# # five_minute_bar.ix[:,3]=obj 
# print(five_minute_bar.ix[:,3])  
# from threading import thread
# 
# list_high=[]
# list_low=[]
# list_close=[]
# list_open=[]
# list_volume=[]
# list_bartime=[]
# 
# def count_pound():
#     if len(list_high)<=5:
#             list_high.append(tick.highPrice)
#     else:
#         self.barHigh=max(list_high)
#         list_high=[]
#              
#             if len(list_low)<=5:
#                 list_low.append(tick.lowPrice)
#             else:
#                 self.barLow=min(list_low)
#                 list_low=[]
#              
#             if len(list_close)<=5:
#                 list_close.append(tick.lastPrice)
#             else:
#                 self.barClose=list_close[-1]
#                 list_close=[]
#                  
#             if len(list_open)<=5:
#                 list_open.append(tick.openPrice)
#             else:
#                 self.barOpen=list_open[0]
#                 list_open=[]  
#                
#             if len(list_volume)<=5:
#                 list_volume.append(tick.volume)
#             else:
#                 self.Volume=sum(list_volume)
#                 list_volume=[]
#                  
#             if len(list_bartime)<=5:
#                 list_bartime.append(ticktime)
#             else:
#                 self.barTime=list_bartime[-1]
#                 list_bartime=[]
#                  
#             self.onBar(self.barOpen,self.barHigh,self.barLow,
#                    self.barClose,self.Volume,self.barTime)    
# from datetime import time,datetime,timedelta
# x="2015/04/28 23:30:00"
# y="2015/04/29 09:00:00"
# r=datetime.strptime(y,"%Y/%m/%d %H:%M:%S")
# m=datetime.strptime(x,"%Y/%m/%d %H:%M:%S")
# # hh,rr=x.split(" ")
# # l,r,s=rr.split(":")
# # t1=time(int(l),int(r),int(s))
# # ss,mm=y.split(" ")
# # q,o,p=mm.split(":")
# # t2=time(int(q),int(o),int(p))
# # t3=t2-t1
# # t2=time(x,"%Y/%m/%d %H:%M:%S")
# # t3=t2-t1
# s=timedelta(hours=23)
# t=datetime.today()
# w=r-m
# t=4
# if  w<=s:
#     print(w)  
# else:
#     print("fail")
from collections import deque
from numpy import cumsum, maximum
# s=[1,2,3,4,5,6,7]
# s.append(1)
# s.append(2)
# # print(s)
# for r in s:
#     print(r)

# animals = {'dog':'dom','tiger':'EN', 'panda':'EN'}
# # for ref, order in self.dictOrder.items():
# for ref,order in animals.items():
#   print(order)
# list_order=[]
# s=dict([('dog', 'dom'), ('tiger', 'EN'), ('panda', 'm'),("2","4")])
# print(len(s))
# for ref,order in s.items():
#     list_order.append(order)
# for i in list_order:
#     print(i)
# x=[2,3,4,5,-5,-2,-1]
# for y in x:
#     if 

# from datetime import datetime,time 
# # d.keys()=[1,2,3,4,5]
# s="2015/3/12 14:50:00"
# g='2015/3/19 13:31:00'
# # for r in y:
# #     peint(e)
# # lists=[]
# # s=datetime.strptime(s,"%Y/%m/%d %H:%M:%S")
# # g=datetime.strptime(g,"%Y/%m/%d %H:%M:%S")
# # d=dict()
# # d[s]=2
# # lists.append(s)
# # lists.append(g)
# # r=sorted([9,3,5,1])
# hh,rr=g.split(" ")
# i=datetime.now()
# s=i.strftime("%Y-%m-%d %H:%M:%S")
# print(type(s))
# # for i in  lists:
#     print(i)

import json
import csv
d={}
d[u"我的爱"]=3
d["y"]=5
f=open(r"E:\my.txt","w")
s=json.dumps(d, encoding='UTF-8', ensure_ascii=False)
b=json.loads(s)
# print(type(b))
# print(s)
# for key in s: 
#     print(key)
# f.close()
 
with open('E:/txt.csv',"w") as f:
        writer=csv.writer(f,delimiter=",")
        for key,value in d.items():
#             print((key,value))
            writer.writerow([key+u":"+str(value)])
#             writer.writerow([value])
        print(u"交易记录储存完毕")

# print(json.dumps(d, encoding='UTF-8', ensure_ascii=False))





