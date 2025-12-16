# Medical Triage System

AI-powered medical triage that classifies patient urgency as HIGH, MEDIUM, or LOW.

## Setup

Download Docker: [https://www.docker.com/get-started](https://www.docker.com/get-started/)

```bash
export OPENAI_API_KEY="your-key-here"
make lint # Lint/formatting
make up # Run medical_traige.py
```

## Files

- `medical_triage.py` - Main system (modify this)
- `test_cases/train.jsonl` - Train test cases (feel free to use these in prompt eng)
- `test_cases/eval.jsonl` - Eval test cases (treat as blind)


## Core Tasks

1. Design a lightweight system to compare performance of different prompts or models (output: json or csv with columns: prompt, model, accuracy)
2. Use prompt engineering to increase the accuracy on `analyze_case()`
3. Output a confusion matrix. Identify which misclassification is the most dangerous.

## Extra Tasks

4. Identify if there is any correlation between age and urgency. If so, is it significant?
5. Design a lightweight method for estimating confidence. How well does it track?

## Bonus

6. Create a lightweight API wrapper around this (where the endpoint /triage accepts the patient json)


