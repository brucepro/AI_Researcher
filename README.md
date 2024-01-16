# Personal Researcher
Program generates a task list based on query, searches each task in the list, saves it to research, reviews the research and generates and answer. 

# API server
currently using the llamacpp completion server. But any api server should work. Recommend a long context model. I am using sciphi but the sensei model they have might handle the search query a bit better, but not sure it would handle the task generation better. 

server.exe -m ./models/7B/sciphi-self-rag-mistral-7b-32k.Q5_K_M.gguf -c 30000 --n-gpu-layers 21

#
using the lite version of duck duck go since the urlhandler is super simple. 
It also only shows the bot 2500 chars of the search result, that gives the top 5 or so results. 
#
Tested with a 7b model I coded it on. Haven't tried mixtral yet. 

# Support
If you find this useful, https://www.buymeacoffee.com/brucepro