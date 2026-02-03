// history.js - 历史记录页面逻辑

// 导入工具
const { getHistory, clearHistory } = require('../../utils/storage.js');
const { timeAgo } = require('../../utils/date.js');

Page({
  data: {
    // 历史记录
    historyList: [],
    filter: 'all',  // all, recalle, not_recalled, expired

    // 模态窗
    showClearModal: false
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
   * 加载历史记录
   */
  async loadHistory() {
    try {
      const history = await getHistory(this.data.filter);
      const formattedList = this.formatHistory(history);

      this.setData({
        historyList: formattedList
      });

    } catch (error) {
      console.error('加载历史记录失败:', error);
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      });
    }
  },

  /**
   * 格式化历史记录
   */
  formatHistory(history) {
    return history.map(item => {
      const batchCode = item.batchCode || '';

      return {
        ...item,
        batchCode: batchCode.toUpperCase(),
        timeAgo: timeAgo(item.queryTime || Date.now()),
        statusText: this.getStatusText(item.status),
        statusClass: this.getStatusClass(item.status)
      };
    });
  },

  /**
   * 获取状态文本
   */
  getStatusText(status) {
    const statusMap = {
      'querying': '查询中',
      'recalled': '召回中',
      'not_recalled': '未召回',
      'expired': '已结束',
      'not_found': '未找到'
    };

    return statusMap[status] || '未知';
  },

  /**
   * 获取状态样式类
   */
  getStatusClass(status) {
    const classMap = {
      'querying': 'status-querying',
      'recalled': 'status-recalled',
      'not_recalled': 'status-not_recalled',
      'expired': 'status-expired',
      'not_found': 'status-not_found'
    };

    return classMap[status] || 'status-not_found';
  },

  /**
   * 设置筛选
   */
  setFilter(e) {
    const filter = e.currentTarget.dataset.filter;
    this.setData({ filter });

    // 重新加载历史记录
    this.loadHistory();
  },

  /**
   * 跳转到结果页面
   */
  goToResult(e) {
    const batchCode = e.currentTarget.dataset.batch;

    if (batchCode) {
      wx.navigateTo({
        url: `/pages/result/result?batchCode=${batchCode}`
      });
    }
  },

  /**
   * 返回首页
   */
  goBack() {
    wx.navigateBack();
  },

  /**
   * 显示清空确认弹窗
   */
  showClearModal() {
    this.setData({
      showClearModal: true
    });
  },

  /**
   * 隐藏清空确认弹窗
   */
  hideClearModal() {
    this.setData({
      showClearModal: false
    });
  },

  /**
   * 确认清空
   */
  confirmClearReal() {
    try {
      // 清空本地存储
      const cleared = clearHistory();

      if (cleared) {
        this.setData({
          historyList: [],
          showClearModal: false
        });
      } else {
        wx.showToast({
          title: '清空失败',
          icon: 'none'
        });
      }

    } catch (error) {
      console.error('清空失败:', error);
      wx.showToast({
        title: '清空失败',
        icon: 'none'
      });
    }
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
   * 跳转到首页
   */
  goToIndex() {
    wx.switchTab({
      url: '/pages/index/index'
    });
  }
});
