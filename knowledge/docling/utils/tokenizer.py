from typing import Dict, List, Tuple
from tiktoken import get_encoding
from transformers.tokenization_utils_base import PreTrainedTokenizerBase

class OpenAITokenizerWrapper(PreTrainedTokenizerBase):
    """Minimal wrapper for OpenAI's tokenizer compatible with Docling."""

    def __init__(self, model_name: str = "cl100k_base", max_length: int = 8191, **kwargs):
        super().__init__(model_max_length=max_length, **kwargs)
        self.tokenizer = get_encoding(model_name)
        # tiktoken max_token_value is the largest token id; vocab size is +1
        self._vocab_size = int(self.tokenizer.max_token_value) + 1

    # ✅ Fix: truthiness / len() must not raise
    def __len__(self) -> int:
        return self._vocab_size

    # ✅ Optional but extra-safe: avoid any truthiness edge-cases
    def __bool__(self) -> bool:
        return True

    def tokenize(self, text: str, **kwargs) -> List[str]:
        return [str(t) for t in self.tokenizer.encode(text)]

    def _tokenize(self, text: str) -> List[str]:
        return self.tokenize(text)

    def _convert_token_to_id(self, token: str) -> int:
        return int(token)

    def _convert_id_to_token(self, index: int) -> str:
        return str(index)

    def get_vocab(self) -> Dict[str, int]:
        # token->id mapping; this is a placeholder since tiktoken vocab isn't enumerable this way
        return {str(i): i for i in range(self._vocab_size)}

    @property
    def vocab_size(self) -> int:
        return self._vocab_size

    def save_vocabulary(self, *args) -> Tuple[str]:
        return ()

    @classmethod
    def from_pretrained(cls, *args, **kwargs):
        return cls()
