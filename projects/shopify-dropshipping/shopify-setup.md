# LuxeGlow Shopify 完整设置指南

---

## 🎨 第 1 步：Logo 设置（10 分钟）

**操作路径：** Online Store → Themes → Customize → Header

1. 去 Canva.com 制作 Logo（参考 `logo-prompt.md`）
2. 下载 PNG（透明背景）
3. Shopify 后台 → Header → Upload image
4. 调整大小：宽度 200-250px

---

## 🎨 第 2 步：配色设置（5 分钟）

**操作路径：** Online Store → Themes → Customize → Theme Settings → Colors

**设置：**
```
Primary color（按钮/强调）: #B76E79
Secondary color（链接）: #D4AF37
Background: #FFFFFF
Text: #2C2C2C
Secondary text: #757575
```

---

## 🏠 第 3 步：首页装修（30 分钟）

**操作路径：** Online Store → Themes → Customize

**按顺序添加 Sections：**

### Section 1: Image Banner
```
- Upload image（Unsplash 找"woman makeup mirror"）
- Heading: Perfect Lighting, Perfect You
- Subheading: Premium LED Vanity Mirror for the Modern Woman
- Button label: Shop Now
- Button link: /products/luxeglow-pro-led-vanity-mirror
- Image overlay: 35%
```

### Section 2: Collage
```
- Layout: 3 columns
- 上传 3 个图标（Flaticon.com 搜索 light/battery/travel）
- 填写标题和描述（参考 `homepage-copy.md`）
```

### Section 3: Featured Product
```
- Product: 选择 LuxeGlow Pro
- Show: Image, Title, Price, Rating
```

### Section 4: Rich Text
```
- Heading: The LuxeGlow Promise
- Text: 复制 `homepage-copy.md` 内容
- Button: Learn More → /pages/about-us
```

### Section 5: Testimonials
```
- 复制 3 个评价（参考 `homepage-copy.md`）
- 用 Rich Text 或 Custom Liquid 添加
```

### Section 6: Trust Badges
```
- 用 Collage 或 Rich Text 添加 4 个信任标识
- 图标 + 文字形式
```

---

## 📦 第 4 步：产品设置（20 分钟）

**操作路径：** Products → Add product

**填写：**
```
Title: LuxeGlow™ Pro LED Vanity Mirror - Rechargeable Makeup Mirror with 3 Brightness Levels, Portable Folding Design, Rose Gold

Description: 复制 `product-copy.md` HTML 内容（切换到 HTML 编辑器）

Pricing:
- Price: $34.99
- Compare at price: $49.99

Inventory:
- SKU: LG-PRO-RG
- Quantity: 50

Shipping:
- Weight: 280g
- Customs info: Harmonized code 8513.10（灯具类）

Variants:
- Add options: Color
- Values: Rose Gold, Champagne Gold, Classic White
- 分别设置价格和库存

Search engine listing:
- Page title: LuxeGlow Pro LED Vanity Mirror | Free Shipping
- Meta description: Professional-grade LED vanity mirror with 3 brightness levels. Rechargeable, portable, elegant. 30-day returns. Shop now!
```

**产品图片：**
- 上传 5-8 张（参考 `product-copy.md`）
- 第一张设为白底主图

---

## 📄 第 5 步：页面设置（15 分钟）

**操作路径：** Online Store → Pages → Add page

**创建 5 个页面：**

1. **About Us** → 复制 `pages-copy.md` About Us 内容
2. **Shipping Policy** → 复制 Shipping Policy 内容
3. **Return Policy** → 复制 Return Policy 内容
4. **Contact Us** → 复制 Contact Us 内容
5. **FAQ** → 复制 FAQ 内容

---

## ⚙️ 第 6 步：导航设置（5 分钟）

**操作路径：** Online Store → Navigation

### Main Menu
```
- Home → /
- Shop → /collections/all
- About → /pages/about-us
- Contact → /pages/contact-us
```

### Footer Menu
```
- Shipping Policy → /pages/shipping-policy
- Return Policy → /pages/return-policy
- FAQ → /pages/faq
- Privacy Policy → /policies/privacy-policy
- Terms of Service → /policies/terms-of-service
```

---

## 💳 第 7 步：支付设置（10 分钟）

**操作路径：** Settings → Payments

### 激活 PayPal
```
1. PayPal → Activate
2. 登录你的 PayPal 账号
3. 完成连接
```

### 激活 Shopify Payments（信用卡）
```
1. Shopify Payments → Activate
2. 填写信息：
   - Business type: Individual/Sole proprietorship
   - Product description: LED Vanity Mirrors
   - Email: support@luxeglow.com
   - URL: luxeglow.myshopify.com
   - 个人信息（姓名、地址、电话）
3. 等待审核（通常即时通过）
```

---

## 🚚 第 8 步：运费设置（10 分钟）

**操作路径：** Settings → Shipping and delivery

### 创建运费模板

**Zone 1: United States**
```
- Standard Shipping: $5.99
- Free Shipping: $0（Condition: Order price over $30）
```

**Zone 2: Canada, UK, Australia, Europe**
```
- Standard Shipping: $9.99
- Free Shipping: $0（Condition: Order price over $50）
```

**Zone 3: Rest of World**
```
- Standard Shipping: $14.99
- Free Shipping: $0（Condition: Order price over $70）
```

---

## 📧 第 9 步：邮件通知设置（5 分钟）

**操作路径：** Settings → Notifications

**自定义订单确认邮件：**
```
Subject: Thank you for your order! #{{order_number}}

Body:
Hi {{customer.name}},

Thank you for ordering from LuxeGlow! 

Your order #{{order_number}} has been received and will be processed within 1-3 business days.

You'll receive a tracking number via email once your order ships.

Questions? Reply to this email or contact us at support@luxeglow.com.

Thank you for choosing LuxeGlow! ✨

— The LuxeGlow Team
```

---

## 📱 第 10 步：安装必要 Apps（10 分钟）

**操作路径：** Apps → Visit Shopify App Store

### 必装 App（免费）

**1. Judge.me Product Reviews**
```
- 搜索 "Judge.me"
- 安装
- 设置：自动发送邮件请求评价
```

**2. Privy**
```
- 搜索 "Privy"
- 安装
- 设置弹窗："Get 10% off your first order"
```

---

## ✅ 最后检查清单

**店铺设置：**
- [ ] Logo 上传
- [ ] 配色设置完成
- [ ] Favicon 设置（小图标）

**首页：**
- [ ] Hero Banner 设置
- [ ] 6 个 Sections 完成
- [ ] 移动端预览正常

**产品：**
- [ ] 产品标题优化
- [ ] 产品描述完整
- [ ] 5-8 张图片上传
- [ ] 价格设置（原价 + 折扣）
- [ ] 库存数量设置
- [ ] 变体设置（颜色/尺寸）

**页面：**
- [ ] About Us
- [ ] Shipping Policy
- [ ] Return Policy
- [ ] Contact Us
- [ ] FAQ

**导航：**
- [ ] Main Menu 设置
- [ ] Footer Menu 设置

**支付：**
- [ ] PayPal 激活
- [ ] Shopify Payments 激活
- [ ] 测试下单（用测试模式）

**运费：**
- [ ] 运费模板设置
- [ ] 免费送货门槛设置

**技术：**
- [ ] 域名设置（可先用免费的）
- [ ] SSL 证书激活（自动）
- [ ] 邮件通知测试

---

## 🚀 上线前测试

**操作路径：** Online Store → Preferences → Password protection

**取消密码保护：**
```
1. 取消勾选 "Enable password"
2. Save
```

**测试下单：**
```
1. 用另一个浏览器访问店铺
2. 添加产品到购物车
3. 完成结账（用测试支付）
4. 检查邮件通知是否收到
5. 后台查看订单是否正确
```

---

## 📊 上线后监控

**每天检查：**
- [ ] 订单数量
- [ ] 访客数量（Analytics → Dashboard）
- [ ] 转化率（订单数/访客数）
- [ ] 客服邮件

**每周优化：**
- [ ] 分析热销产品
- [ ] 优化低转化页面
- [ ] 添加客户评价
- [ ] 调整广告策略

---

*按这个指南一步步完成，约 2 小时搞定高端店铺！*
