// result.js - 查询结果页面逻辑

// 导入配置和工具
const config = require('../../config/project.config.js');
const { timeAgo, formatDate, formatShortDate, daysRemaining } = require('../../utils/date.js');
const { saveHistory } = require('../../utils/storage.js');

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
    bestBeforeText: '',
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
   * 查询批次号
   */
  async queryBatch(batchCode) {
    try {
      // 模拟数据（实际应该从飞书查询）
      const mockData = this.getMockData(batchCode);

      // 显示结果
      this.showResult(mockData);

    } catch (error) {
      console.error('查询失败:', error);
      this.setData({
        loading: false,
        status: 'error'
      });

      wx.showToast({
        title: '查询失败，请重试',
        icon: 'none'
      });
    }
  },

  /**
   * 获取模拟数据（实际应该调用飞书API）
   */
  getMockData(batchCode) {
    // 批次号匹配数据库
    const database = {
      // 雀巢召回批次（12个产品，多个批次）
      '51450742F1': {
        brand: '雀巢 Nestlé',
        brand_en: 'Nestlé',
        product_name: 'SMA Advanced First Infant Milk',
        pack_size: '800g',
        best_before: 1800556800000, // 2027年5月
        region: 'UK',
        recall_reason: 'Cereulide毒素',
        risk_level: 'high',
        source_url: 'https://www.food.gov.uk/news-alerts/alert/fsa-prin-02-2026-update-1',
        source_type: '政府平台',
        status: 'recalled'
      },
      '52319722BA': {
        brand: '雀巢 Nestlé',
        brand_en: 'Nestlé',
        product_name: 'SMA Advanced First Infant Milk',
        pack_size: '800g',
        best_before: 1800556800000, // 2027年5月
        region: 'UK',
        recall_reason: 'Cereulide毒素',
        risk_level: 'high',
        source_url: 'https://www.food.gov.uk/news-alerts/alert/fsa-prin-02-2026-update-1',
        source_type: '政府平台',
        status: 'recalled'
      },
      '51240742F2': {
        brand: '雀巢 Nestlé',
        brand_en: 'Nestlé',
        product_name: 'SMA Advanced Follow-On Milk',
        pack_size: '800g',
        best_before: 1800556800000, // 2027年5月
        region: 'UK',
        recall_reason: 'Cereulide毒素',
        risk_level: 'high',
        source_url: 'https://www.food.gov.uk/news-alerts/alert/fsa-prin-02-2026-update-1',
        source_type: '政府平台',
        status: 'recalled'
      }
    };

    // 模糊匹配
    let matchedCode = null;
    for (const code in Object.keys(database)) {
      if (code === batchCode) {
        matchedCode = code;
        break;
      }
      // 部分匹配（前4位或后4位）
      if (code.includes(batchCode.slice(0, 4)) || code.includes(batchCode.slice(-4))) {
        matchedCode = code;
        break;
      }
    }

    if (matchedCode) {
      return database[matchedCode];
    } else {
      // 未找到
      return {
        brand: '',
        product_name: '',
        pack_size: '',
        best_before: null,
        region: '',
        recall_reason: '未找到相关信息',
        risk_level: 'low',
        status: 'not_found'
      };
    }
  },

  /**
   * 显示查询结果
   */
  showResult(data) {
    // 格式化数据
    const bestBeforeText = data.best_before ? formatDate(data.best_before) : '';
    const riskLevelText = this.getRiskLevelText(data.risk_level);
    const statusInfo = this.getStatusInfo(data.status);

    this.setData({
      loading: false,
      brand: data.brand,
      productName: data.product_name,
      batchCode: this.data.batchCode,
      packSize: data.pack_size,
      bestBefore: data.best_before,
      bestBeforeText: bestBeforeText,
      region: data.region,
      recallReason: data.recall_reason,
      recallReasonDetail: data.recall_reason,
      risk_level: data.risk_level,
      riskLevelText: riskLevelText.text,
      riskLevelClass: riskLevelText.class,
      sourceUrl: data.source_url,
      sourceType: data.source_type,
      status: data.status,
      statusTitle: statusInfo.title,
      statusIcon: statusInfo.icon,
      statusClass: statusInfo.class,
      notFound: data.status === 'not_found'
    });

    // 保存到历史记录
    this.saveToHistory(data);
  },

  /**
   * 获取风险等级文本和样式
   */
  getRiskLevelText(level) {
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
      recalled: {
        title: '召回中',
        icon: '⚠️',
        class: 'status-recalled'
      },
      not_recalled: {
        title: '未召回',
        icon: '✅',
        class: 'status-success'
      },
      expired: {
        title: '已结束召回',
        icon: '✅',
        class: 'status-success'
      },
      not_found: {
        title: '未在召回名单',
        icon: '✅',
        class: 'status-success'
      },
      querying: {
        title: '查询中',
        icon: '⏳',
        class: 'status-querying'
      }
    };

    return statusMap[status] || statusMap.not_found;
  },

  /**
   * 保存到历史记录
   */
  saveToHistory(data) {
    try {
      const historyItem = {
        batchCode: this.data.batchCode,
        status: data.status,
        productName: data.product_name,
        brand: data.brand,
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
    if (this.data.sourceUrl) {
      wx.setClipboardData({
        data: this.data.sourceUrl,
        success: () => {
          wx.showToast({
            title: '链接已复制',
            icon: 'success'
          });
        }
      });

      // 尝试在浏览器中打开（如果支持）
      // wx.openDocument({
      //   fileType: 'url',
      //   filePath: this.data.sourceUrl
      // });
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
      productName: this.data.product_name,
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
