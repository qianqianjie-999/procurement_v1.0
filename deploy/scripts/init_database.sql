-- ============================================================================
-- 采购管理系统 - MariaDB 数据库初始化脚本
-- 适用于已有 MariaDB 环境的服务器
-- ============================================================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS procurement_system
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- 创建用户并授权 (请修改密码)
CREATE USER IF NOT EXISTS 'procurement'@'localhost'
    IDENTIFIED BY 'YourSecurePassword123!';

GRANT ALL PRIVILEGES ON procurement_system.* TO 'procurement'@'localhost';
FLUSH PRIVILEGES;

-- 使用数据库
USE procurement_system;

-- ============================================================================
-- 用户表
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64) NOT NULL UNIQUE,
    full_name VARCHAR(100),
    password_hash VARCHAR(256) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    email VARCHAR(120) NOT NULL UNIQUE,
    phone VARCHAR(20),
    department VARCHAR(100),
    is_active_field BOOLEAN DEFAULT TRUE NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 采购计划表
-- ============================================================================
CREATE TABLE IF NOT EXISTS purchase_plans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    plan_number VARCHAR(50) NOT NULL UNIQUE,
    plan_name VARCHAR(200) NOT NULL,
    project_manager VARCHAR(100),
    plan_type VARCHAR(50) DEFAULT 'goods',
    status VARCHAR(20) DEFAULT 'draft',
    budget_amount DECIMAL(15,2) DEFAULT 0.00,
    actual_amount DECIMAL(15,2) DEFAULT 0.00,
    currency VARCHAR(3) DEFAULT 'CNY',
    procurement_method VARCHAR(50),
    start_date DATE,
    end_date DATE,
    created_by INT NOT NULL,
    approved_by INT,
    department VARCHAR(100),
    description TEXT,
    remarks TEXT,
    attachment_path VARCHAR(500),
    pdf_path VARCHAR(500),
    scanned_path VARCHAR(500),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    submitted_at DATETIME,
    approved_at DATETIME,
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (approved_by) REFERENCES users(id),
    INDEX idx_plan_number (plan_number),
    INDEX idx_status (status),
    INDEX idx_plan_dates (start_date, end_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 采购明细表
-- ============================================================================
CREATE TABLE IF NOT EXISTS purchase_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    plan_id INT NOT NULL,
    item_number VARCHAR(50),
    item_name VARCHAR(200) NOT NULL,
    brand_model VARCHAR(200),
    specification VARCHAR(500),
    category VARCHAR(100),
    quantity DECIMAL(12,4) NOT NULL DEFAULT 1.0000,
    unit VARCHAR(20),
    batch_quantity DECIMAL(12,4),
    extra_contract_quantity DECIMAL(12,4),
    supplier_name VARCHAR(200),
    supplier_contact VARCHAR(100),
    required_date DATE,
    delivery_address VARCHAR(500),
    remarks TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (plan_id) REFERENCES purchase_plans(id) ON DELETE CASCADE,
    INDEX idx_item_plan (plan_id),
    INDEX idx_item_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 审批流程表
-- ============================================================================
CREATE TABLE IF NOT EXISTS approval_flows (
    id INT AUTO_INCREMENT PRIMARY KEY,
    plan_id INT NOT NULL,
    flow_name VARCHAR(100) NOT NULL,
    flow_type VARCHAR(50) DEFAULT 'standard',
    current_step INT DEFAULT 1,
    total_steps INT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (plan_id) REFERENCES purchase_plans(id) ON DELETE CASCADE,
    INDEX idx_flow_plan (plan_id),
    INDEX idx_flow_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 审批步骤表
-- ============================================================================
CREATE TABLE IF NOT EXISTS approval_steps (
    id INT AUTO_INCREMENT PRIMARY KEY,
    flow_id INT NOT NULL,
    step_order INT NOT NULL,
    step_name VARCHAR(100) NOT NULL,
    step_type VARCHAR(50),
    approver_id INT,
    approver_role VARCHAR(50),
    status VARCHAR(20) DEFAULT 'pending',
    action VARCHAR(20),
    comments TEXT,
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    handled_at DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (flow_id) REFERENCES approval_flows(id) ON DELETE CASCADE,
    FOREIGN KEY (approver_id) REFERENCES users(id),
    INDEX idx_step_flow (flow_id),
    INDEX idx_step_order (step_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 审批日志表
-- ============================================================================
CREATE TABLE IF NOT EXISTS approval_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    plan_id INT NOT NULL,
    flow_id INT,
    step_id INT,
    action VARCHAR(20) NOT NULL,
    previous_status VARCHAR(20),
    new_status VARCHAR(20),
    operator_id INT NOT NULL,
    comments TEXT,
    reason TEXT,
    attachment_path VARCHAR(500),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plan_id) REFERENCES purchase_plans(id) ON DELETE CASCADE,
    FOREIGN KEY (flow_id) REFERENCES approval_flows(id),
    FOREIGN KEY (step_id) REFERENCES approval_steps(id),
    FOREIGN KEY (operator_id) REFERENCES users(id),
    INDEX idx_log_plan (plan_id),
    INDEX idx_log_operator (operator_id),
    INDEX idx_log_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 插入默认用户
-- ============================================================================
-- 管理员用户
-- 用户名：admin
-- 密码：admin123
-- ============================================================================
INSERT INTO users (username, full_name, password_hash, role, email, department)
VALUES ('admin', '系统管理员',
        'scrypt:32768:8:1$yEXrrbK4mep0lw1R$78c2477e5a0b7b7c546c8e41cfc10ddbcc28466f9b14db7898dfb4ff3ed23df7485f1d378623e86200996d39b2d1c91ea52211d8aa3e3842b227bbe48a54ceda',
        'admin',
        'admin@example.com',
        '信息技术部')
ON DUPLICATE KEY UPDATE username=username;

-- ============================================================================
-- 普通用户
-- 用户名：user
-- 密码：user123
-- ============================================================================
INSERT INTO users (username, full_name, password_hash, role, email, department)
VALUES ('user', '普通用户',
        'scrypt:32768:8:1$HJ9oHxIAIBOucrK4$915e3554824b70f9c240af4cb3cdbe1a0f6a95e751d3578875a8c0ade1b6562fd2a07ddd78b1aa565bbaca3d1e3443aff389526e1843913575415e2081a5e582',
        'user',
        'user@example.com',
        '业务部')
ON DUPLICATE KEY UPDATE username=username;

-- ============================================================================
-- 完成提示
-- ============================================================================
SELECT '数据库初始化完成!' AS message;
