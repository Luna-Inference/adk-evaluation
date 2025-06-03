import json
import uuid
from datetime import datetime

# Load questions from task.json
with open('task.json', 'r') as f:
    data = json.load(f)
    questions = data['questions']

# Create evaluation set structure
eval_set = {
    "eval_set_id": f"web_search_eval_set_{datetime.now().strftime('%Y%m%d')}",
    "name": "Web Search Agent Evaluation",
    "description": "Evaluation set for testing web search agent with various difficulty levels",
    "eval_cases": []
}

# Convert each question to an evaluation case
for question in questions:
    # Create a unique ID for each evaluation case
    eval_id = f"q_{question['id']}"
    
    # Create an evaluation case for each question
    eval_case = {
        "eval_id": eval_id,
        "conversation": [
            {
                "invocation_id": str(uuid.uuid4()),
                "user_content": {
                    "parts": [
                        {
                            "text": question["question"]
                        }
                    ],
                    "role": "user"
                },
                # We don't know the expected responses yet, 
                # so we'll leave these empty for now
                "final_response": None,
                "intermediate_data": {
                    "tool_uses": [],
                    "intermediate_responses": []
                }
            }
        ],
        "session_input": {
            "app_name": "multi_tool_agent",
            "user_id": f"eval_user_{question['difficulty']}",
            "state": {
                "difficulty": question["difficulty"],
                "question_id": question["id"]
            }
        },
        "metadata": {
            "difficulty": question["difficulty"],
            "question_id": question["id"]
        }
    }
    
    # Add the evaluation case to the set
    eval_set["eval_cases"].append(eval_case)

# Save the evaluation set to a file
output_filename = f"web_search_eval_{datetime.now().strftime('%Y%m%d')}.evalset.json"
with open(output_filename, 'w') as f:
    json.dump(eval_set, f, indent=2)

print(f"Created evaluation set with {len(questions)} questions: {output_filename}")
print(f"You can now run the evaluation with: adk eval . {output_filename}")
