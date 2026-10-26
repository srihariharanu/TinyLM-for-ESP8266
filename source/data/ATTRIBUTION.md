# Training data sources

General conversation subset:
- HuggingFaceTB/smoltalk, everyday-conversations configuration, training split.
- https://huggingface.co/datasets/HuggingFaceTB/smoltalk
- Original source: HuggingFaceTB/everyday-conversations-llama3.1-2k.
- https://huggingface.co/datasets/HuggingFaceTB/everyday-conversations-llama3.1-2k
- Original dataset license: Apache License 2.0. The license text is saved alongside this notice.
- Changes: extracted adjacent user/assistant pairs, converted text to lowercase ASCII, limited input length, shortened replies to their first sentence where possible, and removed duplicate pairs.

Focused conversation examples:
- Original examples authored for this experiment in prepare_focused.py.
- Multiple phrasings teach basic electronics, model limitations, and simple conversation.
- These pairs are training data, not an inference lookup table. The firmware contains no stored question/answer pairs.

Evaluation:
- Exact held-out prompts are excluded from all training pairs.
- A subset of focused inputs is also reserved for validation loss.
- Keyword scoring is a limited diagnostic. It is not a broad conversational benchmark.
