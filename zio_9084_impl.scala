/*
 * 补充: ZStream.fromInputStreamInterruptible 实现
 * 为 zio/zio#9084 bounty
 */

import zio._
import java.io.InputStream

// 在 ZStream object 中添加
def fromInputStreamInterruptible[
    R <: Any
](is: => InputStream, chunkSize: Int = 8192): ZStream[R, Throwable, Byte] = {
  ZStream.fromZIO(
    ZIO.attemptBlockingCancelable {
      val inputStream = is
      // 提供 cancel 逻辑 - 关闭 InputStream
      ZIO.succeed(inputStream.close()).orDie
    } { inputStream =>
      // 使用 attemptBlockingCancelable 的读取逻辑
      ZIO.attemptBlocking {
        val buffer = new Array[Byte](chunkSize)
        val bytesRead = inputStream.read(buffer)
        if (bytesRead < 0) None
        else if (bytesRead == 0) Some(Chunk.empty)
        else Some(Chunk.fromArray(buffer, 0, bytesRead))
      }
    }
  )
}
