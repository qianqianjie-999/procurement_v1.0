#!/usr/bin/env python3
"""
初始化用户脚本

用于创建初始管理员用户和普通用户
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User


def create_user(username, email, password, role='user', full_name=None, department=None, update_password=False):
    """创建用户"""
    app = create_app()

    with app.app_context():
        # 检查用户是否已存在
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"用户 '{username}' 已存在", end="")
            if update_password:
                existing_user.set_password(password)
                existing_user.role = role
                db.session.commit()
                print(f"，已更新密码和角色为 {role}")
            else:
                print("，跳过创建。")
            return existing_user

        # 创建新用户
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            department=department,
            role=role
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        print(f"创建用户成功：{username} (角色：{role})")
        return user


def main():
    """主函数"""
    print("=" * 50)
    print("初始化用户")
    print("=" * 50)

    # 创建管理员用户
    admin = create_user(
        username='admin',
        email='admin@example.com',
        password='admin123',
        role='admin',
        full_name='系统管理员',
        department='信息部',
        update_password=True
    )

    # 创建普通用户
    user = create_user(
        username='user',
        email='user@example.com',
        password='user123',
        role='user',
        full_name='普通用户',
        department='采购部',
        update_password=True
    )

    print("=" * 50)
    print("初始化完成！")
    print("=" * 50)
    print("\n测试账号：")
    print(f"  管理员：admin / admin123")
    print(f"  普通用户：user / user123")
    print()


if __name__ == '__main__':
    main()
