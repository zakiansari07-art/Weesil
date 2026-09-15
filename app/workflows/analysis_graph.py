from typing import TypedDict
from langgraph.graph import END, START, StateGraph

from app.models.forensics_analyzer import ImageForensicsAnalyzer
from app.models.generator_attributor import GeneratorAttributor
from app.models.llm import ReportGenerator
from app.schemas.predictions import (
    AnalysisResult,
    ForensicsReport,
    ModelPrediction,
)


class ImageAnalysisState(TypedDict, total=False):
    image_path: str
    attribution_raw: dict
    forensics_raw: dict
    result: AnalysisResult
   


def build_analysis_graph(
    
    attributor: GeneratorAttributor,
    forensics: ImageForensicsAnalyzer,
    llm: ReportGenerator
 
):
   

    def attribute_generator(state: ImageAnalysisState) -> dict:
        
        output = attributor.predict(state["image_path"])
        
        
        return {"attribution_raw": output}

    def analyze_forensics(state: ImageAnalysisState) -> dict:
       
        output = forensics.analyze(state["image_path"])
        
        return {"forensics_raw": output}

    def decide_result(state: ImageAnalysisState) -> dict:
        
        attribution_result = ModelPrediction(
            **state["attribution_raw"]
        )
        forensics_result = ForensicsReport(
            **state["forensics_raw"]
        )

        
    
        best_label = attribution_result.label

        if best_label == "Real":
            result = AnalysisResult(
            verdict="likely_real",
            confidence=attribution_result.confidence,
            likely_generator=None,
            probabilities= attribution_result.probabilities,
            explanation=(
                f"The image is likely real with a confidence of {attribution_result.confidence}."),
            
            model_predictions= attribution_result,
            forensics=forensics_result,
            )
             
        else:
             result = AnalysisResult(
                verdict="likely_ai_generated",
                confidence=attribution_result.confidence,
                likely_generator=attribution_result.label,
                probabilities= attribution_result.probabilities,
                explanation=(
                    f"The image is likely ai-generated. The likely source is {attribution_result.label} with"
                    f" a confidence of {attribution_result.confidence}."),
                model_predictions= attribution_result,
                                
                forensics=forensics_result
                             )
            

        return {"result": result}



    def generate_report(state: ImageAnalysisState) -> dict:
        result = state["result"]
        analysis_data = result.model_dump(mode="json")
        

        
        report = llm.generate(analysis_data=analysis_data)
        

       

        updated_result = result.model_copy(
            update={"llm_report": report}
        )

        return {"result": updated_result}
                        
    

    workflow = StateGraph(ImageAnalysisState)

   

    workflow.add_node(
        "attribute_generator",
        attribute_generator
    )

    workflow.add_node(
        "analyze_forensics",
        analyze_forensics
    )

    workflow.add_node(
        "decide_result",
        decide_result
    )

    workflow.add_node(
        "report",
        generate_report
    )



   

    workflow.add_edge(
        START,
        "attribute_generator"
    )

    workflow.add_edge(
        START,
        "analyze_forensics"
    )

   

    workflow.add_edge(
        "attribute_generator",
        "decide_result"
    )

    workflow.add_edge(
        "analyze_forensics",
        "decide_result"
    )


    # ------------------------------------------------------------
    # DECISION → LLM
    # ------------------------------------------------------------

    workflow.add_edge(
        "decide_result",
        "report"
    )

    workflow.add_edge(
        "report",
        END
    )


    return workflow.compile()
