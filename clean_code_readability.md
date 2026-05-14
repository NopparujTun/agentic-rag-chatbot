# Clean Code Readability Techniques

A practical guide to writing code that humans — not just computers — can understand.

---

## 1. Meaningful Naming

The most powerful readability tool is choosing names that clearly express intent.

### Variables & Constants

Bad names force readers to guess. Good names self-document.

```python
# ❌ Hard to understand
d = 86400
t = d * 7

# ✅ Self-explanatory
SECONDS_PER_DAY = 86400
seconds_per_week = SECONDS_PER_DAY * 7
```

### Functions

A function name should describe **what it does**, not how it does it.

```javascript
// ❌ Vague
function process(data) { ... }

// ✅ Descriptive
function filterExpiredSubscriptions(subscriptions) { ... }
```

### Avoid Abbreviations (unless universal)

```python
# ❌ Cryptic
usr_mgr.upd_pwd(u, p)

# ✅ Clear
user_manager.update_password(user, new_password)
```

> **Rule of thumb:** If someone has to ask "what does this mean?", rename it.

---

## 2. Functions Should Do One Thing (Single Responsibility)

A function that does multiple things is harder to read, test, and maintain.

```python
# ❌ Does too much
def process_user(user):
    user["name"] = user["name"].strip()
    db.save(user)
    send_welcome_email(user["email"])
    log_event("user_created", user["id"])

# ✅ Each function has one job
def normalize_user(user):
    user["name"] = user["name"].strip()
    return user

def register_user(user):
    user = normalize_user(user)
    db.save(user)
    send_welcome_email(user["email"])
    log_event("user_created", user["id"])
```

> **Rule of thumb:** If you use "and" to describe what a function does, split it.

---

## 3. Keep Functions Short

Short functions are easier to read, test, and reuse. Aim for functions that fit on one screen (roughly 20–30 lines max).

```javascript
// ❌ Long, hard to scan
function handleOrder(order) {
    if (!order.items || order.items.length === 0) {
        throw new Error("Empty order");
    }
    let total = 0;
    for (const item of order.items) {
        total += item.price * item.quantity;
    }
    if (order.coupon === "SAVE10") {
        total = total * 0.9;
    }
    const tax = total * 0.08;
    order.finalAmount = total + tax;
    db.save(order);
    emailService.sendConfirmation(order.userId, order.finalAmount);
}

// ✅ Broken into readable steps
function calculateSubtotal(items) {
    return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
}

function applyDiscount(subtotal, coupon) {
    return coupon === "SAVE10" ? subtotal * 0.9 : subtotal;
}

function addTax(amount, rate = 0.08) {
    return amount + amount * rate;
}

function handleOrder(order) {
    if (!order.items?.length) throw new Error("Empty order");
    const subtotal = calculateSubtotal(order.items);
    const discounted = applyDiscount(subtotal, order.coupon);
    order.finalAmount = addTax(discounted);
    db.save(order);
    emailService.sendConfirmation(order.userId, order.finalAmount);
}
```

---

## 4. Comments: Explain **Why**, Not **What**

Code should describe *what* it does. Comments should explain *why* a decision was made.

```python
# ❌ Redundant — code already says this
i += 1  # increment i by 1

# ❌ Outdated comment (dangerous)
# Multiply by 2 to convert
result = value * 3  # someone changed the code but not the comment

# ✅ Explains non-obvious reasoning
# Use 1.03 multiplier to account for API rate-limiting headroom
max_requests = base_limit * 1.03

# ✅ Documents why an unusual approach was chosen
# Sorting twice is intentional: first by name for stability,
# then by priority — Python's sort is stable, so order is preserved
users.sort(key=lambda u: u.name)
users.sort(key=lambda u: u.priority, reverse=True)
```

> **Rule of thumb:** If you feel the urge to write a "what" comment, your code may need better naming instead.

---

## 5. Consistent Formatting & Style

Consistent style reduces cognitive load — readers stop noticing *how* the code looks and focus on *what* it does.

```javascript
// ❌ Inconsistent — each function looks different
function getUser(id){
  return db.find(id);}

const deleteUser = (id) => {
db.delete(id)
    return true
}

// ✅ Consistent — same style everywhere
function getUser(id) {
    return db.find(id);
}

function deleteUser(id) {
    db.delete(id);
    return true;
}
```

**Practical tips:**
- Use a linter and formatter (ESLint + Prettier, Black, RuboCop, etc.)
- Agree on conventions with your team and enforce them via CI
- Avoid mixing tabs and spaces, or different quote styles

---

## 6. Avoid Magic Numbers and Strings

Hard-coded values with no explanation are called "magic" because their meaning is mysterious.

```python
# ❌ What is 7? What is 403?
if user.role == 7:
    raise Exception(403)

# ✅ Named constants are self-documenting
ROLE_ADMIN = 7
HTTP_FORBIDDEN = 403

if user.role == ROLE_ADMIN:
    raise PermissionError(HTTP_FORBIDDEN)
```

---

## 7. Positive Conditionals & Early Returns

Negative conditions and deeply nested `if` blocks are hard to follow. Prefer early exits and positive logic.

```javascript
// ❌ Hard to follow — multiple levels of nesting
function processPayment(user, order) {
    if (user) {
        if (user.isActive) {
            if (order.amount > 0) {
                chargeCard(user, order.amount);
            } else {
                throw new Error("Invalid amount");
            }
        } else {
            throw new Error("Inactive user");
        }
    } else {
        throw new Error("No user");
    }
}

// ✅ Guard clauses — flat and readable
function processPayment(user, order) {
    if (!user)            throw new Error("No user");
    if (!user.isActive)   throw new Error("Inactive user");
    if (order.amount <= 0) throw new Error("Invalid amount");

    chargeCard(user, order.amount);
}
```

---

## 8. DRY — Don't Repeat Yourself

Duplication is the enemy of readability. If you change one copy, you must remember to change all others.

```python
# ❌ Same logic repeated
def get_admin_report():
    data = db.query("SELECT * FROM orders WHERE status='complete'")
    data = [d for d in data if d["amount"] > 0]
    return sorted(data, key=lambda d: d["date"])

def get_user_report():
    data = db.query("SELECT * FROM orders WHERE status='complete'")
    data = [d for d in data if d["amount"] > 0]
    return sorted(data, key=lambda d: d["date"])

# ✅ Extract the shared logic
def get_completed_orders():
    data = db.query("SELECT * FROM orders WHERE status='complete'")
    return sorted(
        [d for d in data if d["amount"] > 0],
        key=lambda d: d["date"]
    )

def get_admin_report():
    return get_completed_orders()

def get_user_report():
    return get_completed_orders()
```

---

## 9. Use Whitespace and Structure Visually

Blank lines and grouping signal logical structure — like paragraphs in prose.

```python
# ❌ Wall of code — hard to scan
def create_order(user_id, items, coupon):
    user = db.get_user(user_id)
    if not user:
        raise ValueError("User not found")
    subtotal = sum(i["price"] * i["qty"] for i in items)
    discount = 0.1 if coupon == "SAVE10" else 0
    total = subtotal * (1 - discount)
    order = Order(user=user, items=items, total=total)
    db.save(order)
    notify_user(user, order)
    return order

# ✅ Grouped into logical steps
def create_order(user_id, items, coupon):
    # Validate input
    user = db.get_user(user_id)
    if not user:
        raise ValueError("User not found")

    # Calculate pricing
    subtotal = sum(i["price"] * i["qty"] for i in items)
    discount = 0.1 if coupon == "SAVE10" else 0
    total = subtotal * (1 - discount)

    # Persist and notify
    order = Order(user=user, items=items, total=total)
    db.save(order)
    notify_user(user, order)

    return order
```

---

## 10. Prefer Explicit Over Implicit

Clever code may feel satisfying to write but painful to read later.

```python
# ❌ Clever but confusing
result = [x for x in data if x % 2 == 0][::-1]

# ✅ Explicit steps with clear intent
even_numbers = [x for x in data if x % 2 == 0]
result = list(reversed(even_numbers))
```

```javascript
// ❌ Implicit truthy/falsy abuse
const name = user && user.profile && user.profile.name || "Anonymous";

// ✅ Clear optional chaining
const name = user?.profile?.name ?? "Anonymous";
```

---

## 11. Limit Function Arguments

More than 3 arguments is a sign a function is doing too much — or that you should use an object.

```javascript
// ❌ Hard to call correctly — easy to mix up argument order
function createUser(firstName, lastName, email, age, role, isActive) { ... }

createUser("Alice", "Smith", "alice@example.com", 30, "admin", true);

// ✅ Named parameters via an options object
function createUser({ firstName, lastName, email, age, role, isActive }) { ... }

createUser({
    firstName: "Alice",
    lastName: "Smith",
    email: "alice@example.com",
    age: 30,
    role: "admin",
    isActive: true,
});
```

---

## 12. Write Code for the Reader, Not the Machine

The ultimate principle: **code is read far more often than it is written.** Always ask:

> *"Could someone unfamiliar with this codebase understand what this does in 30 seconds?"*

If the answer is no — rename, extract, simplify, or comment until it is.

---

## Quick Reference Cheat Sheet

| Technique | Key Principle |
|---|---|
| Meaningful Naming | Names should reveal intent |
| Single Responsibility | One function = one job |
| Short Functions | Fits on one screen |
| Comments = Why | Code says what; comments say why |
| Consistent Style | Use a formatter, stick to conventions |
| No Magic Numbers | Use named constants |
| Positive Conditionals | Early returns over deep nesting |
| DRY | Don't repeat logic — extract it |
| Visual Whitespace | Group related logic together |
| Explicit Over Implicit | Clarity beats cleverness |
| Limit Arguments | Use objects for 3+ params |
| Write for the Reader | Ask: can a stranger read this? |

---

*"Any fool can write code that a computer can understand. Good programmers write code that humans can understand."*
— Martin Fowler
