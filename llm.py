from langchain.llms import AzureOpenAI
from langchain.chat_models import AzureChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import re

import yaml


class LLM:
    def __init__(self, conf) -> None:
        self.END_TOKEN = conf["END_TOKEN"]
        self.START_TOKEN = conf["START_TOKEN"]
        self.MID_TOKEN = conf["MID_TOKEN"]
        self.MAX_TOKENS = conf["MAX_TOKENS"]
        self.mk_re = re.compile(r"^(```.*)([\n]?)(.*)")
        # read secret
        with open(conf["openai_key_file"], "r", encoding="utf-8") as f:
            key_conf = yaml.safe_load(f.read())
        self.OPENAI_API_KEY = key_conf["OPENAI_API_KEY"]
        self.OPENAI_API_BASE = key_conf["OPENAI_API_BASE"]
        self.OPENAI_API_VERSION = key_conf["OPENAI_API_VERSION"]
        self.DEPLOYMENT = key_conf["DEPLOYMENT"]
        self.is_chat_model = conf["is_chat_model"]
        if conf["is_chat_model"]:
            self.model = self.get_chat_model()
        else:
            self.model = self.get_llm_model()


    def get_chat_model(self):
        return AzureChatOpenAI(
            openai_api_type="azure",
            openai_api_version=self.OPENAI_API_VERSION,
            openai_api_base=self.OPENAI_API_BASE,
            openai_api_key=self.OPENAI_API_KEY,
            deployment_name=self.DEPLOYMENT,
            temperature=0,
            max_tokens=self.MAX_TOKENS,
        )
    
    def get_llm_model(self):
        return AzureOpenAI(
            openai_api_type="azure",
            openai_api_version=self.OPENAI_API_VERSION,
            openai_api_base=self.OPENAI_API_BASE,
            openai_api_key=self.OPENAI_API_KEY,
            deployment_name=self.DEPLOYMENT,
            temperature=0,
            max_tokens=self.MAX_TOKENS,
        )

    def get_fore_context(self, inputs):
        return inputs[: inputs.find(self.END_TOKEN)].replace(
            self.START_TOKEN, ""
            )
    
    def replace_pos_token(self, context):
        return context.replace(self.START_TOKEN, "{start_token}"
                               ).replace(self.END_TOKEN, "{middle_token}"
                                         ).replace(self.MID_TOKEN, "{end_token}")

    def complete_code(self, code_context):
        """Take the input from the request and output.

        args:
            code_context(str): the code_context

        return(dict): the response
        """
        prompt_context = f"""Please complete code for the given code snippet."""
        code_context = self.get_fore_context(code_context)
        prompt_template = PromptTemplate.from_template(
            prompt_context + "Only output the inserted code without markdown tags or any other non-code tags. The code snippet is the following, delimited by ```. \n\n```{code_context}```")
        output_parser = StrOutputParser()
        chain = prompt_template | self.model | output_parser
        completion = chain.invoke({"code_context": code_context})
        mk_match = self.mk_re.match(completion)
        if mk_match:
            completion = mk_match.group(2) + mk_match.group(3)
        return completion
