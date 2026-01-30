# 飞书多维表格脚本

## 📁 文件说明

### 核心文件

| 文件 | 说明 |
|------|------|
| `feishu_config.py` | 飞书API配置（APP_ID、APP_SECRET、APP_TOKEN） |
| `utils/feishu_client.py` | 飞书客户端封装类 |
| `utils/feishu_tables.py` | 表格结构定义和管理器 |

### 工具脚本

| 脚本 | 用途 |
|------|------|
| `feishu_test.py` | **通用测试工具** - 测试连接、列出表格/字段/记录、插入数据 |
| `setup_table.py` | **表格初始化** - 创建字段并插入测试数据 |

## 🚀 快速开始

### 1. 配置凭证

编辑 `feishu_config.py`:
```python
APP_ID = "cli_xxxxx"           # 应用ID
APP_SECRET = "xxxxxxxx"        # 应用密钥
APP_TOKEN = "bascxxxxx"        # 多维表格Token
TABLE_ID = "tblxxxxx"          # 表格ID
```

### 2. 测试连接

```bash
python3 feishu_test.py
```

功能菜单：
- 测试API连接
- 列出所有表格
- 列出字段
- 列出记录
- 插入测试记录

### 3. 初始化表格

```bash
python3 setup_table.py
```

自动执行：
- 查看当前字段
- 添加召回批次相关字段
- 插入测试数据

## 📊 表格结构

### 召回批次表字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| brand | 文本 | 品牌（雀巢、Abbott等） |
| brand_en | 文本 | 品牌英文名 |
| product_name | 文本 | 产品名称 |
| sub_brand | 文本 | 子品牌（SMA、NAN） |
| batch_codes | 文本 | 批次号列表（逗号分隔） |
| pack_size | 文本 | 包装规格（800g、400g） |
| best_before | 日期时间 | 有效期 |
| region | 文本 | 受影响地区（UK/US/EU/China） |
| recall_reason | 文本 | 召回原因 |
| risk_level | 单选 | 风险等级（高/中/低） |
| source_url | 超链接 | 官方来源链接 |
| source_type | 单选 | 数据源类型（官网/政府平台/FDA/FSA） |
| published_date | 日期时间 | 发布日期 |
| last_updated | 日期时间 | 最后更新日期 |
| status | 单选 | 状态（召回中/已结束/待确认） |

## ⚠️ 注意事项

1. **权限设置**
   - 在飞书多维表格中，点击「...」→「...更多」→「添加文档应用」
   - 添加你的应用并给予「可管理」权限

2. **APP_TOKEN 格式**
   - 应为 `bascxxxxx` 格式
   - 从多维表格 URL 中获取：`https://xxx.feishu.cn/base/bascxxxxx`

3. **Tenant Token**
   - 使用 `tenant_access_token` 而非 `app_access_token`
   - 需要多维表格编辑权限

## 🔧 API调用示例

```python
from utils.feishu_client import FeishuClient

client = FeishuClient(APP_ID, APP_SECRET, APP_TOKEN, table_ids={
    "batches": TABLE_ID
})

# 插入记录
record = {
    "brand": "雀巢",
    "batch_codes": "TEST123456",
    "risk_level": "高"
}
record_id = client.create_record("batches", record)

# 查询记录
records = client.query_records("batches", page_size=20)
```
