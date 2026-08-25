-- Emall MySQL database bootstrap script.
--
-- Recommended order for a fresh environment:
--   1. Log in to MySQL as root/admin and run this file.
--   2. Copy .env.example to .env and set:
--        DB_ENGINE=mysql
--        DB_NAME=emall
--        DB_USER=emall
--        DB_PASSWORD=change-me
--        ENABLE_MOCK_API=true    -- local testing only
--   3. Run Django migrations:
--        .\.venv\Scripts\python.exe backend\manage.py migrate
--   4. Run this file again to insert seed data, or run:
--        .\.venv\Scripts\python.exe backend\manage.py seed_initial_data
--
-- If Django tables do not exist yet, the seed section is skipped automatically.
--
-- Linux server note:
--   Use a strong password, restrict host access when possible, and keep ENABLE_MOCK_API=false.

CREATE DATABASE IF NOT EXISTS `emall`
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'emall'@'localhost' IDENTIFIED BY 'change-me';
CREATE USER IF NOT EXISTS 'emall'@'%' IDENTIFIED BY 'change-me';

GRANT ALL PRIVILEGES ON `emall`.* TO 'emall'@'localhost';
GRANT ALL PRIVILEGES ON `emall`.* TO 'emall'@'%';
FLUSH PRIVILEGES;

USE `emall`;

-- ---------------------------------------------------------------------------
-- Optional post-migration seed data.
-- It is idempotent and can be executed more than once.
-- ---------------------------------------------------------------------------

DROP PROCEDURE IF EXISTS `emall_seed_initial_data`;

DELIMITER $$
CREATE PROCEDURE `emall_seed_initial_data`()
BEGIN
IF (
  SELECT COUNT(*)
  FROM `information_schema`.`tables`
  WHERE `table_schema` = DATABASE()
    AND `table_name` IN ('member_level', 'distribution_config', 'product_category', 'spec_template', 'user')
) = 5 THEN

INSERT INTO `member_level`
  (`id`, `name`, `upgrade_amount`, `team_upgrade_amount`, `commission_rate_lv1`, `commission_rate_lv2`, `discount`, `sort`, `created_at`, `updated_at`)
VALUES
  (1, '普通用户', 0.00, 0.00, 0.00, 0.00, 1.00, 10, NOW(6), NOW(6)),
  (2, '青铜会员', 500.00, 0.00, 0.00, 0.00, 0.95, 20, NOW(6), NOW(6)),
  (3, '白银会员', 2000.00, 0.00, 10.00, 5.00, 0.90, 30, NOW(6), NOW(6)),
  (4, '黄金会员', 2000.00, 10000.00, 15.00, 8.00, 0.85, 40, NOW(6), NOW(6)),
  (5, '钻石会员', 2000.00, 50000.00, 20.00, 10.00, 0.80, 50, NOW(6), NOW(6))
ON DUPLICATE KEY UPDATE
  `name` = VALUES(`name`),
  `upgrade_amount` = VALUES(`upgrade_amount`),
  `team_upgrade_amount` = VALUES(`team_upgrade_amount`),
  `commission_rate_lv1` = VALUES(`commission_rate_lv1`),
  `commission_rate_lv2` = VALUES(`commission_rate_lv2`),
  `discount` = VALUES(`discount`),
  `sort` = VALUES(`sort`),
  `updated_at` = NOW(6);

INSERT INTO `distribution_config`
  (`id`, `name`, `default_rate_lv1`, `default_rate_lv2`, `settlement_delay_days`, `enabled`, `created_at`, `updated_at`)
VALUES
  (1, '平台默认配置', 10.00, 5.00, 7, 1, NOW(6), NOW(6))
ON DUPLICATE KEY UPDATE
  `name` = VALUES(`name`),
  `default_rate_lv1` = VALUES(`default_rate_lv1`),
  `default_rate_lv2` = VALUES(`default_rate_lv2`),
  `settlement_delay_days` = VALUES(`settlement_delay_days`),
  `enabled` = VALUES(`enabled`),
  `updated_at` = NOW(6);

INSERT INTO `product_category`
  (`id`, `parent_id`, `name`, `icon`, `banner`, `sort`, `level`, `path`, `is_show`, `is_distribution`, `seo_title`, `seo_keywords`, `seo_description`, `is_active`, `created_at`, `updated_at`)
VALUES
  (1, NULL, '服饰鞋包', '', '', 50, 1, '', 1, 1, '', '', '', 1, NOW(6), NOW(6)),
  (2, NULL, '美妆个护', '', '', 40, 1, '', 1, 1, '', '', '', 1, NOW(6), NOW(6)),
  (3, NULL, '食品饮料', '', '', 30, 1, '', 1, 1, '', '', '', 1, NOW(6), NOW(6)),
  (4, NULL, '家居日用', '', '', 20, 1, '', 1, 1, '', '', '', 1, NOW(6), NOW(6)),
  (5, NULL, '数码家电', '', '', 10, 1, '', 1, 1, '', '', '', 1, NOW(6), NOW(6))
ON DUPLICATE KEY UPDATE
  `name` = VALUES(`name`),
  `sort` = VALUES(`sort`),
  `is_show` = VALUES(`is_show`),
  `is_distribution` = VALUES(`is_distribution`),
  `is_active` = VALUES(`is_active`),
  `updated_at` = NOW(6);

INSERT INTO `spec_template`
  (`id`, `name`, `spec_names`, `created_at`, `updated_at`)
VALUES
  (1, '颜色/尺码', JSON_ARRAY('颜色', '尺码'), NOW(6), NOW(6)),
  (2, '套餐/容量', JSON_ARRAY('套餐', '容量'), NOW(6), NOW(6))
ON DUPLICATE KEY UPDATE
  `name` = VALUES(`name`),
  `spec_names` = VALUES(`spec_names`),
  `updated_at` = NOW(6);

INSERT INTO `user`
  (`password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`,
   `parent_id`, `path`, `openid`, `mobile`, `nickname`, `avatar`, `level_id`, `role`, `is_distributor`, `city_agent_level`, `city_code`,
   `realname`, `id_card`, `realname_status`, `realname_remark`, `realname_verified_at`)
VALUES
  ('pbkdf2_sha256$1000000$hfrnZyaCp0gYq4Y4ObcPcq$MZwCNJ3a0/83Wi3rQESKeSTpTLYWM7F/7MVeftbG5B0=', NULL, 1,
   'demo_admin', '', '', '', 1, 1, NOW(6), NULL, '', NULL, '13800000000', '平台管理员', '', NULL, 'admin', 0, 0, NULL, '', '', 'unverified', '', NULL),
  ('pbkdf2_sha256$1000000$EbHURGNpCc3iK3mQqm8cQ6$3XiQCQ9BC5J/A8zLpP+pCbqlXz/Zb6zEFNK3tZeBavM=', NULL, 0,
   'demo_buyer', '', '', '', 0, 1, NOW(6), NULL, '', NULL, '13900000000', '测试买家', '', NULL, 'normal', 0, 0, NULL, '', '', 'unverified', '', NULL)
ON DUPLICATE KEY UPDATE
  `password` = VALUES(`password`),
  `is_superuser` = VALUES(`is_superuser`),
  `is_staff` = VALUES(`is_staff`),
  `is_active` = VALUES(`is_active`),
  `mobile` = VALUES(`mobile`),
  `nickname` = VALUES(`nickname`),
  `role` = VALUES(`role`);

ALTER TABLE `member_level` AUTO_INCREMENT = 100;
ALTER TABLE `distribution_config` AUTO_INCREMENT = 100;
ALTER TABLE `product_category` AUTO_INCREMENT = 100;
ALTER TABLE `spec_template` AUTO_INCREMENT = 100;

ELSE
  SELECT 'Django tables do not exist yet. Run python backend/manage.py migrate, then run this SQL again for seed data.' AS `message`;
END IF;
END$$
DELIMITER ;

CALL `emall_seed_initial_data`();
DROP PROCEDURE IF EXISTS `emall_seed_initial_data`;
