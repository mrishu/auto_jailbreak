# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""Auto Jailbreak Environment Client."""

from typing import Dict

from openenv.core import EnvClient
from openenv.core.client_types import StepResult
from openenv.core.env_server.types import State

from .models import AutoJailbreakAction, AutoJailbreakObservation


class AutoJailbreakEnv(EnvClient[AutoJailbreakAction, AutoJailbreakObservation, State]):
    def _step_payload(self, action: AutoJailbreakAction) -> Dict:
        """
        Convert AutoJailbreakAction to JSON payload for step message.

        Args:
            action: AutoJailbreakAction instance

        Returns:
            Dictionary representation suitable for JSON encoding
        """
        return {
            "attack_prompt": action.attack_prompt,
            "delete_target_prev_chat": action.delete_target_prev_chat,
        }

    def _parse_result(self, payload: Dict) -> StepResult[AutoJailbreakObservation]:
        """
        Parse server response into StepResult[AutoJailbreakObservation].

        Args:
            payload: JSON response data from server

        Returns:
            StepResult with AutoJailbreakObservation
        """
        obs_data = payload.get("observation", {})
        observation = AutoJailbreakObservation(
            target_reply=obs_data.get("target_reply", "null"),
            judge_reply=obs_data.get("judge_reply", "null"),
            judge_eval=obs_data.get("judge_eval", {}),
            error=obs_data.get("error", "null"),
            done=payload.get("done", False),
            reward=payload.get("reward"),
            metadata=obs_data.get("metadata", {}),
        )

        return StepResult(
            observation=observation,
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: Dict) -> State:
        """
        Parse server response into State object.

        Args:
            payload: JSON response from state request

        Returns:
            State object with episode_id and step_count
        """
        return State(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
        )
