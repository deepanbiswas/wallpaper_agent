"""
Main Orchestrator for Wallpaper Agent.

Coordinates all agents to execute the full wallpaper generation workflow.
"""
import time
from pathlib import Path
from typing import Optional, Callable, Any
from agents import (
    ThemeDiscoveryAgent,
    ThemeSelectionAgent,
    WallpaperGenerationAgent,
    WallpaperApplicationAgent,
)
from agents.wallpaper_generation.domain import WallpaperRequest
from agents.wallpaper_application.domain import ApplicationRequest
from src.orchestrator.domain import OrchestrationResult, OrchestrationStatus
from utils.logger import get_logger
from config import load_config


class WallpaperOrchestrator:
    """Orchestrator that coordinates all agents for wallpaper generation workflow."""
    
    def __init__(self, config=None, max_retries: int = 3, retry_delay: float = 1.0):
        """
        Initialize Wallpaper Orchestrator.
        
        Args:
            config: Config instance (optional, loads from env if not provided)
            max_retries: Maximum number of retries for failed operations (default: 3)
            retry_delay: Initial delay between retries in seconds (default: 1.0)
        """
        if config is None:
            config = load_config()
        
        self.config = config
        self.logger = get_logger(__name__)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Initialize all agents
        self.theme_discovery_agent = ThemeDiscoveryAgent(config=config)
        self.theme_selection_agent = ThemeSelectionAgent(config=config)
        self.wallpaper_generation_agent = WallpaperGenerationAgent(config=config)
        self.wallpaper_application_agent = WallpaperApplicationAgent()
    
    def _retry_with_backoff(
        self,
        operation: Callable[[], Any],
        operation_name: str,
        is_success: Optional[Callable[[Any], bool]] = None,
    ) -> Any:
        """
        Retry an operation with exponential backoff.
        
        Args:
            operation: Function to retry
            operation_name: Name of operation for logging
            is_success: Optional function to check if result is successful (default: truthy check)
            
        Returns:
            Result of operation
            
        Raises:
            Exception: If operation fails after max retries
        """
        if is_success is None:
            is_success = lambda x: bool(x)
        
        last_exception = None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                result = operation()
                
                if is_success(result):
                    if attempt > 1:
                        self.logger.info(f"{operation_name} succeeded on attempt {attempt}")
                    return result
                else:
                    self.logger.warning(
                        f"{operation_name} returned unsuccessful result on attempt {attempt}/{self.max_retries}"
                    )
                    
            except Exception as e:
                last_exception = e
                self.logger.warning(
                    f"{operation_name} failed on attempt {attempt}/{self.max_retries}: {str(e)}"
                )
            
            # Wait before retry (exponential backoff)
            if attempt < self.max_retries:
                delay = self.retry_delay * (2 ** (attempt - 1))
                self.logger.debug(f"Waiting {delay:.2f}s before retry...")
                time.sleep(delay)
        
        # All retries exhausted
        if last_exception:
            raise last_exception
        else:
            raise RuntimeError(f"{operation_name} failed after {self.max_retries} attempts")
    
    def run(self) -> OrchestrationResult:
        """
        Execute the full wallpaper generation workflow.
        
        Returns:
            OrchestrationResult with status and details
        """
        self.logger.info("Starting wallpaper generation workflow")
        
        try:
            # Step 1: Discover themes (with retry)
            self.logger.info("Step 1: Discovering themes...")
            themes = self._retry_with_backoff(
                operation=lambda: self.theme_discovery_agent.discover_themes(),
                operation_name="Theme discovery",
                is_success=lambda x: bool(x) and len(x) > 0,
            )
            
            self.logger.info(f"Discovered {len(themes)} themes")
            
            # Step 2: Select best theme (with retry)
            self.logger.info("Step 2: Selecting best theme...")
            selected_theme = self._retry_with_backoff(
                operation=lambda: self.theme_selection_agent.select_theme(themes),
                operation_name="Theme selection",
                is_success=lambda x: x is not None,
            )
            
            self.logger.info(f"Selected theme: {selected_theme.get('name', 'Unknown')}")
            
            # Step 3: Generate wallpaper (with retry)
            self.logger.info("Step 3: Generating wallpaper...")
            wallpaper_request = WallpaperRequest(
                theme_name=selected_theme.get("name", ""),
                style_guidelines=selected_theme.get("style_guidelines", {}),
            )
            
            wallpaper_result = self._retry_with_backoff(
                operation=lambda: self.wallpaper_generation_agent.generate_wallpaper(wallpaper_request),
                operation_name="Wallpaper generation",
                is_success=lambda x: x.success if hasattr(x, 'success') else bool(x),
            )
            
            if not wallpaper_result.success:
                error_msg = f"Wallpaper generation failed: {wallpaper_result.error}"
                self.logger.error(error_msg)
                return OrchestrationResult(
                    status=OrchestrationStatus.FAILED,
                    selected_theme=selected_theme,
                    error=error_msg,
                )
            
            self.logger.info(f"Wallpaper generated: {wallpaper_result.file_path}")
            
            # Step 4: Apply wallpaper (with retry)
            self.logger.info("Step 4: Applying wallpaper...")
            application_request = ApplicationRequest(
                file_path=wallpaper_result.file_path,
            )
            
            try:
                application_result = self._retry_with_backoff(
                    operation=lambda: self.wallpaper_application_agent.apply_wallpaper(application_request),
                    operation_name="Wallpaper application",
                    is_success=lambda x: x.success if hasattr(x, 'success') else bool(x),
                )
            except Exception as e:
                # Application failure is not critical - wallpaper was generated
                error_msg = f"Wallpaper application failed: {str(e)}"
                self.logger.warning(error_msg)
                return OrchestrationResult(
                    status=OrchestrationStatus.PARTIAL,
                    selected_theme=selected_theme,
                    wallpaper_path=wallpaper_result.file_path,
                    error=error_msg,
                    metadata={
                        "generation_success": True,
                        "application_success": False,
                    },
                )
            
            if not application_result.success:
                error_msg = f"Wallpaper application failed: {application_result.error}"
                self.logger.warning(error_msg)
                # Wallpaper was generated but not applied - partial success
                return OrchestrationResult(
                    status=OrchestrationStatus.PARTIAL,
                    selected_theme=selected_theme,
                    wallpaper_path=wallpaper_result.file_path,
                    error=error_msg,
                    metadata={
                        "generation_success": True,
                        "application_success": False,
                    },
                )
            
            self.logger.info("Wallpaper applied successfully")
            
            # Success!
            return OrchestrationResult(
                status=OrchestrationStatus.SUCCESS,
                selected_theme=selected_theme,
                wallpaper_path=wallpaper_result.file_path,
                metadata={
                    "generation_success": True,
                    "application_success": True,
                    "desktop_index": application_result.desktop_index,
                },
            )
            
        except Exception as e:
            error_msg = f"Orchestration failed with exception: {str(e)}"
            self.logger.exception(error_msg)
            return OrchestrationResult(
                status=OrchestrationStatus.FAILED,
                error=error_msg,
            )

