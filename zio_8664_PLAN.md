# 💰 **zio#8664 实现方案**

## 📋 **问题分析**

### 当前状态
- ✅ **Smart Assertions** 已经使用 Diff 机制 (SmartAssertions.scala#L280)
- ❌ **Classic Assertions** 没有使用 Diff (AssertionVariants.scala#L68)

### 需求
让 classic assertion 的 `equalTo` 也使用 Diff 渲染，提供更好的错误消息。

## 🔍 **代码分析**

### SmartAssertions.scala (已有实现)
在第 280 行左右，smart assertions 使用了 Diff 机制来渲染差异。

### AssertionVariants.scala (需要修改)
当前实现（第 68 行）：
```scala
def equalTo[A, B](expected: A)(implicit eql: Eql[A, B]): Assertion[B] =
  Assertion[B](
    TestArrow.make[B, Boolean] { actual =>
      val result = (actual, expected) match {
        case (left: Array[_], right: Array[_])         => left.sameElements[Any](right)
        case (left: CharSequence, right: CharSequence) => left.toString == right.toString
        case (left, right)                             => left == right
      }
      TestTrace.boolean(result) {
        if (expected.isInstanceOf[Product]) {
          M.text(diffProduct(actual, expected))  // 已经有 diffProduct!
        } else {
          M.pretty(actual) + M.equals + M.pretty(expected)
        }
      }
    }
    .withCode("equalTo", valueArgument(expected))
  )
```

### 关键发现
AssertionVariants.scala **已经有 `diffProduct` 函数**！
- 第 11-63 行定义了 `diffProduct` 函数
- 这个函数可以递归地比较两个对象并生成差异报告

## 💡 **解决方案**

### 问题
当前代码只在 `expected.isInstanceOf[Product]` 时使用 `diffProduct`，但这不够全面。

### 修改方案
需要扩展使用 `diffProduct` 的条件，让它像 smart assertions 一样使用 Diff。

## 🎯 **实现步骤**

### 1. 查看 SmartAssertions 的完整实现
找到 smart assertions 如何集成 Diff 机制

### 2. 修改 AssertionVariants.scala
- 移除 `isInstanceOf[Product]` 检查
- 总是使用 `diffProduct` 进行比较
- 确保向后兼容

### 3. 编写测试
- 创建测试用例验证 Diff 渲染
- 确保现有测试仍然通过

### 4. 提交 PR
- 创建 Pull Request
- 引用 issue #8664

## 📊 **预期结果**
- Classic assertions 现在显示详细的 Diff
- 错误消息更清晰、更有用
- 与 smart assertions 一致的用户体验

## 💰 **收益**
- **价值**: $50
- **时间**: 1-2小时
- **难度**: ⭐⭐ 低
- **成功率**: 90%

---

**准备开始实现！**
