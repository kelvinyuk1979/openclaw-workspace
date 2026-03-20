---
name: stock-market-pro
description: 专业股票市场分析工具，整合全球多市场数据、技术分析、基本面分析、量化选股等功能。
emoji: 📈
---

# Stock Market Pro - 专业股票分析技能

## 功能概述

整合全球多市场数据，提供专业级的股票分析、量化选股、投资组合管理等功能。

## 支持市场

| 市场 | 代码 | 覆盖范围 |
|------|------|----------|
| **A 股** | SH/SZ/BJ | 沪深京全部股票 |
| **港股** | HKEX | 主板、创业板 |
| **美股** | NYSE/NASDAQ | 全部上市公司 |
| **ETF** | 全球 | 主要 ETF 产品 |
| **期货** | 商品/金融 | 主要期货品种 |
| **外汇** | 主要货币对 | 外汇市场 |

## 核心功能模块

### 📊 1. 实时行情模块

```python
import akshare as ak

# 多市场实时行情
def get_realtime_quotes(symbols, market="all"):
    """
    获取多市场实时行情
    
    Args:
        symbols: 股票代码列表
        market: 市场类型 (A 股/港股/美股/all)
    
    Returns:
        DataFrame: 实时行情数据
    """
    quotes = {}
    
    for symbol in symbols:
        if symbol.startswith('6') or symbol.startswith('0'):
            # A 股
            data = ak.stock_zh_a_spot_em(symbol=symbol)
        elif symbol.startswith('00') or symbol.startswith('01'):
            # 港股
            data = ak.stock_hk_spot_em(symbol=symbol)
        else:
            # 美股
            data = ak.stock_us_spot_em(symbol=symbol)
        
        quotes[symbol] = data
    
    return quotes
```

### 📈 2. 技术分析模块

```python
import talib
import pandas as pd

class TechnicalAnalysis:
    """技术分析引擎"""
    
    def __init__(self, data):
        self.data = data
        self.close = data['close'].values
        self.high = data['high'].values
        self.low = data['low'].values
        self.volume = data['volume'].values
    
    def get_all_indicators(self):
        """获取全部技术指标"""
        return {
            # 趋势指标
            'MA5': talib.SMA(self.close, timeperiod=5),
            'MA10': talib.SMA(self.close, timeperiod=10),
            'MA20': talib.SMA(self.close, timeperiod=20),
            'MA60': talib.SMA(self.close, timeperiod=60),
            'MACD': talib.MACD(self.close),
            'ADX': talib.ADX(self.high, self.low, self.close),
            
            # 动量指标
            'RSI': talib.RSI(self.close, timeperiod=14),
            'KDJ': self.calculate_kdj(),
            'CCI': talib.CCI(self.high, self.low, self.close),
            
            # 波动率指标
            'BOLL': talib.BBANDS(self.close),
            'ATR': talib.ATR(self.high, self.low, self.close),
            
            # 成交量指标
            'OBV': talib.OBV(self.close, self.volume),
            'VR': self.calculate_vr()
        }
    
    def calculate_kdj(self):
        """计算 KDJ 指标"""
        # KDJ 计算逻辑
        pass
    
    def calculate_vr(self):
        """计算 VR 成交量比率"""
        pass
    
    def get_signal(self):
        """生成交易信号"""
        indicators = self.get_all_indicators()
        
        # 金叉/死叉检测
        ma_signal = self.detect_ma_cross(indicators['MA5'], indicators['MA10'])
        
        # MACD 信号
        macd_signal = self.detect_macd_signal(indicators['MACD'])
        
        # RSI 超买超卖
        rsi_signal = self.detect_rsi_signal(indicators['RSI'])
        
        return {
            'signal': 'BUY' if self.bullish(ma_signal, macd_signal, rsi_signal) else 'SELL',
            'confidence': self.calculate_confidence(ma_signal, macd_signal, rsi_signal),
            'indicators': indicators
        }
```

### 💰 3. 基本面分析模块

```python
class FundamentalAnalysis:
    """基本面分析引擎"""
    
    def __init__(self, symbol):
        self.symbol = symbol
        self.financial_data = self.load_financial_data()
    
    def load_financial_data(self):
        """加载财务数据"""
        return {
            'income': self.get_income_statement(),
            'balance': self.get_balance_sheet(),
            'cashflow': self.get_cash_flow()
        }
    
    def get_valuation_metrics(self):
        """获取估值指标"""
        return {
            'PE': self.calculate_pe(),
            'PB': self.calculate_pb(),
            'PS': self.calculate_ps(),
            'PEG': self.calculate_peg(),
            'EV_EBITDA': self.calculate_ev_ebitda(),
            'DCF': self.calculate_dcf()
        }
    
    def get_growth_metrics(self):
        """获取增长指标"""
        return {
            'revenue_growth_3y': self.get_revenue_growth(3),
            'revenue_growth_5y': self.get_revenue_growth(5),
            'earnings_growth_3y': self.get_earnings_growth(3),
            'earnings_growth_5y': self.get_earnings_growth(5),
            'book_value_growth': self.get_book_value_growth()
        }
    
    def get_profitability_metrics(self):
        """获取盈利能力指标"""
        return {
            'ROE': self.calculate_roe(),
            'ROA': self.calculate_roa(),
            'ROIC': self.calculate_roic(),
            'gross_margin': self.get_gross_margin(),
            'operating_margin': self.get_operating_margin(),
            'net_margin': self.get_net_margin()
        }
    
    def get_financial_health(self):
        """财务健康度评估"""
        return {
            'debt_ratio': self.get_debt_ratio(),
            'current_ratio': self.get_current_ratio(),
            'quick_ratio': self.get_quick_ratio(),
            'interest_coverage': self.get_interest_coverage(),
            'altman_z_score': self.calculate_altman_z()
        }
    
    def get_score(self):
        """综合评分"""
        valuation = self.get_valuation_metrics()
        growth = self.get_growth_metrics()
        profitability = self.get_profitability_metrics()
        health = self.get_financial_health()
        
        score = {
            'valuation': self.score_valuation(valuation),  # 0-100
            'growth': self.score_growth(growth),  # 0-100
            'profitability': self.score_profitability(profitability),  # 0-100
            'financial_health': self.score_health(health),  # 0-100
            'total': self.calculate_total_score(valuation, growth, profitability, health)
        }
        
        return score
```

### 🎯 4. 量化选股模块

```python
class QuantitativeStockPicker:
    """量化选股引擎"""
    
    def __init__(self, universe="all"):
        self.universe = universe
        self.stock_pool = self.build_stock_pool()
    
    def build_stock_pool(self):
        """构建股票池"""
        if self.universe == "A 股":
            return self.get_a_shares()
        elif self.universe == "港股":
            return self.get_hk_stocks()
        elif self.universe == "美股":
            return self.get_us_stocks()
        else:
            return self.get_global_stocks()
    
    def screen_by_value(self, min_pe=0, max_pe=30, min_pb=0, max_pb=5):
        """价值选股"""
        criteria = {
            'PE': {'min': min_pe, 'max': max_pe},
            'PB': {'min': min_pb, 'max': max_pb},
            'dividend_yield': {'min': 0.02}  # 股息率>2%
        }
        return self.apply_screen(criteria)
    
    def screen_by_growth(self, min_revenue_growth=0.1, min_earnings_growth=0.15):
        """成长选股"""
        criteria = {
            'revenue_growth_3y': {'min': min_revenue_growth},
            'earnings_growth_3y': {'min': min_earnings_growth},
            'ROE': {'min': 0.15}
        }
        return self.apply_screen(criteria)
    
    def screen_by_momentum(self, lookback_days=252):
        """动量选股"""
        criteria = {
            'return_1m': {'min': 0.05},
            'return_3m': {'min': 0.10},
            'return_6m': {'min': 0.15},
            'relative_strength': {'min': 70}  # RS 评级>70
        }
        return self.apply_screen(criteria)
    
    def screen_by_quality(self):
        """质量选股"""
        criteria = {
            'ROE': {'min': 0.15},
            'ROIC': {'min': 0.10},
            'debt_to_equity': {'max': 0.50},
            'free_cash_flow': {'min': 0}  # 正向 FCF
        }
        return self.apply_screen(criteria)
    
    def screen_by_small_cap_growth(self):
        """小盘股成长选股（整合策略）
        
        筛选条件：
        - 市值低于 20 亿美元（或等值本币）
        - 年收入增长超 20%
        - 营业利润率扩大
        - 强劲资产负债表（债股比<0.5）
        - 内部人员持股>10%
        - 机构持股低<50%
        """
        criteria = {
            'market_cap': {'max': 2000000000},
            'revenue_growth_yoy': {'min': 0.20},
            'operating_margin_trend': 'expanding',
            'debt_to_equity': {'max': 0.5},
            'insider_ownership': {'min': 0.10},
            'institutional_ownership': {'max': 0.50}
        }
        return self.apply_screen(criteria)
        """质量选股"""
        criteria = {
            'ROE': {'min': 0.15},
            'ROIC': {'min': 0.10},
            'debt_ratio': {'max': 0.5},
            'free_cash_flow': {'min': 0},  # 自由现金流为正
            'earnings_quality': {'min': 0.7}
        }
        return self.apply_screen(criteria)
    
    def multi_factor_screen(self, factors=['value', 'growth', 'momentum', 'quality']):
        """多因子选股"""
        results = {}
        
        if 'value' in factors:
            results['value'] = self.screen_by_value()
        if 'growth' in factors:
            results['growth'] = self.screen_by_growth()
        if 'momentum' in factors:
            results['momentum'] = self.screen_by_momentum()
        if 'quality' in factors:
            results['quality'] = self.screen_by_quality()
        
        # 交集选股
        final_pool = self.intersect_all(results)
        
        # 综合评分排序
        ranked = self.rank_by_composite_score(final_pool)
        
        return ranked[:20]  # 返回前 20 只
    
    def apply_screen(self, criteria):
        """应用筛选条件"""
        filtered = []
        for stock in self.stock_pool:
            if self.meets_criteria(stock, criteria):
                filtered.append(stock)
        return filtered
```

### 📉 5. 风险评估模块

```python
class RiskAssessment:
    """风险评估引擎"""
    
    def __init__(self, portfolio):
        self.portfolio = portfolio
        self.returns = self.calculate_returns()
    
    def calculate_var(self, confidence=0.95, horizon=1):
        """计算 VaR (风险价值)"""
        var = np.percentile(self.returns, (1 - confidence) * 100)
        return var * np.sqrt(horizon)
    
    def calculate_cvar(self, confidence=0.95):
        """计算 CVaR (条件风险价值)"""
        var = self.calculate_var(confidence)
        cvar = self.returns[self.returns <= var].mean()
        return cvar
    
    def calculate_beta(self, benchmark_returns):
        """计算 Beta 系数"""
        covariance = np.cov(self.returns, benchmark_returns)[0][1]
        variance = np.var(benchmark_returns)
        beta = covariance / variance
        return beta
    
    def calculate_sharpe_ratio(self, risk_free_rate=0.03):
        """计算夏普比率"""
        excess_return = self.returns.mean() - risk_free_rate / 252
        std_dev = self.returns.std() * np.sqrt(252)
        sharpe = excess_return / std_dev
        return sharpe
    
    def calculate_max_drawdown(self):
        """计算最大回撤"""
        cumulative = (1 + self.returns).cumprod()
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max
        max_dd = drawdown.min()
        return max_dd
    
    def get_risk_metrics(self):
        """获取全部风险指标"""
        return {
            'var_95': self.calculate_var(0.95),
            'cvar_95': self.calculate_cvar(0.95),
            'beta': self.calculate_beta(self.get_benchmark_returns()),
            'sharpe_ratio': self.calculate_sharpe_ratio(),
            'max_drawdown': self.calculate_max_drawdown(),
            'volatility': self.returns.std() * np.sqrt(252),
            'downside_deviation': self.calculate_downside_deviation()
        }
```

### 📋 6. 报告生成模块

```python
class ReportGenerator:
    """报告生成引擎"""
    
    def generate_stock_report(self, symbol, include_technical=True, include_fundamental=True):
        """生成个股深度报告"""
        report = {
            'header': {
                'symbol': symbol,
                'name': self.get_stock_name(symbol),
                'market': self.get_market(symbol),
                'date': datetime.now().strftime('%Y-%m-%d'),
                'price': self.get_current_price(symbol),
                'change': self.get_price_change(symbol)
            },
            'summary': self.generate_summary(symbol),
            'technical': self.generate_technical_section(symbol) if include_technical else None,
            'fundamental': self.generate_fundamental_section(symbol) if include_fundamental else None,
            'valuation': self.generate_valuation_section(symbol),
            'risk': self.generate_risk_section(symbol),
            'recommendation': self.generate_recommendation(symbol)
        }
        
        return self.format_report(report)
    
    def generate_daily_brief(self, date=None):
        """生成每日简报"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        brief = {
            'date': date,
            'market_overview': self.get_market_overview(),
            'top_gainers': self.get_top_gainers(),
            'top_losers': self.get_top_losers(),
            'most_active': self.get_most_active(),
            'sector_performance': self.get_sector_performance(),
            'news_highlights': self.get_news_highlights(),
            'recommendations': self.get_daily_recommendations()
        }
        
        return self.format_brief(brief)
    
    def format_report(self, report):
        """格式化报告输出"""
        md = f"""
# 📈 {report['header']['name']} ({report['header']['symbol']}) 深度分析报告

**日期**: {report['header']['date']}
**当前价格**: {report['header']['price']}
**涨跌幅**: {report['header']['change']}

---

## 📊 核心摘要

{report['summary']}

## 📈 技术分析

{report['technical']}

## 💰 基本面分析

{report['fundamental']}

## 📉 估值分析

{report['valuation']}

## ⚠️ 风险评估

{report['risk']}

## 🎯 投资建议

{report['recommendation']}

---
*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        return md
```

## 使用场景

### ✅ 适用场景

- **个股深度分析** - 全面的基本面 + 技术分析
- **量化选股** - 多因子筛选优质股票
- **投资组合管理** - 风险评估与优化
- **市场研究** - 行业/板块分析
- **交易决策支持** - 技术信号 + 基本面验证

### ❌ 不适用场景

- **高频交易** - 数据延迟不适合
- **日内交易** - 需要实时数据源
- **衍生品定价** - 需要专门的期权/期货模型

## 与其他技能集成

### 与 akshare-stock 集成

```python
# 复用 akshare 数据接口
from akshare_stock import get_stock_data

def enhanced_analysis(symbol):
    # 获取基础数据
    data = get_stock_data(symbol)
    
    # 增强分析
    tech = TechnicalAnalysis(data)
    fundamental = FundamentalAnalysis(symbol)
    quant = QuantitativeStockPicker()
    
    return {
        'technical': tech.get_signal(),
        'fundamental': fundamental.get_score(),
        'quant_ranking': quant.rank_stock(symbol)
    }
```

### 与华尔街分析框架集成

```python
# 输出符合华尔街格式的报告
def wall_street_report(symbol):
    analysis = enhanced_analysis(symbol)
    
    report = f"""
## 📊 {symbol} - 华尔街风格分析

### 护城河评分：{analysis['fundamental']['moat_score']}/10

### 财务健康度
| 指标 | 数值 | 趋势 |
|------|------|------|
| ROE | {analysis['fundamental']['ROE']} | ↑ |
| 负债率 | {analysis['fundamental']['debt_ratio']} | → |

### 技术信号
- 趋势：{analysis['technical']['trend']}
- 动量：{analysis['technical']['momentum']}
- 信号：{analysis['technical']['signal']}

### 投资建议
- **短期**: {analysis['recommendation']['short_term']}
- **长期**: {analysis['recommendation']['long_term']}
"""
    return report
```

## 配置示例

```yaml
# ~/.openclaw/config/stock-market-pro.yaml

data_sources:
  akshare:
    enabled: true
    timeout: 30
  yahoo_finance:
    enabled: true
    timeout: 30
  eastmoney:
    enabled: true
    timeout: 30

analysis:
  technical:
    enabled: true
    indicators:
      - MA
      - MACD
      - RSI
      - KDJ
      - BOLL
  fundamental:
    enabled: true
    metrics:
      - valuation
      - growth
      - profitability
      - financial_health

screening:
  default_factors:
    - value
    - growth
    - momentum
    - quality
  min_market_cap: 1000000000  # 10 亿
  min_avg_volume: 100000

reporting:
  format: markdown
  include_charts: true
  auto_save: true
  output_dir: ~/reports/stocks/
```

## 注意事项

1. **数据延迟** - 免费数据源可能有 15 分钟延迟
2. **不构成投资建议** - 分析结果仅供参考
3. **模型局限性** - 量化模型无法预测黑天鹅事件
4. **定期更新** - 财务数据需定期刷新
5. **回测验证** - 策略需经过历史回测验证

## 高级选股策略

### 1. 📉 低估值选股器

```python
class ValueStockScreener:
    """低估值选股引擎"""
    
    def screen(self):
        """
        筛选条件：
        - P/E 低于行业平均
        - 过去 3-5 年收入和盈利稳定增长
        - 债股比低于行业中位数
        - 正向且增长的自由现金流
        - ROIC 高于行业平均
        - 分析师共识上升至少 30%
        """
        criteria = {
            'pe_ratio': {'max': 'industry_avg'},
            'revenue_growth_3y': {'min': 0.05},
            'earnings_growth_3y': {'min': 0.05},
            'debt_to_equity': {'max': 'industry_median'},
            'free_cash_flow': {'min': 0},
            'fcf_growth': {'min': 0},
            'roic': {'min': 'industry_avg'},
            'analyst_upgrade_30d': {'min': 0.30}
        }
        return self.apply_screen(criteria)
    
    def analyze_company(self, symbol):
        """深度分析单家公司"""
        return {
            'business_overview': self.get_business_overview(symbol),
            'why_undervalued': self.analyze_undervaluation(symbol),
            'key_risks': self.identify_risks(symbol),
            'intrinsic_value_range': self.calculate_intrinsic_value(symbol)
        }
```

### 2. 🔍 内部交易模式分析

```python
class InsiderTradingAnalyzer:
    """内部交易分析引擎"""
    
    def screen_insider_buying(self, industry=None, days=90):
        """
        筛选条件：
        - 多位内部人员购买股份
        - 公开市场购买（非期权行权）
        - 过去 90 天内购买
        - 购买规模相对于内部人员薪酬具有意义
        """
        criteria = {
            'insider_buyers_count': {'min': 2},
            'purchase_type': 'open_market',
            'days_lookback': days,
            'purchase_value_ratio': {'min': 0.1}  # 购买额/年薪 > 10%
        }
        return self.apply_screen(criteria)
    
    def analyze_insider_activity(self, symbol):
        """分析内部交易活动"""
        return {
            'who_bought': self.get_insider_buyers(symbol),
            'how_much': self.get_purchase_amounts(symbol),
            'historical_impact': self.analyze_historical_performance(symbol),
            'management_confidence': self.assess_confidence_level(symbol),
            'red_flags': self.identify_warning_signs(symbol)
        }
```

### 3. 🔄 市场情绪与现实差距

```python
class ContrarianAnalyzer:
    """反向投资分析引擎"""
    
    def find_opportunities(self):
        """
        识别遭大幅抛售但基本面强劲的股票
        """
        criteria = {
            'price_decline_3m': {'min': 0.20},  # 3 个月下跌>20%
            'negative_sentiment_score': {'min': 0.7},
            'fundamental_score': {'min': 0.7},  # 基本面评分>70
            'valuation_vs_history': 'below_average'
        }
        return self.apply_screen(criteria)
    
    def analyze_gap(self, symbol):
        """分析情绪与基本面差距"""
        return {
            'current_narrative': self.get_market_narrative(symbol),
            'actual_performance': self.get_actual_metrics(symbol),
            'temporary_or_permanent': self.assess_issue_permanence(symbol),
            'valuation_vs_history': self.compare_historical_valuation(symbol)
        }
```

### 4. 💰 股息贵族 ROI 计算器

```python
class DividendAristocratsAnalyzer:
    """股息贵族分析引擎"""
    
    def __init__(self):
        # 股息贵族：连续 25 年增长股息的公司
        self.aristocrats = self.get_dividend_aristocrats()
    
    def analyze_portfolio(self):
        """
        分析内容：
        - 假设股息再投资的过去 10 年总回报
        - 当前股息收益率
        - 股息增长率
        - 派息比可持续性
        - 自由现金流覆盖
        """
        results = []
        for symbol in self.aristocrats:
            results.append({
                'symbol': symbol,
                'total_return_10y_cagr': self.calculate_total_return(symbol, 10),
                'current_yield': self.get_current_yield(symbol),
                'dividend_growth_rate': self.get_dividend_growth_rate(symbol),
                'payout_ratio': self.get_payout_ratio(symbol),
                'fcf_coverage': self.get_fcf_coverage(symbol),
                'sustainability_score': self.calculate_sustainability_score(symbol)
            })
        
        # 按收入可靠性和长期总回报排名
        return sorted(results, key=lambda x: (x['sustainability_score'], x['total_return_10y_cagr']), reverse=True)
```

### 5. 💻 科技股炒作 vs 基本面

```python
class TechValuationAnalyzer:
    """科技股估值分析引擎"""
    
    def compare_tech_stocks(self, symbols):
        """
        评估维度：
        - 收入增长 vs 估值倍数
        - 利润率
        - 自由现金流
        - 资本效率
        """
        analysis = []
        for symbol in symbols:
            analysis.append({
                'symbol': symbol,
                'revenue_growth': self.get_revenue_growth(symbol),
                'pe_ratio': self.get_pe_ratio(symbol),
                'peg_ratio': self.get_peg_ratio(symbol),
                'operating_margin': self.get_operating_margin(symbol),
                'fcf_margin': self.get_fcf_margin(symbol),
                'roic': self.get_roic(symbol),
                'valuation_score': self.calculate_valuation_score(symbol)
            })
        
        return analysis
    
    def identify_mispricing(self):
        """识别错误定价"""
        analysis = self.compare_tech_stocks(self.tech_universe)
        
        # 过度乐观（估值过高）
        overpriced = [s for s in analysis if s['valuation_score'] < 30]
        # 被低估
        underpriced = [s for s in analysis if s['valuation_score'] > 70]
        
        return {
            'overpriced': overpriced[:3],
            'underpriced': underpriced[:3],
            'explanation': self.generate_explanation(overpriced, underpriced)
        }
```

### 6. 📊 行业轮动信号检测器

```python
class SectorRotationAnalyzer:
    """行业轮动分析引擎"""
    
    def analyze_macro_environment(self):
        """
        分析宏观经济指标：
        - 利率趋势
        - 通胀数据
        - GDP 增长
        - 就业条件
        """
        return {
            'interest_rate_trend': self.get_rate_trend(),
            'inflation_data': self.get_inflation_metrics(),
            'gdp_growth': self.get_gdp_growth(),
            'employment_conditions': self.get_employment_metrics(),
            'economic_phase': self.determine_economic_phase()  # 扩张/放缓/衰退/复苏
        }
    
    def predict_sector_performance(self, horizon_months=6):
        """预测行业表现"""
        macro = self.analyze_macro_environment()
        
        # 基于经济周期判断行业表现
        if macro['economic_phase'] == 'early_recovery':
            outperform = ['Technology', 'Consumer Discretionary', 'Financials']
            underperform = ['Utilities', 'Consumer Staples']
        elif macro['economic_phase'] == 'late_cycle':
            outperform = ['Energy', 'Materials', 'Healthcare']
            underperform = ['Technology', 'Real Estate']
        
        return {
            'outperform': outperform,
            'underperform': underperform,
            'economic_logic': self.explain_logic(macro),
            'risks': self.identify_risks()
        }
```

### 7. ⚖️ 风险调整回报优化器

```python
class PortfolioOptimizer:
    """投资组合优化引擎"""
    
    def __init__(self, capital=50000, risk_profile='moderate', time_horizon_years=5):
        self.capital = capital
        self.risk_profile = risk_profile  # conservative/moderate/aggressive
        self.time_horizon = time_horizon_years
    
    def build_portfolio(self):
        """
        构建多元化投资组合
        """
        # 根据风险偏好确定资产配置
        if self.risk_profile == 'conservative':
            allocation = {
                'bonds': 0.40,
                'large_cap': 0.35,
                'international': 0.15,
                'alternatives': 0.10
            }
        elif self.risk_profile == 'moderate':
            allocation = {
                'bonds': 0.25,
                'large_cap': 0.40,
                'mid_cap': 0.15,
                'international': 0.15,
                'alternatives': 0.05
            }
        elif self.risk_profile == 'aggressive':
            allocation = {
                'large_cap': 0.40,
                'mid_cap': 0.20,
                'small_cap': 0.15,
                'international': 0.15,
                'alternatives': 0.10
            }
        
        return {
            'asset_allocation': allocation,
            'position_sizing': self.calculate_position_sizes(allocation),
            'expected_return': self.calculate_expected_return(allocation),
            'expected_volatility': self.calculate_expected_volatility(allocation),
            'sharpe_ratio': self.calculate_sharpe_ratio(allocation),
            'rebalancing_rules': self.define_rebalancing_rules(),
            'downside_protection': self.define_downside_protection()
        }
    
    def calculate_position_sizes(self, allocation):
        """计算持仓规模"""
        positions = {}
        for asset_class, pct in allocation.items():
            dollar_amount = self.capital * pct
            positions[asset_class] = {
                'allocation_pct': pct,
                'dollar_amount': dollar_amount,
                'rationale': self.explain_rationale(asset_class)
            }
        return positions
```

## 策略使用示例

### 低估值选股

```python
# 运行低估值选股器
screener = ValueStockScreener()
results = screener.screen()

# 深度分析前 3 名
for symbol in results[:3]:
    analysis = screener.analyze_company(symbol)
    print(f"=== {symbol} ===")
    print(f"业务概述：{analysis['business_overview']}")
    print(f"低估原因：{analysis['why_undervalued']}")
    print(f"关键风险：{analysis['key_risks']}")
    print(f"内在价值：{analysis['intrinsic_value_range']}")
```

### 内部交易追踪

```python
# 识别内部人大量买入的公司
insider = InsiderTradingAnalyzer()
top_picks = insider.screen_insider_buying(days=90)

for symbol in top_picks[:5]:
    activity = insider.analyze_insider_activity(symbol)
    print(f"=== {symbol} ===")
    print(f"谁在购买：{activity['who_bought']}")
    print(f"购买金额：{activity['how_much']}")
    print(f"历史表现：{activity['historical_impact']}")
```

### 反向投资机会

```python
# 寻找被错杀的股票
contrarian = ContrarianAnalyzer()
opportunities = contrarian.find_opportunities()

for symbol in opportunities[:5]:
    gap = contrarian.analyze_gap(symbol)
    print(f"=== {symbol} ===")
    print(f"市场叙事：{gap['current_narrative']}")
    print(f"实际表现：{gap['actual_performance']}")
    print(f"问题性质：{gap['temporary_or_permanent']}")
```

---

## 扩展方向

- 🤖 AI 预测模型集成
- 📱 移动端推送
- 🔔 价格/信号提醒
- 📊 可视化图表增强
- 🌐 更多市场覆盖（欧洲、日本等）
