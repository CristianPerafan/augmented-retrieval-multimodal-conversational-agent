# **Multi-modal RAG Chatbot**

## **Introduction**

## **Installation**

1. Clone the repository
```bash
git clone https://github.com/CristianPerafan/MultiModal-RAG-Chatbot.git
```
2. Create a virtual environment
```bash
python3 -m venv venv
```

3. Activate the virtual environment

    For Windows:
    ```bash
    venv\Scripts\activate
    ```
    For Linux:
    ```bash
    source venv/bin/activate
    ```
4. Install the requirements
```bash
pip install -r requirements.txt
```

5. Create a `.env` file in the root directory and add the following variables:

if you are using the OpenAI API, add the following variables:
```bash
OPENAI_API_KEY=<your_openai_api_key>
```
if you are using the Ollama API, add the following variables:
```bash
OLLAMA_LLM_MODEL=<ollama_llm_model>
OLLAMA_EMBED_MODEL=<ollama_embed_model>
```

## **Model Configuration**

To use the RAG conversational agent, you can configure two types of models:

1. **OpenAI (GPT) Models**
   - You can use the OpenAI API to access GPT models. This requires a valid API key. Be sure to follow OpenAI's instructions to obtain your key and set up your environment.

2. **Local Olla Models**
   - Ollama is a platform that allows you to run language models locally on your machine. This is useful if you want to avoid the latency or cost limitations associated with using an external API.


### Installing Ollama
To install Ollama on your machine, follow the instructions in the [Ollama repository](https://ollama.com/download).

### Configuring the Model
To dowload a local model with Ollama, you can use the following command:
```bash
ollama pull -model <model_name>
```

Replace `<model_name>` with the name of the model you want to download. You can find a list of available models on the [Ollama website](https://ollama.com/models).

### Model Selection for Our Implementation

To use conversational agents in our implementation, the following model are required:


1. **Large Language Model**
   - This model is used to generate responses to user queries. It is a large language model that can generate human-like text based on the input it receives.

2. **Embedding Model**
   - This model is used to generate embeddings for the documents in the knowledge base. It is used to find relevant documents based on the user's query.

For testing and development purposes, we use the following models Ollama models:

- **Large Language Model**: `llama3.2:latest`
- **Embedding Model**: `nomic-embed-text:latest`

Remember to replace the model names in the `.env` file with the models you have downloaded.