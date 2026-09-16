from pathlib import Path
import os
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
print(PROJECT_ROOT)

load_dotenv(PROJECT_ROOT / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")



ATTRIBUTOR_CHECKPOINT_PATH = (
    PROJECT_ROOT
    / "models"
    / "best_models_checkpoint"
    / "multi_task__AdamW_with_new_split_best_validation.pth"
)




