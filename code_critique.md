# Consolidated Code Review Areas

## **Core Categories for Code Analysis & Validation**

> **Note:** This document consolidates the key areas covered across all code review documentation for Java/Spring Boot microservices.

---

## **1. CODE QUALITY**

### Summary
Maintains high code standards through metrics, conventions, and best practices. Ensures code is readable, maintainable, and follows industry standards for long-term sustainability.

### Confidence Level
**High** - Code quality metrics are measurable and enforceable through automated tools.

### Metrics
| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Method length | ≤ 30 lines | SonarQube, PMD |
| Cyclomatic complexity | ≤ 10 per method | Code complexity tools |
| Code duplication | < 3% | Copy-paste detector |
| Code coverage | ≥ 80% | JaCoCo |
| Technical debt ratio | < 5% | SonarQube |
| Code smells | 0 critical | Static analysis |
| Overly verbose or repetitive code | 0 | Code review |
| Meaningful names | 100% | Code review |
| Code modularity (SRP) | 100% | Architecture analysis |
| Correct HTTP status codes | 100% | API testing |
| Invalid dependencies | 0 | Dependency validation |
| Valid imports | 100% | Import analysis |
| Unused dependencies | 0 | Dependency audit |
| Implemented comments | 100% | Code review |
| Race conditions | 0 | Concurrency analysis |
| Deadlocks possible | 0 | Concurrency analysis |
| Unbounded threads/tasks | 0 | Resource management |
| Missing default values | 0 | Configuration review |
| Config separation (dev/staging/prod) | 100% | Configuration audit |
| Valid config keys | 100% | Configuration validation |
| Circular imports | 0 | Dependency analysis |

### Method & Class Standards:
- Method length limit (≤30 lines excluding comments)
- Cyclomatic complexity (≤10 per method)
- Class size management (≤10 public methods)
- Parameter count limits (≤3 parameters)
- Class cohesion assessment

### Best Practices:
- No magic numbers (use named constants)
- `Optional<T>` for nullable returns
- Immutable DTOs using records or builder pattern
- Use of generics (no raw types)
- Proper null checks
- Meaningful and self-documenting variable names
- No TODO comments in production code
- No debug statements (`System.out.println`)
- No star imports (`import x.y.*`)
- Proper exception handling

### Code Quality Metrics:
- Readability assessment
- DRY principle compliance (no code duplication)
- Code smell detection
- Nested conditionals check
- Complexity reduction strategies
- Refactoring opportunities

### Common Issues & Fixes

#### Issue 1: Method too long (>30 lines)
**Detection:** Method exceeds 30 lines
**Fix:** Extract smaller methods
```java
// ❌ Before
public void processOrder(Order order) {
    // 50 lines of code
}

// ✅ After
public void processOrder(Order order) {
    validateOrder(order);
    calculateTotal(order);
    applyDiscounts(order);
    saveOrder(order);
}
```

#### Issue 2: High cyclomatic complexity
**Detection:** Method has complexity > 10
**Fix:** Simplify conditionals, use strategy pattern, or extract methods

#### Issue 3: Magic numbers
**Detection:** Numeric literals in code
**Fix:**
```java
// ❌ Before
if (retryCount > 3) { ... }

// ✅ After
private static final int MAX_RETRY_COUNT = 3;
if (retryCount > MAX_RETRY_COUNT) { ... }
```

#### Issue 4: Code duplication
**Detection:** Similar code blocks in multiple places
**Fix:** Extract common logic into reusable methods or utility classes

---

## **2. CUSTOM CRITIQUE**

### Summary
Provides structured prompts and questions for developers to self-review code before submission, promoting quality awareness and reducing review cycles. Includes team-specific standards and custom validation rules.

### Confidence Level
**Medium** - Effectiveness depends on developer discipline and understanding of principles.

### Metrics
| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Pre-commit checklist completion | 100% | Developer attestation |
| Issues found in self-review | Track trend | Self-review reports |
| Review cycle time | Reduce by 30% | PR metrics |
| Rework after PR | < 20% | Git history analysis |
| Developer adherence | > 90% | Survey + audit |

### Pre-Commit Self-Review:
- Architecture self-check
- Security self-check
- Code quality self-check
- Performance self-check

### Deep Dive Self-Critique:
- Method-level analysis (purpose, parameters, return values, exceptions, testing)
- Class-level analysis (single responsibility, dependencies, size, cohesion, naming)
- Error handling evaluation

### Assessment Questions:
- Can I explain what this does in one sentence?
- Are all parameters necessary?
- What can go wrong?
- How would I test this?
- Does this follow SOLID principles?

### Common Issues & Fixes

#### Issue 1: Incomplete self-review
**Detection:** Issues that should be caught before PR
**Fix:** Use structured checklist before every commit

#### Issue 2: Unclear method purpose
**Detection:** Can't explain method in one sentence
**Fix:** Method is doing too much - split into smaller methods

#### Issue 3: Too many parameters
**Detection:** Method has > 3 parameters
**Fix:** 
```java
// ❌ Before
void createUser(String name, String email, int age, String phone, String address);

// ✅ After
void createUser(UserRequest request);
```

#### Issue 4: Untestable code
**Detection:** Difficulty writing unit tests
**Fix:** Code is too complex or tightly coupled - refactor for testability

---

## **3. SECURITY**

### Summary
Protects sensitive data and prevents security vulnerabilities through proper data masking, input validation, encryption, and secure coding practices. Critical for compliance and data protection.

### Confidence Level
**Critical** - Security issues can lead to data breaches and compliance violations. Must be 100% compliant.

### Metrics
| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Sensitive data in logs | 0 occurrences | Log analysis + pattern matching |
| Unmasked PII in responses | 0 occurrences | Response inspection |
| SQL injection vulnerabilities | 0 | OWASP ZAP, SpotBugs security |
| Hardcoded secrets | 0 | Secret scanning tools |
| Missing input validation | 0 | Bean validation check |
| Unencrypted sensitive fields | 0 | Database schema review |

### Sensitive Data Protection:
- **Masking patterns for all sensitive data types:**
  - Credit Card: `XXXX-XXXX-XXXX-{last4}`
  - SSN/National ID: `XXX-XX-{last4}`
  - Phone: `XXXXXX{last4}`
  - Email: `{first2}***@{domain}`
  - Account Number: `XXXXXX{last4}`
  - API Key: `{first4}...{last4}`
- No sensitive data in logs
- No sensitive data in URLs
- No sensitive data in error messages
- Encryption at rest for sensitive fields
- No hardcoded credentials or secrets

### Input Validation:
- Bean validation annotations (`@NotNull`, `@NotBlank`, `@Email`, `@Pattern`, `@Size`, `@Min`, `@Max`)
- SQL injection prevention with parameterized queries
- No string concatenation in queries
- Type conversion validation

### Common Issues & Fixes

#### Issue 1: Sensitive data logged without masking
**Detection:** Log statements contain credit card, SSN, or password fields
**Fix:**
```java
// ❌ Before
log.info("Processing payment for card: {}", cardNumber);

// ✅ After
log.info("Processing payment for card: {}", MaskingUtil.maskCreditCard(cardNumber));
```

#### Issue 2: Missing input validation
**Detection:** DTO fields without validation annotations
**Fix:**
```java
// ❌ Before
public class UserRequest {
    private String email;
    private Integer age;
}

// ✅ After
public class UserRequest {
    @NotBlank @Email
    private String email;
    
    @NotNull @Min(18) @Max(150)
    private Integer age;
}
```

#### Issue 3: SQL injection vulnerability
**Detection:** String concatenation in queries
**Fix:**
```java
// ❌ Before
@Query("SELECT u FROM User u WHERE u.email = '" + email + "'")

// ✅ After
@Query("SELECT u FROM User u WHERE u.email = :email")
Optional<User> findByEmail(@Param("email") String email);
```

#### Issue 4: Hardcoded credentials
**Detection:** API keys, passwords in source code
**Fix:** Use environment variables or secret management tools (AWS Secrets Manager, Vault)

---

## **4. ERROR HANDLING**

### Summary
Implements comprehensive error handling to provide meaningful error messages, maintain system stability, and prevent information leakage while ensuring proper logging and recovery.

### Confidence Level
**High** - Error handling patterns are detectable through code analysis and exception flow tracking.

### Metrics
| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Uncaught exceptions | 0 | Global exception handler coverage |
| Generic exception catches | 0 | Static analysis |
| Stack traces in responses | 0 | Response validation (prod) |
| Error response consistency | 100% | API contract testing |
| Exception logging | 100% | Log analysis |
| Recovery mechanisms | 100% coverage | Error scenario testing |
| Meaningful error messages | 100% | Error message review |
| Retries and fallbacks | 100% | Resilience testing |
| Null and boundary checks | 100% | Code review |
| Incorrect variable logging | 0 | Log validation |

### Exception Management:
- Global exception handler (`@RestControllerAdvice`)
- Domain-specific custom exceptions:
  - `ResourceNotFoundException`
  - `DuplicateResourceException`
  - `BusinessValidationException`
- Proper exception propagation up the call stack
- Catching specific exceptions (not generic `Exception`)

### Error Responses:
- Consistent error format with code, message, timestamp
- No stack traces exposed to clients in production
- User-friendly error messages
- Internal details not revealed
- Appropriate HTTP status codes
- Error detail arrays for validation failures

### Error Handling Best Practices:
- Proper error logging with context
- Exception handling patterns
- Error recovery strategies

### Common Issues & Fixes

#### Issue 1: Missing global exception handler
**Detection:** Exceptions propagate to framework default handler
**Fix:**
```java
// ✅ Add global handler
@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleNotFound(ResourceNotFoundException ex) {
        return ResponseEntity.status(404).body(new ErrorResponse(ex.getMessage()));
    }
}
```

#### Issue 2: Exposing stack traces
**Detection:** Exception details in production responses
**Fix:** Log full exception, return sanitized message to client

#### Issue 3: Catching generic Exception
**Detection:** `catch (Exception e)` blocks
**Fix:**
```java
// ❌ Before
catch (Exception e) { ... }

// ✅ After
catch (ResourceNotFoundException | ValidationException e) { ... }
```

#### Issue 4: Inconsistent error format
**Detection:** Different error response structures
**Fix:** Use standardized `ApiResponse<T>` wrapper for all responses

---

## **5. ARCHITECTURE & DESIGN**

### Summary
Ensures proper architectural patterns and design principles are followed in microservices development. Focuses on maintaining clean separation of concerns, applying SOLID principles, and creating scalable, maintainable code structures.

### Confidence Level
**High** - Architecture violations are easily detectable through static analysis and code review patterns.

### Metrics
| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Layer violations | 0 | Static analysis (PMD, Checkstyle) |
| Business logic in controllers | 0 | Code review + pattern detection |
| Class dependencies | ≤ 4 per class | Dependency analysis tools |
| Method parameters | ≤ 3 per method | Static analysis |
| Methods per class | ≤ 10 public methods | Code metrics |
| Unnecessary abstraction | 0 | Architecture review |
| Fake configuration keys | 0 | Configuration validation |
| Wrong function parameters | 0 | Type checking & validation |
| Architecture invented without instruction | 0 | Design review |
| Dependency version mismatch | 0 | Dependency analysis |
| Unnecessary libraries | 0 | Dependency audit |
| SOLID principles violations | 0 | Design pattern analysis |
| Over-engineered layers | 0 | Architecture review |

### Items Covered:
- Layer separation enforcement (Controller → Service → Repository)
- No business logic in controllers
- Design patterns and best practices
- Dependency management and justification
- Single responsibility principle
- Class cohesion and coupling
- Scalability considerations
- Over-engineering vs under-engineering assessment
- Method-level analysis (purpose, parameters, return values)
- Class-level analysis (size, dependencies, cohesion)

### Common Issues & Fixes

#### Issue 1: Controllers accessing repositories directly
**Detection:** Controller class has `@Autowired` repository
**Fix:**
```java
// ❌ Before
@RestController
public class UserController {
    @Autowired private UserRepository repository;
}

// ✅ After
@RestController
public class UserController {
    @Autowired private UserService userService;
}
```

#### Issue 2: Business logic in controllers
**Detection:** Controllers contain conditional logic, calculations, or validations
**Fix:** Move all business logic to service layer

#### Issue 3: Too many dependencies (>4)
**Detection:** Constructor has more than 4 parameters
**Fix:** Refactor into smaller, focused classes or use facade pattern

---

## **6. PERFORMANCE OPTIMIZATION**

### Summary
Optimizes application performance through efficient database queries, caching strategies, and resource management. Prevents performance bottlenecks and ensures scalability.

### Confidence Level
**Medium-High** - Performance issues can be detected through profiling and load testing, but may vary by environment.

### Metrics
| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| N+1 queries | 0 occurrences | Hibernate statistics, query logging |
| Average response time | < 200ms | APM tools (New Relic, Datadog) |
| Database connection pool usage | < 80% | HikariCP metrics |
| Cache hit ratio | > 80% | Cache monitoring |
| Thread pool saturation | < 70% | JVM monitoring |
| Memory usage | < 80% heap | JVM profiling |

### Database Performance:
- N+1 query prevention using `@EntityGraph` or fetch joins
- `@BatchSize` for collections
- Pagination requirements for all list endpoints (`Page<T>`)
- Connection pool configuration (HikariCP settings)
- Proper indexing considerations
- Query optimization
- Transaction boundaries

### Caching:
- Caching strategy for frequently accessed data
- Cache invalidation patterns
- `@Cacheable`, `@CacheEvict`, `@CachePut` annotations
- TTL configuration
- Redis integration considerations

### Resource Management:
- No large object creation in loops
- Thread-safe operations
- Stream vs collection appropriateness
- Memory leak prevention
- Async operations for long-running tasks (`@Async`)
- Thread pool configuration
- Transaction optimization

### Common Issues & Fixes

#### Issue 1: N+1 query problem
**Detection:** Multiple SELECT queries for related entities
**Fix:**
```java
// ❌ Before
@Query("SELECT u FROM User u")
List<User> findAll(); // Triggers N+1 for orders

// ✅ After
@EntityGraph(attributePaths = {"orders"})
List<User> findAll();
```

#### Issue 2: Missing pagination
**Detection:** List endpoints without Pageable parameter
**Fix:**
```java
// ❌ Before
List<User> getAllUsers();

// ✅ After
Page<User> getAllUsers(Pageable pageable);
```

#### Issue 3: Inefficient caching
**Detection:** Repeated database queries for same data
**Fix:**
```java
// ✅ Add caching
@Cacheable(value = "products", key = "#id")
public Product getById(Long id) { ... }
```

#### Issue 4: Large objects in loops
**Detection:** Object instantiation inside loops
**Fix:** Move object creation outside loop or use object pooling

---

## **7. LOGGING**

### Summary
Implements structured, secure logging with appropriate levels and context to enable effective debugging, monitoring, and audit trails without exposing sensitive information.

### Confidence Level
**High** - Logging practices are verifiable through log output analysis and static code analysis.

### Metrics
| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Sensitive data in logs | 0 occurrences | Log scanning tools |
| System.out.println usage | 0 | Static analysis |
| Missing correlation IDs | 0% | Log analysis |
| Incorrect log levels | < 5% | Manual review |
| Exception logging | 100% | Exception handler audit |
| MDC usage | 100% | Request tracing check |
| Tracing spans added | 100% | Distributed tracing check |
| Structured logging | 100% | Log format validation |

### Structured Logging:
- SLF4J usage (not `System.out.println`)
- MDC (Mapped Diagnostic Context) for correlation IDs
- Request path tracking
- Request tracing across services

### Log Levels:
- **ERROR:** Exceptions and failures requiring immediate attention
- **WARN:** Recoverable issues, deprecation notices
- **INFO:** Business events, key operations
- **DEBUG:** Technical details for troubleshooting
- **TRACE:** Detailed debugging (rarely used in production)

### Security:
- No sensitive data in logs (passwords, tokens, PII, credit cards)
- Proper data masking before logging
- No passwords/API keys in log output

### Best Practices:
- Entry/exit logging at DEBUG level
- Correlation ID in all logs (`X-Correlation-ID`)
- Aspect-oriented logging (`@Aspect`)
- Method execution time logging
- Exception logging with stack traces (ERROR level only)
- Consistent log patterns with logback/log4j2

### Common Issues & Fixes

#### Issue 1: Using System.out.println
**Detection:** `System.out` or `System.err` calls in code
**Fix:**
```java
// ❌ Before
System.out.println("User created: " + userId);

// ✅ After
log.info("User created with ID: {}", userId);
```

#### Issue 2: Logging sensitive data
**Detection:** PII, passwords, tokens in log statements
**Fix:**
```java
// ❌ Before
log.info("User: {}, Password: {}", username, password);

// ✅ After
log.info("User login attempt: {}", username);
```

#### Issue 3: Missing correlation ID
**Detection:** Logs without request tracing
**Fix:**
```java
// ✅ Add MDC filter
MDC.put("correlationId", request.getHeader("X-Correlation-ID"));
```

#### Issue 4: Wrong log level
**Detection:** INFO used for debug details, ERROR for warnings
**Fix:** Follow log level guidelines (ERROR for exceptions, INFO for business events, DEBUG for details)

---

## **8. LLM AS A JUDGE**

### Summary
Detects AI-generated code quality issues including hallucinated functions, invented libraries, placeholder code, and other common problems from AI-assisted development. Ensures AI-generated code is production-ready and not relying on non-existent functionality.

### Confidence Level
**High** - AI-specific patterns are detectable through code analysis and validation against known libraries/APIs.

### Metrics
| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Hallucinated Functions | 0 | Function validation against actual APIs |
| Non-existent Libraries | 0 | Import validation, dependency check |
| Fake Configuration Keys | 0 | Config validation against documentation |
| Generic Placeholder Code | 0 | TODO/placeholder detection |
| Invented API Endpoints | 0 | Route validation against framework |
| Copy-Paste Inconsistencies | 0 | Code duplication analysis |
| Overconfident Assumptions | 0 | Comment vs implementation validation |
| Inappropriate Design Patterns | 0 | Pattern appropriateness analysis |
| Missing Error Context | 0 | Error handling completeness |
| Unrealistic Performance Claims | 0 | Optimization validation |

### AI-Generated Code Issues:
- No invented functions or methods that don't exist in the actual framework
- All imported libraries and dependencies actually exist
- Configuration keys are valid and documented
- No "TODO" or placeholder implementations in production code
- No fictional REST endpoints or routes
- No duplicated AI-generated blocks with slight variations
- Comments accurately describe implemented functionality
- Design patterns fit the actual use case
- Error handling accounts for real failure scenarios
- Performance optimizations actually work as claimed

### Common Issues & Fixes

#### Issue 1: Hallucinated Function Calls
**Detection:** Function calls to methods that don't exist in the framework
**Fix:**
```java
// ❌ Before (AI invented this method)
repository.findByNameAndEmailOptimized(name, email);

// ✅ After (Use actual Spring Data method)
repository.findByNameAndEmail(name, email);
```

#### Issue 2: Non-existent Library
**Detection:** Imports that reference packages not in dependencies
**Fix:**
```java
// ❌ Before (AI invented this library)
import com.fancy.ai.OptimizedCache;

// ✅ After (Use actual Spring Cache)
import org.springframework.cache.annotation.Cacheable;
```

#### Issue 3: Fake Configuration Keys
**Detection:** Configuration keys that don't exist in application.yml schema
**Fix:**
```yaml
# ❌ Before (AI invented this key)
spring.datasource.auto-optimize: true

# ✅ After (Use actual Spring properties)
spring.jpa.properties.hibernate.jdbc.batch_size: 20
```

#### Issue 4: Generic Placeholder Code
**Detection:** TODO comments or incomplete implementations in production
**Fix:**
```java
// ❌ Before
public void processPayment(Order order) {
    // TODO: Implement payment processing
    throw new UnsupportedOperationException("Not implemented yet");
}

// ✅ After
public void processPayment(Order order) {
    paymentGateway.charge(order.getTotal(), order.getPaymentMethod());
    orderRepository.updateStatus(order.getId(), OrderStatus.PAID);
}
```

#### Issue 5: Overconfident Comments
**Detection:** Comments claiming functionality that isn't actually implemented
**Fix:**
```java
// ❌ Before
// This method uses advanced caching and handles all edge cases
public User getUser(Long id) {
    return userRepository.findById(id).orElse(null);
}

// ✅ After
// Retrieves user by ID, returns null if not found
// TODO: Add caching and error handling
public User getUser(Long id) {
    return userRepository.findById(id).orElse(null);
}
```

---

## **9. DOMAIN-SPECIFIC EXTENSIONS**

### Summary
Industry-specific rules and compliance requirements tailored to different domains like Financial Services, Healthcare, and E-Commerce.

### Confidence Level
**High** - Domain rules are well-defined by industry standards and regulations.

### Metrics
| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Financial Services** | | |
| BigDecimal usage for money | 100% | Static analysis |
| Transaction audit trail | 100% | Audit log verification |
| Regulatory compliance | 100% | Compliance scan |
| PHI encryption | 100% | Security audit |
| HIPAA compliance | 100% | Compliance tools |
| Access logging | 100% | Audit trail check |
| Payment data logging | 0 occurrences | Log scanning |
| Order idempotency | 100% | API testing |
| Transactional integrity | 100% | Database testing |

### Financial Services:
- All monetary calculations must use `BigDecimal`
- Transaction IDs masked in logs
- Audit trail required for financial operations
- Regulatory compliance
- Data field validation

### Healthcare:
- PHI (Protected Health Information) encryption at rest and in transit
- HIPAA compliance logging
- Access logging for patient data
- Minimum necessary data principle
- Data retention policies enforcement

### E-Commerce:
- Payment data never logged
- Order idempotency keys required
- Inventory updates must be transactional
- Price calculations handle currency properly
- Order state machine enforcement

### Customization Framework:
- How to add domain-specific rules
- Custom rule categories structure
- Domain-specific scoring adjustments
- Industry-specific thresholds

### Common Issues & Fixes

#### Issue 1: Using double/float for money calculations
**Detection:** Financial fields as `double` or `float`
**Fix:**
```java
// ❌ Before (Financial)
private double amount;

// ✅ After (Financial)
private BigDecimal amount;
```

#### Issue 2: Missing PHI encryption
**Detection:** Healthcare sensitive fields without encryption
**Fix:**
```java
// ✅ Add encryption converter
@Convert(converter = EncryptedStringConverter.class)
private String ssn;
```

#### Issue 3: Payment data in logs
**Detection:** Credit card numbers in log files (E-Commerce)
**Fix:** Never log payment data; use transaction IDs only

#### Issue 4: Missing audit trail
**Detection:** Financial transactions without audit logging
**Fix:**
```java
// ✅ Add audit logging
@Audited
@Entity
public class Transaction {
    // fields
}
```

---

## **Summary Statistics**

| Metric | Value |
|--------|-------|
| **Total Core Categories** | 9 streamlined areas |
| **Total Metrics Analyzed** | 77 metrics |
| **Total Rules** | 50+ specific rules |
| **Severity Levels** | 3 (Critical, Warning, Info) |
| **Domain Extensions** | 3+ (Financial, Healthcare, E-Commerce) |
| **Primary Focus** | Code Quality, Custom Critique, Security, Error Handling, Architecture, Performance, Logging, LLM as a Judge, Domain Extensions |

**Metrics Breakdown:**
- Code Quality: 21 metrics
- Custom Critique: 10 metrics
- Security: 8 metrics
- Error Handling: 10 metrics
- Architecture: 13 metrics
- Performance: 6 metrics
- Logging: 8 metrics
- LLM as a Judge: 10 metrics
- Domain: 1 metric

---

*Generated from consolidated documentation analysis*  
*Last Updated: December 10, 2024*
