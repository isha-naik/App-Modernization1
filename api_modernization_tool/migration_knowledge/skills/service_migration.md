# Service Layer Migration Guide

## From Struts Business Logic to Spring Service

### Pattern: Service Extraction

**Before (Struts - Logic in Action)**:
```java
public class OrderAction extends ActionSupport {
    private OrderDAO dao;
    private NotificationService notif;
    
    public String createOrder() throws Exception {
        // Business logic mixed with request handling
        Order order = new Order();
        order.setCustomerId(customerId);
        order.setTotal(calculateTotal());
        order.setStatus("PENDING");
        
        // Validation mixed in
        if (order.getTotal() < 0) {
            addActionError("Invalid amount");
            return ERROR;
        }
        
        // Persistence & notification mixed
        dao.save(order);
        notif.sendConfirmation(order);
        
        return SUCCESS;
    }
    
    private double calculateTotal() {
        double total = 0;
        for (Item item : items) {
            total += item.getPrice() * item.getQuantity();
        }
        return total;
    }
}
```

**After (Spring - Separated Concerns)**:
```java
// 1. Service Interface
public interface OrderService {
    Order createOrder(CreateOrderRequest request);
    Order getOrder(Long id);
    void updateOrder(Order order);
}

// 2. Service Implementation
@Service
@Transactional
public class OrderServiceImpl implements OrderService {
    @Autowired
    private OrderRepository orderRepository;
    
    @Autowired
    private NotificationService notificationService;
    
    @Override
    public Order createOrder(CreateOrderRequest request) {
        // Business logic
        Order order = new Order();
        order.setCustomerId(request.getCustomerId());
        order.setTotal(calculateTotal(request.getItems()));
        order.setStatus(OrderStatus.PENDING);
        
        // Validation
        validateOrder(order);
        
        // Persistence
        Order saved = orderRepository.save(order);
        
        // Notification
        notificationService.sendConfirmation(saved);
        
        return saved;
    }
    
    private void validateOrder(Order order) {
        if (order.getTotal() < 0) {
            throw new InvalidOrderException("Invalid amount");
        }
    }
    
    private double calculateTotal(List<Item> items) {
        return items.stream()
            .mapToDouble(i -> i.getPrice() * i.getQuantity())
            .sum();
    }
}

// 3. Controller Uses Service
@RestController
@RequestMapping("/api/orders")
public class OrderController {
    @Autowired
    private OrderService orderService;
    
    @PostMapping
    public ResponseEntity<?> createOrder(@RequestBody CreateOrderRequest request) {
        Order order = orderService.createOrder(request);
        return ResponseEntity
            .created(URI.create("/api/orders/" + order.getId()))
            .body(order);
    }
}
```

## DAO to Repository Pattern

### Before (DAO Pattern)
```java
public class OrderDAO {
    private SessionFactory factory;
    
    public Order save(Order order) {
        Session session = factory.openSession();
        session.save(order);
        session.close();
        return order;
    }
    
    public Order findById(long id) {
        Session session = factory.openSession();
        Order order = session.get(Order.class, id);
        session.close();
        return order;
    }
}
```

### After (Spring Data Repository)
```java
// Just an interface! Spring handles everything
@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {
    List<Order> findByCustomerId(Long customerId);
    List<Order> findByStatus(OrderStatus status);
}

// Usage in Service
@Service
public class OrderServiceImpl {
    @Autowired
    private OrderRepository repository;
    
    public Order getOrder(Long id) {
        return repository.findById(id)
            .orElseThrow(() -> new OrderNotFoundException("Order not found"));
    }
    
    public List<Order> getCustomerOrders(Long customerId) {
        return repository.findByCustomerId(customerId);
    }
}
```

## Transaction Management

### Before (Struts/Hibernate Manual)
```java
Transaction tx = session.beginTransaction();
try {
    order.setStatus("COMPLETED");
    session.save(order);
    tx.commit();
} catch (Exception e) {
    tx.rollback();
    throw e;
}
```

### After (Spring - Automatic)
```java
@Service
@Transactional  // Spring manages transactions automatically
public class OrderService {
    public void completeOrder(Long orderId) {
        Order order = repository.findById(orderId).orElseThrow();
        order.setStatus(OrderStatus.COMPLETED);
        repository.save(order);
        // Commit happens automatically
    }
}
```

## Dependency Injection

### Before (Manual)
```java
public class OrderAction extends ActionSupport {
    private OrderDAO dao;
    private NotificationService notif;
    private EmailService email;
    
    // Manual setter injection
    public void setOrderDAO(OrderDAO dao) {
        this.dao = dao;
    }
    
    // Configuration file manages wiring
}
```

### After (Spring Auto-wiring)
```java
@Service
public class OrderServiceImpl implements OrderService {
    // Option 1: Field injection (simple)
    @Autowired
    private OrderRepository repository;
    
    // Option 2: Constructor injection (preferred)
    private final OrderRepository repository;
    private final NotificationService notification;
    
    public OrderServiceImpl(OrderRepository repo, NotificationService notif) {
        this.repository = repo;
        this.notification = notif;
    }
}
```

## Error Handling

### Before (Struts)
```java
public String saveOrder() {
    try {
        // Logic
    } catch (SQLException e) {
        addActionError("Database error: " + e.getMessage());
        return ERROR;
    }
}
```

### After (Spring)
```java
@Service
public class OrderService {
    public Order saveOrder(Order order) {
        try {
            return repository.save(order);
        } catch (DataIntegrityViolationException e) {
            throw new InvalidOrderException("Order data invalid", e);
        }
    }
}

@ControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(InvalidOrderException.class)
    public ResponseEntity<?> handle(InvalidOrderException e) {
        return ResponseEntity
            .badRequest()
            .body(new ErrorResponse(e.getMessage()));
    }
}
```

## Testing

### Before (Hard to test with Struts)
```java
public void testCreateOrder() {
    OrderAction action = new OrderAction();
    // Hard to mock dependencies
    action.setOrderDAO(dao);  // Manual setup
    action.setNotificationService(notif);
    
    String result = action.createOrder();
    assertEquals("success", result);
}
```

### After (Easy with Spring)
```java
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(OrderController.class)
public class OrderControllerTest {
    @Autowired
    private MockMvc mockMvc;
    
    @MockBean  // Spring mocks automatically
    private OrderService orderService;
    
    @Test
    public void testCreateOrder() throws Exception {
        OrderService given = new Order();
        when(orderService.createOrder(any())).thenReturn(order);
        
        mockMvc.perform(post("/api/orders")
            .contentType(MediaType.APPLICATION_JSON)
            .content(asJson(request)))
            .andExpect(status().isCreated());
    }
}
```
