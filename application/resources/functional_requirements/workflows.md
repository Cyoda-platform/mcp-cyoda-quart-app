# Workflows for Purrfect Pets API

## Pet Workflow

**Name:** PetWorkflow

**States:** Available, Pending, Sold

**Transitions:**

1. **Initial → Available** (Automatic)
   - Processor: PetRegistrationProcessor
   - Criterion: None
   - Description: Register new pet in the system

2. **Available → Pending** (Automatic)
   - Processor: PetReservationProcessor
   - Criterion: PetAvailabilityCriterion
   - Description: Reserve pet when added to order

3. **Pending → Available** (Manual)
   - Processor: PetReleaseProcessor
   - Criterion: None
   - Description: Release pet reservation if order cancelled

4. **Pending → Sold** (Automatic)
   - Processor: PetSaleProcessor
   - Criterion: OrderCompletionCriterion
   - Description: Mark pet as sold when order is completed

```mermaid
stateDiagram-v2
    [*] --> Available : PetRegistrationProcessor
    Available --> Pending : PetReservationProcessor / PetAvailabilityCriterion
    Pending --> Available : PetReleaseProcessor (Manual)
    Pending --> Sold : PetSaleProcessor / OrderCompletionCriterion
    Sold --> [*]
```

---

## Category Workflow

**Name:** CategoryWorkflow

**States:** Active, Inactive

**Transitions:**

1. **Initial → Active** (Automatic)
   - Processor: CategoryActivationProcessor
   - Criterion: None
   - Description: Activate new category

2. **Active → Inactive** (Manual)
   - Processor: CategoryDeactivationProcessor
   - Criterion: CategoryUsageCriterion
   - Description: Deactivate category if no pets assigned

3. **Inactive → Active** (Manual)
   - Processor: CategoryReactivationProcessor
   - Criterion: None
   - Description: Reactivate category

```mermaid
stateDiagram-v2
    [*] --> Active : CategoryActivationProcessor
    Active --> Inactive : CategoryDeactivationProcessor / CategoryUsageCriterion (Manual)
    Inactive --> Active : CategoryReactivationProcessor (Manual)
```

---

## User Workflow

**Name:** UserWorkflow

**States:** Active, Inactive, Suspended

**Transitions:**

1. **Initial → Active** (Automatic)
   - Processor: UserRegistrationProcessor
   - Criterion: None
   - Description: Register new user

2. **Active → Suspended** (Manual)
   - Processor: UserSuspensionProcessor
   - Criterion: UserViolationCriterion
   - Description: Suspend user for policy violations

3. **Active → Inactive** (Manual)
   - Processor: UserDeactivationProcessor
   - Criterion: None
   - Description: Deactivate user account

4. **Suspended → Active** (Manual)
   - Processor: UserReactivationProcessor
   - Criterion: SuspensionReviewCriterion
   - Description: Reactivate suspended user

5. **Inactive → Active** (Manual)
   - Processor: UserReactivationProcessor
   - Criterion: None
   - Description: Reactivate inactive user

```mermaid
stateDiagram-v2
    [*] --> Active : UserRegistrationProcessor
    Active --> Suspended : UserSuspensionProcessor / UserViolationCriterion (Manual)
    Active --> Inactive : UserDeactivationProcessor (Manual)
    Suspended --> Active : UserReactivationProcessor / SuspensionReviewCriterion (Manual)
    Inactive --> Active : UserReactivationProcessor (Manual)
```

---

## Order Workflow

**Name:** OrderWorkflow

**States:** Placed, Approved, Preparing, Shipped, Delivered, Cancelled

**Transitions:**

1. **Initial → Placed** (Automatic)
   - Processor: OrderCreationProcessor
   - Criterion: None
   - Description: Create new order

2. **Placed → Approved** (Automatic)
   - Processor: OrderApprovalProcessor
   - Criterion: OrderValidationCriterion
   - Description: Approve valid orders

3. **Placed → Cancelled** (Manual)
   - Processor: OrderCancellationProcessor
   - Criterion: None
   - Description: Cancel order before approval

4. **Approved → Preparing** (Automatic)
   - Processor: OrderPreparationProcessor
   - Criterion: InventoryAvailabilityCriterion
   - Description: Start order preparation

5. **Approved → Cancelled** (Manual)
   - Processor: OrderCancellationProcessor
   - Criterion: CancellationPolicyCriterion
   - Description: Cancel approved order

6. **Preparing → Shipped** (Manual)
   - Processor: OrderShippingProcessor
   - Criterion: None
   - Description: Ship prepared order

7. **Shipped → Delivered** (Manual)
   - Processor: OrderDeliveryProcessor
   - Criterion: None
   - Description: Mark order as delivered

```mermaid
stateDiagram-v2
    [*] --> Placed : OrderCreationProcessor
    Placed --> Approved : OrderApprovalProcessor / OrderValidationCriterion
    Placed --> Cancelled : OrderCancellationProcessor (Manual)
    Approved --> Preparing : OrderPreparationProcessor / InventoryAvailabilityCriterion
    Approved --> Cancelled : OrderCancellationProcessor / CancellationPolicyCriterion (Manual)
    Preparing --> Shipped : OrderShippingProcessor (Manual)
    Shipped --> Delivered : OrderDeliveryProcessor (Manual)
    Cancelled --> [*]
    Delivered --> [*]
```
