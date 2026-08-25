# Django 后端架构说明

## 目录结构

```text
backend/
  manage.py
  config/
    settings.py        项目配置、数据库、Redis、Celery、DRF
    urls.py            API 总路由
    celery.py          Celery 应用入口
    asgi.py
    wsgi.py
  apps/
    core/              通用能力、健康检查、图片上传、Mock API
                      后台菜单、系统权限、操作日志
    users/             用户、会员等级、实名认证
    catalog/           分类、商品、SKU、库存日志
    orders/            购物车、订单、支付记录、退款、发票、物流
    distribution/      分销配置、团队统计、佣金记录
    marketing/         优惠券、拼团、秒杀
    agents/            城市代理申请、代理区域
    rewards/           奖金池、规则、奖励分配记录
    finance/           钱包、资金流水、提现
```

## 配置策略

- 本地环境通过项目根目录 `.env` 读取配置。
- 当前本地已支持 MySQL；生产环境继续使用 `DB_ENGINE=mysql`。
- Redis 用于 Django cache、Celery broker 和 Celery result backend。
- JWT 作为 API 鉴权基础，默认 access token 有效期 7 天。
- `ENABLE_MOCK_API` 控制 Mock API 是否挂载，生产必须关闭。
- HTTPS、HSTS、Secure Cookie 等生产安全项通过环境变量控制。

## API 前缀

| 前缀 | 模块 |
|---|---|
| `/api/health/` | 健康检查 |
| `/api/auth/` | JWT 登录与刷新 |
| `/api/uploads/` | 管理后台图片上传 |
| `/api/users/` | 用户、会员等级、实名认证 |
| `/api/catalog/` | 分类、商品、SKU、库存 |
| `/api/orders/` | 购物车、订单、支付、退款、发票、物流 |
| `/api/distribution/` | 分销、团队统计、佣金 |
| `/api/marketing/` | 优惠券、拼团、秒杀 |
| `/api/agents/` | 城市代理 |
| `/api/rewards/` | 奖金池 |
| `/api/finance/` | 钱包、资金流水、提现 |
| `/api/system/` | 后台菜单、角色、权限、操作日志 |
| `/api/mock/` | 本地 Mock API，仅开发测试 |

完整接口说明见 [接口说明文档](api-reference.md)。

## 核心业务流

### 下单与履约

```text
商品/SKU -> 加入购物车或直接下单 -> 锁定 SKU 库存
-> 创建支付请求 -> 支付成功 -> 扣减锁定库存
-> 发货 -> 确认收货/后台完成 -> 触发佣金计算
```

### 售后与资金

```text
申请退款 -> 管理员审核 -> 请求第三方退款或 Mock 退款
-> 标记退款成功 -> 恢复订单状态或订单退款完成

钱包收入 -> 提现申请 -> 余额冻结
-> 审核通过/驳回 -> 打款/标记到账 -> 资金流水
```

### 分销与奖励

```text
绑定上级 -> 形成 parent_id + path 分销链
-> 订单完成 -> 一级/二级佣金冻结
-> 到期结算 -> 佣金进入钱包

团队统计 -> 奖金池分配 -> 生成待发放记录
-> 标记发放 -> 奖励进入钱包
```

## Celery 与 Redis

已接入的 Celery 任务：

| 任务 | 用途 |
|---|---|
| `apps.orders.tasks.close_expired_pending_orders_task` | 关闭超时待支付订单并释放库存 |
| `apps.marketing.tasks.expire_coupons_task` | 标记过期优惠券 |
| `apps.distribution.tasks.calculate_order_commission` | 异步佣金计算入口 |
| `apps.distribution.tasks.sync_team_stat` | 同步团队统计 |
| `apps.distribution.tasks.settle_due_commissions_task` | 结算到期佣金 |
| `apps.rewards.tasks.distribute_reward_pool` | 奖金池分配 |

当前定时任务在 `CELERY_BEAT_SCHEDULE` 中配置：

- 每 5 分钟关闭超时订单。
- 每小时处理过期优惠券。
- 每天结算到期佣金。

## 数据建模原则

- 订单商品保存商品标题、SKU 编码和规格快照，避免商品后续编辑影响历史订单。
- 用户分销链使用 `parent_id + path`，当前只计算一级、二级佣金。
- SKU 库存独立于商品总库存，库存变更写入 `stock_log`。
- 拼团、秒杀活动绑定到 SKU，活动购买会生成订单和活动购买记录。
- 佣金、钱包、提现、奖金池均保留明细记录，便于审计。
- 后台菜单表 `admin_menu` 由 `seed_initial_data` 初始化，菜单管理页面可继续维护。

## 测试与演示命令

基础数据：

```powershell
.\.venv\Scripts\python.exe backend\manage.py seed_initial_data
```

该命令会同时初始化：

- 会员等级
- 商品分类
- 规格模板
- 分销默认配置
- 测试账号
- 后台菜单数据

分销、团队、代理、奖金池测试数据：

```powershell
.\.venv\Scripts\python.exe backend\manage.py seed_distribution_demo --settle --reward
.\.venv\Scripts\python.exe backend\manage.py check_distribution_demo
```

关闭超时订单：

```powershell
.\.venv\Scripts\python.exe backend\manage.py close_expired_orders --minutes 30
```
