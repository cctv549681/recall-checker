// index.js - 首页（添加手动输入功能）

// 导入工具
const { saveHistory, timeAgo } = require('../../utils/storage.js');

Page({
  data: {
    // 历史记录
    recentHistory: [],

    // 手动输入
    manualBatchInput: ''
  },

  onLoad(options) {
    // 页面加载时，读取历史记录
    this.loadHistory();
  },

  onShow() {
    // 页面显示时，刷新历史记录
    this.loadHistory();
  },

  /**
   * 读取历史记录
   */
  loadHistory() {
    try {
      const storage = require('../../utils/storage.js');
      const history = storage.getHistory() || [];

      // 只取最近3条
      const recent = history.slice(0, 3);

      this.setData({
        recentHistory: recent
      });
    } catch (error) {
      console.error('加载历史记录失败:', error);
    }
  },

  /**
   * 跳转到相机页面（OCR模式）
   */
  goToCamera() {
    wx.navigateTo({
      url: '/pages/camera/camera'
    });
  },

  /**
   * 跳转到输入页面（手动输入模式）
   */
  goToInput() {
    const manualBatch = this.data.manualBatchInput.trim();

    if (!manualBatch) {
      wx.showToast({
        title: '请输入批次号',
        icon: 'none'
      });
      return;
    }

    // 跳转到查询结果页面
    wx.navigateTo({
      url: `/pages/result/result?batchCode=${manualBatch}`
    });
  },

  /**
   * 手动输入处理
   */
  onManualInput(e) {
    this.setData({
      manualBatchInput: e.detail.value
    });
  },

  /**
   * 清空输入
   */
  clearInput() {
    this.setData({
      manualBatchInput: ''
    });
  },

  /**
   * 跳转到历史页面
   */
  goToHistory() {
    wx.navigateTo({
      url: '/pages/history/history'
    });
  },

  /**
   * 跳转到历史详情
   */
  goToHistoryDetail(e) {
    const batchCode = e.currentTarget.dataset.batch;

    if (!batchCode) {
      wx.showToast({
        title: '批次号不能为空',
        icon: 'none'
      });
      return;
    }

    // 保存到历史记录
    const historyItem = {
      batchCode: batchCode,
      status: 'querying',
      productName: '手动查询',
      queryTime: new Date().getTime()
    };

    const storage = require('../../utils/storage.js');
    storage.saveHistory(historyItem);

    // 跳转到查询结果页面
    wx.navigateTo({
      url: `/pages/result/result?batchCode=${batchCode}`
    });
  }
});
