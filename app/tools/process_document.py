import logging
from typing import Any, Dict, List, Optional

from mcp.types import Tool as MCPTool
from pydantic import BaseModel, Field

from app.tools.base import BaseMCPTool
from app.services.mcp_registry import get_mcp_registry

logger = logging.getLogger(__name__)


class ProcessDocumentArgs(BaseModel):
    file_data: str = Field(..., description="Base64 encoded PDF file")
    skip_filter: bool = Field(default=False, description="Skip content filtering")
    cache_intermediate: bool = Field(
        default=True, description="Cache intermediate results"
    )


class PipelineStep(BaseModel):
    """Represents a single step in the pipeline"""

    tool_name: str
    status: str  # "pending", "running", "completed", "failed"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration_ms: Optional[int] = None


class ProcessDocumentResult(BaseModel):
    markdown: str = Field(..., description="Final formatted Markdown")
    pipeline_steps: List[PipelineStep] = Field(..., description="Execution trace")
    total_duration_ms: int


class ProcessDocumentTool(BaseMCPTool):
    """
    Pipeline tool that processes PDF through multiple stages:
    1. Extract text from PDF
    2. Filter irrelevant content (optional)
    3. Convert to Markdown with LaTeX support
    """

    def __init__(self):
        super().__init__()
        self.registry = get_mcp_registry()
        self._cache: Dict[str, Any] = {}

    def _create_schema(self) -> MCPTool:
        return MCPTool(
            name="process_document",
            description="Complete pipeline: PDF → Text → Filter → Markdown with caching",
            inputSchema=ProcessDocumentArgs.model_json_schema(),
            outputSchema=ProcessDocumentResult.model_json_schema(),
        )

    async def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the document processing pipeline"""
        import time

        logger.info("Starting document processing pipeline")
        start_time = time.time()

        validated_params = ProcessDocumentArgs(**args)
        pipeline_steps: List[PipelineStep] = []

        try:
            # Step 1: PDF to Text
            text_result = await self._execute_step(
                "pdf_to_text",
                {"file_data": validated_params.file_data},
                pipeline_steps,
                cache_key=(
                    f"pdf_{hash(validated_params.file_data[:100])}"
                    if validated_params.cache_intermediate
                    else None
                ),
            )

            # Process each chunk through the complete pipeline
            chunks = text_result["chunks"]
            markdown_chunks: List[str] = []
            
            logger.info(f"Processing {len(chunks)} chunks through full pipeline")
            
            for i, chunk in enumerate(chunks):
                chunk_content = chunk["content"]
                logger.info(f"Processing chunk {i+1}/{len(chunks)}")
                
                # Step 2: Filter Content (optional) - per chunk
                if not validated_params.skip_filter:
                    filter_result = await self._execute_step(
                        "filter_content",
                        {"content": chunk_content},
                        pipeline_steps,
                        cache_key=(
                            f"filter_chunk_{i}_{hash(chunk_content[:100])}"
                            if validated_params.cache_intermediate
                            else None
                        ),
                    )
                    filtered_text = filter_result["filtered_content"]
                else:
                    filtered_text = chunk_content
                    if i == 0:  # Add skipped step only once
                        pipeline_steps.append(
                            PipelineStep(tool_name="filter_content", status="skipped")
                        )
                
                # Step 3: Text to Markdown - per chunk
                markdown_result = await self._execute_step(
                    "text_to_markdown",
                    {"content": filtered_text},
                    pipeline_steps,
                    cache_key=(
                        f"markdown_chunk_{i}_{hash(filtered_text[:100])}"
                        if validated_params.cache_intermediate
                        else None
                    ),
                )
                
                markdown_chunks.append(markdown_result["markdown"])
                logger.debug(f"Chunk {i+1} processed: {len(markdown_result['markdown'])} chars")
            
            # Combine all markdown chunks with proper separation
            final_markdown = "\n\n---\n\n".join(markdown_chunks)
            logger.info(
                f"Pipeline completed: {len(chunks)} chunks → {len(final_markdown)} chars markdown"
            )

            total_duration = int((time.time() - start_time) * 1000)

            result = ProcessDocumentResult(
                markdown=final_markdown,
                pipeline_steps=pipeline_steps,
                total_duration_ms=total_duration,
            )

            logger.info(f"Pipeline completed in {total_duration}ms")
            return result.model_dump()

        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
            # Mark failed step
            for step in pipeline_steps:
                if step.status == "running":
                    step.status = "failed"
                    step.error = str(e)
            raise

    async def _execute_step(
        self,
        tool_name: str,
        args: Dict[str, Any],
        pipeline_steps: List[PipelineStep],
        cache_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute a single pipeline step with caching"""
        import time

        # Check cache
        if cache_key and cache_key in self._cache:
            logger.info(f"Cache hit for {tool_name}")
            cached_result = self._cache[cache_key]
            pipeline_steps.append(
                PipelineStep(
                    tool_name=tool_name,
                    status="cached",
                    result=cached_result,
                    duration_ms=0,
                )
            )
            return cached_result

        # Create step
        step = PipelineStep(tool_name=tool_name, status="running")
        pipeline_steps.append(step)

        logger.info(f"Executing step: {tool_name}")
        step_start = time.time()

        try:
            result = await self.registry.execute_tool(tool_name, args)
            duration = int((time.time() - step_start) * 1000)

            step.status = "completed"
            step.result = result
            step.duration_ms = duration

            # Cache result
            if cache_key:
                self._cache[cache_key] = result

            logger.info(f"Step {tool_name} completed in {duration}ms")
            return result

        except Exception as e:
            step.status = "failed"
            step.error = str(e)
            logger.error(f"Step {tool_name} failed: {str(e)}")
            raise

    def clear_cache(self):
        """Clear the intermediate results cache"""
        self._cache.clear()
        logger.info("Pipeline cache cleared")
