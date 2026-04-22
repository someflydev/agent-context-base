defmodule TenantcoreAuth.ConnCase do
  use ExUnit.CaseTemplate

  using do
    quote do
      @endpoint TenantcoreAuth.Endpoint
      import Plug.Conn
      import Phoenix.ConnTest
      import TenantcoreAuth.ConnCase
    end
  end

  setup _tags do
    {:ok, conn: Phoenix.ConnTest.build_conn()}
  end
end
