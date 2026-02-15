# Controller Migration Guide

## From Struts ActionSupport to Spring Boot @RestController

### Pattern 1: Basic Action to Controller

**Before (Struts ActionSupport)**:
```java
import org.apache.struts2.convention.annotation.Action;
import org.apache.struts2.convention.annotation.Result;
import com.opensymphony.xwork2.ActionSupport;

@Action(value = "users", results = {
    @Result(name = "success", location = "/users.jsp")
})
public class UserAction extends ActionSupport {
    private String username;
    private String password;
    
    @Override
    public String execute() throws Exception {
        // Validate input
        if (username == null || username.isEmpty()) {
            return ERROR;
        }
        
        // Business logic
        return SUCCESS;
    }
    
    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }
}
```

**After (Spring Boot @RestController)**:
```java
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.http.ResponseEntity;

@RestController
@RequestMapping("/api/users")
public class UserController {
    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody LoginRequest request) {
        // Validate input
        if (request.getUsername() == null || request.getUsername().isEmpty()) {
            return ResponseEntity.badRequest().build();
        }
        
        // Business logic
        return ResponseEntity.ok(new LoginResponse("Success"));
    }
}

class LoginRequest {
    private String username;
    private String password;
    // getters/setters
}

class LoginResponse {
    private String message;
    // getters/setters
}
```

### Key Mappings

| Struts | Spring Boot |
|--------|------------|
| `@Action` | `@RequestMapping` + `@GetMapping/@PostMapping/etc` |
| `ActionSupport.execute()` | Controller method |
| `return SUCCESS` | `ResponseEntity.ok(data)` |
| `return ERROR` | `ResponseEntity.badRequest()` |
| ValueStack | Method parameters / RequestBody |
| Result view | ResponseEntity |
| Request parameters | `@RequestParam` |
| Path variables | `@PathVariable` |

### DI Pattern Changes

**Before (Struts with manual DI)**:
```java
public class UserAction extends ActionSupport {
    private UserService userService;
    
    public void setUserService(UserService service) {
        this.userService = service;
    }
}
```

**After (Spring Boot with @Autowired)**:
```java
@RestController
public class UserController {
    @Autowired
    private UserService userService;
    
    // Or constructor injection (preferred):
    public UserController(UserService userService) {
        this.userService = userService;
    }
}
```

## From JAX-RS to Spring Boot

**Before (JAX-RS Resource)**:
```java
import javax.ws.rs.*;
import javax.ws.rs.core.Response;

@Path("/api/products")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
public class ProductResource {
    @GET
    @Path("/{id}")
    public Response getProduct(@PathParam("id") long id) {
        // Implementation
        return Response.ok(product).build();
    }
}
```

**After (Spring Boot)**:
```java
import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;

@RestController
@RequestMapping("/api/products")
public class ProductController {
    @GetMapping("/{id}")
    public ResponseEntity<?> getProduct(@PathVariable long id) {
        // Implementation
        return ResponseEntity.ok(product);
    }
}
```

## Common Pitfalls & Solutions

### 1. Result Forwarding

**Problem**: Struts uses JSP views, Spring Boot uses REST responses

**Solution**:
```java
// Return data, not JSP forwards
@PostMapping("/save")
public ResponseEntity<?> save(@RequestBody Product product) {
    Product saved = service.save(product);
    return ResponseEntity.created(URI.create("/api/products/" + saved.getId()))
        .body(saved);
}
```

### 2. Session Handling

**Problem**: Struts uses ActionContext with session, Spring uses HttpSession

**Solution**:
```java
// Spring way
@PostMapping("/login")
public ResponseEntity<?> login(
    HttpSession session,
    @RequestBody LoginRequest req) {
    
    User user = authenticate(req);
    session.setAttribute("user", user);
    return ResponseEntity.ok(user);
}
```

### 3. Global Exception Handling

**Problem**: Struts throws exceptions, Spring needs handlers

**Solution**:
```java
@ControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(UserNotFoundException.class)
    public ResponseEntity<?> handleUserNotFound(UserNotFoundException e) {
        return ResponseEntity.notFound().build();
    }
}
```
