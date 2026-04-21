plugins {
    kotlin("jvm") version "2.1.21"
    application
}

import org.jetbrains.kotlin.gradle.dsl.JvmTarget

repositories {
    mavenCentral()
}

dependencies {
    implementation("org.http4k:http4k-core:5.33.0.0")
    implementation("org.http4k:http4k-server-jetty:5.33.0.0")
    implementation("org.http4k:http4k-format-jackson:5.33.0.0")
    implementation("io.jsonwebtoken:jjwt-api:0.12.5")
    implementation("com.fasterxml.jackson.datatype:jackson-datatype-jsr310:2.17.1")
    implementation("com.fasterxml.jackson.module:jackson-module-kotlin:2.17.1")
    runtimeOnly("io.jsonwebtoken:jjwt-impl:0.12.5")
    runtimeOnly("io.jsonwebtoken:jjwt-jackson:0.12.5")
    implementation("ch.qos.logback:logback-classic:1.5.6")

    testImplementation(kotlin("test"))
}

application {
    mainClass.set("dev.tenantcore.auth.MainKt")
}

tasks.test {
    useJUnitPlatform()
}

tasks.withType<JavaCompile>().configureEach {
    sourceCompatibility = "21"
    targetCompatibility = "21"
}

kotlin {
    compilerOptions {
        jvmTarget.set(JvmTarget.JVM_21)
    }
}
