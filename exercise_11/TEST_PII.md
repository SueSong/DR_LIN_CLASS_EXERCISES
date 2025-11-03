# How to Test PII Detection

The HITL system automatically detects PII (Personally Identifiable Information) in crisis messages.

## PII Types Detected

The system detects:
- **Email addresses**
- **Phone numbers**
- **SSN (Social Security Numbers)**
- **Credit card numbers**
- **Street addresses**
- **IP addresses**

## Test Messages with PII

Try sending these crisis messages that include PII:

### 1. Email + Crisis
```
My teenager said they want to kill themselves. Contact me at parent@example.com
```

### 2. Phone Number + Crisis
```
I think my child is being abused. My number is 555-123-4567
```

### 3. SSN + Crisis
```
My child is cutting themselves. Their SSN is 123-45-6789
```

### 4. Credit Card + Crisis
```
This is an emergency! My card is 4532-1234-5678-9010
```

### 5. Address + Crisis
```
I found my child unconscious. We're at 123 Main Street, Anytown, CA 90210
```

### 6. IP Address + Crisis
```
My teenager is suicidal. Their IP is 192.168.1.1
```

### 7. Multiple PII Types
```
Emergency! My child took pills. Contact me at parent@email.com or 555-999-8888. We live at 456 Oak Avenue, City, NY 10001
```

## What to Check

After sending a message with PII:

1. **In HITL Queue:**
   - Click on the crisis item
   - Look for "Detected PII" section
   - You should see:
     - PII type (email, phone, etc.)
     - The actual PII value (partially masked or shown)
     - Context around the PII

2. **In Backend Logs:**
   - The HITL queuing will show PII was detected
   - Check the `detected_pii` field in the queue item

## Example Test

1. Send: "My teenager said they want to kill themselves. Contact me at parent@example.com"
2. Go to HITL queue
3. Click on the item
4. Check "Detected PII" section - should show:
   - Type: email
   - Text: parent@example.com
   - Context: surrounding text

PII detection happens automatically when a message is queued to HITL!

