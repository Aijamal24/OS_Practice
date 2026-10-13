# Practical Work 6 — Synchronization

## Variant B

### Files
- race.py: race condition without a mutex.
- race_fixed.py: fixed counter using a mutex.
- producer_consumer.py: circular buffer, semaphores and mutex.
- condition_version.py: circular buffer with a condition variable.
- barrier.py: barrier for four threads and three phases.
- lost_wakeup.py: demonstration of an incorrect if-based wait.

## Correctness invariants
- Buffer occupancy stays between 0 and 5.
- Producers write only when a free slot is available.
- Consumers read only when an item is available.
- Shared buffer state is protected by synchronization.
- Every data item is consumed exactly once.
- All four threads pass each barrier phase together.

## Control questions
1. A semaphore is a counter for resource control and signaling. A mutex is designed for mutual exclusion and normally must be unlocked by its owning thread.
2. A condition variable uses a mutex to protect shared state and coordinate condition checks with waiting. After waking, the condition must be checked again in a while loop.

## Run
python3 race.py
python3 race_fixed.py
python3 producer_consumer.py
python3 condition_version.py
python3 barrier.py
python3 lost_wakeup.py
