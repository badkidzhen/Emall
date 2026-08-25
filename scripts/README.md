# SQL 脚本说明

## `emall_workbench_full_init.sql`

用途：在 MySQL Workbench 中对一个空数据库一次性完成建表和基础数据初始化。

团队日常推荐使用 Django 迁移流程：

```powershell
.\.venv\Scripts\python.exe backend\manage.py migrate
.\.venv\Scripts\python.exe backend\manage.py seed_initial_data
```

`emall_workbench_full_init.sql` 是某一时点的全量 SQL 快照。如果代码后续新增 migration，请优先使用 `migrate`，或重新生成总 SQL 后再用于全量初始化。

它包含：

- Django 系统表
- Emall 业务表
- 外键、索引、唯一约束
- `django_migrations` 迁移记录
- `django_content_type` 和 `auth_permission` 权限基础数据
- 会员等级、分类、规格模板、分销默认配置
- 测试账号 `demo_admin`、`demo_buyer`

执行方式：

1. 打开 MySQL Workbench，连接 Linux 服务器 MySQL。
2. 确认脚本中的数据库名 `Emall` 与 `.env` 中的 `DB_NAME` 一致。
3. 打开 `scripts/emall_workbench_full_init.sql`。
4. 整个文件一次性执行；脚本会自动创建并切换到 `Emall` 数据库。

注意：

- 该脚本会先 `DROP TABLE IF EXISTS` 删除同名表，请只在空库或可重建的测试库中执行。
- Django 5.2 要求 MySQL `8.0.11+`，MySQL 5.7 即使建表成功，后端运行时也会报版本不支持。
- 执行该脚本后，不需要再执行 `python backend/manage.py migrate`；因为脚本已经写入 `django_migrations`。
- 后续如果代码新增了 migration，再通过 `python backend/manage.py migrate` 增量升级。

如果你已经在服务器上直接执行过 `migrate` 和 `seed_initial_data`，一般就不需要再执行这个总脚本。

## `mysql_init.sql`

用途：创建数据库、数据库用户，以及在 Django migration 完成后补基础数据。

它适合 DBA 先创建数据库和账号；业务表仍推荐通过 Django `migrate` 创建，基础数据通过 `seed_initial_data` 写入。
