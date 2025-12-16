import json
from openai import OpenAI
from typing import List, Optional, Literal, Dict, Any, Tuple
import redis
from pydantic import BaseModel, Field
from util import get_api_key_and_redis_client, retrieve_cache, store_cache
from pathlib import Path

PROMPT_TEMPLATE = """
Analyze this medical case and determine urgency level.

Patient Age: {age}
Symptoms: {symptoms}
Medical History: {medical_history}

Classify as HIGH, MEDIUM, or LOW urgency.

Respond in JSON format:
{{
    "urgency": "HIGH/MEDIUM/LOW",
    "reasoning": "Brief explanation"
}}
"""


class TriageCase(BaseModel):
    patient_id: str
    age: int
    symptoms: str
    medical_history: str
    urgency_level: Literal["HIGH", "MEDIUM", "LOW"]
    explanation: str = ""


class TriageResult(BaseModel):
    patient_id: str
    predicted_urgency: Literal["HIGH", "MEDIUM", "LOW"]
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    reasoning: str = "No reasoning provided"


class TrackedEval(BaseModel):
    prompt_template: str
    model: str
    accuracy: float
    num_correct: int
    total: int


class MedicalTriageSystem:
    def __init__(
        self,
        api_key: str,
        prompt_template: str = PROMPT_TEMPLATE,
        model: str = "gpt-4o-mini",
        redis_client: Optional[redis.Redis] = None,
    ):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.redis = redis_client
        self.prompt_template = prompt_template

    def analyze_case(self, case: TriageCase) -> Tuple[Dict[str, Any], bool]:
        """
        Analyze a triage case and return the result with cache status.

        Returns:
            Tuple of (result: dict, cache_hit: bool) where:
            - result: dict containing 'urgency' and 'reasoning' keys
            - cache_hit: True if result came from cache, False if computed
        """
        # Build cache key from model, prompt template, and case details
        cache_key = f"{self.model}|{self.prompt_template}|{case.age}|{case.symptoms}|{case.medical_history}"

        # Try to retrieve from cache
        if cached_result := retrieve_cache(self.redis, cache_key):
            return cached_result, True

        # Cache miss - generate result by calling the API
        prompt = self.prompt_template.format(
            age=case.age, symptoms=case.symptoms, medical_history=case.medical_history
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a medical triage expert."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
        )

        response_data = json.loads(
            response.choices[0]
            .message.content.replace("```json", "")  # type: ignore
            .replace("```", "")
            .strip()
        )

        result = {
            "patient_id": case.patient_id,
            "predicted_urgency": response_data["urgency"],
            "reasoning": response_data.get("reasoning", "No reasoning provided"),
        }

        # Store result in cache (no expiry)
        store_cache(self.redis, cache_key, result, ttl=None)

        return result, False


def evaluate(system: MedicalTriageSystem, cases: List[TriageCase]):
    num_correct = 0
    total = len(cases)

    for case in cases:
        result_dict, cache_hit = system.analyze_case(case)
        result = TriageResult.model_validate(result_dict)
        is_correct = result.predicted_urgency == case.urgency_level
        cache_status = "[CACHED]" if cache_hit else ""

        print(
            f"{case.patient_id}: {result.predicted_urgency} (actual: {case.urgency_level}) {'✓' if is_correct else '✗'} {cache_status}"
        )

        num_correct += 1 if is_correct else 0

    print(f"\nAccuracy: {num_correct / total:.1%} ({num_correct}/{total})")
    return num_correct


def main(
    test_cases_filename: str = "test_cases/train.jsonl",
    model: str = "gpt-4o-mini",
    prompt_template: str = PROMPT_TEMPLATE,
    tracker_filename: str = "tracker.csv",
):
    api_key, redis_client = get_api_key_and_redis_client()
    system = MedicalTriageSystem(
        api_key, prompt_template=prompt_template, model=model, redis_client=redis_client
    )

    with open(Path(__file__).parent / test_cases_filename, "r") as f:
        cases = [TriageCase.model_validate_json(line) for line in f]

    evaluate(system, cases)


if __name__ == "__main__":
    main(test_cases_filename="test_cases/train.jsonl", model="gpt-4o-mini")
    main(test_cases_filename="test_cases/eval.jsonl", model="gpt-4o-mini")
    main(test_cases_filename="test_cases/train.jsonl", model="gpt-4o")
    main(test_cases_filename="test_cases/eval.jsonl", model="gpt-4o")
