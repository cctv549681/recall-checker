// utils/storage.js
// 本地存储工具

/**
 * 保存查询记录
 * @param {Object} record - 查询记录
 */
function saveHistory(record) {
  try {
    const history = wx.getStorageSync('queryHistory') || [];

    // 添加到开头（最新的在前）
    const newRecord = {
      ...record,
      queryTime: new Date().getTime(),
      id: Date.now().toString()
    };

    history.unshift(newRecord);

    // 只保留最近100条
    const trimmed = history.slice(0, 100);

    wx.setStorageSync('queryHistory', trimmed);

    return true;
  } catch (error) {
    console.error('保存历史记录失败:', error);
    return false;
  }
}

/**
 * 获取查询历史
 * @param {string} filter - 过滤条件（all, recalled, not_recalled）
 */
function getHistory(filter = 'all') {
  try {
    const history = wx.getStorageSync('queryHistory') || [];

    if (filter === 'all') {
      return history;
    }

    // 过滤
    return history.filter(item => {
      if (filter === 'recalled') {
        return item.status === 'recalled';
      } else if (filter === 'not_recalled') {
        return item.status === 'not_recalled';
      }
      return true;
    });

  } catch (error) {
    console.error('获取历史记录失败:', error);
    return [];
  }
}

/**
 * 清空历史记录
 */
function clearHistory() {
  try {
    wx.removeStorageSync('queryHistory');

    wx.showToast({
      title: '已清空',
      icon: 'success',
      duration: 2000
    });

    return true;
  } catch (error) {
    console.error('清空历史记录失败:', error);
    return false;
  }
}

/**
 * 保存设置
 */
function saveSetting(key, value) {
  try {
    const settings = wx.getStorageSync('settings') || {};
    settings[key] = value;
    wx.setStorageSync('settings', settings);
    return true;
  } catch (error) {
    console.error('保存设置失败:', error);
    return false;
  }
}

/**
 * 获取设置
 */
function getSetting(key, defaultValue = null) {
  try {
    const settings = wx.getStorageSync('settings') || {};
    return settings[key] !== undefined ? settings[key] : defaultValue;
  } catch (error) {
    console.error('获取设置失败:', error);
    return defaultValue;
  }
}

module.exports = {
  saveHistory,
  getHistory,
  clearHistory,
  saveSetting,
  getSetting
};
