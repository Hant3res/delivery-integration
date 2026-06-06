import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from saga import SagaOrchestrator, SagaStep

class TestSaga(unittest.TestCase):
    """Unit tests for Saga pattern"""
    
    def test_saga_step_execution(self):
        """Test successful saga step execution"""
        executed = False
        
        def action(ctx):
            nonlocal executed
            executed = True
            return {"result": "success"}
        
        def compensation(result):
            pass
        
        step = SagaStep("test_step", action, compensation)
        result = step.action({})
        
        self.assertTrue(executed)
        self.assertEqual(result["result"], "success")
    
    def test_saga_orchestrator_success(self):
        """Test successful saga execution"""
        saga = SagaOrchestrator("test_saga")
        
        def action1(ctx):
            ctx["step1"] = "done"
            return {"status": "ok"}
        
        def compensation1(result):
            pass
        
        def action2(ctx):
            ctx["step2"] = "done"
            return {"status": "ok"}
        
        def compensation2(result):
            pass
        
        saga.add_step("step1", action1, compensation1)
        saga.add_step("step2", action2, compensation2)
        
        result = saga.execute({})
        
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["saga_id"], "test_saga")
    
    def test_saga_orchestrator_failure(self):
        """Test saga execution with failure and compensation"""
        saga = SagaOrchestrator("test_saga_fail")
        
        def action1(ctx):
            ctx["step1"] = "done"
            return {"status": "ok"}
        
        def compensation1(result):
            nonlocal compensated1
            compensated1 = True
        
        def action2(ctx):
            raise Exception("Step 2 failed")
        
        def compensation2(result):
            nonlocal compensated2
            compensated2 = True
        
        compensated1 = False
        compensated2 = False
        
        saga.add_step("step1", action1, compensation1)
        saga.add_step("step2", action2, compensation2)
        
        result = saga.execute({})
        
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["failed_step"], "step2")
        self.assertTrue(compensated1)

if __name__ == '__main__':
    unittest.main()
