import os
import sys
import traceback
import asyncio
from typing import Optional, List

# --- GLOBAL CRASH CATCHER ---
try:
    # 1. Path Injector
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

    # 2. Bulletproof Custom Imports
    try:
        try:
            from auto_jailbreak.client import AutoJailbreakEnv
            from auto_jailbreak.models import AutoJailbreakAction
            from auto_jailbreak.client_tasks import (
                coach_messages_dict,
                attacker_messages_dict,
            )
        except ImportError:
            from .client import AutoJailbreakEnv
            from .models import AutoJailbreakAction
            from .client_tasks import (
                coach_messages_dict,
                attacker_messages_dict,
            )
    except Exception as e:
        smashed_tb = traceback.format_exc().replace(chr(10), " ||| ")
        print(f"!!! FATAL SCRIPT IMPORT ERROR !!! Details: {smashed_tb}", flush=True)
        sys.exit(1)

    # Note: Removed openai import and instantiation for this test just in case
    # it was causing the ModuleNotFoundError.

    # 3. Required Logging Functions
    def log_start(task: str, env: str, model: str) -> None:
        print(f"[START] task={task} env={env} model={model}", flush=True)

    def log_step(
        step: int, action: str, reward: float, done: bool, error: Optional[str]
    ) -> None:
        error_val = error if error else "null"
        done_val = str(done).lower()
        safe_action = action.replace("\n", "\\n").replace("\r", "\\r")
        safe_error = error_val.replace("\n", "\\n").replace("\r", "\\r")
        print(
            f"[STEP] step={step} action={safe_action} reward={reward:.2f} done={done_val} error={safe_error}",
            flush=True,
        )

    def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
        rewards_str = ",".join(f"{r:.2f}" for r in rewards)
        print(
            f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}",
            flush=True,
        )

    # 4. Dummy Main Logic
    async def main():
        print("\n=== ISOLATION TEST: MAIN FUNCTION STARTED ===", flush=True)

        TASK_NAME = "dummy_test_task"
        log_start(task=TASK_NAME, env="dummy_env", model="dummy_model")

        # Fake a step
        print("=== ISOLATION TEST: Faking a step ===", flush=True)
        log_step(step=1, action="Fake action string", reward=1.0, done=True, error=None)

        # Fake an end
        log_end(success=True, steps=1, score=1.0, rewards=[1.0])
        print(
            "=== ISOLATION TEST: MAIN FUNCTION FINISHED SUCCESSFULLY ===\n", flush=True
        )

    if __name__ == "__main__":
        asyncio.run(main())

except Exception as e:
    smashed_tb = traceback.format_exc().replace(chr(10), " ||| ")
    print(f"!!! GLOBAL INFERENCE CRASH !!! Details: {smashed_tb}", flush=True)
    sys.stderr.write(f"!!! GLOBAL INFERENCE CRASH !!! Details: {smashed_tb}\n")
    sys.exit(1)
