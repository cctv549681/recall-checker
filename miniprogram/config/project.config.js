// project.config.json
// 项目配置文件

module.exports = {
  // 百度 OCR API 配置
  baiduOcr: {
    // API Key（需要你在百度智能云申请）
    apiKey: 'YOUR_BAIDU_OCR_API_KEY',

    // API 地址
    apiUrl: 'https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic',

    // 请求配置
    options: {
      'language_type': 'CHN_ENG',
      'detect_direction': 'true',
      'probability': 'false'
    }
  },

  // 飞书 API 配置
  feishu: {
    appId: 'cli_a9f1f4887e38dcd2',
    appSecret: 'aNhAQdFTDJSWaQZnj2dy7dXvDgOzdi7u',
    appToken: 'R7cwbZ2Iaa4v0vs0Fh1cc5KUnEg',
    tableId: 'tblA1YqzSi4aaxeI'
  },

  // 应用配置
  app: {
    appName: '召回查询',
    version: '1.0.0',
    env: 'production',

    // 功能开关
    features: {
      ocr: true,              // OCR 识别
      manualInput: true,      // 手动输入
      history: true,           // 历史记录
      notification: true       // 通知提醒
    }
  },

  // UI 配置
  ui: {
    // 主色调（雀巢主题）
    colors: {
      primary: '#0078D7',      // 雀巢蓝
      secondary: '#00A651',    // 雀巢绿
      warning: '#FF5252',      // 警告/高风险
      success: '#52C41A',      // 成功/安全
      info: '#999999',         // 信息/未召回
      danger: '#FF5252',       // 危险
      background: '#F5F5F5',   // 背景灰
      card: '#FFFFFF',          // 卡片白
      text: {
        primary: '#333333',
        secondary: '#666666',
        muted: '#999999'
      }
    },

    // 字体配置
    fonts: {
      title: 'bold 24px',
      subtitle: 'bold 20px',
      body: 'regular 16px',
      small: 'regular 14px',
      tiny: 'regular 12px'
    },

    // 间距配置
    spacing: {
      xs: 8,
      sm: 12,
      md: 16,
      lg: 24,
      xl: 32
    },

    // 圆角配置
    borderRadius: {
      sm: 8,
      md: 16,
      lg: 24
    }
  },

  // 批次号匹配配置
  batch: {
    // 批次号模式（正则表达式）
    patterns: {
      // 雀巢：8-10位，数字字母混合
      nestle: '\\d{6,8}[A-Za-z]{2}',

      // Abbott：前两位22-37，包含K8/SH/Z2
      abbott: '(22|23|24|25|26|27|28|29|30|31|32|33|34|35|36|37).*(K8|SH|Z2)',

      // Mead Johnson：待补充
      meadJohnson: '',

      // Danone：待补充
      danone: '',

      // FrieslandCampina：待补充
      friesland: '',

      // 通用模式：6-12位字母数字
      generic: '[A-Za-z0-9]{6,12}'
    },

    // 模糊匹配配置
    fuzzy: {
      // 是否启用模糊匹配
      enabled: true,

      // 部分匹配最小长度
      partialMinLength: 4
    }
  }
};
