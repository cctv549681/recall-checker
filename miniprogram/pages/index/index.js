// index.js
// 首页逻辑

Page({
  data: {
    recentHistory: [],
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
    const history = wx.getStorageSync('queryHistory') || [];
    // 只取最近3条
    const recent = history.slice(0, 3);

    this.setData({
      recentHistory: recent
    });
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
   * 跳转到输入页面
   */
  goToInput() {
    wx.navigateTo({
      url: '/pages/camera/camera?mode=input'
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

    wx.navigateTo({
      url: `/pages/result/result?batchCode=${batchCode}`
    });
  },
});
