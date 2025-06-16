FROM maven:3.8.6-openjdk-11-slim AS build

# Configurar diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependência
COPY pom.xml .
COPY src ./src

# Compilar a aplicação
RUN mvn clean package -DskipTests

# Imagem final
FROM openjdk:11-jre-slim

# Configurar diretório de trabalho
WORKDIR /app

# Copiar o JAR compilado
COPY --from=build /app/target/java-processor-1.0.0.jar app.jar

# Expor a porta da aplicação
EXPOSE 8080

# Comando para executar a aplicação
CMD ["java", "-jar", "app.jar"]
