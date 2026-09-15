from app.models.forensics_analyzer import ImageForensicsAnalyzer
from app.models.generator_attributor import GeneratorAttributor
from app.models.llm import ReportGenerator
from app.schemas.predictions import AnalysisResult
from app.workflows.analysis_graph import build_analysis_graph


class AnalysisService:
    """
    ImageTrust's central analysis engine.

    It coordinates the models and turns their raw outputs
    into one safe, user-facing conclusion.
    """

    def __init__(
        self,
        attributor_checkpoint_path: str):
        # Load ML models once.
    
        self.attributor = GeneratorAttributor(attributor_checkpoint_path)

        # Traditional forensic analysis does not require a checkpoint.
        self.forensics = ImageForensicsAnalyzer()

        # Thresholds used by the deterministic decision engine.
        
   

        # LLM is used for explanation/report generation,
        # not for making the final verdict.
        self.llm = ReportGenerator()

        # Build the LangGraph workflow once.
        self.graph = build_analysis_graph(
            attributor=self.attributor,
            forensics=self.forensics,
            llm=self.llm,
           
            
        )

    def analyze(self, image_path: str) -> AnalysisResult:
        """
        Analyze a single image through the complete ImageTrust pipeline.
        """

        final_state = self.graph.invoke(
            {
                "image_path": image_path
            }
        )

        return final_state["result"]