package dev.tenantcore.auth.config;

import dev.tenantcore.auth.domain.InMemoryStore;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.io.IOException;
import java.nio.file.Path;

@Configuration
public class StoreConfig {

    @Bean
    public InMemoryStore inMemoryStore() throws IOException {
        Path fixtureDir = Path.of("..", "domain", "fixtures");
        return InMemoryStore.loadFromFixtures(fixtureDir);
    }
}
