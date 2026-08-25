# Emall UniApp 小程序

这是分销商城小程序端源码，建议使用 HBuilderX 打开 `miniapp/` 并编译到微信开发者工具。

## 开发步骤

1. 配置 `common/config.js` 的 `API_BASE_URL`
2. 用 HBuilderX 编译到 `dist/dev/mp-weixin`
3. 微信开发者工具打开编译后的项目
4. 修改 `miniapp` 源码后重新编译，不要直接改 `dist`

## 后端地址

默认 API 地址：

```js
export const API_BASE_URL = "http://127.0.0.1:8000/api";
```

局域网调试时改成电脑 IP，例如：

```js
export const API_BASE_URL = "http://192.168.1.10:8000/api";
```

## 页面范围

- 首页、分类、搜索、商品详情
- 购物车、下单、订单列表、订单详情、售后
- 用户中心、地址、实名认证、优惠券、钱包
- 分销、团队、代理、奖金池
- 微信登录、JWT 登录、Mock 调试流程

## 登录

当前接入 Django JWT 用户名密码登录接口：

```text
POST /api/auth/token/
```

如果本地开发时后端与小程序端联调异常，优先检查：

- `common/config.js`
- Django 后端是否已启动
- 微信开发者工具里是否重新编译并重新打开项目
