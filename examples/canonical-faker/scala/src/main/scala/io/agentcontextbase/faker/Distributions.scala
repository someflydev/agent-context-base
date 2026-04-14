package io.agentcontextbase.faker

import java.util.UUID
import scala.util.Random

object Distributions {

  def weightedPlan(rng: Random): String = {
    val n = rng.nextInt(100)
    if (n < 50) "free"
    else if (n < 85) "pro"
    else "enterprise"
  }

  def weightedRegion(rng: Random): String = {
    val n = rng.nextInt(100)
    if (n < 40) "us-east"
    else if (n < 65) "us-west"
    else if (n < 85) "eu-west"
    else "ap-southeast"
  }

  def weightedRole(rng: Random): String = {
    val n = rng.nextInt(100)
    if (n < 5) "owner"
    else if (n < 15) "admin"
    else if (n < 75) "member"
    else "viewer"
  }

  def weightedProjectStatus(rng: Random): String = {
    val n = rng.nextInt(100)
    if (n < 60) "active"
    else if (n < 85) "archived"
    else "draft"
  }

  def weightedAction(rng: Random): String = {
    val n = rng.nextInt(100)
    if (n < 40) "updated"
    else if (n < 70) "created"
    else if (n < 85) "deleted"
    else if (n < 95) "invited"
    else "exported"
  }

  def weightedResourceType(rng: Random): String = {
    val n = rng.nextInt(100)
    if (n < 50) "project"
    else if (n < 70) "membership"
    else if (n < 85) "user"
    else if (n < 95) "api_key"
    else "invitation"
  }
}
