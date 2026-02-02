# 百度OCR API集成说明

> **更新日期**: 2026年2月2日 21:20
> **状态**: ✅ 代码完成，待配置API Key

---

## 📋 已完成的工作

### 1. 百度OCR模块

**文件**: `scraper/baidu_ocr.py`

**功能**：
- ✅ 百度OCR客户端封装
- ✅ 访问令牌获取（自动刷新）
- ✅ 通用文字识别API
- ✅ 智能批次号提取算法
- ✅ 置信度评分

**API接口**：
- 获取令牌：`https://aip.baidubce.com/oauth/2.0/token`
- OCR识别：`https://aip.baidubce.com/rest/2.0/ocr/v1/general`

### 2. API服务器集成

**文件**: `scraper/api_server.py`

**新增接口**：
- `POST /api/ocr` - OCR图片识别

**请求格式**：
```json
{
  "image_url": "图片URL",
  "image_base64": "图片Base64编码"
}
```

**响应格式**：
```json
{
  "success": true,
  "data": {
    "batch_code": "51450742F1",
    "confidence": 85,
    "all_candidates": ["51450742F1", "52319722BA", "..."]
  },
  "message": "识别成功"
}
```

---

## 🔑 配置步骤

### 方案A：环境变量（推荐）

**在云服务器配置**：
```bash
# 设置环境变量
export BAIDU_API_KEY="你的API_Key"
export BAIDU_SECRET_KEY="你的Secret_Key"

# 重启API服务器
cd /root/clawd/recall-checker/scraper
./stop_server.sh
./start_production.sh
```

### 方案B：直接修改代码（测试用）

**编辑文件**: `scraper/api_server.py`
```python
# 直接配置API Key（仅用于测试，生产环境不推荐）
BAIDU_API_KEY = "你的API_Key"
BAIDU_SECRET_KEY = "你的Secret_Key"
```

---

## 📝 如何申请百度OCR API Key

### 1. 注册百度智能云

1. 访问：https://cloud.baidu.com/
2. 注册/登录百度账号
3. 进入控制台

### 2. 创建应用并开通OCR服务

1. 点击"管理控制台"
2. 选择"人工智能" → "文字识别"
3. 点击"立即使用"或"开通服务"
4. 创建新应用：
   - 应用名称：`Recall Checker`
   - 应用类型：`文字识别`
5. 开通服务：
   - 选择"通用文字识别（标准版）"（每天免费500次）
   - 或"通用文字识别（高精度版）"（每天免费50次，但准确率更高）
6. 确认开通

### 3. 获取API Key和Secret Key

1. 在应用详情页面找到：
   - **API Key**（AK）
   - **Secret Key**（SK）
2. 复制这两个值
3. 告诉我这两个值，我来帮你配置

---

## 🎯 批次号识别算法

### 识别规则

**批次号特征**：
- 长度：8-12位
- 字符：数字 + 大写字母
- 常见格式：
  - `51450742F1` - 数字+字母
  - `57713T260` - 数字+字母+数字
  - `A12345678` - 字母+数字

### 智能提取算法

1. **OCR文本提取**：从百度OCR结果中提取所有文字
2. **正则匹配**：使用模式 `[A-Z0-9]{8,12}` 提取候选
3. **评分排序**：
   - 长度优先（10-12位最佳）
   - 数字开头优先
   - 包含常见字母（F/A/B/L/P/R）优先
   - 字母数字混合优先
4. **置信度计算**：根据匹配质量计算置信度（60%-95%）

### 候选返回

```json
{
  "batch_code": "51450742F1",
  "confidence": 85,
  "all_candidates": [
    "51450742F1",
    "52319722BA",
    "52819722AA",
    "51240742F2",
    "51570742F3"
  ]
}
```

---

## 📊 测试状态

### 模拟测试（当前）

**API测试**：
```bash
# OCR识别测试
curl -X POST http://14.103.26.111:5001/api/ocr \
  -H "Content-Type: application/json" \
  -d '{"image_url":"https://example.com/test.jpg"}'
```

**返回结果**：
```json
{
  "success": true,
  "data": {
    "batch_code": "51450742F1",
    "confidence": 85
  },
  "message": "识别成功（模拟，请配置BAIDU_API_KEY和BAIDU_SECRET_KEY）"
}
```

### 真实OCR测试（配置API Key后）

**测试流程**：
1. 申请百度OCR API Key
2. 配置环境变量或告知我
3. 重启API服务器
4. 测试真实图片识别

---

## 🔄 工作流程

### 小程序OCR流程

```
用户拍照/选择图片
    ↓
上传到微信云存储
    ↓
调用后端 /api/ocr
    ↓
后端调用百度OCR API
    ↓
返回识别结果（批次号）
    ↓
显示给用户确认
    ↓
用户确认后查询
    ↓
跳转到查询结果页面
```

---

## 📋 待办事项

### 立即需要你做的

1. **申请百度OCR API Key**
   - 访问：https://cloud.baidu.com/
   - 开通文字识别服务
   - 获取API Key和Secret Key

2. **配置API Key**
   - 选择方案A：环境变量（推荐）
   - 或选择方案B：直接修改代码

3. **告知我API Key**
   - 我会帮你配置并重启服务器

### 可选：后期优化

- [ ] 支持更多图片格式（PNG、JPG、WebP）
- [ ] 添加图片压缩优化
- [ ] 批次号去重和模糊匹配
- [ ] OCR识别失败重试机制
- [ ] 添加图片预处理（旋转、裁剪）

---

## 📁 文件清单

### 新增文件
```
scraper/
├── baidu_ocr.py           # 百度OCR客户端模块
└── api_server.py           # API服务器（已更新/api/ocr）
```

### 已更新文件
```
miniprogram/
└── pages/camera/
    └── camera.js            # OCR页面（已更新API调用）
miniprogram/
└── utils/
    └── api_client.js        # API客户端（已更新OCR方法）
```

---

## ✅ 总结

**当前状态**：
- ✅ 百度OCR代码已完成
- ✅ API接口已集成
- ✅ 模拟测试可用
- ⏳ 等待配置API Key

**立即可用**：
- ✅ 所有现有接口（健康检查、批次号查询、统计）
- ⚠️ OCR接口（模拟数据，需要API Key）

**下一步**：
1. 你申请百度OCR API Key
2. 告诉我API Key和Secret Key
3. 我帮你配置并重启服务器
4. 测试真实OCR识别

---

**说明文档生成时间**: 2026年2月2日 21:20
**集成状态**: ✅ 代码完成，待配置
