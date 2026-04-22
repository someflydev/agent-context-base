defmodule TenantcoreAuth.Auth.TokenService do
  use Joken.Config

  alias TenantcoreAuth.Domain.InMemoryStore

  @issuer "tenantcore-auth"
  @audience "tenantcore-api"
  @expiry_seconds 900

  @impl true
  def token_config do
    default_claims(skip: [:exp, :iat, :nbf, :jti, :iss, :aud])
  end

  def issue_token(user, _store \\ InMemoryStore) do
    membership = InMemoryStore.get_active_membership(user.id)
    tenant_id = membership && membership.tenant_id
    tenant_role = membership && membership.tenant_role
    permissions =
      if tenant_role == "super_admin" do
        InMemoryStore.list_permissions()
        |> Enum.map(& &1.name)
        |> Enum.filter(&String.starts_with?(&1, "admin:"))
        |> Enum.sort()
      else
        InMemoryStore.get_effective_permissions(user.id)
      end
    groups =
      if tenant_id do
        InMemoryStore.get_groups_for_user(user.id, tenant_id) |> Enum.map(& &1.slug)
      else
        []
      end

    now = DateTime.utc_now() |> DateTime.to_unix()

    claims = %{
      "iss" => @issuer,
      "aud" => @audience,
      "sub" => user.id,
      "exp" => now + @expiry_seconds,
      "iat" => now,
      "nbf" => now,
      "jti" => Integer.to_string(System.unique_integer([:positive])),
      "tenant_id" => tenant_id,
      "tenant_role" => tenant_role,
      "groups" => groups,
      "permissions" => permissions,
      "acl_ver" => user.acl_ver
    }

    {:ok, token, _claims} = generate_and_sign(claims, signer())
    token
  end

  def sign_claims!(claims) do
    {:ok, token, _claims} = generate_and_sign(claims, signer())
    token
  end

  def verify_token(token) do
    with {:ok, claims} <- verify_and_validate(token, signer()),
         :ok <- verify_standard_claims(claims) do
      {:ok, claims}
    else
      _ -> {:error, :invalid_token}
    end
  end

  defp verify_standard_claims(claims) do
    now = DateTime.utc_now() |> DateTime.to_unix()
    exp = claims["exp"] || 0
    nbf = claims["nbf"] || 0

    cond do
      claims["iss"] != @issuer -> {:error, :issuer}
      claims["aud"] != @audience -> {:error, :audience}
      Enum.any?(~w[sub exp iat nbf jti tenant_role permissions acl_ver], &is_nil(claims[&1])) -> {:error, :claims}
      exp <= now -> {:error, :expired}
      nbf > now -> {:error, :not_before}
      true -> :ok
    end
  end

  defp signer do
    case System.get_env("TENANTCORE_TEST_SECRET") do
      nil -> Joken.Signer.create("HS256", "tenantcore-dev-secret")
      secret -> Joken.Signer.create("HS256", secret)
    end
  end
end
