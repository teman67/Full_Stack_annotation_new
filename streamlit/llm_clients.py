# llm_clients.py
import streamlit as st
import os
import openai
from typing import Optional
from openai import AuthenticationError, OpenAIError
try:
    import anthropic
except ImportError:
    anthropic = None

class LLMClient:
    def __init__(self, api_key, provider, model):  # Fixed: __init__ instead of **init**
        self.api_key = api_key
        self.provider = provider
        self.model = model
       
    def generate(self, prompt, temperature=0.1, max_tokens=1000):
        """
        Enhanced generate method with better error handling
        """
        try:
            if not prompt or prompt.strip() == "":
                raise ValueError("Empty prompt provided")
               
            if self.provider == "OpenAI":
                return self._call_openai(prompt, temperature, max_tokens)
            elif self.provider == "Claude":
                return self._call_claude(prompt, temperature, max_tokens)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
               
        except Exception as e:
            st.error(f"❌ LLM API call failed: {e}")
            return None  # <--- Return None instead of "[]"
   
    def _call_openai(self, prompt, temperature, max_tokens):  # Fixed: _call_openai instead of *call*openai
        import openai
       
        try:
            client = openai.OpenAI(api_key=self.api_key)
           
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a scientific text annotation expert. Always respond with valid JSON array format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=60  # Add timeout
            )
           
            content = response.choices[0].message.content
           
            if not content:
                st.warning("OpenAI returned empty response")
                return "[]"
               
            return content.strip()
           
        except openai.RateLimitError:
            st.error("OpenAI rate limit exceeded. Please wait and try again.")
            return None
        except openai.APITimeoutError:
            st.error("OpenAI API timeout. Please try again.")
            return None
        except openai.AuthenticationError:
            st.error("OpenAI authentication failed. Please check your API key. Have a look at the [OpenAI API Key Guide](https://platform.openai.com/api-keys) for more details.")
            return None
        except Exception as e:
            st.error(f"OpenAI API error: {e}")
            return None
   
    def _call_claude(self, prompt, temperature, max_tokens):  # Fixed: _call_claude instead of *call*claude
        if anthropic is None:
            st.error("Anthropic library not installed. Please install it with: pip install anthropic")
            return "[]"
       
        try:
            client = anthropic.Anthropic(api_key=self.api_key)
           
            response = client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                timeout=60  # Add timeout
            )
           
            content = response.content[0].text if response.content else ""
           
            if not content:
                st.warning("Claude returned empty response")
                return "[]"
               
            return content.strip()
           
        except anthropic.RateLimitError:
            st.error("Claude rate limit exceeded. Please wait and try again.")
            return None
        except anthropic.APITimeoutError:
            st.error("Claude API timeout. Please try again.")
            return None
        except anthropic.AuthenticationError:
            st.error("Claude authentication failed. Please check your API key. Have a look at the [Claude API Key Guide](https://docs.anthropic.com/en/api/overview) for more details.")
            return None
        except Exception as e:
            st.error(f"Claude API error: {e}")
            return None