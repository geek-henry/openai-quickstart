import time
import os
from openai import OpenAI, RateLimitError, APIConnectionError, APIStatusError

from model import Model
from utils import LOG


class OpenAIModel(Model):
    def __init__(self, model: str, api_key: str):
        self.model = model
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    def make_request(self, prompt):
        attempts = 0
        while attempts < 3:
            try:
                if self.model == "gpt-3.5-turbo" or self.model.startswith("gpt-4"):
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "user", "content": prompt}
                        ]
                    )
                    translation = response.choices[0].message.content.strip()
                else:
                    response = self.client.completions.create(
                        model=self.model,
                        prompt=prompt,
                        max_tokens=150,
                        temperature=0
                    )
                    translation = response.choices[0].text.strip()

                return translation, True
            except RateLimitError as e:
                attempts += 1
                if attempts < 3:
                    LOG.warning("Rate limit reached. Waiting for 60 seconds before retrying.")
                    time.sleep(60)
                else:
                    raise Exception("Rate limit reached. Maximum attempts exceeded.")
            except APIConnectionError as e:
                LOG.error("The server could not be reached")
                LOG.error(f"Connection error cause: {e.__cause__}")
                raise Exception(f"API connection error: {e}")
            except APIStatusError as e:
                LOG.error("Another non-200-range status code was received")
                LOG.error(f"Status code: {e.status_code}")
                LOG.error(f"Response: {e.response}")
                raise Exception(f"API status error: {e.status_code}")
            except Exception as e:
                raise Exception(f"发生了未知错误：{e}")
        return "", False
