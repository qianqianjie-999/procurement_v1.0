# 版本部署指南

## 可用版本

| 版本 | 标签 | 说明 |
|------|------|------|
| v1.0 | `v1.0` | 初始稳定版本 |
| v2.0 | `v2.0` | 当前最新版本（推荐） |

## 部署方式

### 1. 部署最新版本 (v2.0)

```bash
# 方式一：指定版本
bash deploy/pull_deploy.sh v2.0

# 方式二：使用 main 分支（最新开发版本）
bash deploy/pull_deploy.sh
```

### 2. 部署特定版本

```bash
# 部署 v1.0 版本
bash deploy/pull_deploy.sh v1.0
```

### 3. 回滚版本

如果需要从 v2.0 回滚到 v1.0：

```bash
cd /var/www/html/procurement
bash deploy/pull_deploy.sh v1.0
sudo systemctl restart httpd
```

## Git 标签管理

### 本地创建标签
```bash
# 创建新版本标签
git tag v2.1 HEAD

# 推送到远程
git push origin v2.1
```

### 查看所有标签
```bash
git tag -l
```

### 切换到特定版本
```bash
git checkout v1.0
```

## 版本差异

### v2.0 新特性
- 优化采购计划详情页面
- 扫描件在线预览功能
- 修复数据库连接超时问题
- UI/UX 改进

### v1.0 功能
- 基础采购计划管理
- 多级审批流程
- PDF 导出功能
- 用户权限管理
