-- 事务审批单表
CREATE TABLE IF NOT EXISTS `approval_requests` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `request_number` VARCHAR(50) NOT NULL,
    `department` VARCHAR(100) NULL,
    `applicant_name` VARCHAR(100) NULL,
    `subject` VARCHAR(500) NOT NULL,
    `content` TEXT NOT NULL,
    `manager_comment` TEXT NULL,
    `manager_signed_at` DATETIME NULL,
    `company_leader_comment` TEXT NULL,
    `company_leader_signed_at` DATETIME NULL,
    `status` VARCHAR(20) NULL DEFAULT 'draft',
    `created_by` INT NULL,
    `scanned_path` VARCHAR(500) NULL,
    `created_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
    `submitted_at` DATETIME NULL,
    `approved_at` DATETIME NULL,
    PRIMARY KEY (`id`),
    UNIQUE INDEX `ix_approval_requests_request_number` (`request_number`),
    INDEX `idx_request_status` (`status`),
    INDEX `idx_request_created_at` (`created_at`),
    CONSTRAINT `fk_approval_requests_user` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
