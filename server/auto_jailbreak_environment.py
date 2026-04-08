# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Auto Jailbreak Environment Implementation.

An environment that can be used for training another LLM to find vulnerabilities in a target LLM
by trying to jailbreak it on some tasks.
"""

import os
import re
import ast
from uuid import uuid4

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

from openai import OpenAI

try:
    from .server_tasks import (
        target_system_prompt_dict,
        judge_system_prompt_dict,
        judge_user_prompt_dict,
        get_reward_from_judge_eval_dict,
    )
except:
    from server.server_tasks import (
        target_system_prompt_dict,
        judge_system_prompt_dict,
        judge_user_prompt_dict,
        get_reward_from_judge_eval_dict,
    )

try:
    from ..models import AutoJailbreakAction, AutoJailbreakObservation
except ImportError:
    from models import AutoJailbreakAction, AutoJailbreakObservation


API_BASE_URL = os.getenv("API_BASE_URL") or "https://router.huggingface.co/v1"
HF_TOKEN = os.getenv("HF_TOKEN")

TASK_NAME = os.getenv("TASK_NAME") or "password_breach"

MODEL_NAME = os.getenv("MODEL_NAME") or "meta-llama/Meta-Llama-3-8B-Instruct"
MODEL_TARGET = os.getenv("MODEL_TARGET") or MODEL_NAME
MODEL_JUDGE = os.getenv("MODEL_JUDGE") or MODEL_NAME


class AutoJailbreakEnvironment(Environment):
    # Enable concurrent WebSocket sessions.
    # Set to True if your environment isolates state between instances.
    # When True, multiple WebSocket clients can connect simultaneously, each
    # getting their own environment instance (when using factory mode in app.py).
    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        """Initialize the auto_jailbreak environment."""
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._reset_count = 0
        self.client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)
        self.MODEL_TARGET = MODEL_TARGET
        self.MODEL_JUDGE = MODEL_JUDGE
        self.target_system_prompt = target_system_prompt_dict[TASK_NAME]
        self.judge_system_prompt = judge_system_prompt_dict[TASK_NAME]
        self.judge_user_prompt = judge_user_prompt_dict[TASK_NAME]
        self.get_reward_from_judge_eval = get_reward_from_judge_eval_dict[TASK_NAME]
        self.target_chat_history = [
            {
                "role": "system",
                "content": self.target_system_prompt,
            },
        ]

    def reset(self) -> AutoJailbreakObservation:
        """
        Reset the environment.

        Returns:
            AutoJailbreakObservation with a ready message
        """
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._reset_count += 1
        self.target_chat_history = [
            {
                "role": "system",
                "content": self.target_system_prompt,
            },
        ]

        return AutoJailbreakObservation(
            target_reply=f"Environment Ready! TASK: {TASK_NAME}.",
            judge_reply="",
            judge_eval={},
            error="null",
            done=False,
            reward=0.0,
        )

    def parse_judge_output(self, judge_reply: str) -> dict:
        """
        Extracts the dictionary from the Judge LLM output and returns it as a dict.
        Handles multi-line strings and inconsistent quoting.
        """
        # Regex explanation:
        # \{        -> Match opening brace
        # [^{}]* -> Match any character that is NOT a brace (non-greedy)
        # \}        -> Match closing brace
        # re.DOTALL -> Allows the dot (.) to match newlines
        match = re.search(r"\{[^{}]*\}", judge_reply, re.DOTALL)

        if not match:
            raise ValueError

        dict_string = match.group(0)

        return ast.literal_eval(dict_string)

    def step(self, action: AutoJailbreakAction) -> AutoJailbreakObservation:  # type: ignore[override]
        """
        Execute a step in the environment:
        1. Send the action (attack_prompt) to the target,
            along with past conversation (chat_history) for long manipulation.
        2. Get the target's reply (target_reply).
        3. Send target_reply to the judge to get reward.
        4. Return target_reply and reward as observation.

        Args:
            action: AutoJailbreakAction containing the attack prompt

        Returns:
            AutoJailbreakObservation with the target's reply and reward
        """
        self._state.step_count += 1

        attack_prompt = action.attack_prompt

        if attack_prompt == "":
            return AutoJailbreakObservation(
                target_reply="",
                judge_reply="",
                judge_eval={},
                error="attack_prompt_not_given",
                done=False,
                reward=0.0,
            )

        if action.delete_target_prev_chat:
            self.target_chat_history = [
                {
                    "role": "system",
                    "content": self.target_system_prompt,
                },
            ]

        ## Attack Target LLM
        attack_payload = {"role": "user", "content": attack_prompt}
        self.target_chat_history.append(attack_payload)
        target_response = self.client.chat.completions.create(
            model=self.MODEL_TARGET,
            messages=self.target_chat_history,
            max_tokens=500,
            temperature=0.1,  # Keep target defenses rigid
        )
        target_reply = target_response.choices[0].message.content
        target_reply = target_reply.strip() if target_reply is not None else ""
        self.target_chat_history.append({"role": "assistant", "content": target_reply})

        ## Send Target Reply to Judge
        judge_payload = [
            {"role": "system", "content": self.judge_system_prompt},
            {"role": "user", "content": self.judge_user_prompt(target_reply)},
        ]
        judge_response = self.client.chat.completions.create(
            model=self.MODEL_JUDGE,
            messages=judge_payload,
            max_tokens=250,
            temperature=0.1,  # Keep judge's evaluation more deterministic
        )
        judge_reply = judge_response.choices[0].message.content
        judge_reply = judge_reply.strip() if judge_reply is not None else ""

        error = "null"
        ## Get reward from judge's reply
        try:
            judge_eval = self.parse_judge_output(judge_reply)
        except (ValueError, SyntaxError):
            judge_eval = {}
            error = "cannot_parse_judge_reply"

        try:
            reward = self.get_reward_from_judge_eval(judge_eval)
        except KeyError:
            if error == "null":
                error = "cannot_get_reward_from_judge_eval"
            reward = 0.0

        return AutoJailbreakObservation(
            target_reply=target_reply,
            judge_reply=judge_reply,
            judge_eval=judge_eval,
            error=error,
            done=False,
            reward=reward,
        )

    @property
    def state(self) -> State:
        """
        Get the current environment state.

        Returns:
            Current State with episode_id and step_count
        """
        return self._state
