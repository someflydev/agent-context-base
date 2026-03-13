FROM clojure:temurin-21-tools-deps

WORKDIR /app

COPY deps.edn ./
RUN clojure -P

COPY src ./src

EXPOSE 3000

CMD ["clojure", "-M", "-m", "clojure-kit-nextjdbc-hiccup-example.core"]
