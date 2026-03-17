# zio-http 快速开始指南

## 🎯 目标：快速完成第一个 bounty

### 最简单的 issues（推荐顺序）

#### 1. #3133 - Flag ZClient.request as deprecated
**难度**: ⭐ 极简单
**价值**: $50
**操作**: 添加 @deprecated 注解

#### 2. #3188 - text/plain response body encoding
**难度**: ⭐⭐ 简单
**价值**: $50
**操作**: 修复编码问题

#### 3. #3141 - HandlerAspect and Path parameters
**难度**: ⭐⭐ 简单
**价值**: $50
**操作**: 修复类型转换

### 快速开始

```bash
cd /root/.bounty-hunter/zio-http

# 1. 创建 fork
gh repo fork zio/zio-http --org flowerjunjie --remote

# 2. 创建分支
git checkout -b fix-3133-deprecate-zclient

# 3. 查找相关文件
find . -name "*.scala" | xargs grep -l "ZClient.request"

# 4. 编辑文件
# 添加 @Deprecated 注解

# 5. 测试
sbt test

# 6. 提交
git add .
git commit -m "Deprecate ZClient.request (fixes #3133)"
git push origin fix-3133-deprecate-zclient

# 7. 创建 PR
gh pr create --title "Deprecate ZClient.request" --body "Fixes #3133"
```

### 预期时间
- 理解需求: 10分钟
- 实现代码: 20分钟
- 测试: 10分钟
- 提交: 5分钟
- **总计: 45分钟**

### 收入
- **$50 per bounty**
- **3-4 bounties/hour**
- **$150-200/hour**

---

**开始赚钱！** 💰
