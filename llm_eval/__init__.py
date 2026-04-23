"""llm-eval: Framework para avaliação de confiabilidade de chatbots baseados em LLMs."""

__version__ = "0.1.0"

from llm_eval.config import Config
from llm_eval.report import ReportGenerator
from llm_eval.runner import Runner

__all__ = ["Config", "Runner", "ReportGenerator", "__version__"]
