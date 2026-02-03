# Code Review 报告

**Review 时间：** 2026-02-03
**Reviewer：** AI Assistant
**版本：** v2.1.1
**范围：** UI/UX 优化 + 错误修复

---

## 📊 Review 总览

| 指标 | 数值 |
|------|------|
| **Review 文件数** | 11 个 |
| **代码行数** | ~3,433 行 |
| **发现问题** | 12 个 |
| **严重问题** | 3 个 |
| **中等问题** | 6 个 |
| **轻微问题** | 3 个 |
| **单元测试覆盖** | 0% ⚠️ |

---

## 🔴 严重问题（必须修复）

### 1. 缺少单元测试 ⚠️⚠️⚠️

**问题描述：**
- 所有修改的代码都没有单元测试
- 包括业务逻辑、工具函数、API 客户端等

**影响：**
- 无法保证代码正确性
- 重构时容易引入 bug
- 难以验证修复的效果

**建议：**
```javascript
// tests/utils/api_client.test.js
describe('RecallApiClient', () => {
  it('应该正确查询批次号', async () => {
    const client = new RecallApiClient();
    const result = await client.queryBatch('51450742F1');
    expect(result.success).toBe(true);
  });

  it('应该处理空批次号', async () => {
    const client = new RecallApiClient();
    await expect(client.queryBatch('')).rejects.toThrow('批次号不能为空');
  });
});

// tests/pages/index/index.test.js
describe('Index Page', () => {
  it('应该正确格式化时间', () => {
    const page = createPage('pages/index/index');
    const now = Date.now();
    const result = page.formatTimeAgo(now - 30000); // 30秒前
    expect(result).toBe('刚刚');
  });
});
```

---

### 2. wx.cloud 依赖未验证 ⚠️⚠️

**问题描述：**
```javascript
// index.js - uploadImage 方法
uploadImage(filePath) {
  return new Promise((resolve, reject) => {
    wx.cloud.uploadFile({  // ❌ 依赖微信云开发
      cloudPath: `ocr_images/${Date.now()}.jpg`,
      filePath: filePath,
      // ...
    });
  });
}
```

**影响：**
- 如果没有启用云开发，OCR 功能将无法使用
- 没有检查云开发是否初始化

**建议：**
```javascript
// 添加云开发检查
uploadImage(filePath) {
  // 检查云开发是否初始化
  if (!wx.cloud) {
    wx.showModal({
      title: '功能不可用',
      content: '请先启用微信云开发',
      showCancel: false
    });
    return Promise.reject(new Error('云开发未启用'));
  }

  return new Promise((resolve, reject) => {
    wx.cloud.uploadFile({ /* ... */ });
  });
}
```

---

### 3. Token 未缓存 ⚠️⚠️

**问题描述：**
```javascript
// api_client.js - getFeishuToken 方法
async getFeishuToken() {
  const url = `${this.feishuApiUrl}/auth/v3/tenant_access_token/internal`;

  return new Promise((resolve, reject) => {
    wx.request({
      url,
      method: 'POST',
      // ❌ 每次都请求新 token，浪费资源
      success: (response) => {
        resolve(result.tenant_access_token);
      }
    });
  });
}
```

**影响：**
- 每次查询飞书 API 都要重新获取 token
- 浪费网络请求和服务器资源
- 可能触发 API 限流

**建议：**
```javascript
class RecallApiClient {
  constructor() {
    this.localApiUrl = 'http://14.103.26.111:5001/api';
    this.feishuApiUrl = config.feishu.apiUrl || 'https://open.feishu.cn/open-apis';
    this.apiType = 'local';
    this.feishuToken = null;  // ✅ 缓存 token
    this.tokenExpireTime = 0;  // ✅ 记录过期时间
  }

  async getFeishuToken() {
    // ✅ 检查 token 是否有效
    if (this.feishuToken && Date.now() < this.tokenExpireTime) {
      return this.feishuToken;
    }

    const url = `${this.feishuApiUrl}/auth/v3/tenant_access_token/internal`;

    return new Promise((resolve, reject) => {
      wx.request({
        url,
        method: 'POST',
        data: {
          app_id: config.feishu.appId,
          app_secret: config.feishu.appSecret
        },
        success: (response) => {
          const result = response.data;

          if (result.code !== 0) {
            reject(new Error(`获取飞书token失败: ${result.msg}`));
          } else {
            // ✅ 缓存 token（默认 2 小时有效）
            this.feishuToken = result.tenant_access_token;
            this.tokenExpireTime = Date.now() + (result.expire || 7200) * 1000;
            resolve(result.tenant_access_token);
          }
        },
        fail: (error) => {
          console.error('获取飞书token失败:', error);
          reject(error);
        }
      });
    });
  }
}
```

---

## 🟡 中等问题（建议修复）

### 4. 代码重复：wx.request 包装

**问题描述：**
```javascript
// 在 queryLocal, queryFeishu, getFeishuToken, getStats, ocrImage, healthCheck
// 都有类似的 wx.request Promise 包装
async queryLocal(batchCode) {
  return new Promise((resolve, reject) => {
    wx.request({
      url,
      method: 'POST',
      success: (res) => resolve(res.data),
      fail: (err) => reject(err)
    });
  });
}

async queryFeishu(batchCode) {
  return new Promise((resolve, reject) => {
    wx.request({
      url,
      method: 'POST',
      success: (res) => resolve(res.data),
      fail: (err) => reject(err)
    });
  });
}

// ... 重复 6 次
```

**建议：**
```javascript
class RecallApiClient {
  /**
   * 通用的 request 方法
   */
  request(options) {
    return new Promise((resolve, reject) => {
      wx.request({
        ...options,
        success: (response) => {
          resolve(response.data);
        },
        fail: (error) => {
          reject(error);
        }
      });
    });
  }

  async queryLocal(batchCode) {
    const url = `${this.localApiUrl}/query`;
    return this.request({
      url,
      method: 'POST',
      header: { 'Content-Type': 'application/json' },
      data: { batch_code: batchCode }
    });
  }

  async ocrImage(imageUrl) {
    const url = `${this.localApiUrl}/ocr`;
    return this.request({
      url,
      method: 'POST',
      header: { 'Content-Type': 'application/json' },
      data: { image_url: imageUrl }
    });
  }
}
```

---

### 5. Magic String 硬编码

**问题描述：**
```javascript
// api_client.js
this.apiType = 'local';  // ❌ Magic String
this.feishuApiUrl = config.feishu.apiUrl || 'https://open.feishu.cn/open-apis';  // ❌ Magic String

// index.js
if (!res.authSetting['scope.camera']) {  // ❌ Magic String
  wx.authorize({ scope: 'scope.camera' });
}
```

**建议：**
```javascript
// constants/api.js
export const API_TYPES = {
  LOCAL: 'local',
  FEISHU: 'feishu'
};

export const SCOPES = {
  CAMERA: 'scope.camera'
};

export const API_URLS = {
  FEISHU_DEFAULT: 'https://open.feishu.cn/open-apis'
};

// api_client.js
import { API_TYPES, API_URLS } from '../../constants/api';

class RecallApiClient {
  constructor() {
    this.apiType = API_TYPES.LOCAL;  // ✅ 使用常量
    this.feishuApiUrl = config.feishu.apiUrl || API_URLS.FEISHU_DEFAULT;
  }
}

// index.js
import { SCOPES } from '../../constants/api';

openCamera() {
  wx.getSetting({
    success: (res) => {
      if (!res.authSetting[SCOPES.CAMERA]) {  // ✅ 使用常量
        wx.authorize({ scope: SCOPES.CAMERA });
      }
    }
  });
}
```

---

### 6. 时间格式化逻辑重复

**问题描述：**
```javascript
// index.js
formatTimeAgo(timestamp) {
  const now = Date.now();
  const diff = now - timestamp;

  if (diff < 60000) {
    return '刚刚';
  } else if (diff < 3600000) {
    return `${Math.floor(diff / 60000)}分钟前`;
  } else if (diff < 86400000) {
    return `${Math.floor(diff / 3600000)}小时前`;
  } else {
    return `${Math.floor(diff / 86400000)}天前`;
  }
}

// history.js 也有类似的逻辑（来自 utils/date.js）
```

**建议：**
```javascript
// utils/date.js
const TIME_UNITS = [
  { name: '分钟', ms: 60000 },
  { name: '小时', ms: 3600000 },
  { name: '天', ms: 86400000 }
];

export function formatTimeAgo(timestamp) {
  const now = Date.now();
  const diff = now - timestamp;

  if (diff < 60000) {
    return '刚刚';
  }

  for (const unit of TIME_UNITS) {
    const value = Math.floor(diff / unit.ms);
    if (value > 0) {
      return `${value}${unit.name}前`;
    }
  }

  return '刚刚';
}

// index.js 和 history.js 都使用
import { formatTimeAgo } from '../../utils/date';
```

---

### 7. 错误提示不够友好

**问题描述：**
```javascript
// index.js
catch (error) {
  console.error('OCR识别失败:', error);  // ❌ 只记录日志，没有提示用户

  wx.showModal({
    title: '识别失败',
    content: error.message || '无法识别批次号，请重新拍照或手动输入',  // ⚠️ 技术术语对用户不友好
    // ...
  });
}
```

**建议：**
```javascript
// 创建错误提示映射
const ERROR_MESSAGES = {
  '上传失败': '图片上传失败，请检查网络',
  'OCR识别失败': '识别失败，请确保图片清晰',
  '获取文件URL失败': '图片处理失败，请重试',
  default: '识别失败，请重新拍照或手动输入'
};

function getUserFriendlyMessage(error) {
  return ERROR_MESSAGES[error.message] || ERROR_MESSAGES.default;
}

// 使用
catch (error) {
  console.error('OCR识别失败:', error);

  wx.showModal({
    title: '识别失败',
    content: getUserFriendlyMessage(error),
    // ...
  });
}
```

---

### 8. 缺少加载状态重置

**问题描述：**
```javascript
// index.js
async startOCR(filePath) {
  this.setData({
    showCamera: false,
    ocrLoading: true
  });

  try {
    // ... OCR 逻辑
  } catch (error) {
    // ...
  } finally {
    this.setData({ ocrLoading: false });  // ✅ 这里重置了
  }
}

// 但在某些错误分支中可能没有重置
```

**建议：**
```javascript
// 使用封装的错误处理
async startOCR(filePath) {
  this.setData({
    showCamera: false,
    ocrLoading: true
  });

  try {
    await this.doOCR(filePath);
  } catch (error) {
    this.handleOCRError(error);
  } finally {
    this.setData({ ocrLoading: false });  // ✅ 确保 always 执行
  }
}
```

---

### 9. 批次号验证规则不一致

**问题描述：**
```javascript
// index.js
if (!/^[A-Z0-9]{5,15}$/i.test(batchCode)) {  // 5-15位字母和数字
  wx.showModal({
    title: '格式提示',
    content: '批次号应为5-15位字母和数字，是否继续查询？',
    // ...
  });
}

// 但历史记录中的批次号可能有不同的格式
```

**建议：**
```javascript
// 创建统一的批次号验证器
class BatchCodeValidator {
  constructor() {
    this.rules = [
      { name: 'length', test: (code) => code.length >= 5 && code.length <= 15 },
      { name: 'alphanumeric', test: (code) => /^[A-Z0-9]+$/i.test(code) }
    ];
  }

  validate(code) {
    const errors = [];

    for (const rule of this.rules) {
      if (!rule.test(code)) {
        errors.push(rule.name);
      }
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }
}

// 使用
const validator = new BatchCodeValidator();
const result = validator.validate(batchCode);

if (!result.valid) {
  wx.showModal({
    title: '格式提示',
    content: `批次号格式不正确：${result.errors.join(', ')}，是否继续查询？`,
    // ...
  });
}
```

---

## 🔵 轻微问题（可选修复）

### 10. Magic Number

**问题描述：**
```javascript
// index.js
if (diff < 60000) {  // ❌ 60000 是什么？
  return '刚刚';
} else if (diff < 3600000) {  // ❌ 3600000 是什么？
  return `${Math.floor(diff / 60000)}分钟前`;
}
```

**建议：**
```javascript
// constants/time.js
export const TIME_CONSTANTS = {
  MINUTE: 60 * 1000,
  HOUR: 60 * 60 * 1000,
  DAY: 24 * 60 * 60 * 1000
};

// 使用
import { TIME_CONSTANTS } from '../../constants/time';

if (diff < TIME_CONSTANTS.MINUTE) {
  return '刚刚';
} else if (diff < TIME_CONSTANTS.HOUR) {
  return `${Math.floor(diff / TIME_CONSTANTS.MINUTE)}分钟前`;
}
```

---

### 11. 缺少 TypeScript 类型定义

**建议：**
```typescript
// types/api.ts
export interface ApiResponse<T> {
  success: boolean;
  message?: string;
  data?: T;
}

export interface RecallRecord {
  brand: string;
  product_name: string;
  batch_codes: string;
  pack_size: string;
  best_before: number;
  region: string;
  recall_reason: string;
  risk_level: string;
  status: string;
}

export interface QueryResult {
  success: boolean;
  matched: boolean;
  records: RecallRecord[];
  total: number;
  message?: string;
}

// types/page.ts
export interface IndexPageData {
  showCamera: boolean;
  cameraContext: any;
  ocrLoading: boolean;
  ocrResult: string;
  manualInput: string;
  recentHistory: HistoryItem[];
}

export interface HistoryItem {
  id: string;
  batchCode: string;
  status: 'safe' | 'danger' | 'unknown' | 'querying';
  productName: string;
  queryTime: number;
}
```

---

### 12. 缺少 JSDoc 注释

**建议：**
```javascript
/**
 * RecallApiClient - 召回查询 API 客户端
 *
 * @class
 * @description 支持本地 API 和飞书 API，自动容错和降级
 *
 * @example
 * const client = new RecallApiClient();
 * const result = await client.queryBatch('51450742F1');
 *
 * @see {@link https://github.com/cctv549681/recall-checker}
 * @version 2.1.1
 */
class RecallApiClient {
  /**
   * 构造函数
   * @constructor
   * @description 初始化 API 客户端，配置基础 URL
   */
  constructor() {
    /** @type {string} 本地 API 基础 URL */
    this.localApiUrl = 'http://14.103.26.111:5001/api';

    /** @type {string} 飞书 API 基础 URL */
    this.feishuApiUrl = config.feishu.apiUrl || 'https://open.feishu.cn/open-apis';

    /** @type {'local' | 'feishu'} 当前使用的 API 类型 */
    this.apiType = 'local';
  }

  /**
   * 查询批次号
   *
   * @param {string} batchCode - 批次号（不区分大小写）
   * @returns {Promise<QueryResult>} 查询结果
   * @throws {Error} 当批次号为空时抛出错误
   *
   * @example
   * const result = await client.queryBatch('51450742F1');
   * if (result.matched) {
   *   console.log('找到召回记录');
   * }
   */
  async queryBatch(batchCode) {
    // ...
  }
}
```

---

## 📝 Review 总结

### 优点 ✅

1. **用户体验大幅提升**
   - 操作流程简化，从 6-7 步减少到 2-3 步
   - 取消多余的确认弹窗
   - 界面设计现代化

2. **错误修复正确**
   - 修复了 `wx.request` 的 Promise 包装问题
   - 添加了缺失的 `goToIndex` 方法
   - 修复了清空确认弹窗的逻辑混乱

3. **代码结构清晰**
   - 方法命名语义化
   - 逻辑分层合理
   - 代码可读性较好

### 需要改进 ⚠️

1. **缺少单元测试** - 这是最严重的问题
2. **代码重复** - `wx.request` 包装逻辑重复
3. **Magic String** - 硬编码字符串较多
4. **错误处理** - 部分错误提示不够友好
5. **Token 缓存** - 飞书 token 未缓存
6. **云开发依赖** - 未检查云开发是否启用

---

## 🎯 建议优先级

### 🔴 高优先级（必须修复）
1. ✅ 添加单元测试
2. ✅ 检查云开发依赖
3. ✅ 实现 token 缓存

### 🟡 中优先级（建议修复）
4. 提取 `wx.request` 包装为通用方法
5. 使用常量替代 Magic String
6. 优化错误提示
7. 添加加载状态保护

### 🔵 低优先级（可选优化）
8. 使用 Magic Number 常量
9. 添加 TypeScript 类型定义
10. 完善 JSDoc 注释

---

## 📚 推荐的测试框架

### Jest + 微信小程序测试工具

```bash
# 安装依赖
npm install --save-dev jest @wechat-miniprogram/miniprogram-simulate

# 配置 jest
# jest.config.js
module.exports = {
  testEnvironment: 'node',
  testMatch: ['**/tests/**/*.test.js'],
  collectCoverageFrom: [
    'miniprogram/**/*.js',
    '!miniprogram/**/*.test.js'
  ]
};
```

### 测试示例

```javascript
// tests/api_client.test.js
const RecallApiClient = require('../../miniprogram/utils/api_client');

describe('RecallApiClient', () => {
  let client;

  beforeEach(() => {
    client = new RecallApiClient();
  });

  describe('queryBatch', () => {
    it('应该正确查询批次号', async () => {
      // Mock wx.request
      global.wx = {
        request: jest.fn((options) => {
          options.success({
            data: { success: true, status: 'recalled', data: [] }
          });
        })
      };

      const result = await client.queryBatch('51450742F1');
      expect(result.success).toBe(true);
    });

    it('应该拒绝空批次号', async () => {
      await expect(client.queryBatch('')).rejects.toThrow('批次号不能为空');
    });
  });
});
```

---

## ✅ 下一步行动

1. **立即修复**（高优先级）
   - [ ] 添加基础单元测试
   - [ ] 检查云开发依赖
   - [ ] 实现 token 缓存

2. **近期修复**（中优先级）
   - [ ] 重构代码，消除重复
   - [ ] 使用常量替代 Magic String
   - [ ] 优化错误提示

3. **长期优化**（低优先级）
   - [ ] 添加 TypeScript
   - [ ] 完善 JSDoc
   - [ ] 提升测试覆盖率到 80%+

---

**Review 完成时间：** 2026-02-03
**Reviewer：** AI Assistant
**下次 Review：** v2.2.0
