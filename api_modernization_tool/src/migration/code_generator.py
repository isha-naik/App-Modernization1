"""Code Generation Module - Generate Modernized Application Code"""
from typing import Dict, Any, List
from src.knowledge_graph.graph import KnowledgeGraph
from src.utils.preferences import ModernizationPreferences


class ModernizedCodeGenerator:
    """Generate modernized code based on preferences"""
    
    def __init__(self, kg: KnowledgeGraph, preferences: ModernizationPreferences):
        self.kg = kg
        self.prefs = preferences
    
    def generate_all_code(self) -> Dict[str, str]:
        """Generate all modernized code files"""
        return {
            "pom.xml": self._generate_pom(),
            "application.yml": self._generate_application_yml(),
            "application-docker.yml": self._generate_docker_config(),
            "Dockerfile": self._generate_dockerfile(),
            "docker-compose.yml": self._generate_docker_compose(),
            "controllers.java": self._generate_controllers(),
            "services.java": self._generate_services(),
            "entities.java": self._generate_entities(),
            "config.java": self._generate_config(),
            "security-config.java": self._generate_security_config(),
            "build.gradle": self._generate_gradle(),
            "kubernetes.yaml": self._generate_kubernetes(),
            "cloudformation.yaml": self._generate_cloudformation(),
        }
    
    def _generate_pom(self) -> str:
        """Generate Maven pom.xml"""
        databases = {
            "PostgreSQL": "org.postgresql:postgresql",
            "MySQL": "mysql:mysql-connector-java",
            "DynamoDB": "software.amazon.awssdk:dynamodb"
        }
        
        db_dependency = databases.get(self.prefs.database_type, 
                                      "org.postgresql:postgresql")
        
        security_starter = "spring-boot-starter-security" if self.prefs.security_framework == "Spring Security" else ""
        graphql_starter = "spring-boot-starter-graphql" if self.prefs.api_style == "GraphQL" else ""
        webflux_starter = "spring-boot-starter-webflux" if self.prefs.reactive_enabled else "spring-boot-starter-web"
        
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.1</version>
        <relativePath/>
    </parent>

    <groupId>com.modernized</groupId>
    <artifactId>app-modernized</artifactId>
    <version>3.0.0</version>
    <name>Modernized Application</name>
    <description>Spring Boot 3.x Modernized Application</description>

    <properties>
        <java.version>17</java.version>
        <maven.compiler.source>17</maven.compiler.source>
        <maven.compiler.target>17</maven.compiler.target>
    </properties>

    <dependencies>
        <!-- Core Spring Boot -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>{webflux_starter}</artifactId>
        </dependency>

        <!-- Spring Security -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-security</artifactId>
        </dependency>

        <!-- Data Access -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>

        <dependency>
            <groupId>{db_dependency.split(':')[0]}</groupId>
            <artifactId>{db_dependency.split(':')[1]}</artifactId>
            <scope>runtime</scope>
        </dependency>

        <!-- Caching -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-redis</artifactId>
        </dependency>

        <dependency>
            <groupId>redis.clients</groupId>
            <artifactId>jedis</artifactId>
        </dependency>

        <!-- GraphQL Support -->
        {"<dependency>" if self.prefs.api_style == "GraphQL" else "<!-- GraphQL disabled -->"}
        {"<groupId>org.springframework.boot</groupId>" if self.prefs.api_style == "GraphQL" else ""}
        {"<artifactId>spring-boot-starter-graphql</artifactId>" if self.prefs.api_style == "GraphQL" else ""}
        {"/>" if self.prefs.api_style == "GraphQL" else ""}

        <!-- AWS Integration -->
        <dependency>
            <groupId>software.amazon.awssdk</groupId>
            <artifactId>bom</artifactId>
            <version>2.20.0</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>

        <!-- Observability -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-actuator</artifactId>
        </dependency>

        <dependency>
            <groupId>io.micrometer</groupId>
            <artifactId>micrometer-registry-prometheus</artifactId>
        </dependency>

        <!-- Logging -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-logging</artifactId>
        </dependency>

        <!-- Testing -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
'''
    
    def _generate_application_yml(self) -> str:
        """Generate application.yml configuration"""
        db_config = {
            "PostgreSQL": """
  datasource:
    url: jdbc:postgresql://localhost:5432/modernized_app
    username: postgres
    password: changeme
  jpa:
    hibernate:
      ddl-auto: validate
    database-platform: org.hibernate.dialect.PostgreSQL10Dialect""",
            "DynamoDB": """
  dynamodb:
    endpoint: https://dynamodb.us-east-1.amazonaws.com
    region: us-east-1
    table-name: app_data"""
        }
        
        cache_config = """
  redis:
    host: localhost
    port: 6379
    timeout: 60000ms
    jedis:
      pool:
        max-active: 8
        max-idle: 8
        min-idle: 0""" if self.prefs.cache_strategy == "Redis" else "  # Caching disabled"
        
        return f'''spring:
  application:
    name: modernized-app
  profiles:
    active: prod

  # Database Configuration
{db_config.get(self.prefs.database_type, "  # Database config")}

  # Cache Configuration
{cache_config}

  # Security
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: https://auth.example.com

# Server Configuration
server:
  port: 8080
  servlet:
    context-path: /api/v3
  compression:
    enabled: true
    min-response-size: 1024

# Actuator
management:
  endpoints:
    web:
      exposure:
        include: health,metrics,prometheus
  metrics:
    export:
      prometheus:
        enabled: true

# Logging
logging:
  level:
    root: INFO
    com.modernized: DEBUG
  pattern:
    console: "%d %p %c{{1}} [%t] %m%n"
    file: "%d %p %c{{1}} [%t] %m%n"
  file:
    name: logs/app.log

# Application Properties
app:
  api:
    version: 3.0.0
    style: {self.prefs.api_style}
  features:
    async-enabled: {str(self.prefs.async_enabled).lower()}
    reactive-enabled: {str(self.prefs.reactive_enabled).lower()}
    caching-enabled: {str(self.prefs.caching_enabled).lower()}
'''
    
    def _generate_docker_config(self) -> str:
        """Generate Docker-specific configuration"""
        return '''spring:
  datasource:
    url: jdbc:postgresql://postgres:5432/modernized_app
    username: postgres
    password: postgres
  redis:
    host: redis
    port: 6379

logging:
  level:
    root: INFO
'''
    
    def _generate_dockerfile(self) -> str:
        """Generate Dockerfile"""
        return '''FROM eclipse-temurin:17-jre-alpine

WORKDIR /app

# Create non-root user
RUN addgroup -S spring && adduser -S spring -G spring

# Copy built application
COPY target/app-modernized-3.0.0.jar app.jar

# Change ownership
RUN chown -R spring:spring /app

USER spring

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/actuator/health || exit 1

EXPOSE 8080

ENTRYPOINT ["java", "-XX:+UseContainerSupport", "-XX:MaxRAMPercentage=75.0", "-jar", "app.jar"]
'''
    
    def _generate_docker_compose(self) -> str:
        """Generate docker-compose.yml"""
        return '''version: '3.8'

services:
  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      SPRING_PROFILES_ACTIVE: docker
      SPRING_DATASOURCE_URL: jdbc:postgresql://postgres:5432/modernized_app
      SPRING_DATASOURCE_USERNAME: postgres
      SPRING_DATASOURCE_PASSWORD: postgres
      SPRING_REDIS_HOST: redis
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - modernized-net
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:8080/actuator/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: modernized_app
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - modernized-net
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    networks:
      - modernized-net
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:

networks:
  modernized-net:
    driver: bridge
'''
    
    def _generate_controllers(self) -> str:
        """Generate Spring REST controllers"""
        if len(self.kg.endpoints) == 0:
            return "// No endpoints detected to modernize"
        
        code = "package com.modernized.controller;\n\n"
        code += "import org.springframework.web.bind.annotation.*;\n"
        code += "import org.springframework.beans.factory.annotation.Autowired;\n"
        code += "import org.springframework.http.ResponseEntity;\n"
        code += "import org.springframework.cache.annotation.Cacheable;\n"
        code += "import com.modernized.service.DataService;\n\n"
        
        code += "@RestController\n"
        code += "@RequestMapping(\"/api/v3/resources\")\n"
        code += "public class ModernizedController {\n\n"
        code += "    @Autowired\n"
        code += "    private DataService dataService;\n\n"
        
        code += "    @GetMapping\n"
        code += "    @Cacheable(\"resources\")\n"
        code += "    public ResponseEntity<?> getAll() {\n"
        code += "        return ResponseEntity.ok(dataService.findAll());\n"
        code += "    }\n\n"
        
        code += "    @GetMapping(\"/{id}\")\n"
        code += "    @Cacheable(value=\"resource\", key=\"#id\")\n"
        code += "    public ResponseEntity<?> getById(@PathVariable Long id) {\n"
        code += "        return dataService.findById(id)\n"
        code += "            .map(ResponseEntity::ok)\n"
        code += "            .orElse(ResponseEntity.notFound().build());\n"
        code += "    }\n\n"
        
        if self.prefs.api_style == "REST":
            code += "    @PostMapping\n"
            code += "    public ResponseEntity<?> create(@RequestBody Object data) {\n"
            code += "        return ResponseEntity.ok(dataService.save(data));\n"
            code += "    }\n\n"
            
            code += "    @PutMapping(\"/{id}\")\n"
            code += "    public ResponseEntity<?> update(@PathVariable Long id, @RequestBody Object data) {\n"
            code += "        return ResponseEntity.ok(dataService.update(id, data));\n"
            code += "    }\n\n"
            
            code += "    @DeleteMapping(\"/{id}\")\n"
            code += "    public ResponseEntity<?> delete(@PathVariable Long id) {\n"
            code += "        dataService.delete(id);\n"
            code += "        return ResponseEntity.noContent().build();\n"
            code += "    }\n"
        
        code += "}\n"
        return code
    
    def _generate_services(self) -> str:
        """Generate service layer"""
        return '''package com.modernized.service;

import org.springframework.stereotype.Service;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.transaction.annotation.Transactional;
import java.util.Optional;
import java.util.List;

@Service
@Transactional(readOnly = true)
public class DataService {

    @Transactional
    public Object save(Object data) {
        // Save logic
        return data;
    }

    @Cacheable(value = "resource", key = "#id")
    public Optional<Object> findById(Long id) {
        // Query logic
        return Optional.empty();
    }

    @Cacheable("resources")
    public List<Object> findAll() {
        // Query logic
        return List.of();
    }

    @Transactional
    public Object update(Long id, Object data) {
        // Update logic
        return data;
    }

    @Transactional
    public void delete(Long id) {
        // Delete logic
    }
}
'''
    
    def _generate_entities(self) -> str:
        """Generate JPA entities"""
        return '''package com.modernized.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Entity
@Table(name = "resources")
@Data
@NoArgsConstructor
public class Resource {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false)
    private String description;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @Version
    private Long version;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}
'''
    
    def _generate_config(self) -> str:
        """Generate Spring configuration"""
        return '''package com.modernized.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.scheduling.annotation.EnableAsync;

@Configuration
@EnableCaching
@EnableAsync
public class ApplicationConfig {
    
    // Bean configurations here
}
'''
    
    def _generate_security_config(self) -> str:
        """Generate security configuration"""
        return f'''package com.modernized.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
@EnableWebSecurity
public class SecurityConfig {{

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {{
        http
            .csrf().disable()
            .authorizeHttpRequests(authz -> authz
                .requestMatchers("/actuator/health").permitAll()
                .requestMatchers("/api/v3/public/**").permitAll()
                .anyRequest().authenticated()
            )
            .oauth2ResourceServer((rs) -> rs
                .jwt((jwt) -> jwt
                    .jwtAuthenticationConverter(jwtAuthenticationConverter())
                )
            );
        
        return http.build();
    }}

    private JwtAuthenticationConverter jwtAuthenticationConverter() {{
        JwtAuthenticationConverter converter = new JwtAuthenticationConverter();
        converter.setJwtGrantedAuthoritiesConverter(jwt -> {{
            // Extract authorities from JWT
            return jwt.getClaimAsStringList("roles").stream()
                .map(SimpleGrantedAuthority::new)
                .collect(Collectors.toList());
        }});
        return converter;
    }}
}}
'''
    
    def _generate_gradle(self) -> str:
        """Generate build.gradle"""
        return '''plugins {
    id 'java'
    id 'org.springframework.boot' version '3.2.1'
    id 'io.spring.dependency-management' version '1.1.4'
}

group = 'com.modernized'
version = '3.0.0'
sourceCompatibility = '17'

repositories {
    mavenCentral()
}

dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    implementation 'org.springframework.boot:spring-boot-starter-security'
    implementation 'org.springframework.boot:spring-boot-starter-data-redis'
    implementation 'org.springframework.boot:spring-boot-starter-actuator'
    
    runtimeOnly 'org.postgresql:postgresql'
    runtimeOnly 'redis.clients:jedis'
    
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
}

tasks.named('test') {
    useJUnitPlatform()
}
'''
    
    def _generate_kubernetes(self) -> str:
        """Generate Kubernetes deployment manifests"""
        return '''apiVersion: apps/v1
kind: Deployment
metadata:
  name: modernized-app
  labels:
    app: modernized-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: modernized-app
  template:
    metadata:
      labels:
        app: modernized-app
    spec:
      containers:
      - name: app
        image: your-registry/modernized-app:3.0.0
        ports:
        - containerPort: 8080
        env:
        - name: SPRING_PROFILES_ACTIVE
          value: "kubernetes"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /actuator/health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /actuator/health/readiness
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: modernized-app-service
spec:
  selector:
    app: modernized-app
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8080
'''
    
    def _generate_cloudformation(self) -> str:
        """Generate AWS CloudFormation template"""
        return '''AWSTemplateFormatVersion: '2010-09-09'
Description: 'CloudFormation template for modernized application on ECS'

Resources:
  ECSCluster:
    Type: AWS::ECS::Cluster
    Properties:
      ClusterName: modernized-app-cluster
      
  ECSTaskDefinition:
    Type: AWS::ECS::TaskDefinition
    Properties:
      Family: modernized-app
      NetworkMode: awsvpc
      RequiresCompatibilities:
        - FARGATE
      Cpu: '512'
      Memory: '1024'
      ExecutionRoleArn: !GetAtt ECSTaskExecutionRole.Arn
      ContainerDefinitions:
        - Name: app
          Image: !Sub '${AWS::AccountId}.dkr.ecr.${AWS::Region}.amazonaws.com/modernized-app:3.0.0'
          PortMappings:
            - ContainerPort: 8080
          Environment:
            - Name: SPRING_PROFILES_ACTIVE
              Value: aws
          LogConfiguration:
            LogDriver: awslogs
            Options:
              awslogs-group: !Ref LogGroup
              awslogs-region: !Ref AWS::Region
              awslogs-stream-prefix: ecs

  ECSService:
    Type: AWS::ECS::Service
    Properties:
      ServiceName: modernized-app-service
      Cluster: !Ref ECSCluster
      TaskDefinition: !Ref ECSTaskDefinition
      DesiredCount: 3
      LaunchType: FARGATE
      NetworkConfiguration:
        AwsvpcConfiguration:
          AssignPublicIp: ENABLED
          Subnets:
            - !Ref PublicSubnet1
            - !Ref PublicSubnet2
          SecurityGroups:
            - !Ref AppSecurityGroup

  RDSInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: db.t3.micro
      Engine: postgres
      MasterUsername: postgres
      MasterUserPassword: !Sub '{{resolve:secretsmanager:modernized-app-db-password:SecretString:password}}'
      AllocatedStorage: '20'
      StorageType: gp3

  ElastiCacheCluster:
    Type: AWS::ElastiCache::CacheCluster
    Properties:
      CacheNodeType: cache.t3.micro
      Engine: redis
      NumCacheNodes: 1

  LogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: /ecs/modernized-app
      RetentionInDays: 7

Outputs:
  ECSClusterName:
    Value: !Ref ECSCluster
  RDSEndpoint:
    Value: !GetAtt RDSInstance.Endpoint.Address
  ElastiCacheEndpoint:
    Value: !GetAtt ElastiCacheCluster.RedisEndpoint.Address
'''
    
    def get_summary(self) -> Dict[str, str]:
        """Get code generation summary"""
        return {
            "framework": self.prefs.target_framework,
            "api_style": self.prefs.api_style,
            "architecture": self.prefs.architecture,
            "database": self.prefs.database_type,
            "files_generated": len(self.generate_all_code()),
            "cloud_platform": self.prefs.cloud_provider
        }
