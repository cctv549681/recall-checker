/**
 * index.utils.test.js - 首页工具函数单元测试
 *
 * @description 测试首页的纯函数（时间格式化、状态映射）
 * @version 2.1.1
 */

// 从 index.js 复制需要测试的纯函数
const formatTimeAgo = (timestamp) => {
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
};

const getStatusClass = (status) => {
  const statusMap = {
    'safe': 'safe',
    'danger': 'danger',
    'unknown': 'unknown',
    'querying': 'unknown'
  };
  return statusMap[status] || 'unknown';
};

const getStatusText = (status) => {
  const statusMap = {
    'safe': '正常',
    'danger': '已召回',
    'unknown': '查询中',
    'querying': '查询中'
  };
  return statusMap[status] || '未知';
};

describe('Index Page Utils', () => {
  describe('formatTimeAgo', () => {
    it('应该显示"刚刚"（小于1分钟）', () => {
      const now = Date.now();
      const result = formatTimeAgo(now - 30000); // 30秒前
      expect(result).toBe('刚刚');
    });

    it('应该显示"X分钟前"（小于1小时）', () => {
      const now = Date.now();
      const result = formatTimeAgo(now - 180000); // 3分钟前
      expect(result).toBe('3分钟前');
    });

    it('应该显示"X小时前"（小于1天）', () => {
      const now = Date.now();
      const result = formatTimeAgo(now - 7200000); // 2小时前
      expect(result).toBe('2小时前');
    });

    it('应该显示"X天前"（大于1天）', () => {
      const now = Date.now();
      const result = formatTimeAgo(now - 172800000); // 2天前
      expect(result).toBe('2天前');
    });

    it('应该边界情况：59秒', () => {
      const now = Date.now();
      const result = formatTimeAgo(now - 59000);
      expect(result).toBe('刚刚');
    });

    it('应该边界情况：1分钟', () => {
      const now = Date.now();
      const result = formatTimeAgo(now - 60000);
      expect(result).toBe('1分钟前');
    });

    it('应该边界情况：1小时', () => {
      const now = Date.now();
      const result = formatTimeAgo(now - 3600000);
      expect(result).toBe('1小时前');
    });

    it('应该边界情况：1天', () => {
      const now = Date.now();
      const result = formatTimeAgo(now - 86400000);
      expect(result).toBe('1天前');
    });

    it('应该处理0时间戳', () => {
      const result = formatTimeAgo(0);
      expect(result).toMatch(/前$/);
    });

    it('应该处理未来时间', () => {
      const future = Date.now() + 10000;
      const result = formatTimeAgo(future);
      expect(result).toBe('刚刚'); // 负数diff会显示"刚刚"
    });
  });

  describe('getStatusClass', () => {
    it('应该返回正确的状态类名', () => {
      expect(getStatusClass('safe')).toBe('safe');
      expect(getStatusClass('danger')).toBe('danger');
      expect(getStatusClass('unknown')).toBe('unknown');
      expect(getStatusClass('querying')).toBe('unknown');
    });

    it('应该为未知状态返回unknown', () => {
      expect(getStatusClass('invalid')).toBe('unknown');
      expect(getStatusClass('')).toBe('unknown');
      expect(getStatusClass(null)).toBe('unknown');
      expect(getStatusClass(undefined)).toBe('unknown');
    });

    it('应该处理大小写', () => {
      expect(getStatusClass('SAFE')).toBe('unknown'); // 严格匹配
      expect(getStatusClass('Safe')).toBe('unknown');
      expect(getStatusClass('safe')).toBe('safe');
    });

    it('应该处理特殊字符', () => {
      expect(getStatusClass('safe-status')).toBe('unknown');
      expect(getStatusClass('safe!')).toBe('unknown');
    });
  });

  describe('getStatusText', () => {
    it('应该返回正确的状态文本', () => {
      expect(getStatusText('safe')).toBe('正常');
      expect(getStatusText('danger')).toBe('已召回');
      expect(getStatusText('unknown')).toBe('查询中');
      expect(getStatusText('querying')).toBe('查询中');
    });

    it('应该为未知状态返回"未知"', () => {
      expect(getStatusText('invalid')).toBe('未知');
      expect(getStatusText('')).toBe('未知');
    });

    it('应该处理大小写', () => {
      expect(getStatusText('SAFE')).toBe('未知'); // 严格匹配
      expect(getStatusText('Safe')).toBe('未知');
      expect(getStatusText('safe')).toBe('正常');
    });

    it('应该处理特殊字符', () => {
      expect(getStatusText('safe-status')).toBe('未知');
      expect(getStatusText('safe!')).toBe('未知');
    });

    it('应该返回中文文本', () => {
      expect(getStatusText('safe')).toBe('正常');
      expect(getStatusText('danger')).toBe('已召回');
      expect(getStatusText('unknown')).toBe('查询中');
    });
  });
});
