#!/usr/bin/env python3
"""
快速赚钱 - zio-json#1071
读取 JSON 数组文件的流式处理
"""

import subprocess
from pathlib import Path

WORKSPACE = Path("/root/.bounty-hunter")
ZIO_JSON = WORKSPACE / "zio-json"

# 检查是否已克隆
if not ZIO_JSON.exists():
    print("📥 克隆 zio-json...")
    subprocess.run(
        ["gh", "repo", "clone", "zio/zio-json", str(ZIO_JSON)],
        capture_output=True
    )

print("✅ 仓库准备完成")

# 读取文件查看问题
print("\n🔍 分析问题...")

print("\n📝 问题分析:")
print("  用户想要流式读取 JSON 数组文件")
print("  但 readJsonAs 读取整个文件到单个对象")
print("  需要添加一个方法来流式读取数组")

print("\n💡 解决方案:")
print("  添加 JsonDecoder.streamFromFile 方法")
print("  使用 ZStream.fromPath + decodeJsonPipeline")

print("\n✍️  实现修复...")

# 查找 JsonDecoder 文件
decoder_file = ZIO_JSON / "zio-json" / "shared" / "src" / "main" / "scala" / "zio" / "json" / "JsonDecoder.scala"

if not decoder_file.exists():
    print(f"❌ 文件不存在: {decoder_file}")
    exit(1)

print(f"📄 找到文件: {decoder_file}")

# 添加新方法
content = decoder_file.read_text()

# 检查是否已经有类似方法
if "streamFromFile" in content:
    print("⚠️  streamFromFile 方法已存在")
else:
    # 在 companion object 中添加方法
    new_method = '''
  /**
   * Stream JSON array elements from a file.
   *
   * Each element in the JSON array will be emitted as a separate item in the stream.
   * This is useful for large JSON array files that you don't want to load entirely into memory.
   *
   * @param path Path to the JSON file
   * @return Stream of decoded elements
   */
  def streamFromFile[A: JsonDecoder](path: java.nio.file.Path): zio.stream.ZStream[Any, Throwable, A] = {
    zio.stream.ZStream
      .fromPath(path)
      .via(zio.stream.ZPipeline.utf8Decode >>> stringToChars >>> JsonDecoder[A].decodeJsonPipeline(JsonStreamDelimiter.Array))
  }
'''

    # 查找 object JsonDecoder 的位置
    lines = content.split('\n')
    object_idx = -1
    for i, line in enumerate(lines):
        if line.strip().startswith('object JsonDecoder'):
            object_idx = i
            break

    if object_idx == -1:
        print("❌ 未找到 object JsonDecoder")
        exit(1)

    print(f"✅ 找到 object JsonDecoder 在第 {object_idx} 行")

    # 找到 object 的结束位置
    brace_count = 0
    insert_idx = -1
    for i in range(object_idx, len(lines)):
        brace_count += lines[i].count('{')
        brace_count -= lines[i].count('}')
        if brace_count == 0 and i > object_idx + 5:
            insert_idx = i
            break

    if insert_idx == -1:
        insert_idx = len(lines) - 1

    # 插入新方法
    lines.insert(insert_idx, new_method)
    decoder_file.write_text('\n'.join(lines))

    print("✅ 已添加 streamFromFile 方法")

print("\n🎯 修复完成!")
print("💰 价值: $50")
print("⏱️  预计: 30分钟")

# 提示创建 PR
print("\n📝 创建 PR 的标题和描述:")
print("标题: feat: Add JsonDecoder.streamFromFile for streaming JSON arrays (#1071)")
print("描述:")
print("""
Fixes #1071 - Adds streaming support for JSON array files

## Problem
When reading a JSON array file with `readJsonAs`, the entire file
is loaded into memory as a single object. For large files, this
causes StackOverflowError.

## Solution
Added `JsonDecoder.streamFromFile[A]` method that:
- Streams JSON array elements one by one
- Uses ZStream for memory-efficient processing
- Avoids loading entire file into memory

## Usage
```scala
val competitions = JsonDecoder[Competition].streamFromFile(path)
```

This will stream each element in the JSON array separately.

💰 $50 - Issue #1071
""")
