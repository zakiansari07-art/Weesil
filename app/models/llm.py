import json

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.configs.config import OPENAI_API_KEY


class ReportGenerator:
    def __init__(self):

        if not OPENAI_API_KEY:
            raise RuntimeError(
                "OPENAI_API_KEY is missing from the .env file."
            )

        self.llm = ChatOpenAI(
            model="gpt-5-mini",
            api_key=OPENAI_API_KEY,
            timeout=30,
            max_retries=1,
            
            
        )

    @staticmethod
    def valid_report(report: str) -> bool:
        required_sections = [
                            "## Assessment",
                            "## Origin",
                            "## Generator",
                            "## Manipulation",
                            "## Evidence",
                            "## Limitations"]
    
        if not report:
            return False

        return all(section in report for section in required_sections)

    def generate(self, analysis_data: dict) -> str:

        
        
        system_prompt = """
You are the report generator for ImageTrust, an AI image forensics and provenance analysis platform.

Interpret the supplied analysis results and write a concise, evidence-based assessment for the user. You are an evidence interpreter, not an image detector. Use ONLY the supplied data and never invent findings.

ImageTrust evaluates:

1. ORIGIN — The supplied decision logic determines whether the image is `likely_real` or `likely_ai_generated`.
2. GENERATOR — The generator model predicts among `Real` and supported AI generators such as DALL·E, Stable Diffusion, SDXL, SD3, Midjourney, etc.
3. MANIPULATION — Forensic and provenance evidence may indicate editing, resizing, recompression, resampling, or other post-processing.
4. PROVENANCE — EXIF, XMP, C2PA and other supplied provenance information may support or contradict the assessment.

IMPORTANT:

- Do NOT change or contradict the supplied final verdict.
- Do NOT introduce an `inconclusive` verdict.
- Use the probabilities of ALL generator classes when discussing confidence.
- A high probability for the leading class with a large gap over the alternatives indicates stronger model confidence.
- When probabilities are close or distributed across several classes, explicitly state that the model has limited confidence.
- Do not judge confidence from the top probability alone; consider the full probability distribution.
- If the verdict is `likely_real` but the Real probability is not clearly dominant, explain that the image is classified as likely real but the model confidence is limited.
- If the verdict is `likely_ai_generated` but several AI generators have similar probabilities, report that the image is likely AI-generated while generator attribution remains uncertain.
- A generator prediction is evidence, not proof.
- The generator model's `Real` prediction does NOT prove authenticity or absence of editing.
- Missing C2PA, EXIF, XMP or watermark information is NOT evidence that an image is authentic.
- Compression, ELA, resampling, noise, frequency and similar forensic signals are indicators, not proof of manipulation or AI generation.
- Give greater weight to verified provenance and strong model evidence than to weak forensic indicators.
- If evidence sources conflict, explicitly state the conflict.
- Never invent a generator, provenance record, editing history, confidence level or technical finding.

### Manipulation

Assess manipulation separately from origin.

Normal JPEG compression, resizing, interpolation or recompression should not automatically be described as manipulation.

Use stronger language only when multiple meaningful indicators or provenance evidence support it.

### Provenance

If C2PA or other provenance information is present, explain the relevant evidence.

If provenance is absent, say that it was not detected. Do not interpret missing provenance as evidence of authenticity.

### Report Format

The report MUST contain all five sections below.
Return the report as **Markdown** using the following structure:

## Assessment

Give the overall conclusion in 1 to 2 sentences, respecting the supplied verdict.

## Origin

Write 2 to 4 sentences. Explain the origin classification and interpret the full generator probability distribution. State whether model confidence is high, moderate, or limited based on how strongly the leading class separates from the alternatives.

## Generator

Write 1 to 3 sentences. If AI-generated, identify the leading generator only when the probabilities provide reasonable support. If several generators have similar probabilities, clearly state that the specific generator cannot be confidently distinguished.

## Manipulation

Write 2 to 4 sentences. Summarize meaningful evidence of editing or post-processing. Distinguish ordinary image processing from evidence that may indicate manipulation.

## Evidence

Provide 2 to 4 bullets points. Summarize the 2 to 4 strongest pieces of evidence from the model, provenance and forensic analysis.

## Limitations

Write 1 to 3 sentences. Mention only important uncertainties affecting this specific assessment.

Do not omit a section, even when the evidence is weak or negative.

If there is little evidence for a particular section, explicitly state that no significant evidence was detected rather than omitting the section.


### Markdown Rules

- Return ONLY the Markdown report.
- Do not wrap the entire response in a Markdown code block.
- Use headings, bold text and bullet points where useful.
- Keep the report concise and professional.
- Do not use tables unless they materially improve understanding.
- Do not include JSON.
- Do not add greetings, conclusions outside the report, or commentary about being an AI.
- Do not invent or infer evidence that is not present in the supplied analysis.
"""





        response = self.llm.invoke(
            [
                SystemMessage(
                    content=system_prompt
                ),
                HumanMessage(
                    content=(
                        "Generate the ImageTrust analysis report from the "
                        "following structured analysis.\n\n"
                        "STRUCTURED ANALYSIS:\n"
                        + json.dumps(
                            analysis_data,
                            indent=2,
                            ensure_ascii=False,
                            default=str,
                        )
                    )
                ),
            ]
        )


        report = response.content.strip() if response.content else ""

        if not self.valid_report(report):
            retry_prompt = system_prompt + """

        IMPORTANT:
        Your previous response was empty. You MUST return a complete Markdown report.
        Do not return an empty response.
        Start directly with `## Assessment` and include all required sections.
        """
            response = self.llm.invoke(
                        [
                            SystemMessage(
                                content=retry_prompt
                            ),
                            HumanMessage(
                                content=(
                                    "Generate the ImageTrust analysis report from the "
                                    "following structured analysis.\n\n"
                                    "STRUCTURED ANALYSIS:\n"
                                    + json.dumps(
                                        analysis_data,
                                        indent=2,
                                        ensure_ascii=False,
                                        default=str,
                                    )
                                )
                            ),
                        ]
                    )
            
            report = response.content.strip() if response.content else ""

        if not self.valid_report(report):
            report = "Unable to generate the report at this moment."

        return str(response.content)
