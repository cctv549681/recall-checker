# Recall Checker - 微信小程序

> **快速查询婴幼儿配方奶粉召回信息，保护宝宝健康**

## 📱 项目简介

这是一个微信小程序，帮助用户快速查询婴幼儿配方奶粉召回信息。

### 核心功能

1. **OCR 批次号识别** 📸
   - 拍照自动识别批次号
   - 相册选择图片
   - 实时识别反馈

2. **手动批次号查询** 🔍
   - 输入批次号查询
   - 支持模糊匹配
   - 实时查询反馈

3. **查询结果展示** 📊
   - 召回状态（召回中/已结束/未召回/未找到）
   - 风险等级（高/中/低）
   - 产品详细信息
   - 官方召回公告链接

4. **查询历史记录** 📋
   - 本地存储查询历史
   - 按状态筛选
   - 快速重复查询

---

## 🚀 快速开始

### 环境要求

- 微信开发者工具
- 小程序 AppID
- 百度 OCR API Key（已配置）
- 飞书应用凭证（已配置）

### 安装步骤

1. **克隆代码**
   ```bash
   git clone https://github.com/cctv549681/recall-checker.git
   cd recall-checker/miniprogram
   ```

2. **配置凭证**

   编辑 `config/project.config.js`，填写你的凭证：
   ```javascript
   baiduOcr: {
     apiKey: 'YOUR_BAIDU_OCR_API_KEY'
   },
   feishu: {
     appId: 'YOUR_FEISHU_APP_ID',
     appSecret: 'YOUR_FEISHU_APP_SECRET',
     appToken: 'YOUR_FEISHU_APP_TOKEN',
     tableId: 'YOUR_FEISHU_TABLE_ID'
   }
   ```

3. **导入项目**

   - 打开微信开发者工具
   - 选择"导入项目"
   - 选择"项目目录"：`recall-checker/miniprogram`
   - 填写 AppID 和项目名称
   - 导入

4. **测试运行**
   - 点击"编译"
   - 点击"预览"
   - 在模拟器中测试

---

## 📁 项目结构

```
recall-checker/
├── miniprogram/              # 小程序主目录
│   ├── app.json              # 小程序配置
│   ├── app.wxss              # 全局样式
│   ├── sitemap.json          # 页面路由
│   ├── config/              # 配置文件
│   │   └── project.config.js
│   ├── pages/              # 页面文件
│   │   ├── index/         # 首页（OCR+手动输入+历史）
│   │   ├── camera/        # OCR识别页面
│   │   ├── result/        # 查询结果页面
│   │   └── history/       # 历史记录页面
│   └── utils/              # 工具模块
│       ├── api.js         # API 请求
│       ├── storage.js      # 本地存储
│       └── date.js         # 日期格式化
└── scraper/                # 后端爬虫
    ├── nestle_scraper.py  # 雀巢召回爬虫
    └── utils/
        ├── feishu_client.py  # 飞书 API 客户端
        ├── feishu_config.py  # 飞书配置
        └── feishu_tables.py  # 表格管理
```

---

## 🎨 页面说明

### 1. 首页

**路径**：`pages/index/index`

**功能**：
- OCR 扫描按钮：跳转到相机页面
- 手动输入框：输入批次号直接查询
- 最近查询记录：显示最近 3 条查询历史
- 点击任意历史记录：查看详情

### 2. OCR 识别页面

**路径**：`pages/camera/camera`

**功能**：
- 相机预览：实时显示相机画面
- 扫描框：引导用户对准批次号
- 相册选择：从相册选择照片
- 拍照按钮：拍照并识别
- 识别结果弹窗：显示识别的批次号和置信度
- 确认/重新识别：控制识别流程

### 3. 查询结果页面

**路径**：`pages/result/result`

**功能**：
- 召回状态卡片：显示召回状态（召回中/已结束/未召回/未找到）
- 风险等级：仅在召回中显示（高/中/低）
- 产品详情：品牌、产品名称、批次、规格、有效期、地区
- 召回原因：详细的召回原因说明
- 官方链接：跳转到官方召回公告
- 保存历史：保存到本地查询历史
- 重新查询：返回首页重新查询

### 4. 历史记录页面

**路径**：`pages/history/history`

**功能**：
- 筛选功能：全部/召回中/未召回/已结束
- 历史列表：显示所有查询记录
- 批次号、状态、产品名称、查询时间
- 点击记录：跳转到查询结果页面
- 清空历史：清空所有本地查询记录

---

## 🎨 设计系统

### 颜色方案

| 用途 | 颜色 | 说明 |
|------|------|------|
| 主色调 | #0078D7 | 雀巢蓝色 |
| 强调色 | #00A651 | 雀巢绿色 |
| 警告色 | #FF5252 | 召回中/高风险 |
| 成功色 | #52C41A | 未召回/安全 |
| 信息色 | #999999 | 未找到/已结束 |
| 背景色 | #F5F5F5 | 浅灰背景 |
| 卡片背景 | #FFFFFF | 白色卡片 |

### 字体系统

| 用途 | 大小 | 字重 |
|------|------|------|
| 大标题 | 24px | Bold |
| 页面标题 | 20px | Bold |
| 卡片标题 | 18px | Bold |
| 正文 | 16px | Regular |
| 辅助文字 | 14px | Regular |
| 小字 | 12px | Regular |

---

## 🔧 配置说明

### 百度 OCR 配置

```javascript
baiduOcr: {
  apiKey: 'YOUR_BAIDU_OCR_API_KEY',
  apiUrl: 'https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic',
  options: {
    'language_type': 'CHN_ENG',
    'detect_direction': 'true',
    'probability': 'false'
  }
}
```

**申请地址**：https://cloud.baidu.com/product/ocr/general

### 飞书配置

```javascript
feishu: {
  appId: 'cli_a9f1f4887e38dcd2',
  appSecret: 'aNhAQdFTDJSWaQZnj2dy7dXvDgOzdi7u',
  appToken: 'R7cwbZ2Iaa4v0vs0Fh1cc5KUnEg',
  tableId: 'tblA1YqzSi4aaxeI'
}
```

---

## 📊 数据结构

### 召回批次表

| 字段名 | 类型 | 说明 |
|--------|------|------|
| brand | 文本 | 品牌（雀巢、Abbott等） |
| brand_en | 文本 | 品牌英文名 |
| product_name | 文本 | 产品名称 |
| sub_brand | 文本 | 子品牌（SMA、NAN等） |
| batch_codes | 文本 | 批次号（逗号分隔） |
| pack_size | 文本 | 包装规格（800g、400g） |
| best_before | 日期时间 | 有效期 |
| region | 文本 | 受影响地区 |
| recall_reason | 文本 | 召回原因 |
| risk_level | 单选 | 风险等级（高/中/低） |
| source_url | 超链接 | 官方来源链接 |
| source_type | 单选 | 数据源类型 |
| published_date | 日期时间 | 发布日期 |
| last_updated | 日期时间 | 最后更新日期 |
| status | 单选 | 状态（召回中/已结束/待确认） |

---

## 🔄 开发计划

### v1.0（当前版本）

✅ **已完成**：
- 小程序基础框架
- 4 个核心页面
- OCR 识别功能
- 手动批次号输入
- 查询结果展示
- 历史记录管理
- 本地数据存储
- 雀巢主题色系
- 响应式布局

⏳ **进行中**：
- 百度 OCR 真实 API 集成
- 飞书查询接口对接
- 批次号匹配逻辑优化
- 错误处理和提示

### v1.1（计划中）

- [ ] Abbott 召回数据采集
- [ ] FDA 召回数据采集
- [ ] 批次号格式验证优化
- [ ] 模糊匹配算法改进
- [ ] 批量查询功能
- [ ] 订阅提醒功能

---

## 📞 技术支持

### 常见问题

**Q: 如何获取百度 OCR API Key？**
A: 访问 https://cloud.baidu.com/product/ocr/general，创建应用并获取 API Key。

**Q: 如何配置飞书多维表格权限？**
A: 在飞书多维表格中，点击"..."→"添加文档应用"，搜索应用 ID 并给予"可管理"权限。

**Q: 如何在小程序中测试？**
A: 使用微信开发者工具的"预览"功能，在模拟器中测试所有功能。

**Q: OCR 识别失败怎么办？**
A: 检查网络连接、百度 OCR API Key 是否正确、图片是否清晰。

**Q: 批次号查询不返回结果？**
A: 确保批次号格式正确（雀巢：8-10位，数字字母混合），检查飞书数据库是否正确配置。

---

## 📄 相关文档

- [小程序开发文档](https://developers.weixin.qq.com/miniprogram/dev/framework/)
- [飞书开放平台](https://open.feishu.cn/)
- [百度 OCR 文档](https://cloud.baidu.com/doc/OCR/)
- [项目设计文档](/docs/xiaochengyuanxing-sheji.md)

---

**版本**：v1.0
**最后更新**：2026-01-30
**开发团队**：Clawdbot
