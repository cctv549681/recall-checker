/**
 * storage.test.js - 存储工具单元测试（最终修复）
 *
 * @description 测试 wx.storage 的封装函数
 * @version 2.1.1
 */

const { saveHistory, getHistory, clearHistory } = require('../../utils/storage.js');

// Mock wx API
global.wx = {
  getStorageSync: jest.fn(),
  setStorageSync: jest.fn(),
  removeStorageSync: jest.fn(),
  showToast: jest.fn()
};

describe('Storage Utils', () => {
  beforeEach(() => {
    // 清除所有 mock 调用记录
    jest.clearAllMocks();
  });

  afterEach(() => {
    // 重置 mock
    global.wx.getStorageSync.mockReset();
    global.wx.setStorageSync.mockReset();
    global.wx.removeStorageSync.mockReset();
    global.wx.showToast.mockReset();
  });

  describe('saveHistory', () => {
    it('应该保存历史记录', () => {
      const record = {
        batchCode: 'ABC123',
        status: 'safe',
        productName: 'OCR识别',
        queryTime: Date.now()
      };

      // Mock 空历史记录
      global.wx.getStorageSync.mockReturnValue([]);

      const result = saveHistory(record);

      // 验证结果
      expect(result).toBe(true);
      expect(global.wx.getStorageSync).toHaveBeenCalledWith('queryHistory');
      expect(global.wx.setStorageSync).toHaveBeenCalled();
    });

    it('应该限制历史记录数量为100条', () => {
      const record = { batchCode: 'ABC123', status: 'safe', productName: '测试' };

      // Mock 100 条历史记录
      const existingHistory = Array.from({ length: 100 }, (_, i) => ({
        batchCode: `OLD${i}`,
        status: 'safe',
        productName: `产品${i}`
      }));

      global.wx.getStorageSync.mockReturnValue(existingHistory);

      saveHistory(record);

      // 验证 setStorageSync 被调用
      expect(global.wx.setStorageSync).toHaveBeenCalled();

      // 获取保存的数据
      const savedData = global.wx.setStorageSync.mock.calls[0][1];
      expect(savedData).toBeDefined();
      expect(savedData.length).toBeLessThanOrEqual(100);
    });

    it('应该在历史记录前面添加新记录', () => {
      const record = { batchCode: 'NEW123', status: 'danger', productName: '新记录' };

      const existingHistory = [
        { batchCode: 'OLD001', status: 'safe', productName: '旧记录1' },
        { batchCode: 'OLD002', status: 'safe', productName: '旧记录2' }
      ];

      global.wx.getStorageSync.mockReturnValue(existingHistory);

      saveHistory(record);

      const savedData = global.wx.setStorageSync.mock.calls[0][1];
      expect(savedData[0].batchCode).toBe('NEW123');
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

    it('应该添加 id 字段到历史记录', () => {
      const record = {
        batchCode: 'ABC123',
        status: 'safe',
        productName: '测试'
      };

      global.wx.getStorageSync.mockReturnValue([]);

      saveHistory(record);

      const savedData = global.wx.setStorageSync.mock.calls[0][1];
      expect(savedData[0].id).toBeDefined();
      expect(typeof savedData[0].id).toBe('string');
    });
  });

  describe('getHistory', () => {
    it('应该获取所有历史记录', () => {
      const history = [
        { batchCode: 'ABC123', status: 'safe', productName: '产品A' },
        { batchCode: 'DEF456', status: 'danger', productName: '产品B' }
      ];

      global.wx.getStorageSync.mockReturnValue(history);

      const result = getHistory('all');

      expect(result).toEqual(history);
      expect(result.length).toBe(2);
    });

    it('应该过滤召回中的记录', () => {
      const history = [
        { batchCode: 'ABC123', status: 'safe', productName: '产品A' },
        { batchCode: 'DEF456', status: 'recalled', productName: '产品B' },
        { batchCode: 'GHI789', status: 'recalled', productName: '产品C' }
      ];

      global.wx.getStorageSync.mockReturnValue(history);

      const result = getHistory('recalled');

      expect(result.length).toBe(2);
      expect(result.every(item => item.status === 'recalled')).toBe(true);
    });

    it('应该过滤未召回的记录', () => {
      const history = [
        { batchCode: 'ABC123', status: 'safe', productName: '产品A' },
        { batchCode: 'DEF456', status: 'not_recalled', productName: '产品B' },
        { batchCode: 'GHI789', status: 'recalled', productName: '产品C' }
      ];

      global.wx.getStorageSync.mockReturnValue(history);

      const result = getHistory('not_recalled');

      // ✅ 修复：应该只返回1条（not_recalled）
      expect(result.length).toBe(1);
      expect(result.every(item => item.status === 'not_recalled')).toBe(true);
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

    it('应该返回原始数据当filter为all时', () => {
      const history = [
        { batchCode: 'ABC123', status: 'safe' },
        { batchCode: 'DEF456', status: 'danger' }
      ];

      global.wx.getStorageSync.mockReturnValue(history);

      const result = getHistory('all');

      expect(result).toBe(history);
    });
  });

  describe('clearHistory', () => {
    it('应该清空历史记录', () => {
      const result = clearHistory();

      expect(result).toBe(true);
      expect(global.wx.removeStorageSync).toHaveBeenCalledWith('queryHistory');
    });

    it('应该显示成功提示', () => {
      const mockToast = jest.fn();
      global.wx.showToast = mockToast;

      clearHistory();

      expect(mockToast).toHaveBeenCalledWith({
        title: '已清空',
        icon: 'success',
        duration: 2000
      });
    });

    it('应该处理清空失败', () => {
      // ✅ 最终修复：Mock 清空失败
      global.wx.removeStorageSync.mockImplementation(() => {
        throw new Error('Clear failed');
      });

      const result = clearHistory();

      expect(result).toBe(false); // ✅ clearHistory 在失败时返回 false
    });

    it('应该在失败时不显示成功提示', () => {
      // Mock 清空失败
      global.wx.removeStorageSync.mockImplementation(() => {
        throw new Error('Clear failed');
      });

      const mockToast = jest.fn();
      global.wx.showToast = mockToast;

      clearHistory();

      // 不应该调用 showToast
      expect(mockToast).not.toHaveBeenCalled();
    });
  });
});
