package io.agentcontextbase.faker

import java.util.UUID

object Pools {
  def deterministicUuid(rng: scala.util.Random): String = {
    val msb = rng.nextLong()
    val lsb = rng.nextLong()
    val uuid = new UUID(msb, lsb)
    // Clear version and variant bits and set to v4 / IETF variant to look somewhat valid
    val v4Msb = (uuid.getMostSignificantBits & 0xFFFFFFFFFFFF0FFFL) | 0x0000000000004000L
    val v4Lsb = (uuid.getLeastSignificantBits & 0x3FFFFFFFFFFFFFFFL) | 0x8000000000000000L
    new UUID(v4Msb, v4Lsb).toString
  }
}
