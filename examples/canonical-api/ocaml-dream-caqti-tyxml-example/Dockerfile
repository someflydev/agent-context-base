FROM ocaml/opam:debian-12-ocaml-5.1

USER root
RUN apt-get update && apt-get install -y --no-install-recommends libev-dev libgmp-dev libsqlite3-dev libssl-dev pkg-config m4 && rm -rf /var/lib/apt/lists/*

USER opam
WORKDIR /app

COPY --chown=opam:opam dune-project ocaml-dream-caqti-tyxml-example.opam ./
RUN opam install . --deps-only -y

COPY --chown=opam:opam bin ./bin
RUN opam exec -- dune build ./bin/main.exe

EXPOSE 8080

CMD ["opam", "exec", "--", "dune", "exec", "./bin/main.exe"]
