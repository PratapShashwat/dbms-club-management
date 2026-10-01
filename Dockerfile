FROM maven:3.9.6-eclipse-temurin-17 AS build
WORKDIR /app
# Copy the pom.xml from the backend folder
COPY backend/pom.xml .
# Copy the source code from the backend folder
COPY backend/src ./src
# Build the Spring Boot application
RUN mvn clean package -DskipTests

# Run stage
FROM eclipse-temurin:17-jre
WORKDIR /app
# Copy the compiled jar from the build stage
COPY --from=build /app/target/club-management-0.0.1-SNAPSHOT.jar app.jar
# Expose the standard Spring Boot port
EXPOSE 8080
# Run the application
ENTRYPOINT ["java", "-jar", "app.jar"]
