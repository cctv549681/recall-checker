// camera.js - OCR 识别页面逻辑

// 导入配置和工具
const config = require('../../config/project.config.js');
const FeishuClient = require('../../scraper/utils/feishu_client.js');
const { saveHistory, timeAgo } = require('../../utils/storage.js');
const { formatDate, formatShortDate } = require('../../utils/date.js');

Page({
  data: {
    // 相机配置
    cameraPosition: 'back',          // 相机位置：front/back
    flash: 'off',                    // 闪光灯
    frameSize: { w: 1000, h: 1000 },

    // 图片相关
    imagePath: '',
    tempFilePath: '',                // 临时图片路径
    imageSrc: '',                     // 图片显示路径

    // OCR 相关
    batchCode: '',                  // 识别的批次号
    confidence: 0,                   // 置信度
    loading: false,                  // 加载状态
    showResult: false,               // 是否显示结果
    recognized: false,                // 是否已识别

    // 历史记录
    recentHistory: [],                // 最近查询记录
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
  loadHistory() {
    try {
      const storage = require('../../utils/storage.js');
      const history = storage.getHistory('all') || [];

      // 显示最近3条
      const recent = history.slice(0, 3);

      this.setData({
        recentHistory: recent
      });

    } catch (error) {
      console.error('加载历史记录失败:', error);
    }
  },

  /**
   * 初始化相机
   */
  initCamera() {
    // 创建相机上下文
    this.ctx = wx.createCameraContext();

    // 设置相机配置
    this.ctx.setFlash(false);

    this.setData({
      cameraPosition: 'back',
      flash: 'off'
    });
  },

  /**
   * 停止相机
   */
  stopCamera() {
    if (this.ctx) {
      this.ctx.stopRecord();
      this.ctx = null;
    }
  },

  /**
   * 从相册选择图片
   */
  onChooseImage() {
    const self = this;

    wx.chooseImage({
      count: 1,
      sizeType: ['original', 'compressed'],
      sourceType: ['album', 'camera'],
      success(res) {
        // 显示选择的图片
        const tempFilePath = res.tempFilePaths[0];

        // 显示确认弹窗
        wx.showModal({
          title: '确认图片',
          content: '是否使用这张照片？',
          confirmText: '确认',
          cancelText: '取消',
          success(modalRes) {
            if (modalRes.confirm) {
              // 确认使用，调用百度 OCR
              self.callBaiduOCR(tempFilePath);
            }
          }
        });
      },
      fail(err) {
        wx.showToast({
          title: '选择图片失败',
          icon: 'none'
        });
      }
    });
  },

  /**
   * 拍照
   */
  onTakePhoto() {
    const self = this;

    // 检查相机权限
    wx.getSetting({
      success(res) {
        if (!res.authSetting['scope.camera']) {
          wx.authorize({
            scope: 'scope.camera',
            success() {
              self.takePhotoInternal();
            }
          });
        } else {
          self.takePhotoInternal();
        }
      }
    });
  },

  /**
   * 内部拍照方法
   */
  takePhotoInternal() {
    const self = this;

    // 启动相机
    this.initCamera();

    // 拍照
    this.ctx.takePhoto({
      quality: 'high',
      success: (res) => {
        const tempFilePath = res.tempImagePath;

        // 预览图片
        self.setData({
          imageSrc: tempFilePath,
          tempFilePath: tempFilePath,
          recognized: false
        });

        // 停止相机
        self.stopCamera();

        // 显示确认弹窗
        wx.showModal({
          title: '确认照片',
          content: '是否使用这张照片进行批次号识别？',
          confirmText: '确认',
          cancelText: '重拍',
          success(modalRes) {
            if (modalRes.confirm) {
              // 确认使用，调用百度 OCR
              self.callBaiduOCR(tempFilePath);
            } else {
              // 重拍，重新初始化相机
              self.initCamera();
            }
          }
        });
      },
      fail(err) {
        wx.showToast({
          title: '拍照失败',
          icon: 'none'
        });
        self.initCamera();
      }
    });
  },

  /**
   * 调用百度 OCR API
   */
  callBaiduOCR(filePath) {
    const self = this;

    // 显示加载状态
    this.setData({
      loading: true,
      showResult: false
    });

    // 模拟 API 调用（实际项目中需要调用百度 OCR）
    // 这里先使用模拟数据
    setTimeout(() => {
      // 模拟识别结果
      const mockResult = {
        batchCode: '51450742F1',
        confidence: 95
      };

      this.setData({
        loading: false,
        batchCode: mockResult.batchCode,
        confidence: mockResult.confidence,
        recognized: true,
        showResult: true,
        imageSrc: filePath
      });

    }, 2000); // 模拟2秒识别时间

    // 实际代码（需要百度 API Key）：
    /*
    wx.request({
      url: config.baiduOcr.apiUrl,
      method: 'POST',
      header: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      data: {
        image: wx.getFileSystemManager().readFileSync(filePath)
      },
      success: (res) => {
        const result = JSON.parse(res.data);

        if (result.words_result && result.words_result.length > 0) {
          // 提取批次号（假设第一个词就是批次号）
          const batchCode = result.words_result[0].words;

          this.setData({
            loading: false,
            batchCode: batchCode,
            confidence: 80,
            recognized: true,
            showResult: true
          });
        } else {
          this.setData({
            loading: false,
            showResult: true,
            recognized: false
          });

          wx.showToast({
            title: '未识别到批次号',
            icon: 'none'
          });
        }
      },
      fail(err) {
        console.error('OCR 调用失败:', err);
        this.setData({
          loading: false,
          showResult: true,
          recognized: false
        });

        wx.showToast({
          title: '识别失败，请重试',
          icon: 'none'
        });
      }
    });
    */
  },

  /**
   * 确认识别结果
   */
  confirmResult() {
    const self = this;

    // 隐藏结果弹窗
    self.setData({
      showResult: false
    });

    // 跳转到查询结果页面
    const batchCode = self.data.batchCode;

    if (batchCode && batchCode.length > 0) {
      // 保存到历史记录
      const historyItem = {
        batchCode: batchCode,
        status: 'querying',
        productName: '识别中...',
        time: new Date().getTime()
      };

      const storage = require('../../utils/storage.js');
      storage.saveHistory(historyItem);

      // 跳转到结果页面
      wx.navigateTo({
        url: `/pages/result/result?batchCode=${batchCode}`
      });
    } else {
      wx.showToast({
        title: '请先识别批次号',
        icon: 'none'
      });
    }
  },

  /**
   * 重新识别
   */
  retakePhoto() {
    // 返回相机模式
    this.setData({
      showResult: false,
      imageSrc: '',
      tempFilePath: '',
      batchCode: '',
      confidence: 0,
      recognized: false
    });

    // 重新初始化相机
    this.initCamera();
  },

  /**
   * 隐藏结果
   */
  hideResult() {
    this.setData({
      showResult: false
    });
  },

  /**
   * 扫码
   */
  onScanCode() {
    wx.showToast({
      title: '扫码功能开发中',
      icon: 'none'
    });
  },

  /**
   * 相机错误处理
   */
  onCameraError(e) {
    console.error('相机错误:', e);
    wx.showToast({
      title: '相机错误，请重试',
      icon: 'none'
    });
  }
});
