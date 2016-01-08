# encoding: UTF-8

'''
ibpy的gateway接入

注意事项：
1. ib api只能获取和操作当前连接后下的单，并且每次重启程序后，之前下的单子收不到
2. ib api的成交也只会推送当前连接后的成交
3. ib api的持仓和账户更新可以订阅成主推模式，因此getAccount和getPosition就用不到了
4. 目前只支持股票和期货交易，ib api里期权合约的确定是基于Contract对象的多个字段，比较复杂暂时没做
5. 海外市场的交易规则和国内有很多细节上的不同，所以一些字段类型的映射可能不合理，如果发现问题欢迎指出
'''

import json
from time import sleep, strftime, localtime
from copy import copy

from PyQt4 import QtGui, QtCore

from ib.ext.Contract import Contract
from ib.ext.Order import Order
from ib.ext.EWrapper import EWrapper
from ib.ext.EClientSocket import EClientSocket

from vtGateway import *


# 以下为一些VT类型和CTP类型的映射字典
# 价格类型映射
priceTypeMap = {}
priceTypeMap[PRICETYPE_LIMITPRICE] = 'LMT'
priceTypeMap[PRICETYPE_MARKETPRICE] = 'MKT'
priceTypeMapReverse = {v: k for k, v in priceTypeMap.items()} 

# 方向类型映射
directionMap = {}
directionMap[DIRECTION_LONG] = 'BUY'
directionMap[DIRECTION_SHORT] = 'SSHORT'
directionMap[DIRECTION_SELL] = 'SELL'
directionMapReverse = {v: k for k, v in directionMap.items()}
directionMapReverse['BOT'] = DIRECTION_LONG
directionMapReverse['SLD'] = DIRECTION_SHORT

# 交易所类型映射
exchangeMap = {}
exchangeMap[EXCHANGE_SMART] = 'SMART'
exchangeMap[EXCHANGE_GLOBEX] = 'GLOBEX'
exchangeMap[EXCHANGE_IDEALPRO] = 'IDEALPRO'
exchangeMapReverse = {v:k for k,v in exchangeMap.items()}

# 报单状态映射
orderStatusMap = {}
orderStatusMap[STATUS_NOTTRADED] = 'Submitted'
orderStatusMap[STATUS_ALLTRADED] = 'Filled'
orderStatusMap[STATUS_CANCELLED] = 'Cancelled'
orderStatusMapReverse = {v:k for k,v in orderStatusMap.items()}
orderStatusMapReverse['PendingSubmit'] = STATUS_UNKNOWN     # 这里未来视乎需求可以拓展vt订单的状态类型
orderStatusMapReverse['PendingCancel'] = STATUS_UNKNOWN
orderStatusMapReverse['PreSubmitted'] = STATUS_UNKNOWN
orderStatusMapReverse['Inactive'] = STATUS_UNKNOWN

# 合约类型映射
productClassMap = {}
productClassMap[PRODUCT_EQUITY] = 'STK'
productClassMap[PRODUCT_FUTURES] = 'FUT'
productClassMap[PRODUCT_OPTION] = 'OPT'
productClassMap[PRODUCT_FOREX] = 'CASH'

# 期权类型映射
optionTypeMap = {}
optionTypeMap[OPTION_CALL] = 'CALL'
optionTypeMap[OPTION_PUT] = 'PUT'
optionTypeMap = {v:k for k,v in optionTypeMap.items()}

# 货币类型映射
currencyMap = {}
currencyMap[CURRENCY_USD] = 'USD'
currencyMap[CURRENCY_CNY] = 'CNY'
currencyMap = {v:k for k,v in currencyMap.items()}

# Tick数据的Field和名称映射
tickFieldMap = {}
tickFieldMap[0] = 'bidVolume1'
tickFieldMap[1] = 'bidPrice1'
tickFieldMap[2] = 'askPrice1'
tickFieldMap[3] = 'askVolume1'
tickFieldMap[4] = 'lastPrice'
tickFieldMap[5] = 'lastVolume'
tickFieldMap[6] = 'highPrice'
tickFieldMap[7] = 'lowPrice'
tickFieldMap[8] = 'volume'
tickFieldMap[14] = 'openPrice'
tickFieldMap[20] = 'openInterest'

# Account数据Key和名称的映射
accountKeyMap = {}
accountKeyMap['NetLiquidationByCurrency'] = 'balance'
accountKeyMap['NetLiquidation'] = 'balance'
accountKeyMap['UnrealizedPnL'] = 'positionProfit'
accountKeyMap['AvailableFunds'] = 'available'
accountKeyMap['MaintMarginReq'] = 'margin'


########################################################################
class IbGateway(VtGateway):
    """IB接口"""

    #----------------------------------------------------------------------
    def __init__(self, eventEngine, gatewayName='IB'):
        """Constructor"""
        super(IbGateway, self).__init__(eventEngine, gatewayName)
        
        self.host = EMPTY_STRING        # 连接地址
        self.port = EMPTY_INT           # 连接端口
        self.clientId = EMPTY_INT       # 用户编号
        
        self.tickerId = 0               # 订阅行情时的代码编号    
        self.tickDict = {}              # tick快照字典，key为tickerId，value为VtTickData对象
        
        self.orderId  = 0               # 订单编号
        self.orderDict = {}             # 报单字典，key为orderId，value为VtOrderData对象
        
        self.accountDict = {}           # 账户字典
        
        self.connected = False          # 连接状态
        
        self.wrapper = IbWrapper(self)                  # 回调接口
        self.connection = EClientSocket(self.wrapper)   # 主动接口

    #----------------------------------------------------------------------
    def connect(self):
        """连接"""
        # 载入json文件
        fileName = self.gatewayName + '_connect.json'
        try:
            f = file(fileName)
        except IOError:
            log = VtLogData()
            log.gatewayName = self.gatewayName
            log.logContent = u'读取连接配置出错，请检查'
            self.onLog(log)
            return
        
        # 解析json文件
        setting = json.load(f)
        try:
            self.host = str(setting['host'])
            self.port = int(setting['port'])
            self.clientId = int(setting['clientId'])
        except KeyError:
            log = VtLogData()
            log.gatewayName = self.gatewayName
            log.logContent = u'连接配置缺少字段，请检查'
            self.onLog(log)
            return            
        
        # 发起连接
        self.connection.eConnect(self.host, self.port, self.clientId)
        
        # 查询服务器时间
        self.connection.reqCurrentTime()
        
        # 请求账户数据主推更新
        self.connection.reqAccountUpdates(True, '')
    
    #----------------------------------------------------------------------
    def subscribe(self, subscribeReq):
        """订阅行情"""
        # 订阅行情
        self.tickerId += 1
        
        contract = Contract()
        contract.m_symbol = str(subscribeReq.symbol)
        contract.m_exchange = exchangeMap.get(subscribeReq.exchange, '')
        contract.m_secType = productClassMap.get(subscribeReq.productClass, '')
        contract.m_currency = currencyMap.get(subscribeReq.currency, '')
        contract.m_expiry = subscribeReq.expiry
        contract.m_strike = subscribeReq.strikePrice
        contract.m_right = optionTypeMap.get(subscribeReq.optionType, '')
    
        self.connection.reqMktData(self.tickerId, contract, '', False)
        
        # 创建Tick对象并保存到字典中
        tick = VtTickData()
        tick.symbol = subscribeReq.symbol
        tick.exchange = subscribeReq.exchange
        tick.vtSymbol = '.'.join([tick.symbol, tick.exchange])
        tick.gatewayName = self.gatewayName
        self.tickDict[self.tickerId] = tick
    
    #----------------------------------------------------------------------
    def sendOrder(self, orderReq):
        """发单"""
        # 增加报单号1，最后再次进行查询
        # 这里双重设计的目的是为了防止某些情况下，连续发单时，nextOrderId的回调推送速度慢导致没有更新
        self.orderId += 1
        
        # 创建合约对象
        contract = Contract()
        contract.m_symbol = str(orderReq.symbol)
        contract.m_exchange = exchangeMap.get(orderReq.exchange, '')
        contract.m_secType = productClassMap.get(orderReq.productClass, '')
        contract.m_currency = currencyMap.get(orderReq.currency, '')
        
        contract.m_expiry = orderReq.expiry
        contract.m_strike = orderReq.strikePrice
        contract.m_right = optionTypeMap.get(orderReq.optionType, '')
        
        # 创建委托对象
        order = Order()
        order.m_orderId = self.orderId
        order.m_clientId = self.clientId
        
        order.m_action = directionMap.get(orderReq.direction, '')
        order.m_lmtPrice = orderReq.price
        order.m_totalQuantity = orderReq.volume
        order.m_orderType = priceTypeMap.get(orderReq.priceType, '')
        
        # 发送委托
        self.connection.placeOrder(self.orderId, contract, order)
        
        # 查询下一个有效编号
        self.connection.reqIds(1)
    
    #----------------------------------------------------------------------
    def cancelOrder(self, cancelOrderReq):
        """撤单"""
        self.connection.cancelOrder(cancelOrderReq.orderID)
    
    #----------------------------------------------------------------------
    def getAccount(self):
        """查询账户资金"""
        log = VtLogData()
        log.gatewayName = self.gatewayName        
        log.logContent = u'IB接口账户信息提供主推更新，无需查询'
        self.onLog(log) 
    
    #----------------------------------------------------------------------
    def getPosition(self):
        """查询持仓"""
        log = VtLogData()
        log.gatewayName = self.gatewayName        
        log.logContent = u'IB接口持仓信息提供主推更新，无需查询'
        self.onLog(log) 
    
    #----------------------------------------------------------------------
    def close(self):
        """关闭"""
        self.connection.eDisconnect()


########################################################################
class IbWrapper(EWrapper):
    """IB回调接口的实现"""

    #----------------------------------------------------------------------
    def __init__(self, gateway):
        """Constructor"""
        super(IbWrapper, self).__init__()
        
        self.connectionStatus = False               # 连接状态
        
        self.gateway = gateway                      # gateway对象
        self.gatewayName = gateway.gatewayName      # gateway对象名称
        
        self.tickDict = gateway.tickDict            # tick快照字典，key为tickerId，value为VtTickData对象
        self.orderDict = gateway.orderDict          # order字典
        self.accountDict = gateway.accountDict      # account字典
       
    #----------------------------------------------------------------------
    def tickPrice(self, tickerId, field, price, canAutoExecute):
        """行情推送（价格相关）"""
        if field in tickFieldMap:
            tick = self.tickDict[tickerId]
            key = tickFieldMap[field]
            tick.__setattr__(key, price)
        else:
            print field

    #----------------------------------------------------------------------
    def tickSize(self, tickerId, field, size):
        """行情推送（量相关）"""
        if field in tickFieldMap:
            tick = self.tickDict[tickerId]
            key = tickFieldMap[field]
            tick.__setattr__(key, size)       
        else:
            print field

    #----------------------------------------------------------------------
    def tickOptionComputation(self, tickerId, field, impliedVol, delta, optPrice, pvDividend, gamma, vega, theta, undPrice):
        """行情推送（期权数值）"""
        pass

    #----------------------------------------------------------------------
    def tickGeneric(self, tickerId, tickType, value):
        """行情推送（某些通用字段）"""
        pass

    #---------------------------------------------------------------------- 
    def tickString(self, tickerId, tickType, value):
        """行情推送，特殊字段相关"""
        if tickType == 45:
            lt = localtime(int(value))
            
            tick = self.tickDict[tickerId]
            tick.time = strftime('%H:%M:%S', lt)
            tick.date = strftime('%Y%m%d')
            
            # 这里使用copy的目的是为了保证推送到事件系统中的对象
            # 不会被当前的API线程修改，否则可能出现多线程数据同步错误
            newtick = copy(tick)
            self.gateway.onTick(newtick)

    #----------------------------------------------------------------------
    def tickEFP(self, tickerId, tickType, basisPoints, formattedBasisPoints, impliedFuture, holdDays, futureExpiry, dividendImpact, dividendsToExpiry):
        """行情推送（合约属性相关）"""
        pass

    #---------------------------------------------------------------------- 
    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld):
        """报单成交回报"""
        pass
        orderId = str(orderId)
        
        if orderId in self.orderDict:
            od = self.orderDict[orderId]
        else:
            od = VtOrderData()  # od代表orderData
            od.orderID = orderId
            od.vtOrderID = '.'.join([self.gatewayName, orderId])
            od.gatewayName = self.gatewayName
            self.orderDict[orderId] = od
        
        od.status = orderStatusMapReverse.get(status, STATUS_UNKNOWN)
        od.tradedVolume = filled
        
        newod = copy(od)
        self.gateway.onOrder(newod)

    #----------------------------------------------------------------------
    def openOrder(self, orderId, contract, order, orderState):
        """报单信息推送"""
        orderId = str(orderId)  # orderId是整数
        
        if orderId in self.orderDict:
            od = self.orderDict[orderId]
        else:
            od = VtOrderData()  # od代表orderData
            od.orderID = orderId
            od.vtOrderID = '.'.join([self.gatewayName, orderId])
            od.symbol = contract.m_symbol
            od.exchange = exchangeMapReverse.get(contract.m_exchange, '')
            od.vtSymbol = '.'.join([od.symbol, od.exchange])  
            od.gatewayName = self.gatewayName
            self.orderDict[orderId] = od
        
        od.direction = directionMapReverse.get(order.m_action, '')
        od.price = order.m_lmtPrice
        od.totalVolume = order.m_totalQuantity
        
        newod = copy(od)
        self.gateway.onOrder(newod)

    #----------------------------------------------------------------------
    def openOrderEnd(self):
        """ generated source for method openOrderEnd """
        pass

    #----------------------------------------------------------------------
    def updateAccountValue(self, key, value, currency, accountName):
        """更新账户数据"""
        # 仅逐个字段更新数据，这里对于没有currency的推送忽略
        if currency:
            name = '.'.join([accountName, currency])
            
            if name in self.accountDict:
                account = self.accountDict[name]
            else:
                account = VtAccountData()
                account.accountID = name
                account.vtAccountID = name
                account.gatewayName = self.gatewayName
                self.accountDict[name] = account
            
            if key in accountKeyMap:
                k = accountKeyMap[key]
                account.__setattr__(k, float(value))
        
    #----------------------------------------------------------------------
    def updatePortfolio(self, contract, position, marketPrice, marketValue, averageCost, unrealizedPNL, realizedPNL, accountName):
        """持仓更新推送"""
        pos = VtPositionData()
        
        pos.symbol = contract.m_symbol
        pos.exchange = exchangeMapReverse.get(contract.m_exchange, contract.m_exchange)
        pos.vtSymbol = '.'.join([pos.symbol, pos.exchange])
        pos.direction = DIRECTION_NET
        pos.position = position
        pos.price = averageCost
        pos.vtPositionName = pos.vtSymbol
        pos.gatewayName = self.gatewayName
        
        self.gateway.onPosition(pos)

    #----------------------------------------------------------------------
    def updateAccountTime(self, timeStamp):
        """更新账户数据的时间"""
        # 推送数据
        for account in self.accountDict.values():
            newaccount = copy(account)
            self.gateway.onAccount(newaccount)

    #----------------------------------------------------------------------
    def accountDownloadEnd(self, accountName):
        """ generated source for method accountDownloadEnd """
        pass

    #----------------------------------------------------------------------
    def nextValidId(self, orderId):
        """下一个有效报单编号更新"""
        self.gateway.orderId = orderId

    #----------------------------------------------------------------------
    def contractDetails(self, reqId, contractDetails):
        """ generated source for method contractDetails """
        pass

    #----------------------------------------------------------------------
    def bondContractDetails(self, reqId, contractDetails):
        """ generated source for method bondContractDetails """

    #----------------------------------------------------------------------
    def contractDetailsEnd(self, reqId):
        """ generated source for method contractDetailsEnd """
        pass

    #----------------------------------------------------------------------
    def execDetails(self, reqId, contract, execution):
        """成交推送"""
        trade = VtTradeData()
        trade.gatewayName = self.gatewayName     
        trade.tradeID = execution.m_execId
        trade.vtTradeID = '.'.join([self.gatewayName, trade.tradeID])
        
        trade.symbol = contract.m_symbol
        trade.exchange = exchangeMapReverse.get(contract.m_exchange, '')
        trade.vtSymbol = '.'.join([trade.symbol, trade.exchange])  
        
        trade.orderID = str(execution.m_orderId)
        trade.direction = directionMapReverse.get(execution.m_side, '')
        trade.price = execution.m_price
        trade.volume = execution.m_shares
        trade.tradeTime = execution.m_time  
        
        self.gateway.onTrade(trade)

    #----------------------------------------------------------------------
    def execDetailsEnd(self, reqId):
        """ generated source for method execDetailsEnd """
        pass

    #----------------------------------------------------------------------
    def updateMktDepth(self, tickerId, position, operation, side, price, size):
        """ generated source for method updateMktDepth """
        pass

    #----------------------------------------------------------------------
    def updateMktDepthL2(self, tickerId, position, marketMaker, operation, side, price, size):
        """ generated source for method updateMktDepthL2 """
        pass

    #----------------------------------------------------------------------
    def updateNewsBulletin(self, msgId, msgType, message, origExchange):
        """ generated source for method updateNewsBulletin """
        pass

    #----------------------------------------------------------------------
    def managedAccounts(self, accountsList):
        """ generated source for method managedAccounts """
        pass

    #----------------------------------------------------------------------
    def receiveFA(self, faDataType, xml):
        """ generated source for method receiveFA """
        pass

    #----------------------------------------------------------------------
    def historicalData(self, reqId, date, open, high, low, close, volume, count, WAP, hasGaps):
        """ generated source for method historicalData """
        pass

    #----------------------------------------------------------------------
    def scannerParameters(self, xml):
        """ generated source for method scannerParameters """
        pass

    #----------------------------------------------------------------------
    def scannerData(self, reqId, rank, contractDetails, distance, benchmark, projection, legsStr):
        ''' generated source for method scannerData '''
        pass

    #----------------------------------------------------------------------
    def scannerDataEnd(self, reqId):
        """ generated source for method scannerDataEnd """
        pass

    #----------------------------------------------------------------------
    def realtimeBar(self, reqId, time, open, high, low, close, volume, wap, count):
        """ generated source for method realtimeBar """
        pass

    #----------------------------------------------------------------------
    def currentTime(self, time):
        """ generated source for method currentTime """
        t = strftime('%H:%M:%S', localtime(time))
        
        self.connectionStatus = True
        self.gateway.connected = True
        
        log = VtLogData()
        log.gatewayName = self.gatewayName
        log.logContent = (u'IB接口连接成功，当前服务器时间%s' %t)
        self.gateway.onLog(log) 

    #----------------------------------------------------------------------
    def fundamentalData(self, reqId, data):
        """ generated source for method fundamentalData """
        pass

    #----------------------------------------------------------------------
    def deltaNeutralValidation(self, reqId, underComp):
        """ generated source for method deltaNeutralValidation """
        pass

    #----------------------------------------------------------------------
    def tickSnapshotEnd(self, reqId):
        """ generated source for method tickSnapshotEnd """
        pass

    #----------------------------------------------------------------------
    def marketDataType(self, reqId, marketDataType):
        """ generated source for method marketDataType """
        pass

    #----------------------------------------------------------------------
    def commissionReport(self, commissionReport):
        """ generated source for method commissionReport """
        pass

    #----------------------------------------------------------------------
    def position(self, account, contract, pos, avgCost):
        """ generated source for method position """
        pass

    #----------------------------------------------------------------------
    def positionEnd(self):
        """ generated source for method positionEnd """
        pass

    #----------------------------------------------------------------------
    def accountSummary(self, reqId, account, tag, value, currency):
        """ generated source for method accountSummary """
        pass

    #----------------------------------------------------------------------
    def accountSummaryEnd(self, reqId):
        """ generated source for method accountSummaryEnd """   
        pass
        
    #----------------------------------------------------------------------
    def error(self, id=None, errorCode=None, errorMsg=None):
        """错误回报"""
        err = VtErrorData()
        err.gatewayName = self.gatewayName
        err.errorID = errorCode
        err.errorMsg = errorMsg
        self.gateway.onError(err)

    #----------------------------------------------------------------------
    def error_0(self, strval=None):
        """错误回报（单一字符串）"""
        err = VtErrorData()
        err.gatewayName = self.gatewayName
        err.errorMsg = strval
        self.gateway.onError(err)

    #----------------------------------------------------------------------
    def error_1(self, id=None, errorCode=None, errorMsg=None):
        """错误回报（字符串和代码）"""
        err = VtErrorData()
        err.gatewayName = self.gatewayName
        err.errorID = errorCode
        err.errorMsg = errorMsg
        self.gateway.onError(err)
        
    #----------------------------------------------------------------------
    def connectionClosed(self):
        """连接断开"""       
        self.connectionStatus = False
        self.gateway.connected = False
        
        log = VtLogData()
        log.gatewayName = self.gatewayName
        log.logContent = (u'IB接口连接断开')
        self.gateway.onLog(log) 
    
    