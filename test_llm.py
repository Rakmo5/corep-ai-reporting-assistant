from core.llm.client import LLMClient

llm = LLMClient()

out = llm.generate("Say hello in one line.")

print(out)
