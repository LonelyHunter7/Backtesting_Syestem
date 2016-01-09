# encoding: UTF-8

#引入系统模块
import csv

#引入第三方模块
import pandas as pd
from pandas import Series,DataFrame
from numpy import cumsum 

 


class TradeData_Analysis():
    """成交记录的数据处理包含三个部分：
    1.数据的预处理,将数据存放在dataframe中
    2.利用dataframe格式的便利，对成交记录进行数理统计分析
    3.将统计分析的结果进行存放"""
    def __init__(self):
        """Constructor"""
        
        #用于存放成交记录的DataFrame容器
        self.frame=None
        
        #绩效分析
        self.profit={} #交易盈利单的字典
        self.loss={} #交易亏损单的字典
        self.total_profit=0 #交易总盈利
        self.total_loss=0 #交易总亏损
        self.retained_porfit=0 #交易净利润
        
        self.total_tradenumber=0 #总交易次数
        self.success_rate=0 #交易成功率
        
        self.continuous_profit_number=0 #最大连续亏损次数
        self.continuous_loss_number=0 #最大连续盈利次数
        
        self.max_retracement=0 #交易最大回撤

    def TradeData_Clean(self,filename):
        """1.成交记录的数据预处理"""
        with open(filename) as f:
            reader=csv.reader(f)
            results=[]
            data_dict={}
            save_index=[]
            for line in reader:
                lines=eval(line[0])
                InstrumentID=lines["InstrumentID"]
                Direction=lines["Direction"] 
                OffsetFlag=lines["OffsetFlag"]
                TradeID=lines["TradeID"]
                Price=lines["Price"] 
                OrderRef=lines["OrderRef"]
                Volume=lines['Volume']
                Time=lines["Time"]
                results=[InstrumentID,Direction,OffsetFlag,TradeID,Price,OrderRef,Volume,Time]
                data_dict[OrderRef]=results    
            self.frame=DataFrame(data_dict).T
            states=["InstrumentID","Direction","OffsetFlag","TradeID","Price","OrderRef",'Volume',"Time"]
            self.frame.columns=states
            indexs=self.frame.index
            for data in indexs:
                data=int(data)
                save_index.append(data)
            self.frame.index=save_index
            self.frame=self.frame.sort_index()
#             print(self.frame)
            
            
    def mathematical_statistics(self):
        """2.成交记录的数理统计"""
        index=0
        resolution=0
        profit_values=[]
        loss_values=[]
        trade=[]
        profit_number=0
        loss_number=0
        profit_numbers=[]
        loss_numbers=[]
        all=[]
        #首先取完整交易的数字，也就是保证计算的交易是偶数次
        if len(self.frame.index) %2==0:
            resolution=len(self.frame.index)
        elif len(self.frame.index)%2 !=0:
            resolution=len(self.frame.index)-1
            
        for index in self.frame.index:
            """用for循环区分出盈利交易和亏损交易，并且加入到相应的字典中去"""
            if index %2==0:
                prices=self.frame.ix[index]["Price"]-self.frame.ix[index-1]["Price"]
                
                if self.frame.ix[index]["Direction"]==1:
                    prices=prices
                elif self.frame.ix[index]["Direction"]==0:
                    prices=0-prices
                
                #将所有的成交值放入到一个列表中，方便进行总交易次数和成功率的计算    
                trade.append(prices)
                #用字典的目的是为了后期盈利曲线的画图
                if prices>0:
                    self.profit[self.frame.ix[index]["Time"]]=prices
                else: 
                    self.loss[self.frame.ix[index]["Time"]]=prices
    
        #交易总盈利
        for time,value in self.profit.items():
            profit_values.append(value)
        self.total_profit=sum(profit_values)*5
        print(self.profit)
        
        #交易总亏损
        for time,value in self.loss.items():
            loss_values.append(value)
        self.total_loss=sum(loss_values)*5
        print(self.loss)
        
        #交易净利润
        self.retained_profit=self.total_profit+self.total_loss
        
        #总交易次数和成功率
        self.total_tradenumber=len(self.profit)+len(self.loss) #交易总次数
        if self.total_tradenumber !=0:
            self.success_rate="%.2f%%" % (float(len(self.profit))*100/float(self.total_tradenumber)) #交易成功率
        
            
        #最大连续盈利次数和最大连续亏损次数
        for line in range(len(trade)):
            if line==0:
                if trade[line]<0:
                    loss_number +=1
                if trade[line]>0:
                    profit_number +=1
                    
            if line>=1:           
                if trade[line]>0 and trade[line-1]>0: 
                    profit_number +=1
                if trade[line]<0 and trade[line-1]<0:
                    loss_number +=1   
                    
                if trade[line]<0 and trade[line-1]>0:
                    profit_numbers.append(profit_number)
                    profit_number=0
                    loss_number +=1
                if trade[line]>0 and trade[line-1]<0:
                    loss_numbers.append(loss_number)
                    loss_number=0
                    profit_number+=1
            if line==len(trade)-1:
                if profit_number>0:
                    profit_numbers.append(profit_number)
                elif loss_number>0:
                    loss_numbers.append(loss_number)
        self.continuous_profit_number=max(profit_numbers)
        self.continuous_loss_number=max(loss_numbers)
        
        #交易最大回测
        #需要用到的变量
        cumsum_profit=cumsum(trade)
        maximum_switch=False
        maximum_value=0
        minimum_swith=False
        minimum_value=0
        retracement=0
        retracement_list=[]
        
        for i in range(len(cumsum_profit)):
            if i>=2:
                if cumsum_profit[i-1]>=cumsum_profit[i-2] and cumsum_profit[i-1]>=cumsum_profit[i]:
                    maximum_switch=True
                    retracement=cumsum_profit[i-1]-cumsum_profit[i]
                    maximum_value=cumsum_profit[i-1]
                    print(retracement)
                
                if maximum_switch==True: 
                    if cumsum_profit[i-1] !=maximum_value and cumsum_profit[i-1]>=cumsum_profit[i]:
                        retracement=retracement+(cumsum_profit[i-1]-cumsum_profit[i])
                    elif cumsum_profit[i-1]<=cumsum_profit[i]:
                        retracement_list.append(retracement)
                        retracement=0
                        maximum_switch=False
            if i==len(cumsum_profit)-1:
                retracement_list.append(retracement)
        
        self.max_retracement=max(retracement_list)
                        

        #打印出各个绩效值
        print(u"交易净  盈利:"+str(self.retained_porfit))
        print(u"交易总盈利:"+str(self.total_profit))
        print(u"交易总亏损:"+str(self.total_loss))
        print(u"总交易次数:"+str(self.total_tradenumber))
        print(u"交易成功率:"+str(self.success_rate))
        print(u"最大连续亏损次数:"+str(self.continuous_profit_number))
        print(u"最大连续盈利次数:"+str(self.continuous_loss_number))
        print(u"交易最大回撤:"+str(self.max_retracement))
        
        
    
            
            
        
        
        
        
        
        
        
        

if __name__=="__main__":
    example=TradeData_Analysis()
    example.TradeData_Clean("E:/test.csv")
    example.mathematical_statistics()