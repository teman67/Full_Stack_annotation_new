import asyncio
import json
import logging
from typing import Optional, List, Dict, Any
import openai
from anthropic import Anthropic
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMClient:
    """
    Async LLM client supporting multiple providers (OpenAI, Claude, Groq)
    Migrated and enhanced from the original Streamlit app
    """
    
    def __init__(self, provider: str, model: str, api_key: Optional[str] = None):
        self.provider = provider
        self.model = model
        self.api_key = api_key or self._get_default_api_key(provider)
        
        if not self.api_key:
            raise ValueError(f"No API key provided for {provider}")
    
    def _get_default_api_key(self, provider: str) -> str:
        """Get default API key from settings"""
        key_map = {
            "OpenAI": settings.openai_api_key,
            "Claude": settings.anthropic_api_key,
            "Groq": settings.groq_api_key,
        }
        return key_map.get(provider, "")
    
    async def generate(self, prompt: str, temperature: float = 0.1, max_tokens: int = 1000) -> Optional[str]:
        """
        Enhanced async generate method with better error handling
        """
        try:
            if not prompt or prompt.strip() == "":
                raise ValueError("Empty prompt provided")
            
            if self.provider == "OpenAI":
                return await self._call_openai(prompt, temperature, max_tokens)
            elif self.provider == "Claude":
                return await self._call_claude(prompt, temperature, max_tokens)
            elif self.provider == "Groq":
                return await self._call_groq(prompt, temperature, max_tokens)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
        
        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            return None
    
    async def _call_openai(self, prompt: str, temperature: float, max_tokens: int) -> Optional[str]:
        """Call OpenAI API asynchronously"""
        try:
            client = openai.AsyncOpenAI(api_key=self.api_key)
            
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a scientific text annotation expert. Always respond with valid JSON array format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            return response.choices[0].message.content
            
        except openai.AuthenticationError:
            logger.error("OpenAI authentication failed - check API key")
            return None
        except openai.RateLimitError:
            logger.error("OpenAI rate limit exceeded")
            return None
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return None
    
    async def _call_claude(self, prompt: str, temperature: float, max_tokens: int) -> Optional[str]:
        """Call Claude API asynchronously"""
        try:
            client = Anthropic(api_key=self.api_key)
            
            # Note: Anthropic client doesn't have async support yet, so we run in executor
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[
                        {
                            "role": "user",
                            "content": f"You are a scientific text annotation expert. Always respond with valid JSON array format.\n\n{prompt}"
                        }
                    ]
                )
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return None
    
    async def _call_groq(self, prompt: str, temperature: float, max_tokens: int) -> Optional[str]:
        """Call Groq API asynchronously"""
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a scientific text annotation expert. Always respond with valid JSON array format."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=data, timeout=30.0)
                response.raise_for_status()
                
                result = response.json()
                return result["choices"][0]["message"]["content"]
                
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return None

class AnnotationService:
    """
    Service for processing annotations with LLMs
    Migrated and enhanced from the original helper.py
    """
    
    def __init__(self):
        self.client = None
    
    async def process_document_annotations(
        self,
        text: str,
        tag_definitions: Dict[str, Any],
        provider: str = "OpenAI",
        model: str = "gpt-4",
        temperature: float = 0.1,
        max_tokens: int = 1000,
        chunk_size: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Process document with LLM to generate annotations
        """
        try:
            self.client = LLMClient(provider, model)
            
            # Split text into chunks if needed
            chunks = self._split_text_into_chunks(text, chunk_size)
            all_annotations = []
            
            for i, chunk in enumerate(chunks):
                logger.info(f"Processing chunk {i+1}/{len(chunks)}")
                
                # Build prompt for this chunk
                prompt = self._build_annotation_prompt(chunk, tag_definitions)
                
                # Get LLM response
                response = await self.client.generate(prompt, temperature, max_tokens)
                
                if response:
                    # Parse and validate annotations
                    chunk_annotations = self._parse_llm_response(response, chunk, i * chunk_size)
                    all_annotations.extend(chunk_annotations)
            
            # Post-process annotations (deduplicate, validate positions, etc.)
            return self._post_process_annotations(all_annotations, text)
            
        except Exception as e:
            logger.error(f"Error processing document annotations: {e}")
            return []
    
    def _split_text_into_chunks(self, text: str, chunk_size: int) -> List[str]:
        """Split text into overlapping chunks"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        overlap = chunk_size // 4  # 25% overlap
        
        for i in range(0, len(text), chunk_size - overlap):
            chunk = text[i:i + chunk_size]
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks
    
    def _build_annotation_prompt(self, text: str, tag_definitions: Dict[str, Any]) -> str:
        """Build annotation prompt for LLM"""
        # This would use the prompt building logic from your prompts_nested.py
        tag_examples = []
        for tag_name, tag_info in tag_definitions.items():
            tag_examples.append(f"- {tag_name}: {tag_info.get('definition', '')}")
        
        prompt = f"""
You are an expert at annotating scientific text. Your task is to identify and extract entities from the given text based on the provided tag definitions.

Tag Definitions:
{chr(10).join(tag_examples)}

Text to annotate:
{text}

Please identify all entities in the text that match the tag definitions above. Return your response as a JSON array where each object has:
- "text": the exact text of the entity
- "start": the start position in the text
- "end": the end position in the text  
- "tag": the tag name
- "confidence": a confidence score between 0 and 1

Ensure all positions are accurate and entities don't overlap inappropriately.
"""
        return prompt
    
    def _parse_llm_response(self, response: str, chunk_text: str, offset: int = 0) -> List[Dict[str, Any]]:
        """Parse LLM response and extract annotations"""
        try:
            # Try to parse as JSON
            if response.startswith('```json'):
                response = response.replace('```json', '').replace('```', '')
            
            annotations = json.loads(response)
            
            if not isinstance(annotations, list):
                return []
            
            validated_annotations = []
            for ann in annotations:
                if self._validate_annotation(ann, chunk_text):
                    # Adjust positions with offset
                    ann['start'] += offset
                    ann['end'] += offset
                    validated_annotations.append(ann)
            
            return validated_annotations
            
        except json.JSONDecodeError:
            logger.error(f"Failed to parse LLM response as JSON: {response}")
            return []
    
    def _validate_annotation(self, annotation: Dict[str, Any], text: str) -> bool:
        """Validate annotation format and positions"""
        required_fields = ['text', 'start', 'end', 'tag']
        
        # Check required fields
        if not all(field in annotation for field in required_fields):
            return False
        
        start = annotation['start']
        end = annotation['end']
        
        # Check position validity
        if start < 0 or end > len(text) or start >= end:
            return False
        
        # Check if extracted text matches
        extracted_text = text[start:end]
        if extracted_text != annotation['text']:
            return False
        
        return True
    
    def _post_process_annotations(self, annotations: List[Dict[str, Any]], full_text: str) -> List[Dict[str, Any]]:
        """Post-process annotations to remove duplicates and fix issues"""
        # Remove duplicates based on position and text
        unique_annotations = []
        seen_positions = set()
        
        for ann in annotations:
            position_key = (ann['start'], ann['end'], ann['text'])
            if position_key not in seen_positions:
                seen_positions.add(position_key)
                unique_annotations.append(ann)
        
        # Sort by start position
        unique_annotations.sort(key=lambda x: x['start'])
        
        return unique_annotations

# Singleton service instance
annotation_service = AnnotationService()
