from . import password_breach
from . import grading_sabotage
from . import chemical_synthesis

MAX_REWARD_PER_STEP_dict = {
    "password_breach": password_breach.MAX_REWARD_PER_STEP,
    "grading_sabotage": grading_sabotage.MAX_REWARD_PER_STEP,
    "chemical_synthesis": chemical_synthesis.MAX_REWARD_PER_STEP,
}

MALICIOUS_GOAL_dict = {
    "password_breach": password_breach.MALICIOUS_GOAL,
    "grading_sabotage": grading_sabotage.MALICIOUS_GOAL,
    "chemical_synthesis": chemical_synthesis.MALICIOUS_GOAL,
}

coach_messages_dict = {
    "password_breach": password_breach.coach_messages,
    "grading_sabotage": grading_sabotage.coach_messages,
    "chemical_synthesis": chemical_synthesis.coach_messages,
}

attacker_messages_dict = {
    "password_breach": password_breach.attacker_messages,
    "grading_sabotage": grading_sabotage.attacker_messages,
    "chemical_synthesis": chemical_synthesis.attacker_messages,
}
