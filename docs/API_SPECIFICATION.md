# API 接口规范

## 概述

本文档定义了个人知识助手项目的 RESTful API 接口规范，包括认证、用户管理、对话、笔记、组织等功能模块的接口。

## 基础规范

### 请求格式

- **Content-Type**: `application/json`
- **认证**: Bearer Token (JWT)
- **编码**: UTF-8

### 响应格式

```json
{
  "success": true,
  "message": "操作成功",
  "data": {}
}
```

### 错误响应

```json
{
  "success": false,
  "message": "错误描述",
  "data": null
}
```

## 认证接口

### POST /api/login

用户登录

**请求体**:

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**响应**:

```json
{
  "success": true,
  "message": "登录成功",
  "data": {
    "user": {
      "id": 1,
      "username": "testuser",
      "email": "user@example.com",
      "is_admin": false,
      "is_banned": false
    },
    "token": "jwt_token_here"
  }
}
```

### POST /api/register

用户注册

**请求体**:

```json
{
  "username": "testuser",
  "email": "user@example.com",
  "password": "password123"
}
```

## 用户管理接口

### GET /api/user/me

获取当前用户信息

### PUT /api/users/{userId}/username

修改用户名

### PUT /api/users/{userId}/password

修改密码

## 对话接口

### POST /api/conversations/new

创建新对话

### GET /api/conversations/history

获取对话历史

### GET /api/conversations/{conversationId}

获取对话详情

### POST /api/ask

发送问题（流式响应）

## 笔记接口

### GET /api/notes/folders

获取笔记文件夹

### POST /api/notes/folders

创建笔记文件夹

### GET /api/notes/titles

获取笔记标题列表

### POST /api/notes

创建笔记

### PUT /api/notes/{noteId}

更新笔记

## 组织接口

### GET /api/organizations/user/{userId}

获取用户组织列表

### POST /api/organizations

创建组织

### POST /api/organizations/join

加入组织

## 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问（用户被封禁） |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 版本控制

当前API版本：v1

所有API端点前缀：`/api/`

## 安全规范

1. 所有敏感操作需要身份验证
2. 密码使用SHA256加密存储
3. JWT token有效期7天
4. 管理员操作需要记录操作日志
5. 文件上传需要验证文件类型和大小
