main_prompt = """
This is the main system prompt.
"""

sub_prompt_1 = "Sub-prompt 1: Provide a detailed analysis."
sub_prompt_2 = "Sub-prompt 2: Summarize the key points."
sub_prompt_3 = "Sub-prompt 3: Offer actionable insights."

sub_prompts = [sub_prompt_1, sub_prompt_2, sub_prompt_3]

# Function to get the full concatenated prompt
def get_full_prompt(house_config):
    return main_prompt + "\n" + "\n".join(sub_prompts) + f"\n\nHouse Configuration:\n{house_config}"
