# World News Summarizer App

This app uses the cohere LLM and GDELT API to quickly show you what's going on in the world right now!


## Approach

I have created the necessary functions for my app in a separate file. These functions are used to create GDELT parameters from natural language using the cohere LLM, query the GDELT API for articles related to these parameters and summarize the articles as well as give reading recommendations using the LLM again. This tool is intended to be used by anybody, who needs to quickly get an overview over current or historic news about any event in any region. However, this tool is specifically useful for high-level executives in international companies, who need to get up-to-date news about what could influence their companies operations worldwide.


## Usage

Using the text input field, users can enter a question about any news-worthy event worldwide, historic or current, in natural language.

The output after processing all the articles is divided into 3 tabs:

1. "Summary": The user can see at a glance the answer to their question together with a few recommended articles to dive deeper.
2. "Articles": The user can see the top 50 articles related to their question sorted by relevance.
3. "Parameters": The user can check which parameters where given to the GDELT API by the LLM based on their question.


## Setup

All functions needed to serve the dashboard were created in a separate file called "news_llm_functions.py". From the actual app ("news_llm_app.py") these functions are sequentially called to generate the wanted output.


## Link

https://world-news-summarizer-app.streamlit.app/
