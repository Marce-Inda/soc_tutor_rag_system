import re
import json

def parse_mock(chain):
    final_answer_match = re.search(r"Final Answer: (.*)", chain, re.DOTALL)
    if final_answer_match:
        try:
            result_json = json.loads(final_answer_match.group(1).strip())
        except:
            cleaned = final_answer_match.group(1).strip().strip("```json").strip("```")
            try: result_json = json.loads(cleaned)
            except: result_json = {}
        print(repr(result_json))

chain = """Final Answer: ```json
{
  "analysis": "...",
  "verified_artifacts": [
      "fact": "some fact"
  ]
}
```
"""
parse_mock(chain)
