# Emall Linux 部署准备

本文档用于把当前项目部署到 Linux 服务器。推荐先在测试服务器完整跑通，再部署生产环境。

## 1. 推荐环境

| 组件 | 建议 |
|---|---|
| 操作系统 | Ubuntu 22.04/24.04 LTS、Debian 12、Rocky Linux 9 |
| Python | 3.12 |
| Web 服务 | Nginx + Gunicorn |
| 数据库 | MySQL 8，字符集 `utf8mb4` |
| 缓存/队列 | Redis 7 |
| 后台任务 | Celery worker + Celery beat |
| 进程管理 | systemd |
| HTTPS | Nginx + 证书，建议使用云厂商证书或 Let's Encrypt |

## 2. 目录规划

建议部署到：

```text
/opt/emall/
  backend/
  admin-web/
  miniapp/
  requirements/
  scripts/
  deploy/
  .venv/
  .env
```

生产静态和媒体目录：

```text
/opt/emall/backend/staticfiles/
/opt/emall/backend/media/
```

## 3. 系统依赖

Ubuntu/Debian 示例：

```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3-pip nginx mysql-server redis-server build-essential pkg-config default-libmysqlclient-dev
```

如果服务器没有 Python 3.12，可使用系统可用的 Python 3.11/3.12，但建议开发、测试、生产尽量一致。

## 4. MySQL 初始化

项目已经提供数据库辅助脚本：

```text
scripts/mysql_init.sql
scripts/emall_workbench_full_init.sql
```

首次执行用于创建数据库和账号：

```bash
mysql -u root -p < /opt/emall/scripts/mysql_init.sql
```

团队部署首选 `python backend/manage.py migrate` 建表。`scripts/emall_workbench_full_init.sql` 只是全量 SQL 快照，只有确认它与当前 migrations 完全一致时才用于一次性初始化。

注意修改脚本中的数据库密码，生产环境不要使用 `change-me`。

## 5. Python 环境和依赖

```bash
cd /opt/emall
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements/prod.txt
```

## 6. 生产环境变量

复制生产模板：

```bash
cp .env.production.example .env
chmod 600 .env
```

必须修改：

```text
DJANGO_SECRET_KEY
DJANGO_ALLOWED_HOSTS
DJANGO_CSRF_TRUSTED_ORIGINS
CORS_ALLOWED_ORIGINS
DB_PASSWORD
WECHAT_* 支付相关参数
```

生产环境必须保持：

```text
DJANGO_DEBUG=false
ENABLE_MOCK_API=false
CORS_ALLOW_ALL_ORIGINS=false
```

## 7. Django 建表和静态文件

```bash
cd /opt/emall
source .venv/bin/activate
python backend/manage.py migrate
python backend/manage.py collectstatic --noinput
python backend/manage.py check --deploy
```

如果是全新数据库，可初始化基础数据：

```bash
python backend/manage.py seed_initial_data
```

`seed_initial_data` 会同时写入会员等级、分类、规格模板、分销配置、测试账号和后台菜单数据。

## 8. Gunicorn 启动测试

```bash
cd /opt/emall
source .venv/bin/activate
gunicorn config.wsgi:application --chdir /opt/emall/backend --bind 127.0.0.1:8000 --workers 3
```

确认健康检查：

```bash
curl http://127.0.0.1:8000/api/health/
```

## 9. systemd 服务

示例文件在：

```text
deploy/systemd/emall-web.service
deploy/systemd/emall-celery-worker.service
deploy/systemd/emall-celery-beat.service
```

安装示例：

```bash
sudo cp deploy/systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now emall-web
sudo systemctl enable --now emall-celery-worker
sudo systemctl enable --now emall-celery-beat
```

`emall-celery-beat.service` 使用 `StateDirectory=emall`，systemd 会自动创建 `/var/lib/emall/` 用于保存 Celery Beat 调度状态。

查看日志：

```bash
journalctl -u emall-web -f
journalctl -u emall-celery-worker -f
journalctl -u emall-celery-beat -f
```

## 10. Nginx

示例文件：

```text
deploy/nginx/emall.conf
```

安装示例：

```bash
sudo cp deploy/nginx/emall.conf /etc/nginx/sites-available/emall.conf
sudo ln -s /etc/nginx/sites-available/emall.conf /etc/nginx/sites-enabled/emall.conf
sudo nginx -t
sudo systemctl reload nginx
```

你需要把示例中的：

```text
api.example.com
admin.example.com
/path/to/fullchain.pem
/path/to/privkey.pem
```

替换成真实域名和证书路径。

## 11. 管理后台部署

管理后台是 `admin-web/` 下的 Vue + Element Plus 项目。

本地或构建机执行：

```bash
cd admin-web
npm install
npm run build
```

构建结果通常在：

```text
admin-web/dist/
```

Nginx 示例中已经预留 `admin.example.com`，直接指向该目录。

## 12. Celery 定时任务

当前 `settings.py` 已配置：

| 任务 | 默认频率 | 用途 |
|---|---:|---|
| `apps.orders.tasks.close_expired_pending_orders_task` | 5 分钟 | 关闭超时未支付订单并释放库存 |
| `apps.marketing.tasks.expire_coupons_task` | 1 小时 | 标记过期优惠券 |
| `apps.distribution.tasks.settle_due_commissions_task` | 1 天 | 结算到期佣金 |

生产环境必须运行 `emall-celery-beat`，否则这些任务不会自动执行。

## 13. Mock API 注意事项

Mock API 只用于本地测试：

```text
/api/mock/
```

生产环境必须设置：

```text
ENABLE_MOCK_API=false
```

否则可能被误用来模拟支付、退款、提现到账。

## 14. 上线前检查清单

- `DJANGO_DEBUG=false`
- `ENABLE_MOCK_API=false`
- `.env` 权限为 `600`
- MySQL 密码已修改，且仅允许必要来源访问
- Redis 不暴露公网
- Nginx 已启用 HTTPS
- `python backend/manage.py check --deploy` 无高风险项
- 管理员默认密码已修改
- 微信支付、退款、回调域名已配置
- 图片上传目录 `backend/media/` 有备份策略
- MySQL 有每日备份和恢复演练
- 日志可通过 `journalctl` 或服务器日志平台查看

## 15. 常用维护命令

```bash
cd /opt/emall
source .venv/bin/activate

python backend/manage.py migrate
python backend/manage.py collectstatic --noinput
python backend/manage.py check --deploy

sudo systemctl restart emall-web
sudo systemctl restart emall-celery-worker
sudo systemctl restart emall-celery-beat
```

备份数据库示例：

```bash
mysqldump -u emall -p --single-transaction --routines --triggers emall > emall_$(date +%F).sql
```
