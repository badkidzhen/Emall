# Emall 接口说明文档

本文档按业务模块说明当前后端 API。后端基于 Django REST Framework，大多数资源接口遵循 REST 风格。

## 1. 基础信息

本地开发地址：

```text
http://127.0.0.1:8000/api
```

生产环境示例：

```text
https://api.example.com/api
```

认证方式：

```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

分页格式由 DRF 提供，列表接口通常返回：

```json
{
  "count": 100,
  "next": "http://example.com/api/xxx/?page=2",
  "previous": null,
  "results": []
}
```

常见状态码：

| 状态码 | 含义 |
|---:|---|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 204 | 删除成功 |
| 400 | 参数错误或业务状态不允许 |
| 401 | 未登录或 Token 失效 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务端异常 |

## 2. 认证接口

| 方法 | 路径 | 权限 | 说明 |
|---|---|---|---|
| POST | `/api/auth/token/` | 公开 | 用户名密码登录，获取 JWT |
| POST | `/api/auth/token/refresh/` | 公开 | 刷新 access token |

登录请求：

```json
{
  "username": "demo_admin",
  "password": "demoAdmin123456"
}
```

登录响应：

```json
{
  "refresh": "...",
  "access": "..."
}
```

## 3. 健康检查和上传

| 方法 | 路径 | 权限 | 说明 |
|---|---|---|---|
| GET | `/api/health/` | 公开 | 服务健康检查 |
| POST | `/api/uploads/images/` | 管理员 | 上传商品、分类等图片 |

图片上传使用 `multipart/form-data`，字段名：

```text
file
```

支持 `jpg`、`png`、`webp`、`gif`，最大 5MB。

## 4. 用户和会员

| 方法 | 路径 | 权限 | 说明 |
|---|---|---|---|
| GET | `/api/users/me/` | 登录用户 | 当前用户信息 |
| GET | `/api/users/` | 管理员 | 用户列表 |
| POST | `/api/users/` | 管理员 | 创建用户 |
| GET | `/api/users/{id}/` | 登录用户/管理员 | 用户详情，普通用户只能看自己 |
| PATCH | `/api/users/{id}/` | 管理员 | 修改用户 |
| DELETE | `/api/users/{id}/` | 管理员 | 删除用户 |
| POST | `/api/users/submit-realname/` | 登录用户 | 提交实名认证 |
| POST | `/api/users/{id}/audit-realname/` | 管理员 | 审核实名认证 |
| GET | `/api/users/levels/` | 公开读 | 会员等级列表 |
| POST | `/api/users/levels/` | 管理员 | 创建会员等级 |

提交实名认证：

```json
{
  "realname": "张三",
  "id_card": "110101199001011234"
}
```

审核实名认证：

```json
{
  "approved": true,
  "remark": "审核通过"
}
```

## 5. 商品、分类、SKU、库存

| 方法 | 路径 | 权限 | 说明 |
|---|---|---|---|
| GET | `/api/catalog/categories/` | 公开读 | 分类列表 |
| GET | `/api/catalog/categories/tree/` | 公开读 | 分类树 |
| POST | `/api/catalog/categories/` | 管理员 | 创建分类 |
| GET | `/api/catalog/products/` | 公开读 | 商品列表 |
| GET | `/api/catalog/products/{id}/` | 公开读 | 商品详情，含 `skus` |
| POST | `/api/catalog/products/` | 管理员 | 创建商品 |
| PATCH | `/api/catalog/products/{id}/` | 管理员 | 修改商品 |
| POST | `/api/catalog/products/{id}/generate-skus/` | 管理员 | 按规格批量生成 SKU |
| GET | `/api/catalog/skus/` | 公开读 | SKU 列表 |
| PATCH | `/api/catalog/skus/{id}/` | 管理员 | 修改 SKU 价格、库存等 |
| GET | `/api/catalog/spec-templates/` | 管理员 | 规格模板 |
| GET | `/api/catalog/stock-logs/` | 管理员 | 库存流水 |

商品列表常用筛选：

```text
?category={分类ID}
?min_price=100&max_price=500
?sale_status=on_sale
?is_distribution=true
?search=关键词
?ordering=-created_at
```

批量生成 SKU：

```json
{
  "spec_options": [
    {"name": "颜色", "values": ["红", "蓝"]},
    {"name": "尺寸", "values": ["S", "M"]}
  ],
  "price": "99.00",
  "market_price": "129.00",
  "stock": 100,
  "warning_stock": 10,
  "overwrite": false
}
```

## 6. 购物车、订单、支付、售后

订单状态枚举：

| 值 | 含义 |
|---|---|
| `pending_payment` | 待付款 |
| `pending_shipment` | 待发货 |
| `pending_receipt` | 待收货 |
| `completed` | 已完成 |
| `refunding` | 售后中 |
| `refunded` | 已退款 |
| `closed` | 已关闭 |

| 方法 | 路径 | 权限 | 说明 |
|---|---|---|---|
| GET | `/api/orders/cart-items/` | 登录用户 | 购物车列表 |
| POST | `/api/orders/cart-items/add/` | 登录用户 | 加入购物车 |
| PATCH | `/api/orders/cart-items/{id}/` | 登录用户 | 修改数量/选中状态 |
| DELETE | `/api/orders/cart-items/{id}/` | 登录用户 | 删除购物车项 |
| GET | `/api/orders/addresses/` | 登录用户 | 收货地址列表 |
| POST | `/api/orders/addresses/` | 登录用户 | 新增收货地址 |
| GET | `/api/orders/` | 登录用户 | 订单列表 |
| POST | `/api/orders/create/` | 登录用户 | 创建订单 |
| GET | `/api/orders/{id}/` | 登录用户 | 订单详情 |
| POST | `/api/orders/{id}/create-payment/` | 登录用户 | 创建支付请求 |
| POST | `/api/orders/{id}/cancel/` | 登录用户 | 取消待支付订单 |
| POST | `/api/orders/{id}/receive/` | 登录用户 | 确认收货 |
| POST | `/api/orders/{id}/apply-refund/` | 登录用户 | 申请退款 |
| POST | `/api/orders/{id}/apply-invoice/` | 登录用户 | 申请发票 |
| POST | `/api/orders/{id}/confirm-paid/` | 管理员 | 开发期手动确认支付 |
| POST | `/api/orders/{id}/ship/` | 管理员 | 发货 |
| POST | `/api/orders/{id}/complete/` | 管理员 | 后台完成订单 |

加入购物车：

```json
{
  "sku": 1,
  "quantity": 2,
  "selected": true
}
```

创建订单：

```json
{
  "items": [
    {"sku_id": 1, "quantity": 2}
  ],
  "from_cart": false,
  "address_id": 1,
  "remark": "请尽快发货"
}
```

直接传地址快照也可以：

```json
{
  "items": [{"sku_id": 1, "quantity": 1}],
  "address": {
    "receiver_name": "张三",
    "receiver_mobile": "13800000000",
    "province": "浙江省",
    "city": "杭州市",
    "district": "西湖区",
    "address_detail": "测试地址"
  }
}
```

创建支付请求：

```json
{
  "channel": "mock",
  "openid": "test-openid"
}
```

发货：

```json
{
  "company": "顺丰速运",
  "tracking_no": "SF123456789",
  "traces": []
}
```

申请退款：

```json
{
  "refund_type": "refund_only",
  "amount": "99.00",
  "reason": "不想要了"
}
```

申请发票：

```json
{
  "invoice_type": "personal",
  "title": "张三",
  "email": "user@example.com",
  "content": "商品明细"
}
```

### 售后管理

| 方法 | 路径 | 权限 | 说明 |
|---|---|---|---|
| GET | `/api/orders/refunds/` | 登录用户/管理员 | 退款列表 |
| POST | `/api/orders/refunds/{id}/approve/` | 管理员 | 退款审核通过 |
| POST | `/api/orders/refunds/{id}/reject/` | 管理员 | 退款驳回 |
| POST | `/api/orders/refunds/{id}/request-gateway/` | 管理员 | 请求第三方退款 |
| POST | `/api/orders/refunds/{id}/mark-refunded/` | 管理员 | 手动标记退款成功 |
| GET | `/api/orders/invoices/` | 登录用户/管理员 | 发票申请列表 |
| POST | `/api/orders/invoices/{id}/issue/` | 管理员 | 开票 |
| GET | `/api/orders/logistics/` | 登录用户/管理员 | 物流记录 |

## 7. 分销、团队、佣金

佣金状态枚举：

| 值 | 含义 |
|---|---|
| `frozen` | 冻结中，等待结算 |
| `settled` | 已结算，已进入钱包 |
| `canceled` | 已取消 |

| 方法 | 路径 | 权限 | 说明 |
|---|---|---|---|
| GET | `/api/distribution/team-stats/` | 登录用户/管理员 | 团队统计 |
| GET | `/api/distribution/team-stats/tree/` | 登录用户 | 当前用户团队树 |
| POST | `/api/distribution/team-stats/sync/` | 管理员 | 同步指定用户团队统计 |
| GET | `/api/distribution/configs/` | 管理员 | 分销配置 |
| POST | `/api/distribution/configs/bind-parent/` | 管理员 | 给指定用户绑定上级 |
| POST | `/api/distribution/configs/bind-mine/` | 登录用户 | 当前用户绑定上级 |
| POST | `/api/distribution/configs/settle-commissions/` | 管理员 | 结算到期佣金 |
| GET | `/api/distribution/commissions/` | 登录用户/管理员 | 佣金记录 |

绑定上级：

```json
{
  "user_id": 3,
  "parent_id": 1
}
```

当前用户绑定上级：

```json
{
  "parent_id": 1
}
```

分销测试脚本：

```powershell
.\.venv\Scripts\python.exe backend\manage.py seed_distribution_demo --settle --reward
.\.venv\Scripts\python.exe backend\manage.py check_distribution_demo
```

## 8. 营销活动

| 方法 | 路径 | 权限 | 说明 |
|---|---|---|---|
| GET | `/api/marketing/coupon-templates/` | 公开读 | 优惠券模板 |
| POST | `/api/marketing/coupon-templates/` | 管理员 | 创建优惠券模板 |
| POST | `/api/marketing/coupon-templates/{id}/claim/` | 登录用户 | 领取优惠券 |
| GET | `/api/marketing/user-coupons/` | 登录用户/管理员 | 用户优惠券 |
| POST | `/api/marketing/user-coupons/expire/` | 管理员 | 手动过期优惠券 |
| GET | `/api/marketing/groups/` | 公开读 | 拼团活动 |
| POST | `/api/marketing/groups/{id}/purchase/` | 登录用户 | 拼团下单 |
| GET | `/api/marketing/seckills/` | 公开读 | 秒杀活动 |
| POST | `/api/marketing/seckills/{id}/purchase/` | 登录用户 | 秒杀下单 |
| GET | `/api/marketing/activity-records/` | 登录用户/管理员 | 活动购买记录 |

活动购买：

```json
{
  "quantity": 1
}
```

## 9. 城市代理

| 方法 | 路径 | 权限 | 说明 |
|---|---|---|---|
| GET | `/api/agents/applications/` | 登录用户/管理员 | 代理申请列表 |
| POST | `/api/agents/applications/` | 登录用户 | 提交代理申请 |
| POST | `/api/agents/applications/{id}/approve/` | 管理员 | 审核通过 |
| POST | `/api/agents/applications/{id}/reject/` | 管理员 | 审核驳回 |
| GET | `/api/agents/` | 登录用户/管理员 | 代理区域列表 |
| POST | `/api/agents/` | 管理员 | 创建代理区域 |

提交代理申请：

```json
{
  "level": 2,
  "region_code": "330100",
  "region_name": "杭州市",
  "contact_name": "张三",
  "contact_phone": "13800000000"
}
```

审核通过：

```json
{
  "commission_rate": "3.00",
  "remark": "审核通过"
}
```

## 10. 奖金池

| 方法 | 路径 | 权限 | 说明 |
|---|---|---|---|
| GET | `/api/rewards/pools/` | 登录用户/管理员 | 奖金池列表 |
| POST | `/api/rewards/pools/` | 管理员 | 创建奖金池 |
| POST | `/api/rewards/pools/{id}/distribute/` | 管理员 | 分配奖金，生成待发放记录 |
| POST | `/api/rewards/pools/{id}/mark-paid/` | 管理员 | 标记发放，入账到钱包 |
| GET | `/api/rewards/rules/` | 管理员 | 奖金池规则 |
| GET | `/api/rewards/records/` | 登录用户/管理员 | 奖励分配记录 |

业务顺序：

```text
创建奖金池 -> 创建/确认规则 -> 点击分配 -> 查看分配记录 -> 标记发放
```

## 11. 钱包、资金流水、提现

| 方法 | 路径 | 权限 | 说明 |
|---|---|---|---|
| GET | `/api/finance/wallets/mine/` | 登录用户 | 当前用户钱包 |
| GET | `/api/finance/wallets/` | 登录用户/管理员 | 钱包列表 |
| GET | `/api/finance/flows/` | 登录用户/管理员 | 资金流水 |
| GET | `/api/finance/withdrawals/` | 登录用户/管理员 | 提现申请列表 |
| POST | `/api/finance/withdrawals/` | 登录用户 | 提交提现 |
| POST | `/api/finance/withdrawals/{id}/approve/` | 管理员 | 提现审核通过 |
| POST | `/api/finance/withdrawals/{id}/reject/` | 管理员 | 提现驳回 |
| POST | `/api/finance/withdrawals/{id}/submit-payout/` | 管理员 | 提交第三方打款 |
| POST | `/api/finance/withdrawals/{id}/mark-paid/` | 管理员 | 手动标记打款成功 |

提交提现：

```json
{
  "amount": "100.00",
  "channel": "manual",
  "account_name": "张三",
  "account_no": "13800000000"
}
```

## 12. 系统权限、角色、菜单

管理后台权限系统基于 Django `User`、`Group`、`Permission` 和项目自定义 `admin_menu` 菜单表实现。

| 方法 | 路径 | 权限 | 说明 |
|---|---|---|---|
| GET | `/api/system/menus/` | 管理员 | 获取后台菜单树，左侧菜单优先读取此接口 |
| GET | `/api/system/menu-items/` | 管理员 | 菜单项列表，不分页 |
| POST | `/api/system/menu-items/` | 管理员 | 新增菜单项 |
| GET | `/api/system/menu-items/{id}/` | 管理员 | 菜单项详情 |
| PUT/PATCH | `/api/system/menu-items/{id}/` | 管理员 | 修改菜单项 |
| DELETE | `/api/system/menu-items/{id}/` | 管理员 | 删除菜单项，子菜单级联删除 |
| GET | `/api/system/roles/` | 管理员 | 角色列表，基于 Django Group |
| POST | `/api/system/roles/` | 管理员 | 创建角色 |
| PUT/PATCH | `/api/system/roles/{id}/` | 管理员 | 修改角色和权限 |
| DELETE | `/api/system/roles/{id}/` | 管理员 | 删除角色 |
| GET | `/api/system/permissions/` | 管理员 | 权限列表，不分页 |
| GET | `/api/system/logs/` | 管理员 | 操作日志，读取 Django admin log |

菜单项示例：

```json
{
  "parent": null,
  "name": "数据中心",
  "code": "data-center",
  "icon": "DataAnalysis",
  "path": "",
  "component": "",
  "permission": "",
  "sort": 100,
  "level": 1,
  "is_show": true
}
```

二级菜单示例：

```json
{
  "parent": 1,
  "name": "订单统计",
  "code": "order-service:/orders/statistics",
  "icon": "",
  "path": "/orders/statistics",
  "component": "ReportPage",
  "permission": "orders:statistics",
  "sort": 5,
  "level": 2,
  "is_show": true
}
```

角色保存示例：

```json
{
  "name": "运营管理员",
  "permissions": [1, 2, 3]
}
```

## 13. Mock 模拟接口

Mock API 只用于本地测试。生产环境必须设置 `ENABLE_MOCK_API=false`。

| 方法 | 路径 | 权限 | 说明 |
|---|---|---|---|
| POST | `/api/mock/payments/{order_id}/success/` | 管理员 | 模拟订单支付成功 |
| POST | `/api/mock/refunds/{refund_id}/success/` | 管理员 | 模拟退款成功 |
| POST | `/api/mock/withdrawals/{withdrawal_id}/paid/` | 管理员 | 模拟提现到账 |
| POST | `/api/mock/wallets/{user_id}/income/` | 管理员 | 给用户钱包加测试收入 |
| POST | `/api/mock/realname/success/` | 登录用户 | 模拟当前用户实名通过 |
| POST | `/api/mock/users/{user_id}/realname-success/` | 管理员 | 模拟指定用户实名通过 |
| POST | `/api/mock/sms/send/` | 公开 | 模拟发送短信，固定验证码 `123456` |
| POST | `/api/mock/sms/verify/` | 公开 | 模拟校验短信 |
| POST | `/api/mock/logistics/{order_id}/delivered/` | 管理员 | 模拟物流签收 |

模拟钱包收入：

```json
{
  "amount": "100.00",
  "remark": "测试余额"
}
```

## 14. 常用测试账号

根目录已记录测试账号：

```text
测试账号.txt
```

基础账号：

| 用户名 | 密码 | 用途 |
|---|---|---|
| `demo_admin` | `demoAdmin123456` | 管理后台、管理员接口 |
| `demo_buyer` | `demo123456` | 小程序普通用户 |

分销测试账号统一密码：

```text
demo123456
```

| 用户名 | 用途 |
|---|---|
| `dist_demo_leader` | 团队长 |
| `dist_demo_direct_1` | 直推分销商 |
| `dist_demo_indirect_1` | 间推用户 |
| `dist_demo_direct_2` | 直推用户 |
| `dist_demo_agent` | 城市代理 |
