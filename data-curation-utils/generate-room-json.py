from openai import OpenAI
import json
import time
import random

client = OpenAI(
    api_key=""
)
# Function to generate a room description
def generate_room_descriptions(n=10000, batch_size=50):
    descriptions = []
    
    prompt_template = """Generate {count} unique short and vivid room descriptions.
Each description should include both a spatial description of the room and a brief scene setup.
Additionally, include a realistic room size in meters as a dictionary with 'x', 'y', and 'z' values.
The output format should be a JSON list where each item is formatted as:
{{
    "description": "<room description>",
    "size": {{"x": <length>, "y": <width>, "z": <height>}}
}}

Example:
[
    {{
        "description": "A modern gaming room filled with arcade machines, with chairs and stools arranged neatly around them.",
        "size": {{"x": 4, "y": 5, "z": 3}}
    }},
    ...
]

Now generate {count} descriptions following this format.
"""

    for i in range(0, n, batch_size):
        count = min(batch_size, n - i)
        prompt = prompt_template.format(count=count)

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": "You are a creative assistant generating structured room descriptions."},
                          {"role": "user", "content": prompt}],
                temperature=0.7
            )
            result = json.loads(response.choices[0].message.content.strip("```json\n").strip("```"))
            descriptions.extend(result)

        except Exception as e:
            print(f"Error at batch {i}: {e}")
            time.sleep(5)  # Wait before retrying
        
        # Avoid rate limits
        time.sleep(1)
        print('--------------------------------')
        print(f"Generated {i+count} descriptions")
        print('--------------------------------')

    return descriptions

# Generate 10,000 room descriptions
room_data = generate_room_descriptions(n=10000)

# Save to file
file_path = "../generated_room_descriptions.json"
with open(file_path, "w") as f:
    json.dump(room_data, f)

print(f"Room descriptions saved to: {file_path}")
