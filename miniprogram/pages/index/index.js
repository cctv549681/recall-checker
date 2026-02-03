// index.js - 首页（重构版：内嵌相机 + 极简流程）

// 导入工具
const apiClient = require('../../utils/api_client.js');
const { saveHistory, getHistory, timeAgo } = require('../../utils/storage.js');

Page({
  data: {
    // 相机状态
    showCamera: false,
    cameraContext: null,

    // OCR识别状态
    ocrLoading: false,
    ocrResult: '',

    // 手动输入
    manualInput: '',

    // 历史记录
    recentHistory: [],
  },

  onLoad(options) {
    this.loadHistory();
  },

  onShow() {
    this.loadHistory();
  },

  /**
   * 加载历史记录
   */
  loadHistory() {
    try {
      const history = getHistory() || [];
      const recent = history.slice(0, 3).map(item => ({
        ...item,
        timeAgo: this.formatTimeAgo(item.queryTime),
        statusClass: this.getStatusClass(item.status),
        statusText: this.getStatusText(item.status)
      }));

      this.setData({
        recentHistory: recent
      });
    } catch (error) {
      console.error('加载历史记录失败:', error);
    }
  },

  /**
   * 打开相机
   */
  openCamera() {
    // 检查相机权限
    wx.getSetting({
      success: (res) => {
        if (!res.authSetting['scope.camera']) {
          wx.authorize({
            scope: 'scope.camera',
            success: () => {
              this.setData({ showCamera: true });
              this.initCamera();
            },
            fail: () => {
              wx.showModal({
                title: '需要相机权限',
                content: '拍照功能需要使用相机权限，是否前往设置？',
                confirmText: '去设置',
                success: (modalRes) => {
                  if (modalRes.confirm) {
                    wx.openSetting();
                  }
                }
              });
            }
          });
        } else {
          this.setData({ showCamera: true });
          this.initCamera();
        }
      }
    });
  },

  /**
   * 初始化相机
   */
  initCamera() {
    this.setData({
      cameraContext: wx.createCameraContext()
    });
  },

  /**
   * 关闭相机
   */
  closeCamera() {
    this.setData({ showCamera: false });
  },

  /**
   * 拍照
   */
  onCameraTakePhoto() {
    const cameraContext = this.data.cameraContext;

    if (!cameraContext) {
      wx.showToast({
        title: '相机初始化失败',
        icon: 'none'
      });
      return;
    }

    // 震动反馈
    wx.vibrateShort({ type: 'light' });

    cameraContext.takePhoto({
      quality: 'high',
      success: (res) => {
        const tempFilePath = res.tempImagePath;
        // 直接进行OCR识别，不显示确认弹窗
        this.startOCR(tempFilePath);
      },
      fail: (err) => {
        console.error('拍照失败:', err);
        wx.showToast({
          title: '拍照失败，请重试',
          icon: 'none'
        });
      }
    });
  },

  /**
   * 从相册选择
   */
  onChooseFromAlbum() {
    wx.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['album'],
      success: (res) => {
        const tempFilePath = res.tempFilePaths[0];
        this.startOCR(tempFilePath);
      },
      fail: (err) => {
        console.error('选择图片失败:', err);
      }
    });
  },

  /**
   * 开始OCR识别
   */
  async startOCR(filePath) {
    this.setData({
      showCamera: false,
      ocrLoading: true
    });

    try {
      // 上传图片
      const uploadResult = await this.uploadImage(filePath);

      if (!uploadResult.success) {
        throw new Error(uploadResult.message || '上传失败');
      }

      // 调用OCR API
      const ocrResult = await apiClient.ocrImage(uploadResult.imageUrl);

      if (!ocrResult.success) {
        throw new Error(ocrResult.message || 'OCR识别失败');
      }

      const batchCode = ocrResult.data.batch_code;

      // 识别成功，保存历史记录并跳转
      this.saveAndNavigate(batchCode, 'OCR识别');

    } catch (error) {
      console.error('OCR识别失败:', error);

      wx.showModal({
        title: '识别失败',
        content: error.message || '无法识别批次号，请重新拍照或手动输入',
        confirmText: '重拍',
        cancelText: '手动输入',
        success: (modalRes) => {
          if (modalRes.confirm) {
            this.setData({ showCamera: true });
          } else {
            // 聚焦到输入框
            this.setData({ manualInput: '' });
          }
        }
      });

    } finally {
      this.setData({ ocrLoading: false });
    }
  },

  /**
   * 上传图片
   */
  uploadImage(filePath) {
    return new Promise((resolve, reject) => {
      wx.cloud.uploadFile({
        cloudPath: `ocr_images/${Date.now()}.jpg`,
        filePath: filePath,
        success: (res) => {
          const fileID = res.fileID;
          wx.cloud.getTempFileURL({
            fileList: [fileID],
            success: (urlRes) => {
              resolve({
                success: true,
                imageUrl: urlRes.fileList[0].tempFileURL,
                fileID: fileID
              });
            },
            fail: (err) => {
              reject({
                success: false,
                message: '获取文件URL失败'
              });
            }
          });
        },
        fail: (err) => {
          reject({
            success: false,
            message: '上传失败'
          });
        }
      });
    });
  },

  /**
   * 手动输入
   */
  onInput(e) {
    this.setData({
      manualInput: e.detail.value
    });
  },

  /**
   * 清空输入
   */
  clearInput() {
    this.setData({ manualInput: '' });
  },

  /**
   * 确认手动输入
   */
  onConfirmInput() {
    const batchCode = this.data.manualInput.trim();

    if (!batchCode) {
      wx.showToast({
        title: '请输入批次号',
        icon: 'none'
      });
      return;
    }

    // 简单验证批次号格式
    if (!/^[A-Z0-9]{5,15}$/i.test(batchCode)) {
      wx.showModal({
        title: '格式提示',
        content: '批次号应为5-15位字母和数字，是否继续查询？',
        confirmText: '继续',
        cancelText: '取消',
        success: (res) => {
          if (res.confirm) {
            this.saveAndNavigate(batchCode, '手动输入');
          }
        }
      });
      return;
    }

    this.saveAndNavigate(batchCode, '手动输入');
  },

  /**
   * 保存历史记录并跳转
   */
  saveAndNavigate(batchCode, source) {
    // 保存到历史记录
    const historyItem = {
      batchCode: batchCode,
      status: 'querying',
      productName: source,
      queryTime: Date.now()
    };

    saveHistory(historyItem);

    // 直接跳转结果页
    wx.navigateTo({
      url: `/pages/result/result?batchCode=${batchCode}`
    });
  },

  /**
   * 点击历史记录项
   */
  onHistoryItemTap(e) {
    const batchCode = e.currentTarget.dataset.batch;

    if (!batchCode) return;

    // 重新查询
    this.saveAndNavigate(batchCode, '历史记录');
  },

  /**
   * 跳转到历史记录页
   */
  goToHistory() {
    wx.navigateTo({
      url: '/pages/history/history'
    });
  },

  /**
   * 格式化时间
   */
  formatTimeAgo(timestamp) {
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
  },

  /**
   * 获取状态样式类
   */
  getStatusClass(status) {
    const statusMap = {
      'safe': 'safe',
      'danger': 'danger',
      'unknown': 'unknown',
      'querying': 'unknown'
    };
    return statusMap[status] || 'unknown';
  },

  /**
   * 获取状态文本
   */
  getStatusText(status) {
    const statusMap = {
      'safe': '正常',
      'danger': '已召回',
      'unknown': '查询中',
      'querying': '查询中'
    };
    return statusMap[status] || '未知';
  }
});
