// utils/api_client.js
// API客户端 - 支持本地API和飞书API

const config = require('../config/project.config.js');

/**
 * 召回查询API客户端
 */
class RecallApiClient {
  constructor() {
    // 使用云服务器API
    this.localApiUrl = 'http://14.103.26.111:5001/api';

    // 飞书API（备用）
    this.feishuApiUrl = config.feishu.apiUrl || 'https://open.feishu.cn/open-apis';

    // 当前使用的API类型
    this.apiType = 'local'; // 'local' 或 'feishu'
  }

  /**
   * 查询批次号
   * @param {string} batchCode - 批次号
   * @returns {Promise<Object>} 查询结果
   */
  async queryBatch(batchCode) {
    if (!batchCode) {
      throw new Error('批次号不能为空');
    }

    // 标准化批次号
    const normalizedBatch = batchCode.trim().toUpperCase();

    console.log(`查询批次号: ${normalizedBatch}, API类型: ${this.apiType}`);

    try {
      // 优先使用本地API
      if (this.apiType === 'local') {
        const result = await this.queryLocal(normalizedBatch);

        if (result.success) {
          return result;
        }

        // 本地API失败，回退到飞书API
        console.warn('本地API失败，回退到飞书API');
        this.apiType = 'feishu';
        return await this.queryFeishu(normalizedBatch);
      } else {
        return await this.queryFeishu(normalizedBatch);
      }
    } catch (error) {
      console.error('查询失败:', error);
      throw error;
    }
  }

  /**
   * 本地API查询
   * @param {string} batchCode - 批次号
   * @returns {Promise<Object>} 查询结果
   */
  async queryLocal(batchCode) {
    const url = `${this.localApiUrl}/query`;

    return new Promise((resolve, reject) => {
      wx.request({
        url,
        method: 'POST',
        header: {
          'Content-Type': 'application/json'
        },
        data: {
          batch_code: batchCode
        },
        success: (response) => {
          const result = response.data;

          if (result.success) {
            // 转换为标准格式
            resolve({
              success: true,
              matched: result.status === 'recalled',
              records: result.data || [],
              total: result.data ? result.data.length : 0,
              message: result.message
            });
          } else {
            resolve({
              success: false,
              matched: false,
              records: [],
              total: 0,
              message: result.message || '查询失败'
            });
          }
        },
        fail: (error) => {
          console.error('本地API查询失败:', error);
          reject(error);
        }
      });
    });
  }

  /**
   * 飞书API查询
   * @param {string} batchCode - 批次号
   * @returns {Promise<Object>} 查询结果
   */
  async queryFeishu(batchCode) {
    const url = `${this.feishuApiUrl}/bitable/v1/apps/${config.feishu.appToken}/tables/${config.feishu.tableId}/records/search`;

    try {
      // 获取token
      const token = await this.getFeishuToken();

      return new Promise((resolve, reject) => {
        wx.request({
          url,
          method: 'POST',
          header: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json; charset=utf-8'
          },
          data: {
            filter: {
              conditions: [
                {
                  field_name: "batch_codes",
                  operator: "contains",
                  value: [batchCode]
                }
              ]
            }
          },
          success: (response) => {
            const result = response.data;

            if (result.code === 0) {
              const records = result.data.items || [];
              resolve({
                success: true,
                matched: records.length > 0,
                records: records,
                total: result.data.total || 0
              });
            } else {
              reject(new Error(`查询失败: ${result.msg}`));
            }
          },
          fail: (error) => {
            console.error('飞书API查询失败:', error);
            reject(error);
          }
        });
      });
    } catch (error) {
      console.error('飞书API查询失败:', error);
      throw error;
    }
  }

  /**
   * 获取飞书token
   * @returns {Promise<string>} token
   */
  async getFeishuToken() {
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

  /**
   * 获取数据统计
   * @returns {Promise<Object>} 统计信息
   */
  async getStats() {
    try {
      // 优先使用本地API
      if (this.apiType === 'local') {
        const url = `${this.localApiUrl}/stats`;

        return new Promise((resolve, reject) => {
          wx.request({
            url,
            method: 'GET',
            success: (response) => {
              resolve(response.data);
            },
            fail: (error) => {
              console.error('获取统计失败:', error);
              reject(error);
            }
          });
        });
      } else {
        // 飞书API不支持统计，返回空
        return {
          success: false,
          message: '飞书API不支持统计'
        };
      }
    } catch (error) {
      console.error('获取统计失败:', error);
      throw error;
    }
  }

  /**
   * OCR图片识别（使用图片URL）
   * @param {string} imageUrl - 图片URL
   * @returns {Promise<Object>} 识别结果
   */
  async ocrImage(imageUrl) {
    const url = `${this.localApiUrl}/ocr`;

    return new Promise((resolve, reject) => {
      wx.request({
        url,
        method: 'POST',
        header: {
          'Content-Type': 'application/json'
        },
        data: {
          image_url: imageUrl
        },
        success: (response) => {
          const result = response.data;

          if (result.success) {
            resolve({
              success: true,
              data: result.data,
              message: result.message
            });
          } else {
            resolve({
              success: false,
              message: result.message || 'OCR识别失败'
            });
          }
        },
        fail: (error) => {
          console.error('OCR识别失败:', error);
          reject(error);
        }
      });
    });
  }

  /**
   * OCR图片识别（使用Base64）
   * @param {string} imageBase64 - 图片Base64数据
   * @returns {Promise<Object>} 识别结果
   */
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

          if (result.success) {
            resolve({
              success: true,
              data: result.data,
              message: result.message
            });
          } else {
            resolve({
              success: false,
              message: result.message || 'OCR识别失败'
            });
          }
        },
        fail: (error) => {
          console.error('OCR识别失败:', error);
          reject(error);
        }
      });
    });
  }

  /**
   * API健康检查
   * @returns {Promise<Object>} 健康状态
   */
  async healthCheck() {
    return new Promise((resolve) => {
      const url = `${this.localApiUrl}/health`;

      wx.request({
        url,
        method: 'GET',
        success: (response) => {
          resolve(response.data);
        },
        fail: (error) => {
          console.error('健康检查失败:', error);
          resolve({
            status: 'error',
            message: error.message
          });
        }
      });
    });
  }
}

module.exports = RecallApiClient;
