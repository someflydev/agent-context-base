package dev.tenantcore.auth.routes

import dev.tenantcore.auth.auth.TokenService
import dev.tenantcore.auth.domain.InMemoryStore
import org.http4k.core.Body
import org.http4k.core.HttpHandler
import org.http4k.core.Response
import org.http4k.core.Status
import org.http4k.format.Jackson.auto

data class TokenRequest(val email: String, val password: String)
data class TokenResponse(val access_token: String, val token_type: String = "Bearer", val expires_in: Int = 900)

class AuthRoutes {
    private val requestLens = Body.auto<TokenRequest>().toLens()
    private val responseLens = Body.auto<TokenResponse>().toLens()

    fun tokenHandler(store: InMemoryStore, tokenService: TokenService): HttpHandler = { request ->
        val payload = requestLens(request)
        val user = store.getUserByEmail(payload.email)
        if (user == null || payload.password != "password") {
            Response(Status.UNAUTHORIZED)
        } else {
            responseLens(TokenResponse(tokenService.issueToken(user, store)), Response(Status.OK))
        }
    }
}
