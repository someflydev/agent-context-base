plugins {
    kotlin("jvm") version "1.9.24"
    application
}

repositories {
    mavenCentral()
}

dependencies {
    implementation("io.github.serpro69:kotlin-faker:2.0.0-rc.6")
    implementation("net.datafaker:datafaker:2.2.2")
    implementation("com.fasterxml.jackson.module:jackson-module-kotlin:2.17.2")
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.2")
    testImplementation("io.kotest:kotest-runner-junit5:5.9.1")
    testImplementation(kotlin("test"))
}

application {
    mainClass.set("io.agentcontextbase.faker.MainKt")
}

tasks.test {
    useJUnitPlatform()
}

kotlin {
    jvmToolchain(21)
}
