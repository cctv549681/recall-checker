/**
 * api_client.test.js - API 客户端单元测试
 *
 * @description 测试 RecallApiClient 类的所有方法
 * @version 2.1.1
 */

const RecallApiClient = require('../../utils/api_client.js');

// Mock wx.request
global.wx = {
  request: jest.fn()
};

describe('RecallApiClient', () => {
  let client;

  beforeEach(() => {
    // 每个测试前创建新实例
    client = new RecallApiClient();

    // 清除 mock 调用记录
    global.wx.request.mockClear();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('constructor', () => {
    it('应该正确初始化 API 客户端', () => {
      expect(client.localApiUrl).toBe('http://14.103.26.111:5001/api');
      expect(client.apiType).toBe('local');
      expect(client.feishuApiUrl).toBeDefined();
    });

    it('应该设置默认 API 类型为 local', () => {
      expect(client.apiType).toBe('local');
    });
  });

  describe('queryBatch', () => {
    it('应该成功查询批次号', async () => {
      // Mock 成功响应
      global.wx.request.mockImplementation((options) => {
        options.success({
          data: {
            success: true,
            status: 'recalled',
            data: [],
            message: '查询成功'
          }
        });
      });

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

    it('应该标准化批次号（去除空格）', async () => {
      global.wx.request.mockImplementation((options) => {
        options.success({
          data: { success: true, status: 'not_recalled', data: [] }
        });
      });

      await client.queryBatch('  abc123  ');

      const requestData = global.wx.request.mock.calls[0][0];
      expect(requestData.data.batch_code).toBe('ABC123');
    });

    it('应该标准化批次号（转大写）', async () => {
      global.wx.request.mockImplementation((options) => {
        options.success({
          data: { success: true, status: 'not_recalled', data: [] }
        });
      });

      await client.queryBatch('abc123');

      const requestData = global.wx.request.mock.calls[0][0];
      expect(requestData.data.batch_code).toBe('ABC123');
    });

    it('应该处理 API 失败', async () => {
      global.wx.request.mockImplementation((options) => {
        options.fail(new Error('Network error'));
      });

      await expect(client.queryBatch('ABC123')).rejects.toThrow('Network error');
    });

    it('应该正确匹配召回状态', async () => {
      global.wx.request.mockImplementation((options) => {
        options.success({
          data: {
            success: true,
            status: 'recalled',
            data: [{ batch_codes: 'ABC123' }]
          }
        });
      });

      const result = await client.queryBatch('ABC123');

      expect(result.matched).toBe(true);
      expect(result.total).toBe(1);
    });

    it('应该正确匹配未召回状态', async () => {
      global.wx.request.mockImplementation((options) => {
        options.success({
          data: {
            success: true,
            status: 'not_found',
            data: []
          }
        });
      });

      const result = await client.queryBatch('ABC123');

      expect(result.matched).toBe(false);
      expect(result.total).toBe(0);
    });
  });

  describe('queryLocal', () => {
    it('应该发送正确的请求到本地 API', async () => {
      global.wx.request.mockImplementation((options) => {
        expect(options.url).toBe('http://14.103.26.111:5001/api/query');
        expect(options.method).toBe('POST');
        expect(options.header['Content-Type']).toBe('application/json');
        options.success({
          data: { success: true, status: 'recalled', data: [] }
        });
      });

      await client.queryLocal('ABC123');
    });

    it('应该发送正确的批次号数据', async () => {
      global.wx.request.mockImplementation((options) => {
        expect(options.data.batch_code).toBe('ABC123');
        options.success({
          data: { success: true, status: 'recalled', data: [] }
        });
      });

      await client.queryLocal('ABC123');
    });

    it('应该处理网络错误', async () => {
      global.wx.request.mockImplementation((options) => {
        options.fail(new Error('Network timeout'));
      });

      await expect(client.queryLocal('ABC123')).rejects.toThrow('Network timeout');
    });
  });

  describe('ocrImage', () => {
    it('应该成功识别图片', async () => {
      global.wx.request.mockImplementation((options) => {
        expect(options.url).toBe('http://14.103.26.111:5001/api/ocr');
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
      expect(result.data.confidence).toBe(95);
    });

    it('应该发送正确的图片 URL', async () => {
      const imageUrl = 'https://example.com/image.jpg';

      global.wx.request.mockImplementation((options) => {
        expect(options.data.image_url).toBe(imageUrl);
        options.success({
          data: { success: true, data: {} }
        });
      });

      await client.ocrImage(imageUrl);
    });

    it('应该处理 OCR 识别失败', async () => {
      global.wx.request.mockImplementation((options) => {
        options.success({
          data: {
            success: false,
            message: 'OCR识别失败'
          }
        });
      });

      const result = await client.ocrImage('https://example.com/image.jpg');

      expect(result.success).toBe(false);
      expect(result.message).toBe('OCR识别失败');
    });

    it('应该处理网络错误', async () => {
      global.wx.request.mockImplementation((options) => {
        options.fail(new Error('Network error'));
      });

      await expect(client.ocrImage('https://example.com/image.jpg')).rejects.toThrow('Network error');
    });
  });

  describe('getStats', () => {
    it('应该成功获取统计信息', async () => {
      const mockStats = {
        success: true,
        data: {
          total_records: 100,
          by_brand: { '雀巢': 50, '雅培': 50 }
        }
      };

      global.wx.request.mockImplementation((options) => {
        expect(options.url).toBe('http://14.103.26.111:5001/api/stats');
        expect(options.method).toBe('GET');
        options.success({ data: mockStats });
      });

      const result = await client.getStats();

      expect(result).toEqual(mockStats);
    });

    it('应该使用 GET 方法', async () => {
      global.wx.request.mockImplementation((options) => {
        expect(options.method).toBe('GET');
        options.success({ data: { success: true } });
      });

      await client.getStats();
    });

    it('应该处理统计获取失败', async () => {
      global.wx.request.mockImplementation((options) => {
        options.fail(new Error('Get stats failed'));
      });

      await expect(client.getStats()).rejects.toThrow('Get stats failed');
    });
  });

  describe('healthCheck', () => {
    it('应该成功执行健康检查', async () => {
      global.wx.request.mockImplementation((options) => {
        expect(options.url).toBe('http://14.103.26.111:5001/api/health');
        options.success({
          data: {
            service: 'recall-checker-api',
            status: 'ok',
            timestamp: '2026-02-03T12:00:00.000Z'
          }
        });
      });

      const result = await client.healthCheck();

      expect(result.service).toBe('recall-checker-api');
      expect(result.status).toBe('ok');
    });

    it('应该处理健康检查失败', async () => {
      global.wx.request.mockImplementation((options) => {
        options.fail(new Error('Health check failed'));
      });

      const result = await client.healthCheck();

      expect(result.status).toBe('error');
      expect(result.message).toBeDefined();
    });

    it('总是返回结果（即使失败）', async () => {
      global.wx.request.mockImplementation((options) => {
        options.fail(new Error('Connection error'));
      });

      const result = await client.healthCheck();

      expect(result).toBeDefined();
      expect(typeof result).toBe('object');
    });
  });
});
