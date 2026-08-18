from typing import Optional
from langchain_groq import ChatGroq

from app.config.env import settings


class LLMConfig:
    """
    Configuration class for managing LLM (Large Language Model) settings and client instantiation.
    """

    def __init__(self):
        self.groq_api_key: Optional[str] = settings.groq_api_key
        self.model: str = settings.llm_model
        self.temperature: float = settings.llm_temperature
        self.max_tokens: Optional[int] = settings.llm_max_tokens

    def get_llm(
        self,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> ChatGroq:
        """
        Instantiate and return a ChatGroq client using configured settings.

        :param model: Optional override for the model name.
        :param temperature: Optional override for sampling temperature.
        :param max_tokens: Optional override for maximum response tokens.
        :param kwargs: Additional keyword arguments passed directly to ChatGroq.
        :return: ChatGroq instance
        """
        api_key = self.groq_api_key
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY environment variable is not set. Please set it in your .env file."
            )

        init_kwargs = {
            "groq_api_key": api_key,
            "model_name": model or self.model,
            "temperature": temperature if temperature is not None else self.temperature,
        }

        tokens = max_tokens if max_tokens is not None else (self.max_tokens or 4096)
        if tokens is not None:
            init_kwargs["max_tokens"] = tokens

        init_kwargs.update(kwargs)
        return ChatGroq(**init_kwargs)


llm_config = LLMConfig()

try:
    llm: Optional[ChatGroq] = llm_config.get_llm()
except ValueError:
    llm = None
