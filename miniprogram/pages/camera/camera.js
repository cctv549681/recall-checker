// camera.js - OCR识别页面（调用真实API）

// 导入工具
const { saveHistory, timeAgo } = require('../../utils/storage.js');
const { formatDate } = require('../../utils/date.js');
const apiClient = require('../../utils/api_client.js');

Page({
  data: {
    // 相机配置
    cameraPosition: 'back',
    flash: 'off',
    frameSize: { w: 1000, h: 1000 },

    // 图片相关
    imagePath: '',
    tempFilePath: '',
    imageSrc: '',

    // OCR 相关
    batchCode: '',
    confidence: 0,
    loading: false,
    showResult: false,
    recognized: false,
    ocrError: '',

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
      const history = wx.getStorageSync('queryHistory') || [];
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
    this.ctx = wx.createCameraContext();
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
        const tempFilePath = res.tempFilePaths[0];

        wx.showModal({
          title: '确认图片',
          content: '是否使用这张照片进行批次号识别？',
          confirmText: '确认',
          cancelText: '取消',
          success(modalRes) {
            if (modalRes.confirm) {
              self.callOCRAPI(tempFilePath);
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

    this.initCamera();

    this.ctx.takePhoto({
      quality: 'high',
      success: (res) => {
        const tempFilePath = res.tempImagePath;

        self.setData({
          imageSrc: tempFilePath,
          tempFilePath: tempFilePath,
          recognized: false
        });

        this.stopCamera();

        wx.showModal({
          title: '确认照片',
          content: '是否使用这张照片进行批次号识别？',
          confirmText: '确认',
          cancelText: '重拍',
          success(modalRes) {
            if (modalRes.confirm) {
              self.callOCRAPI(tempFilePath);
            } else {
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
        this.initCamera();
      }
    });
  },

  /**
   * 调用后端OCR API
   */
  async callOCRAPI(filePath) {
    const self = this;

    self.setData({
      loading: true,
      showResult: false,
      ocrError: ''
    });

    try {
      // 上传图片到临时服务器，获取URL
      const uploadResult = await this.uploadImage(filePath);

      if (!uploadResult.success) {
        throw new Error(uploadResult.message || '上传失败');
      }

      // 调用后端OCR API
      const ocrResult = await this.callBackendOCR(uploadResult.imageUrl);

      if (!ocrResult.success) {
        throw new Error(ocrResult.message || 'OCR识别失败');
      }

      const { batch_code, confidence } = ocrResult.data;

      self.setData({
        loading: false,
        batchCode: batch_code,
        confidence: confidence,
        recognized: true,
        showResult: true
      });

      console.log('OCR识别成功:', { batch_code, confidence });

    } catch (error) {
      console.error('OCR识别失败:', error);

      self.setData({
        loading: false,
        ocrError: error.message || '识别失败，请重试'
      });

      wx.showToast({
        title: error.message || '识别失败',
        icon: 'none',
        duration: 2000
      });
    }
  },

  /**
   * 上传图片到临时服务器
   * 使用微信云存储或临时文件上传接口
   */
  async uploadImage(filePath) {
    return new Promise((resolve, reject) => {
      // 上传图片到微信云存储
      wx.cloud.uploadFile({
        cloudPath: `ocr_images/${Date.now()}.jpg`,
        filePath: filePath,
        success(res) => {
          const fileID = res.fileID;
          // 获取文件URL
          wx.cloud.getTempFileURL({
            fileList: [fileID],
            success(urlRes) => {
              resolve({
                success: true,
                imageUrl: urlRes.fileList[0].tempFileURL,
                fileID: fileID
              });
            },
            fail(err) {
              reject({
                success: false,
                message: '获取文件URL失败'
              });
            }
          });
        },
        fail(err) {
          reject({
            success: false,
            message: '上传失败'
          });
        }
      });
    });
  },

  /**
   * 调用后端OCR接口
   */
  async callBackendOCR(imageUrl) {
    try {
      // 使用后端API的OCR接口
      const apiResult = await apiClient.ocrImage(imageUrl);
      return apiResult;
    } catch (error) {
      console.error('调用后端OCR失败:', error);
      throw error;
    }
  },

  /**
   * 确认识别结果
   */
  confirmResult() {
    const self = this;

    self.setData({
      showResult: false
    });

    const batchCode = self.data.batchCode;

    if (batchCode && batchCode.length > 0) {
      // 保存到历史记录
      const historyItem = {
        batchCode: batchCode,
        status: 'querying',
        productName: 'OCR识别',
        queryTime: new Date().getTime()
      };

      saveHistory(historyItem);

      // 跳转到查询结果页面
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
    this.setData({
      showResult: false,
      imageSrc: '',
      tempFilePath: '',
      batchCode: '',
      confidence: 0,
      recognized: false
    });

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
