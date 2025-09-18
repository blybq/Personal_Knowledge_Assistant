# 数据库设计文档

## 概述

本文档描述了个人知识助手项目的数据库结构设计，包括表结构、字段说明、关系约束等。

## 数据库系统

- **数据库**: MySQL 8.0+
- **字符集**: utf8mb4
- **排序规则**: utf8mb4_0900_ai_ci

## 表结构说明

### users 用户表

存储系统用户信息

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | INT | 主键ID | PRIMARY KEY, AUTO_INCREMENT |
| username | VARCHAR(50) | 用户名 | NOT NULL, UNIQUE |
| email | VARCHAR(100) | 邮箱地址 | NOT NULL, UNIQUE |
| hashed_password | VARCHAR(100) | 加密密码 | NOT NULL |
| is_admin | BOOLEAN | 是否为管理员 | DEFAULT FALSE |
| is_banned | BOOLEAN | 是否被封禁 | DEFAULT FALSE |
| created_at | DATETIME | 创建时间 | DEFAULT CURRENT_TIMESTAMP |
| updated_at | DATETIME | 更新时间 | DEFAULT CURRENT_TIMESTAMP ON UPDATE |

### conversations 对话表

存储用户对话会话

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | INT | 主键ID | PRIMARY KEY, AUTO_INCREMENT |
| user_id | INT | 用户ID | FOREIGN KEY (users.id), NULLABLE |
| organization_id | INT | 组织ID | FOREIGN KEY (organizations.id), NULLABLE |
| title | VARCHAR(100) | 对话标题 | NULLABLE |
| created_at | DATETIME | 创建时间 | DEFAULT CURRENT_TIMESTAMP |
| updated_at | DATETIME | 更新时间 | DEFAULT CURRENT_TIMESTAMP ON UPDATE |

**约束**: `user_id` 和 `organization_id` 不能同时为空，也不能同时不为空

### conversation_messages 对话消息表

存储对话中的问答消息

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | INT | 主键ID | PRIMARY KEY, AUTO_INCREMENT |
| conversation_id | INT | 对话ID | FOREIGN KEY (conversations.id), NOT NULL |
| user_id | INT | 用户ID | FOREIGN KEY (users.id), NULLABLE |
| organization_id | INT | 组织ID | FOREIGN KEY (organizations.id), NULLABLE |
| question | TEXT | 用户问题 | NOT NULL |
| answer | TEXT | AI回答 | NOT NULL |
| created_at | DATETIME | 创建时间 | DEFAULT CURRENT_TIMESTAMP |
| updated_at | DATETIME | 更新时间 | DEFAULT CURRENT_TIMESTAMP ON UPDATE |

### notes 笔记表

存储用户笔记内容

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | INT | 主键ID | PRIMARY KEY, AUTO_INCREMENT |
| title | VARCHAR(200) | 笔记标题 | NOT NULL |
| content | TEXT | 笔记内容 | DEFAULT "" |
| user_id | INT | 用户ID | FOREIGN KEY (users.id), NULLABLE |
| organization_id | INT | 组织ID | FOREIGN KEY (organizations.id), NULLABLE |
| folder_id | INT | 文件夹ID | FOREIGN KEY (note_folders.id), NULLABLE |
| created_at | DATETIME | 创建时间 | DEFAULT CURRENT_TIMESTAMP |
| updated_at | DATETIME | 更新时间 | DEFAULT CURRENT_TIMESTAMP ON UPDATE |

### note_folders 笔记文件夹表

存储笔记文件夹信息

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | INT | 主键ID | PRIMARY KEY, AUTO_INCREMENT |
| name | VARCHAR(100) | 文件夹名称 | NOT NULL |
| user_id | INT | 用户ID | FOREIGN KEY (users.id), NULLABLE |
| organization_id | INT | 组织ID | FOREIGN KEY (organizations.id), NULLABLE |
| parent_id | INT | 父文件夹ID | FOREIGN KEY (note_folders.id), NULLABLE |
| created_at | DATETIME | 创建时间 | DEFAULT CURRENT_TIMESTAMP |
| updated_at | DATETIME | 更新时间 | DEFAULT CURRENT_TIMESTAMP ON UPDATE |

### organizations 组织表

存储团队组织信息

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | INT | 主键ID | PRIMARY KEY, AUTO_INCREMENT |
| name | VARCHAR(100) | 组织名称 | NOT NULL |
| description | TEXT | 组织描述 | NULLABLE |
| invite_code | VARCHAR(50) | 邀请码 | NOT NULL, UNIQUE |
| creator_id | INT | 创建者ID | FOREIGN KEY (users.id), NOT NULL |
| created_at | DATETIME | 创建时间 | DEFAULT CURRENT_TIMESTAMP |
| updated_at | DATETIME | 更新时间 | DEFAULT CURRENT_TIMESTAMP ON UPDATE |

### organization_members 组织成员表

存储组织成员关系

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | INT | 主键ID | PRIMARY KEY, AUTO_INCREMENT |
| user_id | INT | 用户ID | FOREIGN KEY (users.id), NOT NULL |
| organization_id | INT | 组织ID | FOREIGN KEY (organizations.id), NOT NULL |
| is_creator | BOOLEAN | 是否为创建者 | DEFAULT FALSE |
| joined_at | DATETIME | 加入时间 | DEFAULT CURRENT_TIMESTAMP |

**唯一约束**: `user_id` 和 `organization_id` 组合唯一

## 索引设计

### users 表索引

- `ix_users_username` (username)
- `ix_users_email` (email)
- `ix_users_id` (id)

### conversations 表索引

- `user_id` (user_id)
- `ix_conversations_organization_id` (organization_id)

### organizations 表索引

- `invite_code` (invite_code) UNIQUE
- `ix_organizations_creator_id` (creator_id)

## 关系图

```bash
users
  │
  ├── conversations (1:n)
  ├── notes (1:n) 
  ├── note_folders (1:n)
  ├── organizations (作为创建者 1:n)
  └── organization_members (作为成员 1:n)

organizations
  │
  ├── conversations (1:n)
  ├── notes (1:n)
  ├── note_folders (1:n)
  └── organization_members (1:n)

conversations
  │
  └── conversation_messages (1:n)

note_folders
  │
  └── notes (1:n)
```

## 数据字典

### 状态字段说明

- `is_admin`: 0-普通用户, 1-管理员
- `is_banned`: 0-正常, 1-封禁
- `is_creator`: 0-普通成员, 1-组织创建者

## 性能优化建议

1. 为经常查询的字段添加索引
2. 对大文本字段（content, question, answer）考虑使用全文索引
3. 定期清理过期数据
4. 使用数据库连接池管理连接
5. 对频繁更新的表进行分表或分区
