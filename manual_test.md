# Manual Testing Protocol

## Test 1: Create Delivery
**Action:** POST /assign
**Request:**
```json
{"order_id":"MANUAL-001","address":"Moscow","recipient_phone":"+79001234567"}
Expected: 200 OK, task_id returned

Test 2: Get Couriers
Action: GET /couriers
Expected: 200 OK, list of couriers

Test 3: Update Tracking
Action: POST /track/update
Request:
{"task_id":"<task_id>","lat":55.7558,"lng":37.6173}
Expected: 200 OK

Test 4: Get Tracking Status
Action: GET /track/<task_id>
Expected: 200 OK, status info

Test 5: Complete Delivery
Action: POST /track/complete
Request
{"task_id":"<task_id>","proof":"MANUAL_CODE"}
Expected: 200 OK, status "delivered"

Test 6: Send Notification
Action: POST /notify
Request:
{"recipient":"+79001234567","message":"Test","order_id":"MANUAL-001"}
Expected: 200 OK

Test Results
Test	Status	Notes
1	☐ PASS / ☐ FAIL	
2	☐ PASS / ☐ FAIL	
3	☐ PASS / ☐ FAIL	
4	☐ PASS / ☐ FAIL	
5	☐ PASS / ☐ FAIL	
6	☐ PASS / ☐ FAIL	
