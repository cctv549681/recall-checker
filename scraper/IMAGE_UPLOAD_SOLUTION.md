# 图片上传技术方案对比

本文档对比两种图片上传方案，用于 OCR 识别功能。

## 📋 方案概述

### 方案 1：后端上传（当前使用）

**流程：**
```
小程序
  1. 拍照/选择图片
  2. 转换为 base64
  3. POST /api/ocr (image_base64)
      ↓
后端 API
  4. 接收 base64 图片
  5. 上传到 TOS/OSS
  6. 调用 OCR 服务
  7. 返回识别结果
      ↓
小程序
  8. 显示识别结果
```

**优点：**
- ✅ 实现简单，小程序端无需复杂配置
- ✅ 统一处理图片上传和 OCR 识别
- ✅ 后端可以集中控制上传逻辑（如压缩、格式转换）
- ✅ 安全性高，凭证不暴露给前端
- ✅ 易于调试和监控

**缺点：**
- ❌ Base64 编码会增加约 33% 的数据量
- ❌ 后端需要处理所有上传流量
- ❌ 大图片上传较慢（需要传输到后端再上传到 TOS）

**适用场景：**
- 图片较小（< 500KB）
- 并发量不大（QPS < 100）
- 快速验证和开发阶段

---

### 方案 2：预签名 URL（预留方案）

**流程：**
```
小程序
  1. 拍照/选择图片
  2. GET /api/upload/pre-sign?filename=xxx.jpg
      ↓
后端 API
  3. 生成预签名 URL
  4. 返回预签名 URL 给小程序
      ↓
小程序
  5. 直接上传图片到 TOS/OSS（使用预签名 URL）
  6. POST /api/ocr (image_url)
      ↓
后端 API
  7. 从 URL 获取图片
  8. 调用 OCR 服务
  9. 返回识别结果
```

**优点：**
- ✅ 节省后端带宽（小程序直连 TOS/OSS）
- ✅ 上传速度更快（减少一跳）
- ✅ 无需 Base64 编码，节省流量
- ✅ 适合大文件上传

**缺点：**
- ❌ 实现复杂，需要处理预签名 URL 生成
- ❌ 需要管理 URL 过期时间
- ❌ 上传失败需要重试机制
- ❌ 小程序端需要处理上传逻辑

**适用场景：**
- 图片较大（> 500KB）
- 高并发场景（QPS > 100）
- 需要优化后端性能

---

## 🎯 当前方案选择

### 使用：方案 1（后端上传）

**选择理由：**
1. 快速验证，开发效率高
2. 图片一般较小（批次号照片，< 200KB）
3. 并发量不高（QPS < 50）
4. 易于维护和调试

### 预留：方案 2（预签名 URL）

**使用时机：**
- 当图片变大（> 500KB）时
- 当并发量增加（QPS > 100）时
- 当需要优化后端性能时

---

## 📊 方案对比

| 维度 | 方案 1：后端上传 | 方案 2：预签名 URL |
|------|-----------------|------------------|
| **实现复杂度** | ⭐ 简单 | ⭐⭐⭐ 复杂 |
| **小程序端** | ⭐ 简单（base64） | ⭐⭐⭐ 复杂（上传） |
| **后端带宽** | ⭐⭐ 高（接收+上传） | ⭐⭐⭐ 低（仅返回 URL） |
| **用户流量** | ⭐⭐⭐ 高（+33% base64） | ⭐⭐ 低（直接上传） |
| **上传速度** | ⭐⭐ 中等（两跳） | ⭐⭐⭐ 快（直连） |
| **安全性** | ⭐⭐⭐ 高（凭证不暴露） | ⭐⭐ 中（URL 可能泄露） |
| **调试难度** | ⭐ 简单 | ⭐⭐⭐ 复杂 |
| **适合图片大小** | < 500KB | > 500KB |
| **适合并发量** | < 100 QPS | > 100 QPS |

---

## 🚀 方案 1 实现（当前）

### 小程序端

```javascript
// utils/api_client.js
async ocrImageBase64(imageBase64) {
  const url = `${this.localApiUrl}/ocr`;

  return new Promise((resolve, reject) => {
    wx.request({
      url,
      method: 'POST',
      header: {
        'Content-Type': 'application/json'
      },
      data: {
        image_base64: imageBase64
      },
      success: (response) => {
        const result = response.data;
        resolve({
          success: result.success,
          data: result.data,
          message: result.message
        });
      },
      fail: (error) => {
        reject(error);
      }
    });
  });
}
```

### 后端端

```python
# scraper/api_server.py
@app.route('/api/ocr', methods=['POST'])
def ocr_image():
    """OCR 图片识别（接收 base64）"""
    try:
        req_data = request.get_json()
        image_base64 = req_data.get('image_base64', '')

        # 1. 上传到图床（后端上传）
        # 2. 调用 OCR 服务
        # 3. 返回识别结果

        # ...
```

---

## 🔧 方案 2 实现（预留）

### 小程序端

```javascript
// utils/api_client.js
async getPreSignUrl(filename) {
  const url = `${this.localApiUrl}/upload/pre-sign`;

  return new Promise((resolve, reject) => {
    wx.request({
      url,
      method: 'GET',
      data: {
        filename: filename
      },
      success: (response) => {
        resolve(response.data);
      },
      fail: (error) => {
        reject(error);
      }
    });
  });
}

async uploadImageToTOS(filePath, preSignUrl) {
  return new Promise((resolve, reject) => {
    wx.uploadFile({
      url: preSignUrl,
      filePath: filePath,
      name: 'file',
      success: (res) => {
        if (res.statusCode === 200) {
          resolve({
            success: true,
            url: res.data.url
          });
        } else {
          reject(new Error(`上传失败: ${res.statusCode}`));
        }
      },
      fail: (error) => {
        reject(error);
      }
    });
  });
}

async ocrImageDirectUpload(filePath) {
  try {
    // 1. 获取预签名 URL
    const filename = `${Date.now()}.jpg`;
    const preSignResult = await this.getPreSignUrl(filename);

    if (!preSignResult.success) {
      throw new Error('获取预签名 URL 失败');
    }

    // 2. 直接上传到 TOS
    const uploadResult = await this.uploadImageToTOS(
      filePath,
      preSignResult.pre_sign_url
    );

    // 3. 调用 OCR API（使用 URL）
    const ocrResult = await this.ocrImage(uploadResult.url);

    return ocrResult;

  } catch (error) {
    console.error('OCR 识别失败:', error);
    throw error;
  }
}
```

### 后端端（新增）

```python
# scraper/api_server.py
@app.route('/upload/pre-sign', methods=['GET'])
def get_pre_sign_url():
    """
    生成预签名 URL

    请求参数:
        filename: 文件名

    返回:
        {
            "success": true,
            "pre_sign_url": "预签名 URL",
            "public_url": "公共访问 URL",
            "expires_in": 3600
        }
    """
    try:
        filename = request.args.get('filename', '')

        if not filename:
            return jsonify({
                'success': False,
                'message': '文件名不能为空'
            }), 400

        # 生成对象名称
        object_name = f"{os.getenv('VOLCENGINE_BASE_PATH', 'ocr/')}{filename}"

        # 创建预签名 URL（使用 boto3）
        from utils.volcengine_uploader import create_volcengine_uploader

        uploader = create_volcengine_uploader()
        if not uploader:
            return jsonify({
                'success': False,
                'message': '图床未配置'
            }), 400

        # 生成预签名 URL（3600 秒有效期）
        presigned_url = uploader.s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': uploader.bucket,
                'Key': object_name,
                'ContentType': 'image/jpeg'
            },
            ExpiresIn=3600
        )

        # 构建公共访问 URL
        public_url = f"{uploader.public_url}/{urllib.parse.quote(object_name)}"

        return jsonify({
            'success': True,
            'pre_sign_url': presigned_url,
            'public_url': public_url,
            'expires_in': 3600
        })

    except Exception as e:
        logger.error(f"生成预签名 URL 失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
```

### 火山引擎 TOS 上传器增强

```python
# scraper/utils/volcengine_uploader.py

def generate_presigned_url(self, object_name, expires=3600):
    """
    生成预签名 URL

    Args:
        object_name: 对象名称
        expires: 过期时间（秒）

    Returns:
        str: 预签名 URL
    """
    try:
        full_object_name = self._get_full_object_name(object_name)

        presigned_url = self.s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': self.bucket,
                'Key': full_object_name,
                'ContentType': 'image/jpeg'
            },
            ExpiresIn=expires
        )

        return presigned_url

    except Exception as e:
        logger.error(f"生成预签名 URL 失败: {e}")
        return None
```

---

## 📝 实施计划

### 阶段 1：使用方案 1（当前）

- ✅ 已完成
- ✅ 小程序端：base64 上传
- ✅ 后端端：接收 base64 并上传到 TOS
- ✅ OCR 服务集成

### 阶段 2：监控优化（持续）

- 📊 监控上传时间、成功率、带宽使用
- 📊 监控并发量、响应时间
- 📊 收集用户反馈

### 阶段 3：切换方案 2（可选）

**触发条件：**
- 平均上传时间 > 5 秒
- 后端带宽使用 > 100Mbps
- 并发量 > 100 QPS

**实施步骤：**
1. 实现预签名 URL 生成接口
2. 小程序端实现直连上传
3. 灰度测试（10% 流量）
4. 全量切换

---

## 🔐 安全考虑

### 方案 1 安全措施

1. **请求限制**
   - 限制上传图片大小（< 5MB）
   - 限制请求频率（每分钟最多 10 次）

2. **内容验证**
   - 验证 base64 格式
   - 验证图片类型（仅 JPEG/PNG）

3. **日志记录**
   - 记录所有上传请求
   - 监控异常流量

### 方案 2 安全措施

1. **预签名 URL 安全**
   - 设置较短过期时间（3600 秒）
   - 使用 HTTPS 传输
   - 限制单次使用

2. **文件名安全**
   - 验证文件名格式
   - 防止路径遍历攻击
   - 使用时间戳作为文件名

3. **权限控制**
   - 限制上传路径
   - 防止恶意上传

---

## 📚 参考资料

- [火山引擎 TOS 预签名 URL 文档](https://www.volcengine.com/docs/6348/)
- [AWS S3 预签名 URL 文档](https://docs.aws.amazon.com/AmazonS3/latest/userguide/ShareObjectPreSignedURL.html)
- [小程序上传文件 API](https://developers.weixin.qq.com/miniprogram/dev/api/network/upload/wx.uploadFile.html)

---

**文档版本**: v1.0
**创建时间**: 2026-02-06
**当前方案**: 方案 1（后端上传）
**预留方案**: 方案 2（预签名 URL）
