// utils/date.js
// 日期格式化工具

/**
 * 格式化日期为"X分钟/小时/天前"格式
 * @param {number} timestamp - Unix 时间戳
 * @returns {string} 相对时间字符串
 */
function timeAgo(timestamp) {
  if (!timestamp) return '';

  const now = Date.now();
  const diff = now - timestamp;
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (seconds < 60) {
    return `${seconds}秒前`;
  } else if (minutes < 60) {
    return `${minutes}分钟前`;
  } else if (hours < 24) {
    return `${hours}小时前`;
  } else if (days < 7) {
    return `${days}天前`;
  } else {
    return `${Math.floor(days / 7)}周前`;
  }
}

/**
 * 格式化日期为 "YYYY年MM月DD日"格式
 * @param {number} timestamp - Unix 时间戳
 * @returns {string} 格式化日期
 */
function formatDate(timestamp) {
  if (!timestamp) return '';

  const date = new Date(timestamp);
  const year = date.getFullYear();
  const month = date.getMonth() + 1;
  const day = date.getDate();

  return `${year}年${month}月${day}日`;
}

/**
 * 格式化日期为 "MM月DD日"格式
 * @param {number} timestamp - Unix 时间戳
 * @returns {string} 格式化日期
 */
function formatShortDate(timestamp) {
  if (!timestamp) return '';

  const date = new Date(timestamp);
  const month = date.getMonth() + 1;
  const day = date.getDate();

  return `${month}月${day}日`;
}

/**
 * 格式化有效期为 "YYYY年MM月"格式（去掉日）
 * @param {number} timestamp - Unix 时间戳
 * @returns {string} 格式化日期
 */
function formatExpiryDate(timestamp) {
  if (!timestamp) return '';

  const date = new Date(timestamp);
  const year = date.getFullYear();
  const month = date.getMonth() + 1;

  return `${year}年${month}月`;
}

/**
 * 判断日期是否已过期
 * @param {number} timestamp - Unix 时间戳
 * @returns {boolean} 是否过期
 */
function isExpired(timestamp) {
  if (!timestamp) return true;

  const now = Date.now();
  return timestamp < now;
}

/**
 * 计算剩余天数
 * @param {number} timestamp - Unix 时间戳
 * @returns {number} 剩余天数
 */
function daysRemaining(timestamp) {
  if (!timestamp) return 0;

  const diff = timestamp - Date.now();
  const days = Math.ceil(diff / (1000 * 60 * 60 * 24));

  return Math.max(0, days);
}

module.exports = {
  timeAgo,
  formatDate,
  formatShortDate,
  formatExpiryDate,
  isExpired,
  daysRemaining
};
