# 趋势跟踪策略

用最通俗的解释，趋势跟踪策略就是“追涨杀跌”：当一个资产的价格近期上涨的时候，就做多这个品种；当一个资产近期价格下跌的时候，就做空这个品种。

## 为什么趋势跟踪策略会有效？

简单来说，支撑趋势跟踪策略的底层逻辑有三个：
- 信息的传播过程

   因为信息的传播不是瞬间的，是有一个过程的，所以资产价格就会在信息传播的整个过程中出现一个单边上涨（利好消息逐步扩散）或单边下跌（利空消息逐步扩散）的趋势。

- 经济或产业的固有周期

   投资标的所处的行业大多具有一定的周期性，一般是由供需力量的强弱交替变化导致的，在经济上具有一定的惯性。

   周期性意味着这些投资标的存在中长线的上涨和下降趋势。

- 投资者情绪的推动

   投资者的恐惧和兴奋情绪往往会加剧趋势的波动幅度，理性投资者就可以利用其他投资者的过激反应来借势盈利。

## 常见的趋势指标

### 趋势指标 1：近期涨幅

指的是根据投资标的近一段时间的涨跌幅来确定趋势的走势。
例如，追踪一个投资目标，看它最近一个月的涨跌情况，如果上涨超过 5% 就做多，如果下跌超过 5% 就做空，否则就空仓。

### 趋势指标 2：双均线系统

它指的是利用两个不同周期的价格均线之间的关系，来确定趋势的走势。短均线高于长均线，就认为进入上涨趋势（做多信号），反之就认为进入下跌趋势（做空信号）。

### 趋势指标 3：布林带

它是一个经典的交易通道突破类指标。

计算逻辑：
- 首先，根据投资标的最近 20 个交易日收盘价的均值和标准差，确定价格的上轨和下轨。上轨是均价加上两倍标准差，下轨则是均价减去两倍标准差，上下轨之间的价格区域就被称为价格通道。
- 然后，观察价格的变化，当最新价格在上下轨之间变动时，认为是正常波动，当价格突破上下轨时，认为趋势出现。

投资逻辑：
- 当价格曲线上穿上轨的时候，说明上涨趋势建立，需要做多；
- 当价格曲线下穿下轨的时候，说明下跌趋势建立，可以做空；
- 当最新价格重新回到 20 日均线时，说明上涨或者下跌的趋势结束，这时候平仓。

## 策略回测

参考 [趋势跟踪回测代码](./trend-strategy.ipynb)
