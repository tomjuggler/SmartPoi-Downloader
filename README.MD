### Test of FREE LLM's in Aider AI Coding Assistant

1. LLama 3 (Via OpenRouter) openrouter/meta-llama/llama-3-8b-instruct:free 
- Works. Test project setup succeeded with one prompt! 
- For simple projects, this LLM does a great job. It's helpful for setting things up and basic boilerplate code. 
2. Mistral openrouter/mistralai/mistral-7b-instruct:free 
- didn't work at all! Maybe there is another Mistral version that does? 
3. Gemini (Free for now, from Google) gemini/gemini-1.5-pro-latest
- Works. Test prompt setup succeeded with two prompts and one bug fix..
- This is apparently the best at coding (according to Aider devs) 
- Did the job, maybe it is the best, but LLAMA 8B is also fine. 
4. Some LLM's in Ollama running locally on Laptop CPU (Slow) Let's try this lol
- yi-coder is just too slow
- Mistral 7B is going to shut my computer down in a minute. My music is stuttering.... takes 20 min in my experience to do anything at all. Why bother (on CPU)
- Last try with "TinyLLAMA": It might work.. on GPU or TPU. Nope. The LLM did not conform to the edit format. 

Also try these: 
- openrouter/meta-llama/llama-3.1-8b-instruct:free
- openrouter/mattshumer/reflection-70b:free
- openrouter/nousresearch/hermes-3-llama-3.1-405b:free
- openrouter/huggingfaceh4/zephyr-7b-beta:free
- openrouter/microsoft/phi-3-medium-128k-instruct:free

# Test of paid LLM's (some of these are much more capable than the above..) 
1. 