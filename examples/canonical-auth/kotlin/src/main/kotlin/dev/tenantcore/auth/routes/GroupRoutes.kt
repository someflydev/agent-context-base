package dev.tenantcore.auth.routes

import dev.tenantcore.auth.auth.authContext
import dev.tenantcore.auth.domain.Group
import dev.tenantcore.auth.domain.InMemoryStore
import org.http4k.core.Body
import org.http4k.core.HttpHandler
import org.http4k.core.Response
import org.http4k.core.Status
import org.http4k.format.Jackson.auto
import org.http4k.routing.path

data class CreateGroupRequest(val slug: String, val name: String)
data class AssignPermissionRequest(val permission: String)
data class AssignUserRequest(val user_id: String)

class GroupRoutes {
    private val groupsLens = Body.auto<List<Group>>().toLens()
    private val groupLens = Body.auto<Group>().toLens()
    private val createLens = Body.auto<CreateGroupRequest>().toLens()
    private val assignPermissionLens = Body.auto<AssignPermissionRequest>().toLens()
    private val assignUserLens = Body.auto<AssignUserRequest>().toLens()

    fun listHandler(store: InMemoryStore): HttpHandler = { request ->
        groupsLens(store.getAllGroups(request.authContext.tenantId ?: ""), Response(Status.OK))
    }

    fun createHandler(store: InMemoryStore): HttpHandler = { request ->
        val body = createLens(request)
        val group = store.createGroup(request.authContext.tenantId ?: "", body.slug, body.name)
        groupLens(group, Response(Status.CREATED))
    }

    fun assignPermissionHandler(store: InMemoryStore): HttpHandler = { request ->
        val groupId = request.path("id")
        if (groupId == null) {
            Response(Status.NOT_FOUND)
        } else {
            val body = assignPermissionLens(request)
            if (store.assignPermissionToGroup(groupId, body.permission, request.authContext.tenantId ?: "")) {
                Response(Status.OK)
            } else {
                Response(Status.NOT_FOUND)
            }
        }
    }

    fun assignUserHandler(store: InMemoryStore): HttpHandler = { request ->
        val groupId = request.path("id")
        if (groupId == null) {
            Response(Status.NOT_FOUND)
        } else {
            val body = assignUserLens(request)
            if (store.assignUserToGroup(groupId, body.user_id, request.authContext.tenantId ?: "")) {
                Response(Status.OK)
            } else {
                Response(Status.NOT_FOUND)
            }
        }
    }
}
