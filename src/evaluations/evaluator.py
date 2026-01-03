"""
Agent Evaluator - orchestrates evaluation of all agents.

This class acts as a facade/orchestrator that coordinates individual agent evaluators.
"""
from typing import List, Dict, Any, Optional
from pathlib import Path

from .metrics import EvaluationResult
from .discovery_evaluator import DiscoveryEvaluator
from .selection_evaluator import SelectionEvaluator
from .generation_evaluator import GenerationEvaluator
from .application_evaluator import ApplicationEvaluator
from api_clients import LLMClient
from config import get_llm_config, load_config
from utils.logger import get_logger


class AgentEvaluator:
    """
    Orchestrator for evaluating all agents.
    
    Delegates evaluation to specialized evaluators for each agent.
    """
    
    def __init__(self, config=None, llm_client=None):
        """
        Initialize Agent Evaluator.
        
        Args:
            config: Config instance (optional)
            llm_client: LLMClient instance (optional, for LLM-based evaluations)
        """
        if config is None:
            config = load_config()
        
        self.config = config
        self.logger = get_logger(__name__)
        
        # Initialize LLM client if not provided
        if llm_client is None:
            llm_config = get_llm_config(config)
            if llm_config.get("anthropic_api_key") or llm_config.get("openai_api_key"):
                self.llm_client = LLMClient(
                    provider=llm_config["provider"],
                    api_key=llm_config.get(f"{llm_config['provider']}_api_key"),
                    model=llm_config.get("model")
                )
            else:
                self.llm_client = None
        else:
            self.llm_client = llm_client
        
        # Initialize individual evaluators
        self.discovery_evaluator = DiscoveryEvaluator(llm_client=self.llm_client)
        self.selection_evaluator = SelectionEvaluator(llm_client=self.llm_client)
        self.generation_evaluator = GenerationEvaluator(llm_client=self.llm_client)
        self.application_evaluator = ApplicationEvaluator()
    
    def evaluate_discovery_agent(
        self,
        themes: List[Dict[str, Any]],
        week_context: Optional[Dict[str, Any]] = None
    ) -> EvaluationResult:
        """
        Evaluate Theme Discovery Agent output.
        
        Args:
            themes: List of discovered themes
            week_context: Current week context (optional)
            
        Returns:
            EvaluationResult with metrics
        """
        return self.discovery_evaluator.evaluate(themes, week_context)
    
    def evaluate_selection_agent(
        self,
        selected_theme: Dict[str, Any],
        all_themes: List[Dict[str, Any]],
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> EvaluationResult:
        """
        Evaluate Theme Selection Agent output.
        
        Args:
            selected_theme: Selected theme
            all_themes: All available themes
            user_preferences: User preference settings (optional)
            
        Returns:
            EvaluationResult with metrics
        """
        return self.selection_evaluator.evaluate(selected_theme, all_themes, user_preferences)
    
    def evaluate_generation_agent(
        self,
        wallpaper_path: Path,
        theme: Dict[str, Any]
    ) -> EvaluationResult:
        """
        Evaluate Wallpaper Generation Agent output.
        
        Args:
            wallpaper_path: Path to generated wallpaper
            theme: Selected theme
            
        Returns:
            EvaluationResult with metrics
        """
        return self.generation_evaluator.evaluate(wallpaper_path, theme)
    
    def evaluate_application_agent(
        self,
        success: bool,
        desktop_index: Optional[int] = None,
        desktop_count: Optional[int] = None
    ) -> EvaluationResult:
        """
        Evaluate Wallpaper Application Agent output.
        
        Args:
            success: Whether application was successful
            desktop_index: Selected desktop index
            desktop_count: Total desktop count
            
        Returns:
            EvaluationResult with metrics
        """
        return self.application_evaluator.evaluate(success, desktop_index, desktop_count)

