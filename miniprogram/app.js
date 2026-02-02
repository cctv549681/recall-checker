// app.js - 小程序入口文件

/**
 * 小程序入口文件
 * 负责：
 * 1. 注册小程序
 * 2. 生命周期管理
 * 3. 全局数据管理
 * 4. API 初始化
 */

App({
  /**
   * 全局数据
   */
  globalData: {
    // 用户信息
    userInfo: null,

    // 系统信息
    systemInfo: null,

    // API 配置
    apiConfig: {
      baseUrl: '', // TODO: 配置后端 API 地址
      timeout: 10000
    },

    // 飞书配置
    feishu: {
      appToken: '', // TODO: 配置飞书 APP_TOKEN
      tableId: '' // TODO: 配置飞书 TABLE_ID
    }
  },

  /**
   * 小程序初始化完成
   */
  onLaunch(options) {
    console.log('小程序启动', options);

    // 获取系统信息
    this.getSystemInfo();

    // 检查更新
    this.checkUpdate();

    // 初始化
    this.initApp();
  },

  /**
   * 小程序显示
   */
  onShow(options) {
    console.log('小程序显示', options);
  },

  /**
   * 小程序隐藏
   */
  onHide() {
    console.log('小程序隐藏');
  },

  /**
   * 小程序错误
   */
  onError(error) {
    console.error('小程序错误:', error);

    // 错误上报（可选）
    // this.reportError(error);
  },

  /**
   * 页面不存在
   */
  onPageNotFound(res) {
    console.warn('页面不存在:', res);

    // 跳转到首页
    wx.redirectTo({
      url: '/pages/index/index'
    });
  },

  /**
   * 初始化应用
   */
  initApp() {
    // 获取存储的用户信息
    try {
      const userInfo = wx.getStorageSync('userInfo');
      if (userInfo) {
        this.globalData.userInfo = userInfo;
      }
    } catch (error) {
      console.error('获取用户信息失败:', error);
    }
  },

  /**
   * 获取系统信息
   */
  getSystemInfo() {
    wx.getSystemInfo({
      success: (res) => {
        this.globalData.systemInfo = res;
        console.log('系统信息:', res);
      },
      fail: (error) => {
        console.error('获取系统信息失败:', error);
      }
    });
  },

  /**
   * 检查小程序更新
   */
  checkUpdate() {
    if (wx.canIUse('getUpdateManager')) {
      const updateManager = wx.getUpdateManager();

      updateManager.onCheckForUpdate((res) => {
        console.log('检查更新:', res.hasUpdate);
      });

      updateManager.onUpdateReady(() => {
        wx.showModal({
          title: '更新提示',
          content: '新版本已下载，是否重启应用？',
          success(res) {
            if (res.confirm) {
              updateManager.applyUpdate();
            }
          }
        });
      });

      updateManager.onUpdateFailed(() => {
        console.error('新版本下载失败');
      });
    }
  },

  /**
   * 获取全局数据
   */
  getGlobalData() {
    return this.globalData;
  },

  /**
   * 设置全局数据
   */
  setGlobalData(key, value) {
    if (typeof key === 'object') {
      Object.assign(this.globalData, key);
    } else {
      this.globalData[key] = value;
    }
  },

  /**
   * API 请求封装
   */
  request(options) {
    return new Promise((resolve, reject) => {
      const { url, method = 'GET', data = {}, header = {} } = options;

      wx.request({
        url: this.globalData.apiConfig.baseUrl + url,
        method: method,
        data: data,
        header: {
          'content-type': 'application/json',
          ...header
        },
        timeout: this.globalData.apiConfig.timeout,
        success: (res) => {
          if (res.statusCode === 200) {
            resolve(res.data);
          } else {
            reject(res);
          }
        },
        fail: (error) => {
          reject(error);
        }
      });
    });
  }
});
