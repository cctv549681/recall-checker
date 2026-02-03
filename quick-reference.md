# 设计系统快速参考

## 🎨 配色方案

### 主色调
```css
--primary-color: #0078D7              /* 品牌蓝 */
--primary-gradient: linear-gradient(135deg, #0078D7 0%, #005FA3 100%)
```

### 状态色
```css
--success-color: #52C41A              /* 成功/正常 */
--success-gradient: linear-gradient(135deg, #52C41A 0%, #389E0D 100%)

--warning-color: #FF5252              /* 警告/召回 */
--warning-gradient: linear-gradient(135deg, #FF5252 0%, #D32F2F 100%)

--info-color: #999999                 /* 中性 */
```

### 中性色
```css
--gray-50: #FAFAFA
--gray-100: #F5F5F5
--gray-200: #E0E0E0
--gray-300: #CCCCCC
--gray-400: #999999
--gray-500: #666666
--gray-600: #555555
--gray-800: #333333
```

### 背景色
```css
--bg-primary: #F8F9FB                 /* 主背景 */
--bg-secondary: #FFFFFF               /* 卡片背景 */
```

---

## 📐 间距系统

```css
--spacing-xs: 8rpx
--spacing-sm: 16rpx
--spacing-md: 24rpx
--spacing-lg: 32rpx
--spacing-xl: 48rpx
```

### 工具类
```css
.mt-16 { margin-top: 16rpx; }
.mt-24 { margin-top: 24rpx; }
.mt-32 { margin-top: 32rpx; }

.mb-16 { margin-bottom: 16rpx; }
.mb-24 { margin-bottom: 24rpx; }
.mb-32 { margin-bottom: 32rpx; }

.pt-16 { padding-top: 16rpx; }
.pt-32 { padding-top: 32rpx; }

.pb-16 { padding-bottom: 16rpx; }
.pb-32 { padding-bottom: 32rpx; }
```

---

## ⭕ 圆角系统

```css
--radius-sm: 8rpx      /* 小元素：标签、图标 */
--radius-md: 16rpx     /* 按钮、输入框 */
--radius-lg: 24rpx     /* 卡片、弹窗 */
--radius-xl: 32rpx     /* 大容器 */
```

---

## 🌫️ 阴影系统

```css
--shadow-xs: 0 2rpx 4rpx rgba(0, 0, 0, 0.04)
--shadow-sm: 0 2rpx 8rpx rgba(0, 0, 0, 0.06)
--shadow-md: 0 4rpx 16rpx rgba(0, 0, 0, 0.08)
--shadow-lg: 0 8rpx 24rpx rgba(0, 120, 215, 0.15)
--shadow-xl: 0 16rpx 48rpx rgba(0, 120, 215, 0.2)
```

### 阴影使用场景
- `--shadow-sm`: 小卡片、列表项
- `--shadow-md`: 普通卡片
- `--shadow-lg`: 重要卡片、浮动元素
- `--shadow-xl`: 模态框、大弹窗

---

## 🔤 字体系统

### 字体大小
```css
--font-xs: 22rpx      /* 辅助文字 */
--font-sm: 24rpx      /* 小标签 */
--font-base: 28rpx    /* 正文 */
--font-lg: 32rpx      /* 强调文字 */
--font-xl: 36rpx      /* 小标题 */
--font-2xl: 48rpx     /* 大标题 */
```

### 字重
```css
--font-normal: 400
--font-medium: 500
--font-semibold: 600
--font-bold: 700
```

### 行高
```css
--leading-none: 1
--leading-tight: 1.2
--leading-normal: 1.5
--leading-relaxed: 1.75
```

---

## 🎯 组件库

### 按钮

#### 主按钮
```xml
<view class="btn btn-primary">按钮文字</view>
```

#### 次要按钮
```xml
<view class="btn btn-secondary">按钮文字</view>
```

#### 危险按钮
```xml
<view class="btn btn-danger">删除</view>
```

#### 全宽按钮
```xml
<view class="btn btn-primary btn-block">全宽按钮</view>
```

### 卡片

#### 基础卡片
```xml
<view class="card">
  <view class="card-title">标题</view>
  <view class="card-content">内容</view>
</view>
```

#### 大卡片
```xml
<view class="card card-lg">内容</view>
```

### 状态标签

```xml
<view class="status-badge status-safe">正常</view>
<view class="status-badge status-danger">召回</view>
<view class="status-badge status-unknown">未知</view>
```

### 输入框

```xml
<view class="input-wrapper">
  <input class="input" placeholder="请输入..." />
</view>
```

---

## 🎭 动画效果

### 淡入
```css
.fade-in {
  animation: fadeIn 0.3s ease-in;
}
```

### 滑上
```css
.slide-up {
  animation: slideUp 0.3s ease-out;
}
```

### 旋转（加载）
```css
.loading-spinner {
  animation: spin 1s linear infinite;
}
```

### 按钮点击
```css
.btn:active {
  transform: scale(0.98);
  opacity: 0.9;
}
```

---

## 🔧 布局工具

### Flex布局
```css
.flex { display: flex; }
.flex-column { display: flex; flex-direction: column; }
.flex-center { display: flex; align-items: center; justify-content: center; }
.flex-between { display: flex; align-items: center; justify-content: space-between; }
.flex-1 { flex: 1; }
```

### 文本对齐
```css
.text-center { text-align: center; }
.text-left { text-align: left; }
.text-right { text-align: right; }
```

---

## 📱 页面模板

### 标准页面结构
```xml
<view class="page-container">
  <!-- 顶部导航 -->
  <view class="navbar">
    <view class="back-btn" bindtap="goBack">
      <text class="back-icon">←</text>
    </view>
    <text class="navbar-title">页面标题</text>
  </view>

  <!-- 主内容区 -->
  <view class="content">
    <!-- 内容 -->
  </view>

  <!-- 底部固定栏（可选） -->
  <view class="bottom-actions">
    <view class="btn btn-primary">按钮</view>
  </view>
</view>
```

### 带Tab的页面结构
```xml
<view class="page-container">
  <view class="navbar">...</view>

  <!-- Tab栏 -->
  <view class="filter-tabs">
    <view class="tab-item active">全部</view>
    <view class="tab-item">召回</view>
  </view>

  <!-- 列表内容 -->
  <scroll-view class="content-scroll">
    <view class="list">...</view>
  </scroll-view>
</view>
```

---

## 🎨 颜色使用指南

### 何时使用主色调
- 主要操作按钮
- 导航栏背景
- 激活状态
- 链接文字
- 重要图标

### 何时使用成功色
- 安全状态
- 正常结果
- 成功操作
- 完成状态

### 何时使用警告色
- 召回状态
- 危险操作
- 错误提示
- 删除按钮

### 何时使用中性色
- 辅助文字
- 禁用状态
- 边框线条
- 背景层次

---

## ✨ 设计原则

### 1. 层次清晰
- 重要信息突出显示
- 使用大小、颜色区分主次
- 合理留白增强可读性

### 2. 一致性
- 统一的设计语言
- 一致的交互反馈
- 规范的组件使用

### 3. 简洁性
- 减少视觉噪音
- 专注于核心功能
- 避免过度装饰

### 4. 可访问性
- 保证足够的对比度
- 文字大小适中
- 交互区域足够大

---

## 🚀 快速开始

### 新页面创建步骤
1. 复制标准页面模板
2. 替换导航栏标题
3. 添加页面特定内容
4. 引入必要的组件
5. 调整间距和样式

### 样式文件结构
```css
/* 页面级样式 */
page {
  background-color: var(--bg-primary);
}

.page-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 组件样式 */
.component-name {
  /* ... */
}
```

### JavaScript最佳实践
```javascript
Page({
  data: {
    // 状态数据
  },

  onLoad() {
    // 页面加载
  },

  onShow() {
    // 页面显示
  },

  // 事件处理
  handleTap() {
    // 处理逻辑
  }
});
```

---

**最后更新：** 2026-02-03
**版本：** v1.0
