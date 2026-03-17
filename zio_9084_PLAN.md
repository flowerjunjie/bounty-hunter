# 💰 **zio#9084 实现方案**

## 📋 **问题分析**

### 标题
Add ZStream.fromInputStreamInterruptible

### 问题描述
当前的 `ZStream.fromInputStream` 实现使用 `ZIO.attemptBlocking`，当 fiber 被中断时，如果底层 `InputStream.read` 阻塞，中断也会被阻塞。

需要创建一个使用 `ZIO.attemptBlockingCancelable` 的版本，用于需要长时间阻塞且可被中断的场景。

## 🔍 **技术分析**

### 当前实现问题
- 使用 `ZIO.attemptBlocking` - 不可中断的阻塞操作
- 当 `InputStream.read` 阻塞时，fiber 中断也会被阻塞

### 解决方案
- 使用 `ZIO.attemptBlockingCancelable` - 可中断的阻塞操作
- 提供 `fromInputStreamInterruptible` 方法
- 允许超时和中断

## 🎯 **实现步骤**

### 1. 找到现有实现
- 位置: `zio/stream/ZStream.scala`
- 查找 `fromInputStream` 方法

### 2. 创建新方法
```scala
def fromInputStreamInterruptible(
  is: => InputStream,
  chunkSize: Int = 8192
): ZStream[Any, Throwable, Byte]
```

### 3. 使用 attemptBlockingCancelable
- 替换 `attemptBlocking` 为 `attemptBlockingCancelable`
- 添加取消逻辑

### 4. 测试
- 编写测试用例
- 验证中断行为

## 💰 **预期收益**
- **价值**: $50
- **难度**: ⭐⭐⭐ 中等
- **时间**: 2-3小时
- **成功率**: 85%

## 📝 **实现细节**

### 关键代码模式
```scala
ZIO.attemptBlockingCancelable {
  // 打开 InputStream
  val inputStream = is
  // 提供 cancel 逻辑
  ZIO.succeed(inputStream.close()).orDie
} { inputStream =>
  // 读取逻辑
}
```

---

**准备开始实现！**
