# Processors

## EggAlarm Processors

### EggAlarmCreationProcessor

**Entity**: EggAlarm
**Input Data**: userId, eggType, title (optional)
**Description**: Creates a new egg alarm with the specified parameters and calculates the cooking duration based on egg type.

**Expected Entity Output**: 
- Creates new EggAlarm entity with CREATED state
- Sets duration based on eggType (soft: 180s, medium: 240s, hard: 360s)
- Sets scheduledTime and createdAt
- Transition: null (entity creation)

**Pseudocode**:
```
process(inputData):
    validate eggType is one of [SOFT_BOILED, MEDIUM_BOILED, HARD_BOILED]
    validate userId exists
    
    duration = getDurationForEggType(eggType)
    currentTime = getCurrentTime()
    
    eggAlarm = new EggAlarm()
    eggAlarm.id = generateUniqueId()
    eggAlarm.userId = inputData.userId
    eggAlarm.eggType = inputData.eggType
    eggAlarm.duration = duration
    eggAlarm.createdAt = currentTime
    eggAlarm.scheduledTime = currentTime + duration
    eggAlarm.title = inputData.title or getDefaultTitle(eggType)
    eggAlarm.isActive = false
    
    save(eggAlarm)
    return eggAlarm
```

### EggAlarmActivationProcessor

**Entity**: EggAlarm
**Input Data**: eggAlarmId
**Description**: Activates the egg alarm and starts the countdown timer.

**Expected Entity Output**: 
- Updates EggAlarm entity to ACTIVE state
- Sets isActive to true
- Recalculates scheduledTime from current time
- Transition: CREATED → ACTIVE

**Pseudocode**:
```
process(inputData):
    eggAlarm = getEggAlarmById(inputData.eggAlarmId)
    currentTime = getCurrentTime()
    
    eggAlarm.isActive = true
    eggAlarm.scheduledTime = currentTime + eggAlarm.duration
    
    startTimer(eggAlarm.id, eggAlarm.duration)
    save(eggAlarm)
    
    return eggAlarm
```

### EggAlarmCompletionProcessor

**Entity**: EggAlarm
**Input Data**: eggAlarmId
**Description**: Completes the alarm when the timer expires and sends notification to the user.

**Expected Entity Output**: 
- Updates EggAlarm entity to COMPLETED state
- Sets isActive to false
- Sends notification to user
- Transition: ACTIVE → COMPLETED

**Pseudocode**:
```
process(inputData):
    eggAlarm = getEggAlarmById(inputData.eggAlarmId)
    user = getUserById(eggAlarm.userId)
    
    eggAlarm.isActive = false
    save(eggAlarm)
    
    notificationMessage = "Your " + eggAlarm.eggType + " eggs are ready!"
    sendNotification(user, notificationMessage)
    playAlarmSound()
    
    return eggAlarm
```

### EggAlarmCancellationProcessor

**Entity**: EggAlarm
**Input Data**: eggAlarmId
**Description**: Cancels an active or created alarm.

**Expected Entity Output**: 
- Updates EggAlarm entity to CANCELLED state
- Sets isActive to false
- Stops any running timer
- Transition: CREATED → CANCELLED or ACTIVE → CANCELLED

**Pseudocode**:
```
process(inputData):
    eggAlarm = getEggAlarmById(inputData.eggAlarmId)
    
    if eggAlarm.isActive:
        stopTimer(eggAlarm.id)
    
    eggAlarm.isActive = false
    save(eggAlarm)
    
    return eggAlarm
```

### EggAlarmResetProcessor

**Entity**: EggAlarm
**Input Data**: eggAlarmId
**Description**: Resets a completed alarm to create a new one with the same settings.

**Expected Entity Output**: 
- Creates new EggAlarm entity with CREATED state using same settings
- Transition: COMPLETED → CREATED

**Pseudocode**:
```
process(inputData):
    originalAlarm = getEggAlarmById(inputData.eggAlarmId)
    currentTime = getCurrentTime()
    
    newAlarm = new EggAlarm()
    newAlarm.id = generateUniqueId()
    newAlarm.userId = originalAlarm.userId
    newAlarm.eggType = originalAlarm.eggType
    newAlarm.duration = originalAlarm.duration
    newAlarm.title = originalAlarm.title
    newAlarm.createdAt = currentTime
    newAlarm.scheduledTime = currentTime + originalAlarm.duration
    newAlarm.isActive = false
    
    save(newAlarm)
    return newAlarm
```

### EggAlarmExpirationProcessor

**Entity**: EggAlarm
**Input Data**: eggAlarmId
**Description**: Marks an alarm as expired when notification timeout is reached.

**Expected Entity Output**: 
- Updates EggAlarm entity to EXPIRED state
- Sets isActive to false
- Transition: ACTIVE → EXPIRED

**Pseudocode**:
```
process(inputData):
    eggAlarm = getEggAlarmById(inputData.eggAlarmId)
    
    eggAlarm.isActive = false
    save(eggAlarm)
    
    stopAlarmSound()
    return eggAlarm
```

## User Processors

### UserRegistrationProcessor

**Entity**: User
**Input Data**: username, email, preferences (optional)
**Description**: Creates a new user account.

**Expected Entity Output**: 
- Creates new User entity with REGISTERED state
- Transition: null (entity creation)

**Pseudocode**:
```
process(inputData):
    validate email format
    validate username is unique
    validate email is unique
    
    user = new User()
    user.id = generateUniqueId()
    user.username = inputData.username
    user.email = inputData.email
    user.createdAt = getCurrentTime()
    user.preferences = inputData.preferences or getDefaultPreferences()
    
    save(user)
    sendVerificationEmail(user.email)
    
    return user
```

### UserActivationProcessor

**Entity**: User
**Input Data**: userId
**Description**: Activates a registered user account.

**Expected Entity Output**: 
- Updates User entity to ACTIVE state
- Transition: REGISTERED → ACTIVE

**Pseudocode**:
```
process(inputData):
    user = getUserById(inputData.userId)
    save(user)
    
    sendWelcomeEmail(user.email)
    return user
```

### UserSuspensionProcessor

**Entity**: User
**Input Data**: userId, reason
**Description**: Suspends an active user account.

**Expected Entity Output**: 
- Updates User entity to SUSPENDED state
- Transition: ACTIVE → SUSPENDED

**Pseudocode**:
```
process(inputData):
    user = getUserById(inputData.userId)
    save(user)
    
    cancelAllActiveAlarms(user.id)
    sendSuspensionNotification(user.email, inputData.reason)
    
    return user
```

### UserReactivationProcessor

**Entity**: User
**Input Data**: userId
**Description**: Reactivates a suspended user account.

**Expected Entity Output**: 
- Updates User entity to ACTIVE state
- Transition: SUSPENDED → ACTIVE

**Pseudocode**:
```
process(inputData):
    user = getUserById(inputData.userId)
    save(user)
    
    sendReactivationNotification(user.email)
    return user
```

### UserDeletionProcessor

**Entity**: User
**Input Data**: userId
**Description**: Marks a user account for deletion.

**Expected Entity Output**: 
- Updates User entity to DELETED state
- Transition: ACTIVE → DELETED or SUSPENDED → DELETED

**Pseudocode**:
```
process(inputData):
    user = getUserById(inputData.userId)
    save(user)
    
    cancelAllActiveAlarms(user.id)
    scheduleDataDeletion(user.id)
    
    return user
```
