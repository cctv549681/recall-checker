# 单元测试快速开始指南

**创建时间：** 2026-02-03
**版本：** v2.1.1

---

## 📊 当前测试覆盖率

| 模块 | 覆盖率 | 状态 |
|------|--------|------|
| `pages/index` | 0% | ❌ 未测试 |
| `pages/history` | 0% | ❌ 未测试 |
| `pages/result` | 0% | ❌ 未测试 |
| `pages/camera` | 0% | ❌ 未测试 |
| `utils/api_client` | 0% | ❌ 未测试 |
| `utils/storage` | 0% | ❌ 未测试 |
| **总计** | **0%** | ⚠️ 需要改进 |

---

## 🚀 快速开始

### 1. 安装测试依赖

```bash
cd /root/clawd/recall-checker/miniprogram
npm install --save-dev jest @wechat-miniprogram/miniprogram-simulate
```

### 2. 创建 Jest 配置

创建 `jest.config.js`：

```javascript
module.exports = {
  testEnvironment: 'node',
  testMatch: ['**/__tests__/**/*.test.js'],
  collectCoverageFrom: [
    '**/*.js',
    '!**/node_modules/**',
    '!**/__tests__/**'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
};
```

### 3. 创建测试目录

```bash
mkdir -p __tests__
mkdir -p __tests__/utils
mkdir -p __tests__/pages
```

---

## 📝 测试示例

### 1. 测试 api_client.js

创建 `__tests__/utils/api_client.test.js`：

```javascript
const RecallApiClient = require('../../miniprogram/utils/api_client');

// Mock wx.request
global.wx = {
  request: jest.fn((options) => {
    // 模拟成功响应
    options.success({
      data: {
        success: true,
        status: 'recalled',
        data: [],
        message: '查询成功'
      }
    });
  })
};

describe('RecallApiClient', () => {
  let client;

  beforeEach(() => {
    // 每个测试前创建新实例
    client = new RecallApiClient();
    // 清除 mock 调用记录
    global.wx.request.mockClear();
  });

  describe('constructor', () => {
    it('应该正确初始化 API 客户端', () => {
      expect(client.localApiUrl).toBe('http://14.103.26.111:5001/api');
      expect(client.apiType).toBe('local');
    });
  });

  describe('queryBatch', () => {
    it('应该成功查询批次号', async () => {
      const result = await client.queryBatch('51450742F1');

      expect(result.success).toBe(true);
      expect(result.matched).toBe(true);
      expect(global.wx.request).toHaveBeenCalled();
    });

    it('应该拒绝空批次号', async () => {
      await expect(client.queryBatch('')).rejects.toThrow('批次号不能为空');
      await expect(client.queryBatch(null)).rejects.toThrow('批次号不能为空');
      await expect(client.queryBatch(undefined)).rejects.toThrow('批次号不能为空');
    });

    it('应该标准化批次号', async () => {
      const result = await client.queryBatch('  abc123  ');

      // 检查 wx.request 是否被调用，并且 batch_code 被标准化
      const requestData = global.wx.request.mock.calls[0][0];
      expect(requestData.data.batch_code).toBe('ABC123');
    });
  });

  describe('queryLocal', () => {
    it('应该发送正确的请求', async () => {
      await client.queryBatch('51450742F1');

      const callArgs = global.wx.request.mock.calls[0][0];
      expect(callArgs.url).toBe('http://14.103.26.111:5001/api/query');
      expect(callArgs.method).toBe('POST');
      expect(callArgs.data.batch_code).toBe('51450742F1');
    });

    it('应该处理 API 失败', async () => {
      // Mock 失败响应
      global.wx.request = jest.fn((options) => {
        options.fail(new Error('网络错误'));
      });

      const newClient = new RecallApiClient();

      await expect(newClient.queryLocal('51450742F1')).rejects.toThrow('网络错误');
    });
  });

  describe('ocrImage', () => {
    it('应该成功识别图片', async () => {
      // Mock 成功响应
      global.wx.request = jest.fn((options) => {
        options.success({
          data: {
            success: true,
            data: {
              batch_code: '51450742F1',
              confidence: 95
            },
            message: '识别成功'
          }
        });
      });

      const result = await client.ocrImage('https://example.com/image.jpg');

      expect(result.success).toBe(true);
      expect(result.data.batch_code).toBe('51450742F1');
    });
  });
});
```

---

### 2. 测试 storage.js

创建 `__tests__/utils/storage.test.js`：

```javascript
const { saveHistory, getHistory, clearHistory } = require('../../miniprogram/utils/storage');

// Mock wx.getStorageSync 和 wx.setStorageSync
global.wx = {
  getStorageSync: jest.fn(),
  setStorageSync: jest.fn(),
  removeStorageSync: jest.fn()
};

describe('Storage Utils', () => {
  beforeEach(() => {
    // 清除所有 mock 调用记录
    global.wx.getStorageSync.mockClear();
    global.wx.setStorageSync.mockClear();
    global.wx.removeStorageSync.mockClear();
  });

  describe('saveHistory', () => {
    it('应该保存历史记录', () => {
      const record = {
        batchCode: '51450742F1',
        status: 'safe',
        productName: 'OCR识别',
        queryTime: Date.now()
      };

      global.wx.getStorageSync.mockReturnValue([]);

      const result = saveHistory(record);

      expect(result).toBe(true);
      expect(global.wx.getStorageSync).toHaveBeenCalledWith('queryHistory');
      expect(global.wx.setStorageSync).toHaveBeenCalled();
    });

    it('应该限制历史记录数量为100条', () => {
      const record = { batchCode: 'ABC123', status: 'safe' };

      // Mock 100 条历史记录
      const existingHistory = Array.from({ length: 100 }, (_, i) => ({
        batchCode: `OLD${i}`,
        status: 'safe'
      }));

      global.wx.getStorageSync.mockReturnValue(existingHistory);

      saveHistory(record);

      // 检查 setStorageSync 是否被调用
      const setCalls = global.wx.setStorageSync.mock.calls;
      const savedHistory = setCalls[0][1]; // 第二个参数是保存的数据

      expect(savedHistory.length).toBe(100);
      expect(savedHistory[0].batchCode).toBe('ABC123');
    });

    it('应该处理存储错误', () => {
      const record = { batchCode: 'ABC123', status: 'safe' };

      // Mock 存储失败
      global.wx.setStorageSync.mockImplementation(() => {
        throw new Error('Storage full');
      });

      const result = saveHistory(record);

      expect(result).toBe(false);
    });
  });

  describe('getHistory', () => {
    it('应该获取所有历史记录', () => {
      const history = [
        { batchCode: 'ABC123', status: 'safe' },
        { batchCode: 'DEF456', status: 'danger' }
      ];

      global.wx.getStorageSync.mockReturnValue(history);

      const result = getHistory('all');

      expect(result).toEqual(history);
      expect(result.length).toBe(2);
    });

    it('应该过滤召回中的记录', () => {
      const history = [
        { batchCode: 'ABC123', status: 'safe' },
        { batchCode: 'DEF456', status: 'recalled' },
        { batchCode: 'GHI789', status: 'recalled' }
      ];

      global.wx.getStorageSync.mockReturnValue(history);

      const result = getHistory('recalled');

      expect(result.length).toBe(2);
      expect(result.every(item => item.status === 'recalled')).toBe(true);
    });

    it('应该返回空数组如果没有历史记录', () => {
      global.wx.getStorageSync.mockReturnValue([]);

      const result = getHistory('all');

      expect(result).toEqual([]);
    });

    it('应该处理存储错误', () => {
      // Mock 存储失败
      global.wx.getStorageSync.mockImplementation(() => {
        throw new Error('Storage error');
      });

      const result = getHistory('all');

      expect(result).toEqual([]);
    });
  });

  describe('clearHistory', () => {
    it('应该清空历史记录', () => {
      const result = clearHistory();

      expect(result).toBe(true);
      expect(global.wx.removeStorageSync).toHaveBeenCalledWith('queryHistory');
    });

    it('应该处理清空失败', () => {
      // Mock 清空失败
      global.wx.removeStorageSync.mockImplementation(() => {
        throw new Error('Clear failed');
      });

      const result = clearHistory();

      expect(result).toBe(false);
    });
  });
});
```

---

### 3. 测试 index.js（页面逻辑）

创建 `__tests__/pages/index.test.js`：

```javascript
const createPage = require('@wechat-miniprogram/miniprogram-simulate').createPage;
const path = require('path');

const pagePath = path.resolve(__dirname, '../../miniprogram/pages/index/index');

describe('Index Page', () => {
  let page;

  beforeEach(() => {
    // Mock wx API
    global.wx = {
      getStorageInfoSync: jest.fn(() => ({ currentSize: 1024 })),
      getStorageSync: jest.fn(() => []),
      setStorageSync: jest.fn(),
      navigateTo: jest.fn()
    };

    // 创建页面实例
    page = createPage(pagePath);
  });

  afterEach(() => {
    // 清理页面实例
    page.dispose();
  });

  describe('loadHistory', () => {
    it('应该加载历史记录', () => {
      const history = [
        {
          batchCode: 'ABC123',
          status: 'safe',
          productName: 'OCR识别',
          queryTime: Date.now() - 300000 // 5分钟前
        }
      ];

      global.wx.getStorageSync.mockReturnValue(history);

      page.callMethod('loadHistory');

      const data = page.data;
      expect(data.recentHistory).toBeDefined();
      expect(data.recentHistory.length).toBeGreaterThan(0);
    });

    it('应该处理加载失败', () => {
      // Mock 加载失败
      global.wx.getStorageSync.mockImplementation(() => {
        throw new Error('Load failed');
      });

      // 不应该抛出错误
      expect(() => {
        page.callMethod('loadHistory');
      }).not.toThrow();
    });
  });

  describe('formatTimeAgo', () => {
    it('应该显示"刚刚"', () => {
      const now = Date.now();
      const result = page.callMethod('formatTimeAgo', now - 30000); // 30秒前
      expect(result).toBe('刚刚');
    });

    it('应该显示"X分钟前"', () => {
      const now = Date.now();
      const result = page.callMethod('formatTimeAgo', now - 180000); // 3分钟前
      expect(result).toBe('3分钟前');
    });

    it('应该显示"X小时前"', () => {
      const now = Date.now();
      const result = page.callMethod('formatTimeAgo', now - 7200000); // 2小时前
      expect(result).toBe('2小时前');
    });

    it('应该显示"X天前"', () => {
      const now = Date.now();
      const result = page.callMethod('formatTimeAgo', now - 172800000); // 2天前
      expect(result).toBe('2天前');
    });
  });

  describe('getStatusClass', () => {
    it('应该返回正确的状态类名', () => {
      expect(page.callMethod('getStatusClass', 'safe')).toBe('safe');
      expect(page.callMethod('getStatusClass', 'danger')).toBe('danger');
      expect(page.callMethod('getStatusClass', 'unknown')).toBe('unknown');
      expect(page.callMethod('getStatusClass', 'querying')).toBe('unknown');
      expect(page.callMethod('getStatusClass', 'invalid')).toBe('unknown');
    });
  });

  describe('getStatusText', () => {
    it('应该返回正确的状态文本', () => {
      expect(page.callMethod('getStatusText', 'safe')).toBe('正常');
      expect(page.callMethod('getStatusText', 'danger')).toBe('已召回');
      expect(page.callMethod('getStatusText', 'unknown')).toBe('查询中');
      expect(page.callMethod('getStatusText', 'querying')).toBe('查询中');
      expect(page.callMethod('getStatusText', 'invalid')).toBe('未知');
    });
  });

  describe('onInput', () => {
    it('应该更新输入值', () => {
      const event = { detail: { value: 'ABC123' } };
      page.callMethod('onInput', event);

      expect(page.data.manualInput).toBe('ABC123');
    });
  });

  describe('clearInput', () => {
    it('应该清空输入值', () => {
      page.setData({ manualInput: 'ABC123' });
      page.callMethod('clearInput');

      expect(page.data.manualInput).toBe('');
    });
  });

  describe('goToHistory', () => {
    it('应该跳转到历史页面', () => {
      page.callMethod('goToHistory');

      expect(global.wx.navigateTo).toHaveBeenCalledWith({
        url: '/pages/history/history'
      });
    });
  });
});
```

---

## 🏃 运行测试

### 运行所有测试

```bash
npm test
```

### 运行特定测试文件

```bash
npm test api_client.test.js
```

### 运行测试并查看覆盖率

```bash
npm test -- --coverage
```

### 监听模式（自动重新运行）

```bash
npm test -- --watch
```

---

## 📊 测试覆盖率目标

| 模块 | 目标覆盖率 | 当前覆盖率 | 状态 |
|------|----------|----------|------|
| utils/api_client.js | 80% | 0% | ❌ |
| utils/storage.js | 90% | 0% | ❌ |
| pages/index/index.js | 70% | 0% | ❌ |
| pages/history/history.js | 70% | 0% | ❌ |
| **总体** | **80%** | **0%** | ❌ |

---

## ✅ 测试检查清单

### 单元测试
- [ ] api_client.js - API 客户端
- [ ] storage.js - 存储工具
- [ ] date.js - 日期工具
- [ ] api.js - API 工具

### 页面测试
- [ ] index.js - 首页
- [ ] history.js - 历史页
- [ ] result.js - 结果页
- [ ] camera.js - 相机页

### 集成测试
- [ ] OCR 识别流程
- [ ] 批次号查询流程
- [ ] 历史记录保存和加载

---

## 🎯 测试最佳实践

### 1. 测试命名规范

```javascript
// ✅ 好的命名
it('应该成功查询批次号', () => {});
it('应该拒绝空批次号', () => {});
it('应该标准化批次号', () => {});

// ❌ 不好的命名
it('test 1', () => {});
it('query test', () => {});
```

### 2. 测试 AAA 模式

```javascript
// ✅ AAA 模式（Arrange-Act-Assert）
it('应该成功查询批次号', () => {
  // Arrange（准备）
  const batchCode = '51450742F1';

  // Act（执行）
  const result = await client.queryBatch(batchCode);

  // Assert（断言）
  expect(result.success).toBe(true);
});
```

### 3. 测试覆盖率

```javascript
// ✅ 测试所有分支
it('应该处理成功情况', () => {});
it('应该处理失败情况', () => {});
it('应该处理边界情况', () => {});

// ❌ 只测试成功情况
it('应该成功', () => {});
```

### 4. Mock 外部依赖

```javascript
// ✅ Mock 微信 API
global.wx = {
  request: jest.fn(),
  getStorageSync: jest.fn(),
  setStorageSync: jest.fn()
};

// ❌ 不 Mock，直接测试（会导致失败）
```

---

## 📚 参考资源

### Jest 文档
- [Jest 官方文档](https://jestjs.io/)
- [Jest API 参考](https://jestjs.io/docs/api)
- [Jest 匹配器](https://jestjs.io/docs/expect)

### 微信小程序测试
- [miniprogram-simulate 文档](https://developers.weixin.qq.com/miniprogram/dev/framework/custom-component/traditional.html)
- [微信小程序单元测试指南](https://developers.weixin.qq.com/miniprogram/dev/framework/custom-component/traditional.html)

### 测试最佳实践
- [测试覆盖率](https://en.wikipedia.org/wiki/Code_coverage)
- [TDD 开发模式](https://en.wikipedia.org/wiki/Test-driven_development)

---

**创建时间：** 2026-02-03
**版本：** v2.1.1
**维护者：** AI Assistant
