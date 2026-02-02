# 数据源修复报告

> **报告日期**: 2026年2月2日
> **修复状态**: 部分完成

---

## 📊 修复结果总结

### ✅ 已修复的数据源

| 数据源 | 状态 | 可用URL | 用途 |
|--------|------|----------|------|
| 英国FSA | ✅ 正常 | https://www.food.gov.uk/news-alerts | 雀巢召回数据 |
| 飞鹤官网 | ✅ 正常 | https://www.feihe.com/ | 飞鹤召回检查 |
| 雀巢官网 | ✅ 正常 | https://www.nestle.com.cn/ | 雀巢召回检查 |
| 雅培官网 | ✅ 正常 | https://www.abbott.com.cn/ | 雅培召回检查 |
| 伊利官网 | ✅ 正常 | https://www.yili.com/ | 金领冠召回检查 |

### ❌ 无法修复的数据源

| 数据源 | 问题 | 原因 | 影响范围 |
|--------|------|------|----------|
| **中国SAMR** | ❌ 严重 | 网站404，导航有限 | 所有中国品牌 |
| **美国FDA** | ❌ 严重 | 网站404 | 美国品牌召回 |
| **爱他美官网** | ❌ 中等 | 无法访问 | 爱他美召回检查 |
| **美素佳儿官网** | ❌ 中等 | 连接被拒绝 | 美素佳儿召回检查 |
| **a2官网** | ❌ 中等 | 域名错误或重定向 | a2召回检查 |
| **澳洲FSANZ** | ❌ 轻微 | URL结构变更 | 澳洲品牌召回 |

---

## 🔍 详细分析

### 中国SAMR问题分析

**问题描述**：
- SAMR网站（www.samr.gov.cn）大部分页面返回404
- 尝试的URL全部失败：
  - /cpzljd/ - 产品质量监督
  - /tzgg/ - 通知公告
  - /zw/cpzljd/ - 政务产品质量监督
  - /zljds/ - 质量监督司（唯一可访问）

**可能原因**：
1. 网站改版，URL结构变更
2. 部分页面需要登录
3. 网站使用JavaScript动态加载
4. 可能有爬虫防护

**临时解决方案**：
1. 手动访问SAMR网站查找召回信息
2. 订阅SAMR召回邮件通知
3. 通过新闻媒体获取召回信息
4. 使用省级市场监管部门网站

**长期解决方案**：
1. 联系SAMR获取正确的API接口
2. 等待网站改版稳定
3. 开发基于截图的OCR识别（如果必须）

---

### 美国FDA问题分析

**问题描述**：
- FDA网站（www.fda.gov）返回404
- 尝试的所有召回页面URL均失效：
  - /safety/recalls-market-withdrawals-safety-alerts
  - /food/recalls-outbreaks-contaminations
  - /food/recalls
  - /safety/recalls

**可能原因**：
1. 网站改版
2. 网站维护或故障
3. 地区访问限制
4. CDN问题

**临时解决方案**：
1. 使用欧盟RASFF作为替代
2. 通过其他媒体获取美国召回信息
3. 使用RSS或邮件订阅

**长期解决方案**：
1. 等待FDA网站恢复正常
2. 联系FDA获取正确的API
3. 建立美国合作伙伴关系

---

### 品牌官网问题分析

**爱他美 (Aptamil)**：
- ✅ 期望URL: www.aptamil.cn
- ❌ 实际: 无法访问
- 可能原因: 网站维护、域名变更、地区限制

**美素佳儿 (Friso)**：
- ✅ 期望URL: www.friso.com.cn
- ❌ 实际: 连接被拒绝
- 可能原因: 服务器防火墙、反爬虫

**a2至初 (a2)**：
- ✅ 期望URL: www.a2nutrition.com.cn
- ❌ 实际: 加载其他公司网站
- 可能原因: 域名已过期或转让

**临时解决方案**：
1. 使用国际官网检查召回信息
2. 通过社交媒体获取品牌公告
3. 监控零售商召回通知

---

## 💡 修复建议

### 短期方案（本周内）

1. **手动检查流程**
   - 每天手动访问英国FSA
   - 每周手动检查可用的品牌官网
   - 订阅主要品牌的邮件通知

2. **使用可用数据源**
   - 专注于英国FSA（雀巢）
   - 监控新闻媒体（中国品牌）
   - 使用社交媒体（品牌公告）

3. **建立临时监控**
   - 设置百度/谷歌搜索提醒（召回关键词）
   - 订阅RSS feeds（如果可用）
   - 关注品牌官方微信公众号

### 中期方案（1个月内）

1. **重新探索SAMR网站**
   - 手动访问找到正确的召回页面URL
   - 使用浏览器开发者工具分析网站
   - 尝试找到API接口

2. **联系数据源**
   - 联系SAMR官方获取召回数据接口
   - 联系品牌公司获取召回通知渠道
   - 加入行业协会获取信息

3. **建立合作关系**
   - 与数据提供商合作（如FDA、RASFF）
   - 与行业媒体合作获取信息
   - 建立社区用户报告机制

### 长期方案（3-6个月）

1. **开发自动化系统**
   - 使用Selenium/Puppeteer处理JavaScript页面
   - 开发基于截图的OCR识别
   - 建立多源数据融合系统

2. **建立用户社区**
   - 鼓励用户提交召回信息
   - 建立召回信息共享平台
   - 开发用户评分和验证机制

3. **AI辅助监控**
   - 使用NLP从新闻中提取召回信息
   - 监控社交媒体召回关键词
   - 自动生成召回摘要

---

## 📋 更新的品牌配置

### 当前可用配置

```json
{
  "nestle": {
    "name": "雀巢",
    "name_en": "Nestlé",
    "sources": [
      {
        "country": "UK",
        "source_type": "政府平台",
        "url": "https://www.food.gov.uk/news-alerts",
        "status": "working",
        "priority": 1
      }
    ]
  },
  "feihe": {
    "name": "飞鹤",
    "name_en": "Feihe",
    "sources": [
      {
        "country": "CN",
        "source_type": "官网",
        "url": "https://www.feihe.com/",
        "status": "working",
        "priority": 2
      }
    ]
  },
  "abbott": {
    "name": "雅培",
    "name_en": "Abbott",
    "sources": [
      {
        "country": "CN",
        "source_type": "官网",
        "url": "https://www.abbott.com.cn/",
        "status": "working",
        "priority": 2
      }
    ]
  },
  "jinlingguan": {
    "name": "金领冠",
    "name_en": "Jinlingguan",
    "sources": [
      {
        "country": "CN",
        "source_type": "官网",
        "url": "https://www.yili.com/",
        "status": "working",
        "priority": 2
      }
    ]
  }
}
```

### 需要重新配置的品牌

```json
{
  "aptamil": {
    "name": "爱他美",
    "name_en": "Aptamil",
    "sources": [
      {
        "country": "UK",
        "source_type": "政府平台",
        "url": "https://www.food.gov.uk/news-alerts",
        "status": "working",
        "priority": 1,
        "note": "使用UK FSA搜索Aptamil关键词"
      },
      {
        "country": "CN",
        "source_type": "官网",
        "url": "https://www.aptamil.com/",
        "status": "broken",
        "priority": 3,
        "note": "需要找到正确的中国官网"
      }
    ]
  },
  "friso": {
    "name": "美素佳儿",
    "name_en": "Friso",
    "sources": [
      {
        "country": "CN",
        "source_type": "官网",
        "url": "https://www.friso.com.cn/",
        "status": "broken",
        "priority": 3,
        "note": "连接被拒绝，需要手动访问"
      },
      {
        "country": "NL",
        "source_type": "政府平台",
        "url": "https://www.nvwa.nl",
        "status": "untested",
        "priority": 4,
        "note": "未测试，需要验证"
      }
    ]
  },
  "a2": {
    "name": "a2至初",
    "name_en": "a2",
    "sources": [
      {
        "country": "CN",
        "source_type": "官网",
        "url": "https://www.a2nutrition.com.cn/",
        "status": "broken",
        "priority": 3,
        "note": "域名错误或重定向"
      },
      {
        "country": "NZ",
        "source_type": "政府平台",
        "url": "https://www.mpi.govt.nz",
        "status": "untested",
        "priority": 4,
        "note": "未测试，需要验证"
      }
    ]
  }
}
```

---

## 🚀 立即可行的数据采集方案

### 方案A：聚焦英国FSA（推荐）

**优势**：
- ✅ 数据源稳定可靠
- ✅ 数据最新有效
- ✅ 爬虫已开发完成
- ✅ 覆盖雀巢、爱他美等品牌

**执行步骤**：
1. 扩展雀巢爬虫，增加搜索其他品牌
2. 定期运行爬虫（每天/每周）
3. 自动插入飞书表格

**覆盖品牌**：
- 雀巢 (SMA)
- 爱他美 (Aptamil)
- 其他英国市场的奶粉品牌

---

### 方案B：新闻媒体监控

**优势**：
- ✅ 覆盖所有品牌
- ✅ 信息及时
- ✅ 无需爬虫

**执行步骤**：
1. 设置新闻搜索关键词（召回、奶粉、品牌名）
2. 使用RSS或API获取新闻
3. NLP提取召回信息
4. 人工审核确认

**监控关键词**：
- "奶粉召回"
- "婴儿奶粉召回"
- "雅培召回"
- "爱他美召回"
- "飞鹤召回"
- 等等

---

### 方案C：混合方案（最佳）

结合方案A和方案B：
1. 主要依赖英国FSA（自动化、准确）
2. 辅助新闻监控（全面、及时）
3. 手动验证关键召回信息

---

## 📊 最终建议

### MVP阶段（立即上线）

**数据源配置**：
- ✅ 英国FSA（雀巢、爱他美）
- ✅ 飞鹤官网（手动检查）
- ✅ 新闻监控（关键词搜索）

**品牌覆盖**：
- 雀巢：完整支持
- 爱他美：部分支持（英国召回）
- 飞鹤：手动监控
- 其他品牌：暂不支持

### 迭代优化

**第1周**：
- 扩展FSA爬虫支持更多品牌
- 建立新闻监控机制
- 手动检查中国品牌召回

**第1月**：
- 找到并修复SAMR数据源
- 开发FDA替代方案
- 建立用户反馈机制

**第3月**：
- 实现全品牌覆盖
- 建立自动监控
- 开发AI辅助提取

---

## ✅ Owner结论

**修复状态**: 🟡 **部分完成，需要持续优化**

**当前最佳方案**:
1. **立即**: 使用英国FSA扩展品牌覆盖
2. **短期**: 建立新闻监控机制
3. **中期**: 修复SAMR/FDA数据源
4. **长期**: 开发AI辅助自动化

**小程序可以上线**: ✅
- 当前数据（雀巢38条）足够支持MVP
- 显示"当前支持雀巢品牌查询"
- 后台持续扩展其他品牌

---

**报告生成时间**: 2026年2月2日 17:00
**Owner**: Recall Checker Project Owner
