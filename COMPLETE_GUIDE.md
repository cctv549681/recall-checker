# Recall Checker - 完整使用指南

> **当前状态**: 核心功能已完成 ✅
> **更新时间**: 2026-01-31 16:30

---

## 📊 系统架构

```
┌─────────────┐
│  微信小程序   │
│  (前端）     │
└──────┬──────┘
       │
       │ HTTP API
       ▼
┌─────────────┐
│ Flask API    │ ← http://127.0.0.1:5001
│  服务器       │
└──────┬──────┘
       │
       │ 查询/批量插入
       ▼
┌─────────────┐
│  飞书多维表格  │ ← 3122条召回记录
└─────────────┘
```

---

## 🚀 快速启动

### 1. 启动API服务器

```bash
cd /root/clawd/recall-checker/scraper
python3 api_server.py
```

服务器将在 `http://127.0.0.1:5001` 启动

**输出示例：**
```
INFO: 启动召回查询API服务器，端口: 5001
INFO: 飞书表格: tblA1YqzSi4aaxeI
INFO: 预热缓存...
INFO: 成功获取飞书token
INFO: 成功获取 3122 条召回记录
INFO: 更新缓存: 3122 条记录
* Running on http://127.0.0.1:5001
```

---

### 2. 测试API接口

#### 2.1 健康检查
```bash
curl http://127.0.0.1:5001/api/health
```

**响应示例：**
```json
{
  "service": "recall-checker-api",
  "status": "ok",
  "timestamp": "2026-01-31T08:30:00.000Z"
}
```

#### 2.2 查询召回批次号
```bash
curl -X POST http://127.0.0.1:5001/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "batch_code": "51450742F1"
  }'
```

**响应示例：**
```json
{
  "success": true,
  "status": "recalled",
  "message": "找到 5 条召回记录",
  "data": [
    {
      "brand": "雀巢 Nestlé",
      "brand_en": "Nestlé",
      "product_name": "SMA Advanced First Infant Milk",
      "sub_brand": "SMA",
      "batch_codes": "51450742F1,52319722BA",
      "pack_size": "800g",
      "best_before": 1800556800000,
      "region": "UK",
      "recall_reason": "Cereulide毒素",
      "risk_level": "高",
      "status": "召回中"
    }
  ]
}
```

#### 2.3 查询不存在的批次号
```bash
curl -X POST http://127.0.0.1:5001/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "batch_code": "INVALID999"
  }'
```

**响应示例：**
```json
{
  "success": true,
  "status": "not_found",
  "message": "未找到召回记录",
  "data": []
}
```

#### 2.4 获取数据统计
```bash
curl http://127.0.0.1:5001/api/stats
```

**响应示例：**
```json
{
  "success": true,
  "message": "获取统计成功",
  "data": {
    "total_records": 3122,
    "by_brand": {
      "雅培 Abbott": 3084,
      "雀巢 Nestlé": 38
    },
    "by_status": {
      "已结束": 3084,
      "召回中": 38
    }
  }
}
```

---

## 📱 小程序配置

### 1. 修改API配置

编辑 `/miniprogram/utils/api_client.js`:

```javascript
constructor() {
  // 本地API服务器地址
  this.localApiUrl = 'http://127.0.0.1:5001/api';
  
  // 飞书API（备用）
  this.feishuApiUrl = 'https://open.feishu.cn/open-apis';
  
  // 当前使用的API类型
  this.apiType = 'local'; // 'local' 或 'feishu'
}
```

**注意**：
- 开发环境使用 `http://127.0.0.1:5001/api`
- 生产环境需要修改为云服务器地址

### 2. 在微信开发者工具中测试

1. 打开微信开发者工具
2. 导入 `/root/clawd/recall-checker/miniprogram` 目录
3. 配置 AppID
4. 点击编译

### 3. 测试查询功能

#### 方式1：手动输入批次号

1. 在首页的输入框中输入：`51450742F1`
2. 点击"查询"按钮
3. 跳转到结果页面，应该显示召回信息

#### 方式2：OCR识别

1. 点击"拍照查询"按钮
2. 拍摄奶粉罐批次号区域
3. 系统自动识别并查询

#### 方式3：历史记录

1. 点击"历史记录"按钮
2. 选择历史查询记录
3. 查看详细结果

---

## 🧪 测试用例

### 测试用例1：查询召回批次号

| 批次号 | 品牌 | 预期结果 |
|--------|------|---------|
| 51450742F1 | 雀巢 | 找到（召回中） |
| 57713T260 | 雅培 | 找到（已结束） |
| INVALID999 | - | 未找到 |

**测试命令：**
```bash
# 雀巢
curl -X POST http://127.0.0.1:5001/api/query \
  -H "Content-Type: application/json" \
  -d '{"batch_code":"51450742F1"}'

# 雅培
curl -X POST http://127.0.0.1:5001/api/query \
  -H "Content-Type: application/json" \
  -d '{"batch_code":"57713T260"}'

# 不存在
curl -X POST http://127.0.0.1:5001/api/query \
  -H "Content-Type: application/json" \
  -d '{"batch_code":"INVALID999"}'
```

### 测试用例2：部分批次号匹配

| 部分批次号 | 预期结果 |
|-----------|---------|
| 5145 | 应该匹配雀巢批次号 |
| 57713 | 应该匹配雅培批次号 |

**测试命令：**
```bash
curl -X POST http://127.0.0.1:5001/api/query \
  -H "Content-Type: application/json" \
  -d '{"batch_code":"5145"}'
```

---

## 📊 数据统计

### 当前数据量

| 品牌 | 记录数 | 状态 |
|------|--------|------|
| 雀巢 Nestlé | 38 | 召回中 |
| 雅培 Abbott | 3084 | 已结束 |
| **总计** | **3122** | - |

### 数据分布

#### 按品牌分布
- 雅培 Abbott: 3084条 (98.8%)
- 雀巢 Nestlé: 38条 (1.2%)

#### 按状态分布
- 已结束: 3084条 (98.8%)
- 召回中: 38条 (1.2%)

---

## 🔧 故障排查

### 问题1：API服务器无法启动

**症状：**
```
Address already in use
Port 5001 is in use by another program
```

**解决方案：**
```bash
# 查找占用端口的进程
lsof -i :5001

# 杀死进程
kill -9 <PID>

# 或修改端口（编辑 api_server.py）
# 将 port = 5001 改为 port = 5002
```

### 问题2：小程序无法连接API

**症状：**
```
request:fail
net::ERR_CONNECTION_REFUSED
```

**原因**：
- API服务器未启动
- 端口配置错误
- 网络连接问题

**解决方案：**
1. 检查API服务器是否正在运行
2. 检查小程序中的API地址配置
3. 确保微信开发者工具的网络设置正确

### 问题3：查询返回空结果

**可能原因**：
- 批次号不存在
- 批次号格式错误
- 数据库中的批次号格式不一致

**调试步骤：**
1. 在API服务器日志中查看查询记录
2. 使用curl测试API是否正常返回
3. 检查飞书表格中的数据

---

## 📝 下一步任务

### 高优先级（必须完成）

1. **小程序API配置完成** ⏸️
   - [x] 创建API客户端
   - [x] 修改结果页面使用真实API
   - [ ] 在微信开发者工具中测试
   - [ ] 修复网络连接问题

2. **OCR功能集成** ⏸️
   - [x] 创建百度OCR配置
   - [ ] 申请百度OCR API Key
   - [ ] 测试图片识别
   - [ ] 优化批次号提取算法

3. **部署到云服务器** ⏸️
   - [ ] 购买云服务器（阿里云/腾讯云）
   - [ ] 部署Flask API
   - [ ] 配置域名和SSL
   - [ ] 修改小程序配置指向云服务器

4. **小程序审核提交** ⏸️
   - [ ] 完成所有功能测试
   - [ ] 准备审核材料
   - [ ] 提交审核
   - [ ] 等待审核通过

### 中优先级（优化提升）

5. **扩展其他品牌数据** ⏸️
   - [ ] 测试爱他美爬虫
   - [ ] 测试飞鹤爬虫
   - [ ] 测试美素佳儿爬虫
   - [ ] 测试a2至初爬虫
   - [ ] 测试金领冠爬虫

6. **性能优化** ⏸️
   - [ ] 优化API查询速度
   - [ ] 实现数据分页
   - [ ] 添加请求缓存
   - [ ] 优化小程序加载速度

---

## 📞 联系方式

- **API服务器**: http://127.0.0.1:5001
- **健康检查**: http://127.0.0.1:5001/api/health
- **查询接口**: POST http://127.0.0.1:5001/api/query
- **统计接口**: GET http://127.0.0.1:5001/api/stats

---

**最后更新**: 2026-01-31 16:30
**版本**: v2.0
**状态**: ✅ 核心功能完成，待测试和上线
