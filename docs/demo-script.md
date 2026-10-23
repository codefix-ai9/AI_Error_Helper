# 10-Minute Demonstration Script

This script provides an evaluator or instructor walkthrough for the AI-Based Programming Error Helper dashboard. It covers 6 distinct scenarios showing multi-language support, hybrid determinism, graceful degradation, and persistence.

---

## Demonstration Overview

| Step | Time | Scenario | Key Teaching / Architectural Point |
| :---: | :---: | :--- | :--- |
| **1** | 00:00 - 02:00 | **Python NameError** | AST parser + rule engine + diff view + provenance badges |
| **2** | 02:00 - 03:30 | **JavaScript TypeError** | Multi-language support + MOCK mode badge indicator |
| **3** | 03:30 - 05:00 | **Java NullPointer** | Compiler/runtime stack trace interpretation |
| **4** | 05:00 - 06:30 | **Unknown / Ambiguous Case** | Authority lock: no hallucination, graceful fallback |
| **5** | 06:30 - 08:00 | **AI Provider Disabled** | Verbatim §7.7 banner, 100% deterministic guidance |
| **6** | 08:00 - 10:00 | **History & Analytics** | SQLite persistence, search, filters, SVG trend chart |

---

## Scenario 1: Python Undefined Variable (00:00 - 02:00)

### Action
1. Open the dashboard at `http://127.0.0.1:5173/`.
2. Select **Python** from the Language dropdown.
3. Paste the following into the **Source Code** and **Error Message** panels:

**Source Code**:
```python
def compute_total(prices):
    subtotal = sum(prices)
    tax = subtotal * 0.08
    return total + tax

print(compute_total([10, 20, 30]))
```

**Error Message**:
```text
Traceback (most recent call last):
  File "main.py", line 4, in compute_total
    return total + tax
NameError: name 'total' is not defined
```

4. Click **Run Hybrid Analysis**.

### What to Observe & Explain
- **Provenance Badges**: Notice the green `STATIC FACT` badge next to Category (`Name / Reference`), Severity (`HIGH`), and Line (`4`).
- **Static Findings**: Parser confirms `total` is accessed before definition.
- **AI Explanation**: Purple `AI ASSISTED` badge explaining identifier binding and variable scope.
- **Diff View**: Side-by-side view showing `- return total + tax` vs `+ return subtotal + tax`.
- **Verification Note**: Confirms syntax check passes on corrected snippet.

---

## Scenario 2: JavaScript TypeError (02:00 - 03:30)

### Action
1. Select **JavaScript** from the Language dropdown.
2. Paste the following:

**Source Code**:
```javascript
function getUserDisplayName(user) {
  return user.profile.name.toUpperCase();
}

console.log(getUserDisplayName(null));
```

**Error Message**:
```text
TypeError: Cannot read properties of null (reading 'profile')
    at getUserDisplayName (app.js:2:15)
    at Object.<anonymous> (app.js:5:13)
```

3. Click **Run Hybrid Analysis**.

### What to Observe & Explain
- Demonstrates JavaScript runtime classification.
- Line 2 accurately pinpointed.
- Suggested fix introduces optional chaining (`user?.profile?.name`) or null check guards.

---

## Scenario 3: Java NullPointerException (03:30 - 05:00)

### Action
1. Select **Java** from the Language dropdown.
2. Paste the following:

**Source Code**:
```java
public class UserManager {
    public static void main(String[] args) {
        String username = null;
        if (username.equals("admin")) {
            System.out.println("Access granted.");
        }
    }
}
```

**Error Message**:
```text
Exception in thread "main" java.lang.NullPointerException: Cannot invoke "String.equals(Object)" because "username" is null
    at UserManager.main(UserManager.java:4)
```

3. Click **Run Hybrid Analysis**.

### What to Observe & Explain
- Error accurately classified as `Runtime` with `HIGH` severity.
- Highlights literal-first pattern: `"admin".equals(username)` or explicit `username != null` check.

---

## Scenario 4: Ambiguous / Unknown Case (05:00 - 06:30)

### Action
1. Select **Python**.
2. Paste an uninformative error:

**Source Code**:
```python
def process_data(data):
    # complex processing
    return [d * 2 for d in data]
```

**Error Message**:
```text
Application error code: 0x8849F - unexpected state
```

3. Click **Run Hybrid Analysis**.

### What to Observe & Explain
- **Authority Lock**: The system classifies the error strictly as `Unknown / Requires Review` with `confidence: null`.
- **Anti-Hallucination**: Rather than pretending to know what went wrong, the dashboard displays an uncertainty note and prompts the student to provide reproducible error tracebacks.

---

## Scenario 5: AI-Off / Graceful Fallback (06:30 - 08:00)

### Action
1. Set `LLM_PROVIDER=disabled` in `backend/.env` (or simulate AI failure).
2. Analyze any Python error.

### What to Observe & Explain
- **Verbatim Banner**: The warning banner appears prominently:
  > *"AI explanation unavailable. Showing deterministic static analysis and rule-based guidance only."*
- **No Crash / 200 OK**: The app never crashes; the student still receives confirmed line numbers, rule matches, and template debugging steps.

---

## Scenario 6: History & Analytics (08:00 - 10:00)

### Action
1. Click the **History** tab in the navigation header.
   - Show the table populated from the previous analyses.
   - Test the debounced search bar (type `total` to filter).
   - Filter by language: select `JavaScript`.
   - Click **View** on an item to inspect the stored result.
   - Delete a record using the red **Delete** button and confirm deletion.
2. Click the **Analytics** tab.
   - Show the metric summary cards (Total Analyses, Most Common Error, etc.).
   - Review the SVG activity trend chart.
   - Review the CSS distribution bars for error categories and severity levels.
3. Click **Analyze** tab and use **Export JSON** or **Export Text** to demonstrate clipboard/file export.
