import json

from guardian.policy_compiler import compile_policy


def load_guardian_policy(user_policy: str = None) -> dict:
    """
    Load Guardian's default policy and optionally override it
    with a natural-language user policy.
    """

    with open("config/policy.json", "r") as file:
        policy = json.load(file)

    if user_policy:
        compiled_policy = compile_policy(user_policy)
        policy.update(compiled_policy)

    return policy