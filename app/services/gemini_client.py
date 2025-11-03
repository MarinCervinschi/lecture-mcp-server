from google import genai
from google.genai import types
from typing import Optional
from dataclasses import dataclass
import asyncio
import time
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class GeminiAPIError(Exception):
    """Raised when Gemini API call fails."""

    pass


class GeminiRateLimitError(GeminiAPIError):
    """Raised when rate limit is exceeded."""

    pass


class GeminiAuthError(GeminiAPIError):
    """Raised when authentication fails."""

    pass


@dataclass
class GeminiResponse:
    """Response from Gemini API."""

    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    finish_reason: str


class RateLimiter:
    """Simple rate limiter for API calls."""

    def __init__(self, max_requests_per_minute: int):
        self.max_requests = max_requests_per_minute
        self.requests = []
        self.lock = asyncio.Lock()

    async def acquire(self):
        """Wait if necessary to respect rate limit."""
        async with self.lock:
            now = time.time()
            # Remove requests older than 1 minute
            self.requests = [req for req in self.requests if now - req < 60]

            if len(self.requests) >= self.max_requests:
                # Wait until oldest request is 60 seconds old
                wait_time = 60 - (now - self.requests[0])
                if wait_time > 0:
                    logger.warning(f"Rate limit reached, waiting {wait_time:.2f}s")
                    await asyncio.sleep(wait_time)
                    # Clean up again after waiting
                    now = time.time()
                    self.requests = [req for req in self.requests if now - req < 60]

            self.requests.append(time.time())


class GeminiClient:
    """
    Client for interacting with Google Gemini API.
    """

    def __init__(self):
        """Initialize Gemini client."""
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self.temperature = settings.GEMINI_TEMPERATURE
        self.max_tokens = settings.GEMINI_MAX_TOKENS

        if not self.api_key:
            raise GeminiAuthError("GEMINI_API_KEY not configured")

        self.client = genai.Client(api_key=self.api_key)

        self.rate_limiter = RateLimiter(settings.GEMINI_MAX_REQUESTS_PER_MINUTE)

        logger.info(f"Initialized Gemini client with model: {self.model_name}")

    async def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> GeminiResponse:
        """
        Generate text using Gemini API.

        Args:
            prompt: Input prompt
            temperature: Temperature override
            max_tokens: Max tokens override

        Returns:
            GeminiResponse: Generated response

        Raises:
            GeminiAPIError: If generation fails
        """
        await self.rate_limiter.acquire()

        try:
            logger.debug(f"Generating response for prompt (length: {len(prompt)})")

            config = types.GenerateContentConfig(
                temperature=temperature or self.temperature,
                max_output_tokens=max_tokens or self.max_tokens,
            )

            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config,
            )

            if not response.candidates:
                raise GeminiAPIError("No candidates in response")

            candidate = response.candidates[0]

            if not candidate.content or not candidate.content.parts:
                raise GeminiAPIError("No content in response")

            content = candidate.content.parts[0].text

            if not content:
                raise GeminiAPIError("Empty content in response")

            usage = response.usage_metadata
            prompt_tokens = usage.prompt_token_count if usage else 0
            completion_tokens = usage.candidates_token_count if usage else 0
            total_tokens = usage.total_token_count if usage else 0

            if candidate.finish_reason is None:
                finish_reason = "UNKNOWN"
            else:
                finish_reason = (
                    candidate.finish_reason.name
                    if hasattr(candidate, "finish_reason")
                    else "UNKNOWN"
                )

            logger.info(
                f"Generated response: {len(content)} chars, "
                f"{total_tokens} tokens, reason: {finish_reason}"
            )

            return GeminiResponse(
                content=content,
                model=self.model_name,
                prompt_tokens=prompt_tokens or 0,
                completion_tokens=completion_tokens or 0,
                total_tokens=total_tokens or 0,
                finish_reason=finish_reason,
            )

        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}", exc_info=True)

            error_str = str(e).lower()
            if "quota" in error_str or "rate" in error_str or "429" in error_str:
                raise GeminiRateLimitError(f"Rate limit exceeded: {str(e)}")
            elif "api key" in error_str or "auth" in error_str or "401" in error_str:
                raise GeminiAuthError(f"Authentication failed: {str(e)}")
            else:
                raise GeminiAPIError(f"Generation failed: {str(e)}")

    async def generate_with_retry(
        self, prompt: str, max_retries: int = 3, **kwargs
    ) -> GeminiResponse:
        """
        Generate with automatic retry on failure.

        Args:
            prompt: Input prompt
            max_retries: Maximum number of retries
            **kwargs: Additional generation parameters

        Returns:
            GeminiResponse: Generated response

        Raises:
            GeminiAPIError: If all retries fail
        """
        last_error = None

        for attempt in range(max_retries):
            try:
                return await self.generate(prompt, **kwargs)
            except GeminiRateLimitError as e:
                # Wait exponentially for rate limit errors
                wait_time = 2**attempt
                logger.warning(
                    f"Rate limit hit (attempt {attempt + 1}/{max_retries}), "
                    f"waiting {wait_time}s"
                )
                await asyncio.sleep(wait_time)
                last_error = e
            except GeminiAPIError as e:
                # For other errors, retry with shorter wait
                if attempt < max_retries - 1:
                    wait_time = 1
                    logger.warning(
                        f"API error (attempt {attempt + 1}/{max_retries}), "
                        f"retrying in {wait_time}s: {str(e)}"
                    )
                    await asyncio.sleep(wait_time)
                last_error = e

        raise last_error or GeminiAPIError("All retries failed")

    async def test_connection(self) -> bool:
        """
        Test if API connection works.

        Returns:
            bool: True if connection successful
        """
        try:
            response = await self.generate("Say 'OK'", max_tokens=30)
            logger.info(
                f'Gemini API connection test successful. Response: "{response.content}"'
            )
            return True
        except Exception as e:
            logger.error(f"Gemini API connection test failed: {str(e)}")
            return False


_gemini_client: Optional[GeminiClient] = None


def get_gemini_client() -> GeminiClient:
    """
    Get or create Gemini client instance.

    Returns:
        GeminiClient: Gemini client instance
    """
    global _gemini_client

    if _gemini_client is None:
        _gemini_client = GeminiClient()

    return _gemini_client
