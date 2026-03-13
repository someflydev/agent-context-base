plugins {
    kotlin("jvm") version "1.9.24"
    application
}

repositories {
    mavenCentral()
}

dependencies {
    implementation("org.http4k:http4k-core:5.33.0.0")
    implementation("org.http4k:http4k-format-jackson:5.33.0.0")
    implementation("org.http4k:http4k-server-jetty:5.33.0.0")
    implementation("org.jetbrains.exposed:exposed-core:0.50.1")
    implementation("org.jetbrains.exposed:exposed-jdbc:0.50.1")
    implementation("com.h2database:h2:2.2.224")
    implementation("ch.qos.logback:logback-classic:1.5.6")
    testImplementation(kotlin("test"))
}

application {
    mainClass.set("example.MainKt")
}

kotlin {
    jvmToolchain(21)
}
