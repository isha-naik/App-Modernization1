# Spring Boot 3 Migration Guide

## Jakarta EE Transition

The major change in Spring Boot 3 is the move from `javax.*` to `jakarta.*` packages.

### Key Changes

| Old (Spring Boot 2) | New (Spring Boot 3) | What Changed |
|-------|-------|------------|
| `javax.servlet` | `jakarta.servlet` | Servlet API |
| `javax.persistence` | `jakarta.persistence` | JPA |
| `javax.annotation` | `jakarta.annotation` | Common annotations |
| `javax.ws.rs` | `jakarta.ws.rs` | JAX-RS |
| `java.base` | `java.base` | Java 17+ required |

### Step-by-Step Migration

1. **Update Java Version to 17**
```xml
<!-- pom.xml -->
<properties>
    <maven.compiler.source>17</maven.compiler.source>
    <maven.compiler.target>17</maven.compiler.target>
</properties>
```

2. **Update Spring Boot**
```xml
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.0.0</version>
</parent>
```

3. **Update Imports**
```java
// OLD
import javax.persistence.Entity;
import javax.servlet.http.HttpServletRequest;

// NEW
import jakarta.persistence.Entity;
import jakarta.servlet.http.HttpServletRequest;
```

4. **Automatic Conversion (Recommended)**
```bash
# Use IDE refactor or gradle plugin
./gradlew classes
# Gradle automatically applies Jakarta EE migration
```

## REST Endpoint Examples

### Spring Boot 3 REST API

```java
package com.example.api.controller;

import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;
import org.springframework.http.HttpStatus;
import org.springframework.beans.factory.annotation.Autowired;
import jakarta.validation.Valid;  // Note: jakarta.*

@RestController
@RequestMapping("/api/v1/users")
public class UserController {
    @Autowired
    private UserService userService;
    
    // GET /api/v1/users
    @GetMapping
    public ResponseEntity<List<UserDTO>> getAllUsers() {
        return ResponseEntity.ok(userService.getAll());
    }
    
    // GET /api/v1/users/{id}
    @GetMapping("/{id}")
    public ResponseEntity<UserDTO> getUserById(@PathVariable Long id) {
        return userService.getById(id)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }
    
    // POST /api/v1/users
    @PostMapping
    public ResponseEntity<UserDTO> createUser(@Valid @RequestBody CreateUserRequest request) {
        UserDTO created = userService.create(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }
    
    // PUT /api/v1/users/{id}
    @PutMapping("/{id}")
    public ResponseEntity<UserDTO> updateUser(
        @PathVariable Long id,
        @Valid @RequestBody UpdateUserRequest request) {
        
        UserDTO updated = userService.update(id, request);
        return ResponseEntity.ok(updated);
    }
    
    // DELETE /api/v1/users/{id}
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        userService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
```

### Entity with Jakarta Persistence

```java
package com.example.api.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.*;

@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @NotBlank(message = "Username is required")
    @Column(unique = true, nullable = false)
    private String username;
    
    @Email(message = "Invalid email")
    @Column(nullable = false)
    private String email;
    
    @Column(nullable = false)
    private String passwordHash;
    
    @CreationTimestamp
    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;
    
    @UpdateTimestamp
    @Column(nullable = false)
    private LocalDateTime updatedAt;
    
    // Getters & Setters
}
```

### Repository

```java
package com.example.api.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import com.example.api.entity.User;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByUsername(String username);
    Optional<User> findByEmail(String email);
    List<User> findByEmailContaining(String email);
}
```

### Service

```java
package com.example.api.service;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import com.example.api.dto.CreateUserRequest;
import com.example.api.entity.User;
import com.example.api.repository.UserRepository;

@Service
@Transactional
public class UserService {
    private final UserRepository repository;
    
    public UserService(UserRepository repository) {
        this.repository = repository;
    }
    
    @Transactional(readOnly = true)
    public List<UserDTO> getAll() {
        return repository.findAll()
            .stream()
            .map(UserDTO::fromEntity)
            .collect(Collectors.toList());
    }
    
    public UserDTO create(CreateUserRequest request) {
        User user = new User();
        user.setUsername(request.getUsername());
        user.setEmail(request.getEmail());
        user.setPasswordHash(hashPassword(request.getPassword()));
        
        User saved = repository.save(user);
        return UserDTO.fromEntity(saved);
    }
}
```

## Configuration

### application.yml (Spring Boot 3)

```yaml
spring:
  application:
    name: api-modernization-service
  
  jpa:
    hibernate:
      ddl-auto: validate
    properties:
      hibernate:
        dialect: org.hibernate.dialect.PostgreSQL10Dialect
        format_sql: true
        use_sql_comments: true
  
  datasource:
    url: jdbc:postgresql://localhost:5432/api_db
    username: postgres
    password: password
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
  
  jackson:
    serialization:
      write-dates-as-timestamps: false
      indent-output: true

server:
  port: 8080
  servlet:
    context-path: /api

logging:
  level:
    root: INFO
    com.example: DEBUG
```

## Breaking Changes to Watch

1. **Method Security**: `@EnableWebSecurity` now optional
2. **Servlet**: Only jakarta.servlet supported
3. **Java Version**: Minimum 17 required
4. **Deprecated Methods**: Many Spring 2 methods removed

## Troubleshooting Migration

### Issue: "Cannot find symbol: class Entity"
**Solution**: Update imports from `javax.persistence` to `jakarta.persistence`

### Issue: "Cannot find symbol: class HttpServletRequest"
**Solution**: Update imports from `javax.servlet` to `jakarta.servlet`

### Issue: Spring version mismatch
**Solution**: Use Spring Boot 3.0+ BOM in parent POM
