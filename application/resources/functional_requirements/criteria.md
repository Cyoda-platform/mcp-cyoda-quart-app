# Criteria

## EggAlarm Criteria

### EggAlarmValidationCriterion

**Entity**: EggAlarm
**Description**: Validates that an egg alarm can be activated.

**Validation Rules**:
- Alarm must be in CREATED state
- User must exist and be in ACTIVE state
- Egg type must be valid (SOFT_BOILED, MEDIUM_BOILED, HARD_BOILED)
- Duration must be positive
- User must not have more than 5 active alarms

**Pseudocode**:
```
evaluate(eggAlarm):
    if eggAlarm.meta.state != "CREATED":
        return false, "Alarm must be in CREATED state to activate"
    
    user = getUserById(eggAlarm.userId)
    if user == null or user.meta.state != "ACTIVE":
        return false, "User must be active to activate alarm"
    
    if eggAlarm.eggType not in ["SOFT_BOILED", "MEDIUM_BOILED", "HARD_BOILED"]:
        return false, "Invalid egg type"
    
    if eggAlarm.duration <= 0:
        return false, "Duration must be positive"
    
    activeAlarmsCount = countActiveAlarmsByUser(eggAlarm.userId)
    if activeAlarmsCount >= 5:
        return false, "User cannot have more than 5 active alarms"
    
    return true, "Validation passed"
```

### EggAlarmTimerCriterion

**Entity**: EggAlarm
**Description**: Checks if the alarm timer has elapsed and the alarm should be completed.

**Validation Rules**:
- Alarm must be in ACTIVE state
- Current time must be greater than or equal to scheduledTime
- Alarm must be active

**Pseudocode**:
```
evaluate(eggAlarm):
    if eggAlarm.meta.state != "ACTIVE":
        return false, "Alarm must be in ACTIVE state"
    
    if not eggAlarm.isActive:
        return false, "Alarm must be active"
    
    currentTime = getCurrentTime()
    if currentTime < eggAlarm.scheduledTime:
        return false, "Timer has not elapsed yet"
    
    return true, "Timer has elapsed"
```

### EggAlarmExpirationCriterion

**Entity**: EggAlarm
**Description**: Checks if an alarm notification has expired (not acknowledged within timeout period).

**Validation Rules**:
- Alarm must be in ACTIVE state
- Current time must be greater than scheduledTime + notification timeout (5 minutes)
- Alarm must still be active

**Pseudocode**:
```
evaluate(eggAlarm):
    if eggAlarm.meta.state != "ACTIVE":
        return false, "Alarm must be in ACTIVE state"
    
    if not eggAlarm.isActive:
        return false, "Alarm must be active"
    
    currentTime = getCurrentTime()
    notificationTimeout = 300 // 5 minutes in seconds
    expirationTime = eggAlarm.scheduledTime + notificationTimeout
    
    if currentTime < expirationTime:
        return false, "Notification has not expired yet"
    
    return true, "Notification has expired"
```

## User Criteria

### UserVerificationCriterion

**Entity**: User
**Description**: Validates that a user can be activated (email verification completed).

**Validation Rules**:
- User must be in REGISTERED state
- Email verification must be completed
- Username and email must still be unique

**Pseudocode**:
```
evaluate(user):
    if user.meta.state != "REGISTERED":
        return false, "User must be in REGISTERED state"
    
    if not isEmailVerified(user.email):
        return false, "Email verification not completed"
    
    if not isUsernameUnique(user.username, user.id):
        return false, "Username is no longer unique"
    
    if not isEmailUnique(user.email, user.id):
        return false, "Email is no longer unique"
    
    return true, "User can be activated"
```

### UserSuspensionCriterion

**Entity**: User
**Description**: Validates that a user can be suspended.

**Validation Rules**:
- User must be in ACTIVE state
- Suspension reason must be provided
- User must not be an admin user

**Pseudocode**:
```
evaluate(user, reason):
    if user.meta.state != "ACTIVE":
        return false, "User must be in ACTIVE state to suspend"
    
    if reason == null or reason.trim().isEmpty():
        return false, "Suspension reason must be provided"
    
    if isAdminUser(user.id):
        return false, "Admin users cannot be suspended"
    
    return true, "User can be suspended"
```

### UserReactivationCriterion

**Entity**: User
**Description**: Validates that a suspended user can be reactivated.

**Validation Rules**:
- User must be in SUSPENDED state
- Suspension period must have elapsed (if applicable)
- User account must not be flagged for permanent suspension

**Pseudocode**:
```
evaluate(user):
    if user.meta.state != "SUSPENDED":
        return false, "User must be in SUSPENDED state"
    
    if isPermanentlySuspended(user.id):
        return false, "User is permanently suspended"
    
    suspensionRecord = getSuspensionRecord(user.id)
    if suspensionRecord.hasMinimumPeriod():
        currentTime = getCurrentTime()
        if currentTime < suspensionRecord.earliestReactivationTime:
            return false, "Minimum suspension period has not elapsed"
    
    return true, "User can be reactivated"
```
