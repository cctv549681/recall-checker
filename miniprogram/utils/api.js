// utils/api.js
// API 请求工具

// 导入配置
const config = require('../config/project.config.js');

/**
 * 飞书 API 客户端
 */
class FeishuClient {
  constructor() {
    this.baseURL = config.feishu.apiUrl;
    this.appToken = config.feishu.appToken;
    this.tableId = config.feishu.tableId;
  }

  /**
   * 获取 tenant_access_token
   */
  async getToken() {
    const url = `${this.baseURL}/auth/v3/tenant_access_token/internal`;
    
    try {
      const response = await wx.request({
        url,
        method: 'POST',
        data: {
          app_id: config.feishu.appId,
          app_secret: config.feishu.appSecret
        }
      });

      const result = response.data;

      if (result.code !== 0) {
        throw new Error(`获取飞书token失败: ${result.msg}`);
      }

      return result.tenant_access_token;
    } catch (error) {
      console.error('获取飞书token失败:', error);
      throw error;
    }
  }

  /**
   * 查询批次号是否在召回名单中
   * @param {string} batchCode - 批次号
   * @returns {Promise<Object>} 查询结果
   */
  async queryBatch(batchCode) {
    if (!batchCode) {
      throw new Error('批次号不能为空');
    }

    // 标准化批次号（去除空格、统一大小写）
    const normalizedBatch = batchCode.trim().toUpperCase();

    try {
      // 获取飞书 token
      const token = await this.getToken();

      // 查询记录
      const url = `${this.baseURL}/bitable/v1/apps/${this.appToken}/tables/${this.tableId}/records/search`;
      
      const response = await wx.request({
        url,
        method: 'POST',
        header: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json; charset=utf-8'
        },
        data: {
          filter: {
            // 查询所有记录（实际应该在前端过滤）
            conditions: []
          },
          // 一次获取更多数据，支持模糊匹配
          page_size: 100
        }
      });

      const result = response.data;

      if (result.code !== 0) {
        throw new Error(`查询失败: ${result.msg}`);
      }

      const records = result.data.items || [];

      // 匹配批次号
      const matched = this.matchBatch(normalizedBatch, records);

      return {
        success: true,
        matched: matched.length > 0,
        records: matched,
        total: records.length
      };

    } catch (error) {
      console.error('查询批次号失败:', error);
      throw error;
    }
  }

  /**
   * 批次号匹配逻辑
   * @param {string} batch - 查询的批次号
   * @param {Array} records - 飞书记录
   * @returns {Array} 匹配的记录
   */
  matchBatch(batch, records) {
    const matched = [];

    for (const record of records) {
      const fields = record.fields || {};
      const batchCodesField = fields.batch_codes || '';
      
      // 分割批次号（可能多个，逗号、空格分隔）
      const codes = batchCodesField.split(/[,，\s]+/).filter(code => code.trim());

      for (const code of codes) {
        // 标准化并比较
        const normalizedCode = code.trim().toUpperCase();
        
        // 精确匹配
        if (normalizedCode === batch) {
          matched.push(record);
          break; // 找到一个匹配就跳出
        }

        // 模糊匹配（批次号的一部分）
        if (config.batch.fuzzy.enabled && batch.length >= config.batch.fuzzy.partialMinLength) {
          if (code.includes(batch) || batch.includes(code)) {
            matched.push(record);
            break;
          }
        }
      }
    }

    return matched;
  }

  /**
   * 保存查询历史
   * @param {Object} record - 查询记录
   */
  async saveHistory(record) {
    try {
      const history = wx.getStorageSync('queryHistory') || [];

      // 添加到开头（最新的在前）
      history.unshift({
        ...record,
        queryTime: new Date().getTime(),
        id: Date.now().toString()
      });

      // 只保留最近100条
      const trimmed = history.slice(0, 100);

      wx.setStorageSync('queryHistory', trimmed);

      return true;
    } catch (error) {
      console.error('保存历史记录失败:', error);
      return false;
    }
  }

  /**
   * 获取查询历史
   * @param {string} filter - 过滤条件（all, recalled, not_recalled）
   * @returns {Promise<Array>} 历史记录
   */
  async getHistory(filter = 'all') {
    try {
      const history = wx.getStorageSync('queryHistory') || [];

      if (filter === 'all') {
        return history;
      }

      // 过滤
      return history.filter(item => {
        if (filter === 'recalled') {
          return item.status === 'recalled';
        } else if (filter === 'not_recalled') {
          return item.status === 'not_recalled';
        }
        return true;
      });

    } catch (error) {
      console.error('获取历史记录失败:', error);
      return [];
    }
  }

  /**
   * 清空历史记录
   */
  clearHistory() {
    try {
      wx.removeStorageSync('queryHistory');
      wx.showToast({
        title: '已清空',
        icon: 'success',
        duration: 2000
      });
      return true;
    } catch (error) {
      console.error('清空历史记录失败:', error);
      return false;
    }
  }
}

module.exports = FeishuClient;
