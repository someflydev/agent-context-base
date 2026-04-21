package dev.tenantcore.auth.routes

import dev.tenantcore.auth.auth.authContext
import dev.tenantcore.auth.domain.InMemoryStore
import dev.tenantcore.auth.domain.User
import org.http4k.core.Body
import org.http4k.core.HttpHandler
import org.http4k.core.Response
import org.http4k.core.Status
import org.http4k.format.Jackson.auto
import org.http4k.routing.path

data class InviteUserRequest(val email: String, val display_name: String, val group_slugs: List<String> = emptyList())
data class PatchUserRequest(val display_name: String)
data class UserPatchResponse(val id: String, val email: String, val display_name: String)

class UserRoutes {
    private val usersLens = Body.auto<List<User>>().toLens()
    private val userLens = Body.auto<User>().toLens()
    private val inviteLens = Body.auto<InviteUserRequest>().toLens()
    private val patchRequestLens = Body.auto<PatchUserRequest>().toLens()
    private val patchResponseLens = Body.auto<UserPatchResponse>().toLens()

    fun listHandler(store: InMemoryStore): HttpHandler = { request ->
        usersLens(store.getAllUsers(request.authContext.tenantId ?: ""), Response(Status.OK))
    }

    fun inviteHandler(store: InMemoryStore): HttpHandler = { request ->
        val body = inviteLens(request)
        val user = store.inviteUser(request.authContext.tenantId ?: "", body.email, body.display_name, body.group_slugs)
        userLens(user, Response(Status.CREATED))
    }

    fun getHandler(store: InMemoryStore): HttpHandler = { request ->
        val userId = request.path("id")
        if (userId == null) {
            Response(Status.NOT_FOUND)
        } else {
            val user = store.getUserById(userId)
            if (user == null || user.tenantId != request.authContext.tenantId) {
                Response(Status.FORBIDDEN)
            } else {
                userLens(user, Response(Status.OK))
            }
        }
    }

    fun patchHandler(store: InMemoryStore): HttpHandler = { request ->
        val userId = request.path("id")
        if (userId == null) {
            Response(Status.NOT_FOUND)
        } else {
            val user = store.getUserById(userId)
            if (user == null || user.tenantId != request.authContext.tenantId) {
                Response(Status.FORBIDDEN)
            } else {
                val body = patchRequestLens(request)
                patchResponseLens(UserPatchResponse(user.id, user.email, body.display_name), Response(Status.OK))
            }
        }
    }
}
