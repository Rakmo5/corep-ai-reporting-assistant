import json

from core.llm.client import LLMClient


class ReportingAgent:
    """
    Orchestrates RAG + LLM for COREP reporting.
    """

    def __init__(self, retriever, schema: dict):

        self.retriever = retriever
        self.schema = schema
        self.llm = LLMClient()

    # --------------------------------------------------
    # Robust JSON extractor
    # --------------------------------------------------

    def _extract_json(self, text: str) -> dict:
        """
        Safely extract JSON from LLM output with fallback cleanup.
        """

        text = text.strip()

        # Remove markdown
        if text.startswith("```"):
            text = text.replace("```json", "").replace("```", "").strip()

        # Find JSON block
        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1:
            raise ValueError("No JSON found in LLM response")

        json_str = text[start:end + 1]

        # Try normal parse
        try:
            return json.loads(json_str)

        except json.JSONDecodeError:

            # Fallback cleanup
            fixed = json_str

            # Replace single quotes
            fixed = fixed.replace("'", '"')

            # Remove trailing commas
            fixed = fixed.replace(",}", "}").replace(",]", "]")

            try:
                return json.loads(fixed)

            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON after cleanup: {e}")

    # --------------------------------------------------
    # Main Run
    # --------------------------------------------------

    def run(self, user_data: dict) -> dict:

        from core.tools.calculator import Calculator
        from core.tools.field_mapper import FieldMapper
        from core.tools.audit_logger import AuditLogger
        from core.tools.rule_matcher import RuleMatcher


        # ---------------- Step 1: Inputs ---------------- #

        question_text = user_data.get("question", "")
        scenario_text = user_data.get("scenario", "")

        # ---------------- Step 2: RAG ---------------- #

        query = question_text or "COREP capital CET1 AT1 Tier1 Tier2 ratios RWA reporting"

        rules = self.retriever.retrieve(query)
        # Pre-match rules using embeddings
        matched_rules = RuleMatcher.match_fields(
            self.retriever.embedder,
            self.retriever.store,
            self.retriever.chunks,
            top_k=2
        )

        # ---------------- Step 3: LLM Prompt ---------------- #

        prompt = f"""
        You are a regulatory reporting assistant.

        STRICT INSTRUCTIONS:
        - You MUST return valid JSON.
        - Use double quotes for ALL keys and values.
        - Do NOT explain.
        - Do NOT use markdown.
        - Do NOT add text outside JSON.
        - You may ONLY use the pre-matched rules provided below.

        User Question:
        {question_text}

        Reporting Scenario:
        {scenario_text}

        Pre-matched rules (from semantic similarity):

        CET1:
        {matched_rules["cet1"]}

        AT1:
        {matched_rules["at1"]}

        Tier1:
        {matched_rules["tier1"]}

        Tier2:
        {matched_rules["tier2"]}

        Total Capital:
        {matched_rules["total"]}

        CET1 Ratio:
        {matched_rules["cet1_ratio"]}

        Tier1 Ratio:
        {matched_rules["tier1_ratio"]}

        Total Ratio:
        {matched_rules["total_ratio"]}

        Task:
        Select the most appropriate rule for each field from the pre-matched rules.

        Return ONLY valid JSON:

        {{
        "cet1_rule": "...",
        "at1_rule": "...",
        "tier1_rule": "...",
        "tier2_rule": "...",
        "total_rule": "...",
        "cet1_ratio_rule": "...",
        "tier1_ratio_rule": "...",
        "total_ratio_rule": "..."
        }}
        """



        response = self.llm.generate(prompt)

        mapping = self._extract_json(response)

        # ---------------- Step 4: Read Inputs ---------------- #

        cet1 = float(user_data.get("cet1", 0))
        at1 = float(user_data.get("at1", 0))
        tier2 = float(user_data.get("tier2", 0))
        rwa = float(user_data.get("rwa", 1))

        # ---------------- Step 5: Calculations ---------------- #

        tier1 = Calculator.compute_tier1(cet1, at1)
        total = Calculator.compute_total(tier1, tier2)

        cet1_ratio = Calculator.compute_ratio(cet1, rwa)
        tier1_ratio = Calculator.compute_ratio(tier1, rwa)
        total_ratio = Calculator.compute_ratio(total, rwa)

        # ---------------- Step 6: Field Mapping ---------------- #

        fields = {
            FieldMapper.get_field("cet1"): cet1,
            FieldMapper.get_field("at1"): at1,
            FieldMapper.get_field("tier1"): tier1,
            FieldMapper.get_field("tier2"): tier2,
            FieldMapper.get_field("total"): total,
            FieldMapper.get_field("rwa"): rwa,
            FieldMapper.get_field("cet1_ratio"): cet1_ratio,
            FieldMapper.get_field("tier1_ratio"): tier1_ratio,
            FieldMapper.get_field("total_ratio"): total_ratio,
        }

        # ---------------- Step 7: Audit Trail ---------------- #

        sources = {}

        sources.update(AuditLogger.build("r010", mapping["cet1_rule"]))
        sources.update(AuditLogger.build("r015", mapping["at1_rule"]))
        sources.update(AuditLogger.build("r020", mapping["tier1_rule"]))
        sources.update(AuditLogger.build("r025", mapping["tier2_rule"]))
        sources.update(AuditLogger.build("r030", mapping["total_rule"]))
        sources.update(AuditLogger.build("r060", mapping["cet1_ratio_rule"]))
        sources.update(AuditLogger.build("r070", mapping["tier1_ratio_rule"]))
        sources.update(AuditLogger.build("r080", mapping["total_ratio_rule"]))

        # ---------------- Step 8: Build Report ---------------- #

        report = {
            "template": self.schema["template"],
            "fields": fields,
            "sources": sources,
            "currency": self.schema.get("currency", "GBP")
        }

        return report

    # --------------------------------------------------
    # Retry Wrapper
    # --------------------------------------------------

    def run_with_retry(self, user_data: dict, validator, max_retries: int = 2):
        """
        Run agent with automatic correction if validation fails.
        """

        last_errors = []

        for _ in range(max_retries + 1):

            result = self.run(user_data)

            errors = validator.validate(result)

            if not errors:
                return result, errors

            last_errors = errors

            correction_prompt = f"""
The generated report has the following validation errors:

{errors}

Please correct the report.
Return ONLY valid JSON.
"""

            response = self.llm.generate(correction_prompt)

            try:
                fixed = self._extract_json(response)
                return fixed, validator.validate(fixed)

            except Exception:
                continue

        return result, last_errors
