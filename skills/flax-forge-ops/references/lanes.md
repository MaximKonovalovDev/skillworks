# Gateway lanes (from factory/sidecars.json)

Chat defaults to the local model lane with OpenRouter fallback. Vision and
embed default to OpenRouter-backed lanes. Media lanes queue work to GPU
workers. Every lane refuses loudly without its key and never fakes bytes.
