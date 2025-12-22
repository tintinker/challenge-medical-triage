# Medical Triage System

AI-powered medical triage that classifies patient urgency as HIGH, MEDIUM, or LOW.

## Setup

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

1. Perform a tiny bit of EDA on the train data. Is there a relationship between age and urgency? What list of conditions are present?
2. Design a lightweight system to compare performance of different prompts or models (output: csv with columns: prompt, model, accuracy)
3. Use prompt engineering to increase the accuracy on `analyze_case()`
4. Output a confusion matrix. Identify which misclassification is the most dangerous.

## Extra Tasks
5. Design a lightweight method for estimating confidence. How well does it track?
6. Create a lightweight API wrapper around this (where the endpoint /triage accepts the patient json)


