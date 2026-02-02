// result.js - 查询结果页面逻辑（使用真实API）

// 导入配置和工具
const config = require('../../config/project.config.js');
const apiClient = require('../../utils/api_client.js');
const { saveHistory, timeAgo } = require('../../utils/storage.js');
const { formatDate, formatShortDate, daysRemaining } = require('../../utils/date.js');

Page({
  data: {
    // 页面状态
    loading: true,
    batchCode: '',
    status: 'not_found',  // querying, recalled, not_recalled, not_found, expired

    // 产品详情
    brand: '',
    productName: '',
    batchCode: '',
    packSize: '',
    bestBefore: null,
    region: '',
    recallReason: '',
    recallReasonDetail: '',

    // 风险等级
    riskLevel: '',
    riskLevelText: '',
    riskLevelClass: '',

    // 来源
    sourceUrl: '',
    sourceType: '',

    // 状态相关
    statusTitle: '',
    statusIcon: '',
    statusClass: '',

    // 未找到时
    notFound: false,
    notFoundText: ''
  },

  onLoad(options) {
    // 获取批次号
    const batchCode = options.batchCode || '';

    if (!batchCode) {
      wx.showToast({
          title: '批次号不能为空',
          icon: 'none'
        });
      wx.navigateBack();
      return;
    }

    console.log('查询批次号:', batchCode);

    this.setData({
      batchCode: batchCode,
      loading: true
    });

    // 开始查询
    this.queryBatch(batchCode);
  },

  /**
   * 查询批次号（使用真实API）
   */
  async queryBatch(batchCode) {
    try {
      // 标准化批次号
      const normalizedBatch = batchCode.trim().toUpperCase();

      // 调用 API 查询
      const result = await apiClient.queryBatch(normalizedBatch);

      if (!result.success) {
        throw new Error(result.message || '查询失败');
      }

      // 显示结果
      if (result.matched && result.records && result.records.length > 0) {
        // 找到召回记录
        const record = result.records[0];
        this.showResult(record);
      } else {
        // 未找到召回记录
        this.showNotFound();
      }

    } catch (error) {
      console.error('查询失败:', error);
      wx.showToast({
        title: error.message || '查询失败',
        icon: 'none'
      });
      this.showNotFound();
    }
  },

  /**
   * 显示查询结果
   */
  showResult(record) {
    const fields = record.fields || {};

    // 格式化日期
    const bestBefore = fields.best_before ? formatDate(fields.best_before) : '';
    const bestBeforeShort = fields.best_before ? formatShortDate(fields.best_before) : '';

    // 获取风险等级信息
    const riskLevel = fields.risk_level || 'low';
    const riskInfo = this.getRiskLevelInfo(riskLevel);

    // 获取状态信息
    const statusInfo = this.getStatusInfo(fields.status);

    this.setData({
      loading: false,
      brand: fields.brand || '',
      productName: fields.product_name || '',
      batchCode: this.data.batchCode,
      packSize: fields.pack_size || '',
      bestBefore: fields.best_before,
      bestBeforeText: bestBefore,
      region: fields.region || '',
      recallReason: fields.recall_reason || '',
      recallReasonDetail: fields.recall_reason || '',
      risk_level: riskLevel,
      riskLevelText: riskInfo.text,
      riskLevelClass: riskInfo.class,
      sourceUrl: fields.source_url ? fields.source_url.link : '',
      sourceType: fields.source_type || '',
      status: fields.status || 'not_found',
      statusTitle: statusInfo.title,
      statusIcon: statusInfo.icon,
      statusClass: statusInfo.class,
      notFound: false
    });

    // 保存到历史记录
    this.saveToHistory(record);
  },

  /**
   * 显示未找到状态
   */
  showNotFound() {
    const notFoundTexts = [
      '未找到相关信息',
      '该批次号不在召回名单中',
      '您的产品是安全的'
    ];

    const randomText = notFoundTexts[Math.floor(Math.random() * notFoundTexts.length)];

    this.setData({
      loading: false,
      notFound: true,
      notFoundText: randomText,
      status: 'not_found',
      statusTitle: '未在召回名单',
      statusIcon: '✅',
      statusClass: 'status-success'
    });
  },

  /**
   * 获取风险等级文本和样式
   */
  getRiskLevelInfo(level) {
    const levels = {
      high: { text: '高', class: 'risk-high' },
      medium: { text: '中', class: 'risk-medium' },
      low: { text: '低', class: 'risk-low' }
    };

    return levels[level] || levels.low;
  },

  /**
   * 获取状态信息
   */
  getStatusInfo(status) {
    const statusMap = {
      'querying': {
        title: '查询中',
        icon: '⏳',
        class: 'status-querying'
      },
      'recalled': {
        title: '召回中',
        icon: '⚠️',
        class: 'status-recalled'
      },
      'not_recalled': {
        title: '未召回',
        icon: '✅',
        class: 'status-success'
      },
      'expired': {
        title: '已结束召回',
        icon: '✅',
        class: 'status-success'
      },
      'not_found': {
        title: '未在召回名单',
        icon: '✅',
        class: 'status-success'
      }
    };

    return statusMap[status] || statusMap.not_found;
  },

  /**
   * 保存到历史记录
   */
  saveToHistory(record) {
    try {
      const fields = record.fields || {};
      const batchCode = fields.batch_codes || '';

      const historyItem = {
        batchCode: batchCode,
        status: fields.status || 'not_found',
        productName: fields.product_name || '',
        brand: fields.brand || '',
        queryTime: new Date().getTime()
      };

      saveHistory(historyItem);
      console.log('已保存历史记录:', historyItem);

    } catch (error) {
      console.error('保存历史记录失败:', error);
    }
  },

  /**
   * 返回首页
   */
  goBack() {
    wx.navigateBack();
  },

  /**
   * 跳转到相机页面
   */
  goToCamera() {
    wx.navigateTo({
      url: '/pages/camera/camera'
    });
  },

  /**
   * 打开官方链接
   */
  openOfficialLink() {
    const url = this.data.sourceUrl;

    if (url) {
      // 复制链接到剪贴板
      wx.setClipboardData({
        data: url,
        success: () => {
          wx.showToast({
            title: '链接已复制',
            icon: 'success',
            duration: 2000
          });
        }
      });

      // 尝试打开链接
      wx.showModal({
        title: '官方链接',
        content: `是否打开官方召回公告？\n${url}`,
        confirmText: '打开',
        cancelText: '取消',
        success(modalRes) {
          if (modalRes.confirm) {
            wx.openDocument({
              fileType: 'url',
              filePath: url
            });
          }
        }
      });

    } else {
      wx.showToast({
        title: '暂无官方链接',
        icon: 'none'
      });
    }
  },

  /**
   * 保存到历史
   */
  saveToHistory() {
    const data = {
      batchCode: this.data.batchCode,
      status: this.data.status,
      productName: this.data.productName,
      brand: this.data.brand,
      queryTime: new Date().getTime()
    };

    saveHistory(data);

    wx.showToast({
      title: '已保存记录',
      icon: 'success'
    });
  },

  /**
   * 重新查询
   */
  retry() {
    this.queryBatch(this.data.batchCode);
  }
});
