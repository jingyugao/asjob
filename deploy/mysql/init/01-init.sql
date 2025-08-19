-- 创建数据库
CREATE DATABASE IF NOT EXISTS chatjob CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE chatjob;

-- 创建连接器表
CREATE TABLE IF NOT EXISTS connectors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    db_type VARCHAR(50) NOT NULL,
    host VARCHAR(255) NOT NULL,
    port INT NOT NULL,
    username VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    database_name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_name (name)
);

-- 创建知识库表
CREATE TABLE IF NOT EXISTS knowledge (
    id INT AUTO_INCREMENT PRIMARY KEY,
    target_type VARCHAR(50) NOT NULL,
    target_name VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 创建任务模板表
CREATE TABLE IF NOT EXISTS job_templates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    template_type VARCHAR(50) DEFAULT 'db_query',
    default_config JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_name (name)
);

-- 创建定时任务表
CREATE TABLE IF NOT EXISTS scheduled_jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    template_id INT NOT NULL,
    schedule_type VARCHAR(20) DEFAULT 'cron',
    cron_expression VARCHAR(100),
    interval_seconds INT,
    is_active BOOLEAN DEFAULT TRUE,
    next_run_time TIMESTAMP NULL,
    override_config JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_name (name),
    FOREIGN KEY (template_id) REFERENCES job_templates(id) ON DELETE CASCADE
);

-- 创建任务运行记录表
CREATE TABLE IF NOT EXISTS job_runs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    started_at TIMESTAMP NULL,
    finished_at TIMESTAMP NULL,
    duration_ms INT,
    rows_affected INT,
    result JSON,
    error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES scheduled_jobs(id) ON DELETE CASCADE
);

-- 创建用户表（示例）
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 插入示例数据
INSERT IGNORE INTO users (username, email) VALUES 
('admin', 'admin@example.com'),
('test', 'test@example.com');

-- 插入示例任务模板
INSERT IGNORE INTO job_templates (name, description, template_type, default_config) VALUES 
('数据库查询模板', '通用的数据库查询任务模板', 'db_query', '{"query": "SELECT 1", "timeout": 30}'),
('数据同步模板', '数据同步任务模板', 'data_sync', '{"source": "", "target": "", "batch_size": 1000}');

-- 插入示例定时任务
INSERT IGNORE INTO scheduled_jobs (name, template_id, schedule_type, cron_expression, is_active) VALUES 
('每日健康检查', 1, 'cron', '0 2 * * *', TRUE),
('每小时数据同步', 2, 'cron', '0 * * * *', TRUE);
