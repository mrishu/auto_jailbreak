from . import password_breach
from . import chemical_synthesis
from . import grading_sabotage

target_system_prompt_dict = {
    "password_breach": password_breach.target_system_prompt,
    "chemical_synthesis": chemical_synthesis.target_system_prompt,
    "grading_sabotage": grading_sabotage.target_system_prompt,
}

judge_system_prompt_dict = {
    "password_breach": password_breach.judge_system_prompt,
    "chemical_synthesis": chemical_synthesis.judge_system_prompt,
    "grading_sabotage": grading_sabotage.judge_system_prompt,
}

get_reward_from_judge_eval_dict = {
    "password_breach": password_breach.get_reward_from_judge_eval,
    "chemical_synthesis": chemical_synthesis.get_reward_from_judge_eval,
    "grading_sabotage": grading_sabotage.get_reward_from_judge_eval,
}

judge_user_prompt_dict = {
    "password_breach": password_breach.judge_user_prompt,
    "chemical_synthesis": chemical_synthesis.judge_user_prompt,
    "grading_sabotage": grading_sabotage.judge_user_prompt,
}
