# 火山引擎 TOS 图床集成

本文档说明如何使用火山引擎 TOS 作为 OCR 服务的图床。

## 📋 概述

火山引擎 TOS（Tinder Object Storage）是火山引擎提供的对象存储服务，支持海量数据存储、高性能并发访问，可用作 GLM OCR 的图片上传器。

## 🔧 配置步骤

### 1. 获取火山引擎凭证

1. 访问 [火山引擎控制台](https://console.volcengine.com/tos)
2. 创建或选择一个存储桶（Bucket）
3. 获取访问密钥：
   - `Access Key ID`
   - `Secret Access Key`
4. 记录存储桶信息：
   - `Bucket 名称`
   - `Region`（如 `cn-beijing`）
   - `Endpoint`（如 `https://tos-cn-beijing.volces.com`）

### 2. 配置环境变量

创建或编辑 `/root/clawd/recall-checker/scraper/.env` 文件：

```bash
# OCR 配置
OCR_PROVIDER=glm
ZHIPU_API_KEY=your_zhipu_api_key_here

# 图床配置
OCR_IMAGE_UPLOADER=volcengine

# 火山引擎 TOS 配置
VOLCENGINE_ACCESS_KEY_ID=your_access_key_id
VOLCENGINE_SECRET_KEY=your_secret_key
VOLCENGINE_BUCKET=your-bucket-name
VOLCENGINE_REGION=cn-beijing
VOLCENGINE_ENDPOINT=https://tos-cn-beijing.volces.com
VOLCENGINE_BASE_PATH=ocr/
```

### 3. 加载环境变量

临时加载（当前会话）：
```bash
cd /root/clawd/recall-checker/scraper
export $(cat .env | xargs)
```

永久加载（写入 ~/.bashrc）：
```bash
cat .env >> ~/.bashrc
source ~/.bashrc
```

## 🧪 测试

### 测试图床上传器

```bash
cd /root/clawd/recall-checker/scraper

# 设置环境变量
export VOLCENGINE_ACCESS_KEY_ID=your_key
export VOLCENGINE_SECRET_KEY=your_secret
export VOLCENGINE_REGION=cn-beijing
export VOLCENGINE_BUCKET=your-bucket

# 运行测试
./venv/bin/python test_volcengine_uploader.py
```

### 测试 OCR 服务

```bash
# 启动 API 服务器
./venv/bin/python api_server.py

# 测试 OCR 状态
curl http://localhost:5001/api/ocr/status
```

## 📂 项目结构

```
scraper/
├── utils/
│   └── volcengine_uploader.py    # 火山引擎 TOS 上传器
├── ocr_service.py                 # OCR 服务（已集成火山引擎）
├── .env.example                   # 环境变量模板
├── .env                          # 环境变量配置
└── test_volcengine_uploader.py    # 测试脚本
```

## 🎯 使用方式

### 在 OCR 服务中使用

OCR 服务会自动读取环境变量并使用火山引擎 TOS 作为图床：

```python
# 在 OCR 服务中
OCR_PROVIDER=glm
OCR_IMAGE_UPLOADER=volcengine

# 服务会自动使用火山引擎 TOS 上传图片
```

### 独立使用火山引擎上传器

```python
from utils.volcengine_uploader import VolcengineTOSUploader

# 创建上传器
uploader = VolcengineTOSUploader(
    access_key_id='your_key',
    secret_key='your_secret',
    region='cn-beijing',
    bucket='your-bucket'
)

# 上传文件
result = uploader.upload_file('image.jpg')

if result['success']:
    print(f"上传成功: {result['url']}")
else:
    print(f"上传失败: {result['error']}")

# 上传字节数据
result = uploader.upload_bytes(
    data=b'Hello',
    object_name='test.txt',
    content_type='text/plain'
)
```

## 🔐 安全建议

1. **不要提交 `.env` 文件到 Git**
   - `.env` 文件包含敏感信息，已在 `.gitignore` 中排除

2. **使用最小权限原则**
   - 为 OCR 服务创建专用的访问密钥
   - 只授予必要的权限（上传、读取）

3. **定期轮换密钥**
   - 建议每 3 个月轮换一次访问密钥

4. **使用 HTTPS**
   - 确保 API 调用使用 HTTPS 协议

## 💰 费用说明

火山引擎 TOS 的费用主要包括：
- **存储费用**：根据存储量和存储类型计费
- **请求费用**：根据 PUT/GET 请求次数计费
- **流量费用**：公网下行流量计费

详见 [火山引擎 TOS 定价](https://www.volcengine.com/product/tos/pricing)

## 🌟 优势

| 特性 | 火山引擎 TOS |
|------|--------------|
| **性能** | 高性能并发写入，单桶无限容量 |
| **稳定性** | 自研分布式对象存储技术，大规模部署 |
| **成本** | 多种存储类型，根据访问频率自动分层 |
| **CDN** | 支持 CDN 加速，提升访问速度 |
| **可靠性** | 多副本存储，数据持久性 99.999999999% |

## 📚 参考资料

- [火山引擎 TOS 官方文档](https://www.volcengine.com/docs/6348/)
- [火山引擎 TOS API 参考](https://www.volcengine.com/docs/6348/)
- [火山引擎控制台](https://console.volcengine.com/tos)

## 🆘 常见问题

### Q1: 上传失败提示 403 Forbidden？

**A:** 检查以下几点：
1. 访问密钥是否正确
2. 存储桶名称和区域是否正确
3. 访问密钥是否有读写权限

### Q2: 上传成功但无法访问图片？

**A:** 检查存储桶的访问权限：
1. 登录火山引擎控制台
2. 进入存储桶设置
3. 确认存储桶是否设置为"公共读"或配置了正确的访问策略

### Q3: 如何查看上传的文件？

**A:** 有两种方式：
1. 通过火山引擎控制台查看文件列表
2. 使用返回的 URL 直接访问（如果存储桶是公共读的）

---

**更新时间**：2026-02-06
**版本**：v1.0
