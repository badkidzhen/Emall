-- Emall full MySQL initialization script for MySQL Workbench.
-- Generated from the current Django models and migrations.
-- Target: an empty or rebuildable MySQL 8.0.11+ database.
--
-- Usage in MySQL Workbench:
--   1. Open the connection to the Linux MySQL server.
--   2. Confirm the database name below matches your .env DB_NAME.
--   3. Execute this whole file once.
--
-- Important:
--   Django 5.2 requires MySQL 8.0.11 or later. MySQL 5.7 is not supported by the backend runtime.
--   This script marks Django migrations as applied, so do not run `manage.py migrate` before it on the same empty database.

SET NAMES utf8mb4;
SET time_zone = '+00:00';
SET FOREIGN_KEY_CHECKS = 0;

CREATE DATABASE IF NOT EXISTS `Emall`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
USE `Emall`;

-- ---------------------------------------------------------------------------
-- Drop existing tables in dependency-safe order.
-- Only run this script against an empty or disposable schema.
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS `withdraw_application`;
DROP TABLE IF EXISTS `wallet`;
DROP TABLE IF EXISTS `user_user_permissions`;
DROP TABLE IF EXISTS `user_team_stat`;
DROP TABLE IF EXISTS `user_groups`;
DROP TABLE IF EXISTS `user_coupon`;
DROP TABLE IF EXISTS `user`;
DROP TABLE IF EXISTS `stock_log`;
DROP TABLE IF EXISTS `spec_template`;
DROP TABLE IF EXISTS `seckill_activity`;
DROP TABLE IF EXISTS `reward_pool_rule`;
DROP TABLE IF EXISTS `reward_pool`;
DROP TABLE IF EXISTS `reward_distribution_record`;
DROP TABLE IF EXISTS `refund_application`;
DROP TABLE IF EXISTS `product_sku`;
DROP TABLE IF EXISTS `product_category_relation`;
DROP TABLE IF EXISTS `product_category`;
DROP TABLE IF EXISTS `product`;
DROP TABLE IF EXISTS `payment_record`;
DROP TABLE IF EXISTS `order_item`;
DROP TABLE IF EXISTS `order_address`;
DROP TABLE IF EXISTS `order`;
DROP TABLE IF EXISTS `member_level`;
DROP TABLE IF EXISTS `logistics_record`;
DROP TABLE IF EXISTS `invoice_application`;
DROP TABLE IF EXISTS `group_buying_activity`;
DROP TABLE IF EXISTS `fund_flow`;
DROP TABLE IF EXISTS `django_session`;
DROP TABLE IF EXISTS `django_migrations`;
DROP TABLE IF EXISTS `django_content_type`;
DROP TABLE IF EXISTS `django_admin_log`;
DROP TABLE IF EXISTS `distribution_config`;
DROP TABLE IF EXISTS `coupon_template_products`;
DROP TABLE IF EXISTS `coupon_template_categories`;
DROP TABLE IF EXISTS `coupon_template`;
DROP TABLE IF EXISTS `commission_record`;
DROP TABLE IF EXISTS `city_agent_application`;
DROP TABLE IF EXISTS `city_agent`;
DROP TABLE IF EXISTS `cart_item`;
DROP TABLE IF EXISTS `auth_permission`;
DROP TABLE IF EXISTS `auth_group_permissions`;
DROP TABLE IF EXISTS `auth_group`;
DROP TABLE IF EXISTS `activity_purchase_record`;

-- ---------------------------------------------------------------------------
-- Create tables, indexes and foreign keys.
-- ---------------------------------------------------------------------------
CREATE TABLE `django_migrations` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `app` varchar(255) NOT NULL, `name` varchar(255) NOT NULL, `applied` datetime(6) NOT NULL);
CREATE TABLE `django_admin_log` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `action_time` datetime(6) NOT NULL, `user_id` bigint NOT NULL, `content_type_id` integer NULL, `object_id` longtext NULL, `object_repr` varchar(200) NOT NULL, `action_flag` smallint UNSIGNED NOT NULL CHECK (`action_flag` >= 0), `change_message` longtext NOT NULL);
CREATE TABLE `auth_permission` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `name` varchar(255) NOT NULL, `content_type_id` integer NOT NULL, `codename` varchar(100) NOT NULL);
CREATE TABLE `auth_group` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `name` varchar(150) NOT NULL UNIQUE);
CREATE TABLE `auth_group_permissions` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `group_id` integer NOT NULL, `permission_id` integer NOT NULL);
CREATE TABLE `django_content_type` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `app_label` varchar(100) NOT NULL, `model` varchar(100) NOT NULL);
CREATE TABLE `django_session` (`session_key` varchar(40) NOT NULL PRIMARY KEY, `session_data` longtext NOT NULL, `expire_date` datetime(6) NOT NULL);
CREATE TABLE `member_level` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `created_at` datetime(6) NOT NULL, `updated_at` datetime(6) NOT NULL, `name` varchar(50) NOT NULL, `upgrade_amount` numeric(12, 2) NOT NULL, `team_upgrade_amount` numeric(12, 2) NOT NULL, `commission_rate_lv1` numeric(5, 2) NOT NULL, `commission_rate_lv2` numeric(5, 2) NOT NULL, `discount` numeric(4, 2) NOT NULL, `sort` integer UNSIGNED NOT NULL CHECK (`sort` >= 0));
CREATE TABLE `user` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `password` varchar(128) NOT NULL, `last_login` datetime(6) NULL, `is_superuser` bool NOT NULL, `username` varchar(150) NOT NULL UNIQUE, `first_name` varchar(150) NOT NULL, `last_name` varchar(150) NOT NULL, `email` varchar(254) NOT NULL, `is_staff` bool NOT NULL, `is_active` bool NOT NULL, `date_joined` datetime(6) NOT NULL, `parent_id` bigint NULL, `path` varchar(255) NOT NULL, `openid` varchar(64) NULL UNIQUE, `mobile` varchar(20) NULL UNIQUE, `nickname` varchar(50) NOT NULL, `avatar` varchar(500) NOT NULL, `level_id` bigint NULL, `role` varchar(32) NOT NULL, `is_distributor` bool NOT NULL, `city_agent_level` smallint UNSIGNED NOT NULL CHECK (`city_agent_level` >= 0), `city_code` varchar(20) NULL, `realname` varchar(50) NOT NULL, `id_card` varchar(32) NOT NULL, `realname_status` varchar(20) NOT NULL, `realname_remark` varchar(255) NOT NULL, `realname_verified_at` datetime(6) NULL);
CREATE TABLE `user_groups` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `user_id` bigint NOT NULL, `group_id` integer NOT NULL);
CREATE TABLE `user_user_permissions` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `user_id` bigint NOT NULL, `permission_id` integer NOT NULL);
CREATE TABLE `product_category` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `created_at` datetime(6) NOT NULL, `updated_at` datetime(6) NOT NULL, `is_active` bool NOT NULL, `parent_id` bigint NULL, `name` varchar(100) NOT NULL, `icon` varchar(500) NOT NULL, `banner` varchar(500) NOT NULL, `sort` integer UNSIGNED NOT NULL CHECK (`sort` >= 0), `level` smallint UNSIGNED NOT NULL CHECK (`level` >= 0), `path` varchar(255) NOT NULL, `is_show` bool NOT NULL, `is_distribution` bool NOT NULL, `seo_title` varchar(200) NOT NULL, `seo_keywords` varchar(255) NOT NULL, `seo_description` varchar(500) NOT NULL);
CREATE TABLE `product` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `created_at` datetime(6) NOT NULL, `updated_at` datetime(6) NOT NULL, `is_active` bool NOT NULL, `title` varchar(200) NOT NULL, `sub_title` varchar(255) NOT NULL, `cover` varchar(500) NOT NULL, `detail` longtext NOT NULL, `sale_status` varchar(20) NOT NULL, `price` numeric(12, 2) NOT NULL, `market_price` numeric(12, 2) NOT NULL, `total_stock` integer NOT NULL, `is_distribution` bool NOT NULL, `commission_type` varchar(20) NOT NULL, `commission_rate_lv1` numeric(5, 2) NOT NULL, `commission_rate_lv2` numeric(5, 2) NOT NULL);
CREATE TABLE `product_category_relation` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `product_id` bigint NOT NULL, `category_id` bigint NOT NULL, `is_main` bool NOT NULL, CONSTRAINT `uk_product_category` UNIQUE (`product_id`, `category_id`));
CREATE TABLE `spec_template` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `created_at` datetime(6) NOT NULL, `updated_at` datetime(6) NOT NULL, `name` varchar(100) NOT NULL, `spec_names` json NOT NULL);
CREATE TABLE `product_sku` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `created_at` datetime(6) NOT NULL, `updated_at` datetime(6) NOT NULL, `is_active` bool NOT NULL, `product_id` bigint NOT NULL, `sku_code` varchar(64) NOT NULL UNIQUE, `specs` json NOT NULL, `price` numeric(12, 2) NOT NULL, `market_price` numeric(12, 2) NOT NULL, `stock` integer NOT NULL, `locked_stock` integer NOT NULL, `warning_stock` integer NOT NULL, `image` varchar(500) NOT NULL);
CREATE TABLE `stock_log` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `created_at` datetime(6) NOT NULL, `updated_at` datetime(6) NOT NULL, `sku_id` bigint NOT NULL, `change_type` varchar(20) NOT NULL, `quantity` integer NOT NULL, `before_stock` integer NOT NULL, `after_stock` integer NOT NULL, `remark` varchar(255) NOT NULL);
CREATE TABLE `payment_record` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `created_at` datetime(6) NOT NULL, `updated_at` datetime(6) NOT NULL, `order_id` bigint NOT NULL, `payment_no` varchar(128) NOT NULL UNIQUE, `channel` varchar(20) NOT NULL, `amount` numeric(12, 2) NOT NULL, `status` varchar(20) NOT NULL, `gateway_trade_no` varchar(128) NOT NULL, `paid_at` datetime(6) NULL, `raw_payload` json NOT NULL);
CREATE TABLE `cart_item` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `created_at` datetime(6) NOT NULL, `updated_at` datetime(6) NOT NULL, `user_id` bigint NOT NULL, `sku_id` bigint NOT NULL, `quantity` integer UNSIGNED NOT NULL CHECK (`quantity` >= 0), `selected` bool NOT NULL, CONSTRAINT `uk_cart_user_sku` UNIQUE (`user_id`, `sku_id`));
CREATE TABLE `order` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `created_at` datetime(6) NOT NULL, `updated_at` datetime(6) NOT NULL, `order_no` varchar(64) NOT NULL UNIQUE, `user_id` bigint NOT NULL, `status` varchar(32) NOT NULL, `total_amount` numeric(12, 2) NOT NULL, `discount_amount` numeric(12, 2) NOT NULL, `pay_amount` numeric(12, 2) NOT NULL, `paid_at` datetime(6) NULL, `completed_at` datetime(6) NULL, `remark` varchar(255) NOT NULL, `receiver_name` varchar(50) NOT NULL, `receiver_mobile` varchar(20) NOT NULL, `province` varchar(50) NOT NULL, `city` varchar(50) NOT NULL, `district` varchar(50) NOT NULL, `address_detail` varchar(255) NOT NULL, `postal_code` varchar(20) NOT NULL);
CREATE TABLE `order_item` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `created_at` datetime(6) NOT NULL, `updated_at` datetime(6) NOT NULL, `order_id` bigint NOT NULL, `product_id` bigint NOT NULL, `sku_id` bigint NOT NULL, `product_title` varchar(200) NOT NULL, `sku_code` varchar(64) NOT NULL, `spec_json` json NOT NULL, `price` numeric(12, 2) NOT NULL, `quantity` integer UNSIGNED NOT NULL CHECK (`quantity` >= 0), `total_amount` numeric(12, 2) NOT NULL);
CREATE TABLE `order_address` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `created_at` datetime(6) NOT NULL, `updated_at` datetime(6) NOT NULL, `user_id` bigint NOT NULL, `receiver_name` varchar(50) NOT NULL, `receiver_mobile` varchar(20) NOT NULL, `province` varchar(50) NOT NULL, `city` varchar(50) NOT NULL, `district` varchar(50) NOT NULL, `address_detail` varchar(255) NOT NULL, `postal_code` varchar(20) NOT NULL, `is_default` bool NOT NULL);
CREATE TABLE `invoice_application` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `created_at` datetime(6) NOT NULL, `updated_at` datetime(6) NOT NULL, `order_id` bigint NOT NULL UNIQUE, `user_id` bigint NOT NULL, `invoice_type` varchar(20) NOT NULL, `title` varchar(100) NOT NULL, `tax_no` varchar(50) NOT NULL, `email` varchar(254) NOT NULL, `content` varchar(100) NOT NULL, `amount` numeric(12, 2) NOT NULL, `status` varchar(20) NOT NULL, `audit_remark` varchar(255) NOT NULL, `issued_at` datetime(6) NULL);
CREATE TABLE `logistics_record` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `created_at` datetime(6) NOT NULL, `updated_at` datetime(6) NOT NULL, `order_id` bigint NOT NULL UNIQUE, `company` varchar(100) NOT NULL, `tracking_no` varchar(100) NOT NULL, `shipped_at` datetime(6) NULL, `delivered_at` datetime(6) NULL, `traces` json NOT NULL, `raw_payload` json NOT NULL);
CREATE TABLE `refund_application` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `created_at` datetime(6) NOT NULL, `updated_at` datetime(6) NOT NULL, `refund_no` varchar(64) NOT NULL UNIQUE, `order_id` bigint NOT NULL, `user_id` bigint NOT NULL, `refund_type` varchar(30) NOT NULL, `reason` varchar(255) NOT NULL, `amount` numeric(12, 2) NOT NULL, `status` varchar(20) NOT NULL, `audit_remark` varchar(255) NOT NULL, `gateway_refund_no` varchar(128) NOT NULL, `requested_at` datetime(6) NULL, `refunded_at` datetime(6) NULL, `raw_payload` json NOT NULL);
CREATE TABLE `user_team_stat` (`created_at` datetime(6) NOT NULL, `updated_at` datetime(6) NOT NULL, `user_id` bigint NOT NULL PRIMARY KEY, `team_count` integer UNSIGNED NOT NULL CHECK (`team_count` >= 0), `direct_count` integer UNSIGNED NOT NULL CHECK (`direct_count` >= 0), `indirect_count` integer UNSIGNED NOT NULL CHECK (`indirect_count` >= 0), `team_order_amount` numeric(12, 2) NOT NULL, `team_commission` numeric(12, 2) NOT NULL);
CREATE TABLE `distribution_config` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `created_at` datetime(6) NOT NULL, `updated_at` datetime(6) NOT NULL, `name` varchar(100) NOT NULL, `default_rate_lv1` numeric(5, 2) NOT NULL, `default_rate_lv2` numeric(5, 2) NOT NULL, `settlement_delay_days` integer UNSIGNED NOT NULL CHECK (`settlement_delay_days` >= 0), `enabled` bool NOT NULL);
CREATE TABLE `commission_record` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `created_at` datetime(6) NOT NULL, `updated_at` datetime(6) NOT NULL, `user_id` bigint NOT NULL, `order_id` bigint NOT NULL, `source_user_id` bigint NOT NULL, `level` smallint UNSIGNED NOT NULL CHECK (`level` >= 0), `rate` numeric(5, 2) NOT NULL, `amount` numeric(12, 2) NOT NULL, `status` varchar(20) NOT NULL, `settle_at` datetime(6) NULL);
CREATE TABLE `activity_purchase_record` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `created_at` datetime(6) NOT NULL, `updated_at` datetime(6) NOT NULL, `user_id` bigint NOT NULL, `activity_type` varchar(20) NOT NULL, `activity_id` bigint UNSIGNED NOT NULL CHECK (`activity_id` >= 0), `order_id` bigint NOT NULL, `quantity` integer UNSIGNED NOT NULL CHECK (`quantity` >= 0));
CREATE TABLE `coupon_template` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `created_at` datetime(6) NOT NULL, `updated_at` datetime(6) NOT NULL, `name` varchar(100) NOT NULL, `coupon_type` varchar(32) NOT NULL, `threshold_amount` numeric(12, 2) NOT NULL, `discount_amount` numeric(12, 2) NOT NULL, `discount_rate` numeric(4, 2) NOT NULL, `total_quantity` integer UNSIGNED NOT NULL CHECK (`total_quantity` >= 0), `per_user_limit` integer UNSIGNED NOT NULL CHECK (`per_user_limit` >= 0), `started_at` datetime(6) NOT NULL, `ended_at` datetime(6) NOT NULL, `valid_days` integer UNSIGNED NOT NULL CHECK (`valid_days` >= 0));
CREATE TABLE `coupon_template_products` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `coupontemplate_id` bigint NOT NULL, `product_id` bigint NOT NULL);
CREATE TABLE `coupon_template_categories` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `coupontemplate_id` bigint NOT NULL, `productcategory_id` bigint NOT NULL);
CREATE TABLE `user_coupon` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `created_at` datetime(6) NOT NULL, `updated_at` datetime(6) NOT NULL, `user_id` bigint NOT NULL, `template_id` bigint NOT NULL, `status` varchar(20) NOT NULL, `valid_from` datetime(6) NOT NULL, `valid_to` datetime(6) NOT NULL, `used_at` datetime(6) NULL);
CREATE TABLE `group_buying_activity` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `created_at` datetime(6) NOT NULL, `updated_at` datetime(6) NOT NULL, `name` varchar(100) NOT NULL, `sku_id` bigint NOT NULL, `group_price` numeric(12, 2) NOT NULL, `min_members` integer UNSIGNED NOT NULL CHECK (`min_members` >= 0), `stock` integer UNSIGNED NOT NULL CHECK (`stock` >= 0), `started_at` datetime(6) NOT NULL, `ended_at` datetime(6) NOT NULL, `enabled` bool NOT NULL);
CREATE TABLE `seckill_activity` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `created_at` datetime(6) NOT NULL, `updated_at` datetime(6) NOT NULL, `name` varchar(100) NOT NULL, `sku_id` bigint NOT NULL, `seckill_price` numeric(12, 2) NOT NULL, `stock` integer UNSIGNED NOT NULL CHECK (`stock` >= 0), `per_user_limit` integer UNSIGNED NOT NULL CHECK (`per_user_limit` >= 0), `started_at` datetime(6) NOT NULL, `ended_at` datetime(6) NOT NULL, `enabled` bool NOT NULL);
CREATE TABLE `city_agent_application` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `created_at` datetime(6) NOT NULL, `updated_at` datetime(6) NOT NULL, `user_id` bigint NOT NULL, `level` smallint UNSIGNED NOT NULL CHECK (`level` >= 0), `region_code` varchar(20) NOT NULL, `region_name` varchar(100) NOT NULL, `contact_name` varchar(50) NOT NULL, `contact_phone` varchar(20) NOT NULL, `status` varchar(20) NOT NULL, `audit_remark` varchar(255) NOT NULL);
CREATE TABLE `city_agent` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `created_at` datetime(6) NOT NULL, `updated_at` datetime(6) NOT NULL, `user_id` bigint NOT NULL, `level` smallint UNSIGNED NOT NULL CHECK (`level` >= 0), `region_code` varchar(20) NOT NULL, `region_name` varchar(100) NOT NULL, `commission_rate` numeric(5, 2) NOT NULL, `enabled` bool NOT NULL, CONSTRAINT `uk_agent_level_region` UNIQUE (`level`, `region_code`));
CREATE TABLE `reward_pool` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `created_at` datetime(6) NOT NULL, `updated_at` datetime(6) NOT NULL, `name` varchar(100) NOT NULL, `pool_type` varchar(32) NOT NULL, `amount` numeric(12, 2) NOT NULL, `min_performance` numeric(12, 2) NOT NULL, `max_user_ratio` numeric(5, 2) NOT NULL, `enabled` bool NOT NULL);
CREATE TABLE `reward_pool_rule` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `created_at` datetime(6) NOT NULL, `updated_at` datetime(6) NOT NULL, `pool_id` bigint NOT NULL, `team_amount_weight` numeric(5, 2) NOT NULL, `team_count_weight` numeric(5, 2) NOT NULL, `personal_amount_weight` numeric(5, 2) NOT NULL, `rank_config` json NOT NULL);
CREATE TABLE `reward_distribution_record` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `created_at` datetime(6) NOT NULL, `updated_at` datetime(6) NOT NULL, `pool_id` bigint NOT NULL, `user_id` bigint NOT NULL, `score` numeric(18, 4) NOT NULL, `amount` numeric(12, 2) NOT NULL, `status` varchar(20) NOT NULL, `distributed_at` datetime(6) NULL);
CREATE TABLE `wallet` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `created_at` datetime(6) NOT NULL, `updated_at` datetime(6) NOT NULL, `user_id` bigint NOT NULL UNIQUE, `balance` numeric(12, 2) NOT NULL, `frozen_balance` numeric(12, 2) NOT NULL, `total_income` numeric(12, 2) NOT NULL, `total_withdraw` numeric(12, 2) NOT NULL);
CREATE TABLE `fund_flow` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `created_at` datetime(6) NOT NULL, `updated_at` datetime(6) NOT NULL, `user_id` bigint NOT NULL, `wallet_id` bigint NOT NULL, `flow_type` varchar(20) NOT NULL, `amount` numeric(12, 2) NOT NULL, `balance_after` numeric(12, 2) NOT NULL, `biz_type` varchar(50) NOT NULL, `biz_id` varchar(64) NOT NULL, `remark` varchar(255) NOT NULL);
CREATE TABLE `withdraw_application` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `created_at` datetime(6) NOT NULL, `updated_at` datetime(6) NOT NULL, `user_id` bigint NOT NULL, `amount` numeric(12, 2) NOT NULL, `channel` varchar(20) NOT NULL, `account_name` varchar(100) NOT NULL, `account_no` varchar(100) NOT NULL, `status` varchar(20) NOT NULL, `audit_remark` varchar(255) NOT NULL, `audited_at` datetime(6) NULL, `payout_no` varchar(128) NOT NULL, `paid_at` datetime(6) NULL, `raw_payload` json NOT NULL);
ALTER TABLE `django_admin_log` ADD CONSTRAINT `django_admin_log_user_id_c564eba6_fk_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);
ALTER TABLE `django_admin_log` ADD CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);
ALTER TABLE `auth_permission` ADD CONSTRAINT `auth_permission_content_type_id_codename_01ab375a_uniq` UNIQUE (`content_type_id`, `codename`);
ALTER TABLE `auth_permission` ADD CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);
ALTER TABLE `auth_group_permissions` ADD CONSTRAINT `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` UNIQUE (`group_id`, `permission_id`);
ALTER TABLE `auth_group_permissions` ADD CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);
ALTER TABLE `auth_group_permissions` ADD CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`);
ALTER TABLE `django_content_type` ADD CONSTRAINT `django_content_type_app_label_model_76bd3d3b_uniq` UNIQUE (`app_label`, `model`);
CREATE INDEX `django_session_expire_date_a5c62663` ON `django_session` (`expire_date`);
ALTER TABLE `user` ADD CONSTRAINT `user_parent_id_5a52f839_fk_user_id` FOREIGN KEY (`parent_id`) REFERENCES `user` (`id`);
ALTER TABLE `user` ADD CONSTRAINT `user_level_id_ba920527_fk_member_level_id` FOREIGN KEY (`level_id`) REFERENCES `member_level` (`id`);
CREATE INDEX `idx_user_parent` ON `user` (`parent_id`);
CREATE INDEX `idx_user_path` ON `user` (`path`);
CREATE INDEX `idx_user_openid` ON `user` (`openid`);
CREATE INDEX `idx_user_mobile` ON `user` (`mobile`);
ALTER TABLE `user_groups` ADD CONSTRAINT `user_groups_user_id_group_id_40beef00_uniq` UNIQUE (`user_id`, `group_id`);
ALTER TABLE `user_groups` ADD CONSTRAINT `user_groups_user_id_abaea130_fk_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);
ALTER TABLE `user_groups` ADD CONSTRAINT `user_groups_group_id_b76f8aba_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);
ALTER TABLE `user_user_permissions` ADD CONSTRAINT `user_user_permissions_user_id_permission_id_7dc6e2e0_uniq` UNIQUE (`user_id`, `permission_id`);
ALTER TABLE `user_user_permissions` ADD CONSTRAINT `user_user_permissions_user_id_ed4a47ea_fk_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);
ALTER TABLE `user_user_permissions` ADD CONSTRAINT `user_user_permission_permission_id_9deb68a3_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`);
ALTER TABLE `product_category` ADD CONSTRAINT `product_category_parent_id_f6860923_fk_product_category_id` FOREIGN KEY (`parent_id`) REFERENCES `product_category` (`id`);
CREATE INDEX `idx_category_parent` ON `product_category` (`parent_id`);
CREATE INDEX `idx_category_path` ON `product_category` (`path`);
CREATE INDEX `idx_category_show_sort` ON `product_category` (`is_show`, `sort`);
CREATE INDEX `idx_product_sale_status` ON `product` (`sale_status`);
CREATE INDEX `idx_product_distribution` ON `product` (`is_distribution`);
ALTER TABLE `product_category_relation` ADD CONSTRAINT `product_category_relation_product_id_5f2cf581_fk_product_id` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`);
ALTER TABLE `product_category_relation` ADD CONSTRAINT `product_category_rel_category_id_4d2c009b_fk_product_c` FOREIGN KEY (`category_id`) REFERENCES `product_category` (`id`);
ALTER TABLE `product_sku` ADD CONSTRAINT `product_sku_product_id_ecb13de3_fk_product_id` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`);
CREATE INDEX `idx_sku_product` ON `product_sku` (`product_id`);
CREATE INDEX `idx_sku_code` ON `product_sku` (`sku_code`);
ALTER TABLE `stock_log` ADD CONSTRAINT `stock_log_sku_id_0e7bd227_fk_product_sku_id` FOREIGN KEY (`sku_id`) REFERENCES `product_sku` (`id`);
ALTER TABLE `payment_record` ADD CONSTRAINT `payment_record_order_id_9a3b944e_fk_order_id` FOREIGN KEY (`order_id`) REFERENCES `order` (`id`);
CREATE INDEX `idx_payment_order_status` ON `payment_record` (`order_id`, `status`);
CREATE INDEX `idx_payment_no` ON `payment_record` (`payment_no`);
ALTER TABLE `cart_item` ADD CONSTRAINT `cart_item_user_id_70f45bd5_fk_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);
ALTER TABLE `cart_item` ADD CONSTRAINT `cart_item_sku_id_f859ee1f_fk_product_sku_id` FOREIGN KEY (`sku_id`) REFERENCES `product_sku` (`id`);
ALTER TABLE `order` ADD CONSTRAINT `order_user_id_e323497c_fk_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);
CREATE INDEX `idx_order_no` ON `order` (`order_no`);
CREATE INDEX `idx_order_user_status` ON `order` (`user_id`, `status`);
ALTER TABLE `order_item` ADD CONSTRAINT `order_item_order_id_0ca9e92e_fk_order_id` FOREIGN KEY (`order_id`) REFERENCES `order` (`id`);
ALTER TABLE `order_item` ADD CONSTRAINT `order_item_product_id_62a1cc4c_fk_product_id` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`);
ALTER TABLE `order_item` ADD CONSTRAINT `order_item_sku_id_fc0567f5_fk_product_sku_id` FOREIGN KEY (`sku_id`) REFERENCES `product_sku` (`id`);
ALTER TABLE `order_address` ADD CONSTRAINT `order_address_user_id_b58eb949_fk_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);
CREATE INDEX `idx_addr_user_default` ON `order_address` (`user_id`, `is_default`);
ALTER TABLE `invoice_application` ADD CONSTRAINT `invoice_application_order_id_7bc5b471_fk_order_id` FOREIGN KEY (`order_id`) REFERENCES `order` (`id`);
ALTER TABLE `invoice_application` ADD CONSTRAINT `invoice_application_user_id_2d2b72b2_fk_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);
CREATE INDEX `idx_invoice_user_status` ON `invoice_application` (`user_id`, `status`);
ALTER TABLE `logistics_record` ADD CONSTRAINT `logistics_record_order_id_7ec94446_fk_order_id` FOREIGN KEY (`order_id`) REFERENCES `order` (`id`);
CREATE INDEX `idx_logistics_tracking` ON `logistics_record` (`tracking_no`);
ALTER TABLE `refund_application` ADD CONSTRAINT `refund_application_order_id_de27a9d6_fk_order_id` FOREIGN KEY (`order_id`) REFERENCES `order` (`id`);
ALTER TABLE `refund_application` ADD CONSTRAINT `refund_application_user_id_f2256667_fk_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);
CREATE INDEX `idx_refund_order_status` ON `refund_application` (`order_id`, `status`);
CREATE INDEX `idx_refund_user_status` ON `refund_application` (`user_id`, `status`);
CREATE INDEX `idx_refund_no` ON `refund_application` (`refund_no`);
ALTER TABLE `user_team_stat` ADD CONSTRAINT `user_team_stat_user_id_40cda547_fk_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);
ALTER TABLE `commission_record` ADD CONSTRAINT `commission_record_user_id_a79e6d34_fk_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);
ALTER TABLE `commission_record` ADD CONSTRAINT `commission_record_order_id_fbbf97f9_fk_order_id` FOREIGN KEY (`order_id`) REFERENCES `order` (`id`);
ALTER TABLE `commission_record` ADD CONSTRAINT `commission_record_source_user_id_def83ffe_fk_user_id` FOREIGN KEY (`source_user_id`) REFERENCES `user` (`id`);
CREATE INDEX `idx_commission_user_status` ON `commission_record` (`user_id`, `status`);
CREATE INDEX `idx_commission_order` ON `commission_record` (`order_id`);
ALTER TABLE `activity_purchase_record` ADD CONSTRAINT `activity_purchase_record_user_id_ca48a5b0_fk_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);
ALTER TABLE `activity_purchase_record` ADD CONSTRAINT `activity_purchase_record_order_id_aeae914d_fk_order_id` FOREIGN KEY (`order_id`) REFERENCES `order` (`id`);
CREATE INDEX `idx_activity_user` ON `activity_purchase_record` (`user_id`, `activity_type`, `activity_id`);
CREATE INDEX `idx_activity_lookup` ON `activity_purchase_record` (`activity_type`, `activity_id`);
ALTER TABLE `coupon_template_products` ADD CONSTRAINT `coupon_template_products_coupontemplate_id_produc_48b0cd3d_uniq` UNIQUE (`coupontemplate_id`, `product_id`);
ALTER TABLE `coupon_template_products` ADD CONSTRAINT `coupon_template_prod_coupontemplate_id_fe01ab2a_fk_coupon_te` FOREIGN KEY (`coupontemplate_id`) REFERENCES `coupon_template` (`id`);
ALTER TABLE `coupon_template_products` ADD CONSTRAINT `coupon_template_products_product_id_65863758_fk_product_id` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`);
ALTER TABLE `coupon_template_categories` ADD CONSTRAINT `coupon_template_categori_coupontemplate_id_produc_7fc3e31c_uniq` UNIQUE (`coupontemplate_id`, `productcategory_id`);
ALTER TABLE `coupon_template_categories` ADD CONSTRAINT `coupon_template_cate_coupontemplate_id_134f42c8_fk_coupon_te` FOREIGN KEY (`coupontemplate_id`) REFERENCES `coupon_template` (`id`);
ALTER TABLE `coupon_template_categories` ADD CONSTRAINT `coupon_template_cate_productcategory_id_73c181dd_fk_product_c` FOREIGN KEY (`productcategory_id`) REFERENCES `product_category` (`id`);
ALTER TABLE `user_coupon` ADD CONSTRAINT `user_coupon_user_id_3dcd074d_fk_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);
ALTER TABLE `user_coupon` ADD CONSTRAINT `user_coupon_template_id_157282fa_fk_coupon_template_id` FOREIGN KEY (`template_id`) REFERENCES `coupon_template` (`id`);
CREATE INDEX `idx_coupon_user_status` ON `user_coupon` (`user_id`, `status`);
ALTER TABLE `group_buying_activity` ADD CONSTRAINT `group_buying_activity_sku_id_4a37fffe_fk_product_sku_id` FOREIGN KEY (`sku_id`) REFERENCES `product_sku` (`id`);
ALTER TABLE `seckill_activity` ADD CONSTRAINT `seckill_activity_sku_id_778963c9_fk_product_sku_id` FOREIGN KEY (`sku_id`) REFERENCES `product_sku` (`id`);
ALTER TABLE `city_agent_application` ADD CONSTRAINT `city_agent_application_user_id_0091a871_fk_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);
ALTER TABLE `city_agent` ADD CONSTRAINT `city_agent_user_id_5ff378cf_fk_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);
ALTER TABLE `reward_pool_rule` ADD CONSTRAINT `reward_pool_rule_pool_id_4064b24d_fk_reward_pool_id` FOREIGN KEY (`pool_id`) REFERENCES `reward_pool` (`id`);
ALTER TABLE `reward_distribution_record` ADD CONSTRAINT `reward_distribution_record_pool_id_69d99719_fk_reward_pool_id` FOREIGN KEY (`pool_id`) REFERENCES `reward_pool` (`id`);
ALTER TABLE `reward_distribution_record` ADD CONSTRAINT `reward_distribution_record_user_id_e9cb6368_fk_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);
CREATE INDEX `idx_reward_pool_status` ON `reward_distribution_record` (`pool_id`, `status`);
CREATE INDEX `idx_reward_user_status` ON `reward_distribution_record` (`user_id`, `status`);
ALTER TABLE `wallet` ADD CONSTRAINT `wallet_user_id_03d82c01_fk_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);
ALTER TABLE `fund_flow` ADD CONSTRAINT `fund_flow_user_id_65f32d6b_fk_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);
ALTER TABLE `fund_flow` ADD CONSTRAINT `fund_flow_wallet_id_efed194d_fk_wallet_id` FOREIGN KEY (`wallet_id`) REFERENCES `wallet` (`id`);
CREATE INDEX `idx_fund_user_type` ON `fund_flow` (`user_id`, `flow_type`);
CREATE INDEX `idx_fund_biz` ON `fund_flow` (`biz_type`, `biz_id`);
ALTER TABLE `withdraw_application` ADD CONSTRAINT `withdraw_application_user_id_1fdbeee1_fk_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);
CREATE INDEX `idx_withdraw_user_status` ON `withdraw_application` (`user_id`, `status`);

-- ---------------------------------------------------------------------------
-- Mark Django migrations as applied.
-- ---------------------------------------------------------------------------
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES
  (1, 'contenttypes', '0001_initial', NOW(6)),
  (2, 'contenttypes', '0002_remove_content_type_name', NOW(6)),
  (3, 'auth', '0001_initial', NOW(6)),
  (4, 'auth', '0002_alter_permission_name_max_length', NOW(6)),
  (5, 'auth', '0003_alter_user_email_max_length', NOW(6)),
  (6, 'auth', '0004_alter_user_username_opts', NOW(6)),
  (7, 'auth', '0005_alter_user_last_login_null', NOW(6)),
  (8, 'auth', '0006_require_contenttypes_0002', NOW(6)),
  (9, 'auth', '0007_alter_validators_add_error_messages', NOW(6)),
  (10, 'auth', '0008_alter_user_username_max_length', NOW(6)),
  (11, 'auth', '0009_alter_user_last_name_max_length', NOW(6)),
  (12, 'auth', '0010_alter_group_name_max_length', NOW(6)),
  (13, 'auth', '0011_update_proxy_permissions', NOW(6)),
  (14, 'auth', '0012_alter_user_first_name_max_length', NOW(6)),
  (15, 'admin', '0001_initial', NOW(6)),
  (16, 'admin', '0002_logentry_remove_auto_add', NOW(6)),
  (17, 'admin', '0003_logentry_add_action_flag_choices', NOW(6)),
  (18, 'sessions', '0001_initial', NOW(6)),
  (19, 'users', '0001_initial', NOW(6)),
  (20, 'users', '0002_user_realname_remark_user_realname_status_and_more', NOW(6)),
  (21, 'agents', '0001_initial', NOW(6)),
  (22, 'agents', '0002_initial', NOW(6)),
  (23, 'catalog', '0001_initial', NOW(6)),
  (24, 'orders', '0001_initial', NOW(6)),
  (25, 'orders', '0002_initial', NOW(6)),
  (26, 'orders', '0003_paymentrecord', NOW(6)),
  (27, 'orders', '0004_order_address_detail_order_city_order_district_and_more', NOW(6)),
  (28, 'distribution', '0001_initial', NOW(6)),
  (29, 'distribution', '0002_initial', NOW(6)),
  (30, 'finance', '0001_initial', NOW(6)),
  (31, 'finance', '0002_withdrawapplication_channel_and_more', NOW(6)),
  (32, 'marketing', '0001_initial', NOW(6)),
  (33, 'marketing', '0002_initial', NOW(6)),
  (34, 'marketing', '0003_activitypurchaserecord', NOW(6)),
  (35, 'rewards', '0001_initial', NOW(6)),
  (36, 'rewards', '0002_initial', NOW(6));
ALTER TABLE `django_migrations` AUTO_INCREMENT = 1000;

-- ---------------------------------------------------------------------------
-- Seed Django content types and permissions.
-- ---------------------------------------------------------------------------
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES
  (1, 'admin', 'logentry'),
  (2, 'auth', 'group'),
  (3, 'auth', 'permission'),
  (4, 'contenttypes', 'contenttype'),
  (5, 'sessions', 'session'),
  (6, 'users', 'memberlevel'),
  (7, 'users', 'user'),
  (8, 'catalog', 'product'),
  (9, 'catalog', 'productcategory'),
  (10, 'catalog', 'productcategoryrelation'),
  (11, 'catalog', 'productsku'),
  (12, 'catalog', 'spectemplate'),
  (13, 'catalog', 'stocklog'),
  (14, 'orders', 'cartitem'),
  (15, 'orders', 'invoiceapplication'),
  (16, 'orders', 'logisticsrecord'),
  (17, 'orders', 'order'),
  (18, 'orders', 'orderaddress'),
  (19, 'orders', 'orderitem'),
  (20, 'orders', 'paymentrecord'),
  (21, 'orders', 'refundapplication'),
  (22, 'distribution', 'commissionrecord'),
  (23, 'distribution', 'distributionconfigmodel'),
  (24, 'distribution', 'userteamstat'),
  (25, 'marketing', 'activitypurchaserecord'),
  (26, 'marketing', 'coupontemplate'),
  (27, 'marketing', 'groupbuyingactivity'),
  (28, 'marketing', 'seckillactivity'),
  (29, 'marketing', 'usercoupon'),
  (30, 'agents', 'cityagent'),
  (31, 'agents', 'cityagentapplication'),
  (32, 'rewards', 'rewarddistributionrecord'),
  (33, 'rewards', 'rewardpool'),
  (34, 'rewards', 'rewardpoolrule'),
  (35, 'finance', 'fundflow'),
  (36, 'finance', 'wallet'),
  (37, 'finance', 'withdrawapplication');
ALTER TABLE `django_content_type` AUTO_INCREMENT = 1000;

INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES
  (1, 'Can add log entry', 1, 'add_logentry'),
  (2, 'Can change log entry', 1, 'change_logentry'),
  (3, 'Can delete log entry', 1, 'delete_logentry'),
  (4, 'Can view log entry', 1, 'view_logentry'),
  (5, 'Can add group', 2, 'add_group'),
  (6, 'Can change group', 2, 'change_group'),
  (7, 'Can delete group', 2, 'delete_group'),
  (8, 'Can view group', 2, 'view_group'),
  (9, 'Can add permission', 3, 'add_permission'),
  (10, 'Can change permission', 3, 'change_permission'),
  (11, 'Can delete permission', 3, 'delete_permission'),
  (12, 'Can view permission', 3, 'view_permission'),
  (13, 'Can add content type', 4, 'add_contenttype'),
  (14, 'Can change content type', 4, 'change_contenttype'),
  (15, 'Can delete content type', 4, 'delete_contenttype'),
  (16, 'Can view content type', 4, 'view_contenttype'),
  (17, 'Can add session', 5, 'add_session'),
  (18, 'Can change session', 5, 'change_session'),
  (19, 'Can delete session', 5, 'delete_session'),
  (20, 'Can view session', 5, 'view_session'),
  (21, 'Can add 会员等级', 6, 'add_memberlevel'),
  (22, 'Can change 会员等级', 6, 'change_memberlevel'),
  (23, 'Can delete 会员等级', 6, 'delete_memberlevel'),
  (24, 'Can view 会员等级', 6, 'view_memberlevel'),
  (25, 'Can add 用户', 7, 'add_user'),
  (26, 'Can change 用户', 7, 'change_user'),
  (27, 'Can delete 用户', 7, 'delete_user'),
  (28, 'Can view 用户', 7, 'view_user'),
  (29, 'Can add 商品', 8, 'add_product'),
  (30, 'Can change 商品', 8, 'change_product'),
  (31, 'Can delete 商品', 8, 'delete_product'),
  (32, 'Can view 商品', 8, 'view_product'),
  (33, 'Can add 商品分类', 9, 'add_productcategory'),
  (34, 'Can change 商品分类', 9, 'change_productcategory'),
  (35, 'Can delete 商品分类', 9, 'delete_productcategory'),
  (36, 'Can view 商品分类', 9, 'view_productcategory'),
  (37, 'Can add 商品分类关联', 10, 'add_productcategoryrelation'),
  (38, 'Can change 商品分类关联', 10, 'change_productcategoryrelation'),
  (39, 'Can delete 商品分类关联', 10, 'delete_productcategoryrelation'),
  (40, 'Can view 商品分类关联', 10, 'view_productcategoryrelation'),
  (41, 'Can add 商品 SKU', 11, 'add_productsku'),
  (42, 'Can change 商品 SKU', 11, 'change_productsku'),
  (43, 'Can delete 商品 SKU', 11, 'delete_productsku'),
  (44, 'Can view 商品 SKU', 11, 'view_productsku'),
  (45, 'Can add 规格模板', 12, 'add_spectemplate'),
  (46, 'Can change 规格模板', 12, 'change_spectemplate'),
  (47, 'Can delete 规格模板', 12, 'delete_spectemplate'),
  (48, 'Can view 规格模板', 12, 'view_spectemplate'),
  (49, 'Can add 库存变更日志', 13, 'add_stocklog'),
  (50, 'Can change 库存变更日志', 13, 'change_stocklog'),
  (51, 'Can delete 库存变更日志', 13, 'delete_stocklog'),
  (52, 'Can view 库存变更日志', 13, 'view_stocklog'),
  (53, 'Can add 购物车', 14, 'add_cartitem'),
  (54, 'Can change 购物车', 14, 'change_cartitem'),
  (55, 'Can delete 购物车', 14, 'delete_cartitem'),
  (56, 'Can view 购物车', 14, 'view_cartitem'),
  (57, 'Can add Invoice Application', 15, 'add_invoiceapplication'),
  (58, 'Can change Invoice Application', 15, 'change_invoiceapplication'),
  (59, 'Can delete Invoice Application', 15, 'delete_invoiceapplication'),
  (60, 'Can view Invoice Application', 15, 'view_invoiceapplication'),
  (61, 'Can add Logistics Record', 16, 'add_logisticsrecord'),
  (62, 'Can change Logistics Record', 16, 'change_logisticsrecord'),
  (63, 'Can delete Logistics Record', 16, 'delete_logisticsrecord'),
  (64, 'Can view Logistics Record', 16, 'view_logisticsrecord'),
  (65, 'Can add 订单', 17, 'add_order'),
  (66, 'Can change 订单', 17, 'change_order'),
  (67, 'Can delete 订单', 17, 'delete_order'),
  (68, 'Can view 订单', 17, 'view_order'),
  (69, 'Can add Order Address', 18, 'add_orderaddress'),
  (70, 'Can change Order Address', 18, 'change_orderaddress'),
  (71, 'Can delete Order Address', 18, 'delete_orderaddress'),
  (72, 'Can view Order Address', 18, 'view_orderaddress'),
  (73, 'Can add 订单商品', 19, 'add_orderitem'),
  (74, 'Can change 订单商品', 19, 'change_orderitem'),
  (75, 'Can delete 订单商品', 19, 'delete_orderitem'),
  (76, 'Can view 订单商品', 19, 'view_orderitem'),
  (77, 'Can add Payment Record', 20, 'add_paymentrecord'),
  (78, 'Can change Payment Record', 20, 'change_paymentrecord'),
  (79, 'Can delete Payment Record', 20, 'delete_paymentrecord'),
  (80, 'Can view Payment Record', 20, 'view_paymentrecord'),
  (81, 'Can add Refund Application', 21, 'add_refundapplication'),
  (82, 'Can change Refund Application', 21, 'change_refundapplication'),
  (83, 'Can delete Refund Application', 21, 'delete_refundapplication'),
  (84, 'Can view Refund Application', 21, 'view_refundapplication'),
  (85, 'Can add 佣金明细', 22, 'add_commissionrecord'),
  (86, 'Can change 佣金明细', 22, 'change_commissionrecord'),
  (87, 'Can delete 佣金明细', 22, 'delete_commissionrecord'),
  (88, 'Can view 佣金明细', 22, 'view_commissionrecord'),
  (89, 'Can add 分销配置', 23, 'add_distributionconfigmodel'),
  (90, 'Can change 分销配置', 23, 'change_distributionconfigmodel'),
  (91, 'Can delete 分销配置', 23, 'delete_distributionconfigmodel'),
  (92, 'Can view 分销配置', 23, 'view_distributionconfigmodel'),
  (93, 'Can add 团队统计', 24, 'add_userteamstat'),
  (94, 'Can change 团队统计', 24, 'change_userteamstat'),
  (95, 'Can delete 团队统计', 24, 'delete_userteamstat'),
  (96, 'Can view 团队统计', 24, 'view_userteamstat'),
  (97, 'Can add Activity Purchase Record', 25, 'add_activitypurchaserecord'),
  (98, 'Can change Activity Purchase Record', 25, 'change_activitypurchaserecord'),
  (99, 'Can delete Activity Purchase Record', 25, 'delete_activitypurchaserecord'),
  (100, 'Can view Activity Purchase Record', 25, 'view_activitypurchaserecord'),
  (101, 'Can add 优惠券模板', 26, 'add_coupontemplate'),
  (102, 'Can change 优惠券模板', 26, 'change_coupontemplate'),
  (103, 'Can delete 优惠券模板', 26, 'delete_coupontemplate'),
  (104, 'Can view 优惠券模板', 26, 'view_coupontemplate'),
  (105, 'Can add 团购活动', 27, 'add_groupbuyingactivity'),
  (106, 'Can change 团购活动', 27, 'change_groupbuyingactivity'),
  (107, 'Can delete 团购活动', 27, 'delete_groupbuyingactivity'),
  (108, 'Can view 团购活动', 27, 'view_groupbuyingactivity'),
  (109, 'Can add 秒杀活动', 28, 'add_seckillactivity'),
  (110, 'Can change 秒杀活动', 28, 'change_seckillactivity'),
  (111, 'Can delete 秒杀活动', 28, 'delete_seckillactivity'),
  (112, 'Can view 秒杀活动', 28, 'view_seckillactivity'),
  (113, 'Can add 用户优惠券', 29, 'add_usercoupon'),
  (114, 'Can change 用户优惠券', 29, 'change_usercoupon'),
  (115, 'Can delete 用户优惠券', 29, 'delete_usercoupon'),
  (116, 'Can view 用户优惠券', 29, 'view_usercoupon'),
  (117, 'Can add 城市代理', 30, 'add_cityagent'),
  (118, 'Can change 城市代理', 30, 'change_cityagent'),
  (119, 'Can delete 城市代理', 30, 'delete_cityagent'),
  (120, 'Can view 城市代理', 30, 'view_cityagent'),
  (121, 'Can add 代理申请', 31, 'add_cityagentapplication'),
  (122, 'Can change 代理申请', 31, 'change_cityagentapplication'),
  (123, 'Can delete 代理申请', 31, 'delete_cityagentapplication'),
  (124, 'Can view 代理申请', 31, 'view_cityagentapplication'),
  (125, 'Can add 奖金池分配记录', 32, 'add_rewarddistributionrecord'),
  (126, 'Can change 奖金池分配记录', 32, 'change_rewarddistributionrecord'),
  (127, 'Can delete 奖金池分配记录', 32, 'delete_rewarddistributionrecord'),
  (128, 'Can view 奖金池分配记录', 32, 'view_rewarddistributionrecord'),
  (129, 'Can add 奖金池', 33, 'add_rewardpool'),
  (130, 'Can change 奖金池', 33, 'change_rewardpool'),
  (131, 'Can delete 奖金池', 33, 'delete_rewardpool'),
  (132, 'Can view 奖金池', 33, 'view_rewardpool'),
  (133, 'Can add 奖金池规则', 34, 'add_rewardpoolrule'),
  (134, 'Can change 奖金池规则', 34, 'change_rewardpoolrule'),
  (135, 'Can delete 奖金池规则', 34, 'delete_rewardpoolrule'),
  (136, 'Can view 奖金池规则', 34, 'view_rewardpoolrule'),
  (137, 'Can add Fund Flow', 35, 'add_fundflow'),
  (138, 'Can change Fund Flow', 35, 'change_fundflow'),
  (139, 'Can delete Fund Flow', 35, 'delete_fundflow'),
  (140, 'Can view Fund Flow', 35, 'view_fundflow'),
  (141, 'Can add Wallet', 36, 'add_wallet'),
  (142, 'Can change Wallet', 36, 'change_wallet'),
  (143, 'Can delete Wallet', 36, 'delete_wallet'),
  (144, 'Can view Wallet', 36, 'view_wallet'),
  (145, 'Can add Withdraw Application', 37, 'add_withdrawapplication'),
  (146, 'Can change Withdraw Application', 37, 'change_withdrawapplication'),
  (147, 'Can delete Withdraw Application', 37, 'delete_withdrawapplication'),
  (148, 'Can view Withdraw Application', 37, 'view_withdrawapplication');
ALTER TABLE `auth_permission` AUTO_INCREMENT = 1000;


-- ---------------------------------------------------------------------------
-- Seed baseline mall data.
-- ---------------------------------------------------------------------------

INSERT INTO `member_level`
  (`id`, `name`, `upgrade_amount`, `team_upgrade_amount`, `commission_rate_lv1`, `commission_rate_lv2`, `discount`, `sort`, `created_at`, `updated_at`)
VALUES
  (1, '普通用户', 0.00, 0.00, 0.00, 0.00, 1.00, 10, NOW(6), NOW(6)),
  (2, '青铜会员', 500.00, 0.00, 0.00, 0.00, 0.95, 20, NOW(6), NOW(6)),
  (3, '白银会员', 2000.00, 0.00, 10.00, 5.00, 0.90, 30, NOW(6), NOW(6)),
  (4, '黄金会员', 2000.00, 10000.00, 15.00, 8.00, 0.85, 40, NOW(6), NOW(6)),
  (5, '钻石会员', 2000.00, 50000.00, 20.00, 10.00, 0.80, 50, NOW(6), NOW(6));

INSERT INTO `distribution_config`
  (`id`, `name`, `default_rate_lv1`, `default_rate_lv2`, `settlement_delay_days`, `enabled`, `created_at`, `updated_at`)
VALUES
  (1, '平台默认配置', 10.00, 5.00, 7, 1, NOW(6), NOW(6));

INSERT INTO `product_category`
  (`id`, `parent_id`, `name`, `icon`, `banner`, `sort`, `level`, `path`, `is_show`, `is_distribution`, `seo_title`, `seo_keywords`, `seo_description`, `is_active`, `created_at`, `updated_at`)
VALUES
  (1, NULL, '服饰鞋包', '', '', 50, 1, '', 1, 1, '', '', '', 1, NOW(6), NOW(6)),
  (2, 1, '女装', '', '', 10, 2, ',1,', 1, 1, '', '', '', 1, NOW(6), NOW(6)),
  (3, 2, 'T恤', '', '', 10, 3, ',1,2,', 1, 1, '', '', '', 1, NOW(6), NOW(6)),
  (4, 2, '连衣裙', '', '', 20, 3, ',1,2,', 1, 1, '', '', '', 1, NOW(6), NOW(6)),
  (5, 2, '牛仔裤', '', '', 30, 3, ',1,2,', 1, 1, '', '', '', 1, NOW(6), NOW(6)),
  (6, 1, '男装', '', '', 20, 2, ',1,', 1, 1, '', '', '', 1, NOW(6), NOW(6)),
  (7, 1, '鞋靴', '', '', 30, 2, ',1,', 1, 1, '', '', '', 1, NOW(6), NOW(6)),
  (8, NULL, '美妆个护', '', '', 40, 1, '', 1, 1, '', '', '', 1, NOW(6), NOW(6)),
  (9, 8, '护肤', '', '', 10, 2, ',8,', 1, 1, '', '', '', 1, NOW(6), NOW(6)),
  (10, 8, '彩妆', '', '', 20, 2, ',8,', 1, 1, '', '', '', 1, NOW(6), NOW(6)),
  (11, 8, '洗护', '', '', 30, 2, ',8,', 1, 1, '', '', '', 1, NOW(6), NOW(6)),
  (12, NULL, '食品饮料', '', '', 30, 1, '', 1, 1, '', '', '', 1, NOW(6), NOW(6)),
  (13, NULL, '家居日用', '', '', 20, 1, '', 1, 1, '', '', '', 1, NOW(6), NOW(6)),
  (14, NULL, '数码家电', '', '', 10, 1, '', 1, 1, '', '', '', 1, NOW(6), NOW(6));

INSERT INTO `spec_template`
  (`id`, `name`, `spec_names`, `created_at`, `updated_at`)
VALUES
  (1, '颜色/尺码', JSON_ARRAY('颜色', '尺码'), NOW(6), NOW(6)),
  (2, '套餐/容量', JSON_ARRAY('套餐', '容量'), NOW(6), NOW(6));

INSERT INTO `user`
  (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`,
   `parent_id`, `path`, `openid`, `mobile`, `nickname`, `avatar`, `level_id`, `role`, `is_distributor`, `city_agent_level`, `city_code`,
   `realname`, `id_card`, `realname_status`, `realname_remark`, `realname_verified_at`)
VALUES
  (1, 'pbkdf2_sha256$1000000$hfrnZyaCp0gYq4Y4ObcPcq$MZwCNJ3a0/83Wi3rQESKeSTpTLYWM7F/7MVeftbG5B0=', NULL, 1,
   'demo_admin', '', '', '', 1, 1, NOW(6), NULL, '', NULL, '13800000000', '平台管理员', '', NULL, 'admin', 0, 0, NULL, '', '', 'unverified', '', NULL),
  (2, 'pbkdf2_sha256$1000000$EbHURGNpCc3iK3mQqm8cQ6$3XiQCQ9BC5J/A8zLpP+pCbqlXz/Zb6zEFNK3tZeBavM=', NULL, 0,
   'demo_buyer', '', '', '', 0, 1, NOW(6), NULL, '', NULL, '13900000000', '测试买家', '', NULL, 'normal', 0, 0, NULL, '', '', 'unverified', '', NULL);

ALTER TABLE `member_level` AUTO_INCREMENT = 100;
ALTER TABLE `distribution_config` AUTO_INCREMENT = 100;
ALTER TABLE `product_category` AUTO_INCREMENT = 100;
ALTER TABLE `spec_template` AUTO_INCREMENT = 100;
ALTER TABLE `user` AUTO_INCREMENT = 100;

SET FOREIGN_KEY_CHECKS = 1;

SELECT 'Emall schema and seed data initialized successfully.' AS `message`;
