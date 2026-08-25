# Emall 分销商城

Emall 是一个分销商城完整项目，包含 Django REST Framework 后端、Vue3 + Element Plus PC 管理后台、UniApp 微信小程序端。当前已覆盖商城基础交易、商品/SKU、订单售后、会员、分销团队、城市代理、奖金池、财务提现、后台权限菜单、Mock 第三方接口等核心能力。

## 目录结构

```text
backend/       Django + DRF 后端
admin-web/     Vue3 + Element Plus 管理后台
miniapp/       UniApp 微信小程序源码
docs/          API、架构、部署、集成说明文档
deploy/        Nginx 和 systemd 部署配置示例
requirements/  Python 依赖清单
scripts/       MySQL 初始化和 Workbench 脚本
tools/         项目辅助工具
```

## 技术栈

| 模块 | 技术 |
|---|---|
| 后端 | Python 3.12、Django 5.2、Django REST Framework、Simple JWT |
| 数据库 | MySQL 8，开发期也可临时使用 SQLite |
| 缓存/队列 | Redis、Celery、Celery Beat |
| 管理后台 | Vue3、Vite、Pinia、Element Plus |
| 小程序 | UniApp，编译到微信小程序 |

## 从零启动后端

1. 复制环境变量模板：

```powershell
copy .env.example .env
```

2. 创建并启用虚拟环境：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. 安装依赖：

```powershell
python -m pip install --upgrade pip
pip install -r requirements\dev.txt
```

4. 初始化数据库：

```powershell
.\.venv\Scripts\python.exe backend\manage.py migrate
.\.venv\Scripts\python.exe backend\manage.py seed_initial_data
```

5. 启动后端：

```powershell
.\.venv\Scripts\python.exe backend\manage.py runserver 0.0.0.0:8000
```

健康检查：

```text
GET http://127.0.0.1:8000/api/health/
```

## MySQL 使用方式

推荐团队开发和服务器部署都使用 MySQL 8。`.env` 中配置：

```text
DB_ENGINE=mysql
DB_NAME=emall
DB_USER=emall
DB_PASSWORD=your-password
DB_HOST=127.0.0.1
DB_PORT=3306
```

然后执行：

```powershell
.\.venv\Scripts\python.exe backend\manage.py migrate
.\.venv\Scripts\python.exe backend\manage.py seed_initial_data
```

`seed_initial_data` 会初始化会员等级、商品分类、规格模板、分销配置、测试账号、后台菜单数据。

## 管理后台

```powershell
cd admin-web
npm install
npm run dev
```

开发地址：

```text
http://localhost:5173
```

Vite 默认把 `/api` 代理到 `http://127.0.0.1:8000`。如后端地址不同，修改 `admin-web/vite.config.js`。

## 微信小程序

用 HBuilderX 打开 `miniapp/`，运行到微信开发者工具。

API 地址在：

```text
miniapp/common/config.js
```

不要直接修改 `miniapp/unpackage/dist/dev/mp-weixin`，应修改 `miniapp` 源码后重新编译。

## 测试账号

基础测试账号由 `seed_initial_data` 生成，也记录在 `测试账号.txt`。

| 用户名 | 密码 | 用途 |
|---|---|---|
| `demo_admin` | `demoAdmin123456` | 管理后台、Django Admin、管理员接口 |
| `demo_buyer` | `demo123456` | 小程序普通用户 |

分销演示数据：

```powershell
.\.venv\Scripts\python.exe backend\manage.py seed_distribution_demo --settle --reward
.\.venv\Scripts\python.exe backend\manage.py check_distribution_demo
```

## 常用命令

```powershell
# 后端检查
.\.venv\Scripts\python.exe backend\manage.py check

# 生成迁移
.\.venv\Scripts\python.exe backend\manage.py makemigrations

# 执行迁移
.\.venv\Scripts\python.exe backend\manage.py migrate

# 关闭超时订单
.\.venv\Scripts\python.exe backend\manage.py close_expired_orders --minutes 30

# 管理后台构建
cd admin-web
npm run build
```

## 重要文档

- [API 接口说明](docs/api-reference.md)
- [后端架构说明](docs/backend-architecture.md)
- [Linux 部署准备](docs/deployment-linux.md)
- [第三方资金接口占位说明](docs/money-integrations.md)
- [需求分析与模块拆分](docs/requirements-analysis.md)
- [数据库脚本说明](scripts/README.md)

## GitHub 提交注意事项

不要提交：

- `.env`
- `.venv/`
- `admin-web/node_modules/`
- `admin-web/dist/`
- `miniapp/unpackage/`
- `backend/media/`
- `backend/staticfiles/`

`.gitignore` 已包含这些路径。团队成员拉取代码后，应根据 `.env.example` 自行创建本地 `.env`。

## 生产部署

生产环境参考：

- `.env.production.example`
- [Linux 部署准备](docs/deployment-linux.md)
- `deploy/nginx/`
- `deploy/systemd/`

生产环境必须关闭：

```text
DJANGO_DEBUG=false
ENABLE_MOCK_API=false
CORS_ALLOW_ALL_ORIGINS=false
```
