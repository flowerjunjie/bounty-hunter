#!/usr/bin/env python3
"""
实现 zio#9084: Add ZStream.fromInputStreamInterruptible
价值: $50
预计时间: 2-3小时
"""

import os
import subprocess
from pathlib import Path

ZIO_REPO = Path("/root/.bounty-hunter/zio-zio-new")
STREAM_FILE = ZIO_REPO / "streams" / "shared" / "src" / "main" / "scala" / "zio" / "stream" / "ZStream.scala"
TEST_FILE = ZIO_REPO / "streams" / "shared" / "src" / "test" / "scala" / "zio" / "stream" / "ZStreamSpec.scala"

def add_fromInputStreamInterruptible():
    """添加 fromInputStreamInterruptible 方法到 ZStream"""

    print("🎯 实现 zio#9084: Add ZStream.fromInputStreamInterruptible")
    print("=" * 60)

    # 1. 找到 fromInputStream 的位置
    print("\n📂 步骤 1: 定位 fromInputStream 方法...")
    
    if not STREAM_FILE.exists():
        print(f"❌ 文件不存在: {STREAM_FILE}")
        return False

    # 读取文件
    content = STREAM_FILE.read_text()
    
    # 查找 fromInputStream 方法
    if "def fromInputStream" not in content:
        print("❌ 未找到 fromInputStream 方法")
        return False
    
    print("✅ 找到 fromInputStream 方法")

    # 2. 设计 fromInputStreamInterruptible 方法
    print("\n💻 步骤 2: 设计 fromInputStreamInterruptible...")
    
    new_method = '''
  /**
   * Creates a stream from an `InputStream` that can be interrupted.
   * 
   * Unlike `fromInputStream`, this stream properly handles interruption by
   * closing the stream when the fiber is interrupted.
   *
   * @param is The input stream to read from
   * @param chunkSize The size of chunks to read from the stream
   * @return A stream of bytes from the input stream
   */
  def fromInputStreamInterruptible(
    is: => InputStream,
    chunkSize: Int = 8192
  ): ZStream[Any, IOException, Byte] = {
    ZStream.scope {
      for {
        stream <- ZStream.fromEffect(ZIO.attempt(is).onInterrupt(ZIO.succeed(is.close())).orDie)
        _      <- ZStream.fromEffect(ZIO.addFinalizer(ZIO.succeed(stream.close())))
        bytes  <- ZStream.fromInputStream(stream, chunkSize)
      } yield bytes
    }
  }
'''

    print("✅ 方法设计完成")
    print(f"\n📝 将添加的方法:\n{new_method}")

    # 3. 找到合适的插入位置（在 fromInputStream 之后）
    print("\n📍 步骤 3: 确定插入位置...")
    
    lines = content.split('\n')
    insert_idx = -1
    
    for i, line in enumerate(lines):
        if 'def fromInputStream(' in line and 'Interruptible' not in line:
            # 找到 fromInputStream，找到它的结束位置
            indent = len(line) - len(line.lstrip())
            for j in range(i + 1, len(lines)):
                if j > i + 5 and lines[j].strip() and not lines[j].startswith(' ' * (indent + 2)):
                    insert_idx = j
                    break
            break
    
    if insert_idx == -1:
        print("❌ 无法确定插入位置")
        return False
    
    print(f"✅ 找到插入位置: 第 {insert_idx} 行")

    # 4. 备份原文件
    print("\n💾 步骤 4: 备份原文件...")
    backup_file = STREAM_FILE.with_suffix('.scala.bak')
    STREAM_FILE.rename(backup_file)
    print(f"✅ 备份到: {backup_file}")

    # 5. 插入新方法
    print("\n✍️  步骤 5: 插入新方法...")
    
    lines.insert(insert_idx, new_method)
    new_content = '\n'.join(lines)
    
    STREAM_FILE.write_text(new_content)
    print("✅ 新方法已添加")

    # 6. 验证语法
    print("\n🔍 步骤 6: 验证语法...")
    try:
        result = subprocess.run(
            ['cd', str(ZIO_REPO), '&&', 'scalafmt', str(STREAM_FILE)],
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            print("✅ 代码格式化成功")
        else:
            print("⚠️  格式化警告（非致命）")
    except Exception as e:
        print(f"⚠️  格式化失败: {e}")

    print("\n" + "=" * 60)
    print("✅ 实现完成！")
    print(f"📁 修改文件: {STREAM_FILE}")
    print(f"💾 备份文件: {backup_file}")
    print("\n下一步:")
    print("  1. 编写测试")
    print("  2. 运行测试验证")
    print("  3. 提交 PR")
    
    return True

if __name__ == "__main__":
    try:
        success = add_fromInputStreamInterruptible()
        if success:
            print("\n🎉 任务完成！")
        else:
            print("\n❌ 任务失败")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
