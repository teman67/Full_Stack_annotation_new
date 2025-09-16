# Entity length validation utility
import streamlit as st
from stop_word_filter import is_stop_word

def validate_entity_length(entity_text, entity_type="main"):
    """
    Validate entity length and word count to prevent over-annotation of sentences/phrases.
    
    Args:
        entity_text (str): The text of the entity to validate
        entity_type (str): Type of entity ("main" or "nested") for messaging
        
    Returns:
        tuple: (is_valid, reason) where is_valid is bool and reason is str
    """
    # Define maximum entity length (in characters) to prevent over-annotation
    MAX_ENTITY_LENGTH = 100  # Reasonable limit for scientific entities
    MAX_WORD_COUNT = 10      # Maximum number of words in an entity
    
    if not entity_text:
        return False, "Empty text"
    
    # Check if it's a stop word
    if is_stop_word(entity_text):
        return False, f"Common word/stop word: '{entity_text}'"
    
    # Check character length
    if len(entity_text) > MAX_ENTITY_LENGTH:
        return False, f"Too long ({len(entity_text)} chars > {MAX_ENTITY_LENGTH})"
    
    # Check word count
    word_count = len(entity_text.split())
    if word_count > MAX_WORD_COUNT:
        return False, f"Too many words ({word_count} > {MAX_WORD_COUNT})"
    
    # Check if it looks like a sentence (contains sentence-ending punctuation)
    sentence_indicators = ['. ', '? ', '! ']
    if any(indicator in entity_text for indicator in sentence_indicators):
        return False, "Contains sentence structure"
    
    # Check for very long phrases that span multiple clauses
    clause_indicators = [', and ', ', or ', ', but ', '; ']
    if any(indicator in entity_text for indicator in clause_indicators):
        return False, "Contains multiple clauses"
    
    return True, "Valid"

def filter_entities_by_length(entities, chunk_index=None):
    """
    Filter out overly long entities from a list of entities.
    
    Args:
        entities (list): List of entity dictionaries
        chunk_index (int): Optional chunk index for logging
        
    Returns:
        tuple: (filtered_entities, filtered_count)
    """
    filtered_entities = []
    filtered_count = 0
    
    for entity in entities:
        if not isinstance(entity, dict):
            continue
            
        entity_text = entity.get('text', '')
        is_valid, reason = validate_entity_length(entity_text)
        
        if not is_valid:
            if chunk_index is not None:
                st.warning(f"Chunk {chunk_index}: Filtered out overly long entity: '{entity_text[:50]}...' ({reason})")
            else:
                st.warning(f"Filtered out overly long entity: '{entity_text[:50]}...' ({reason})")
            filtered_count += 1
            continue
        
        # If entity has nested entities, validate them too
        if 'nested_entities' in entity and isinstance(entity['nested_entities'], list):
            valid_nested = []
            for nested_entity in entity['nested_entities']:
                nested_text = nested_entity.get('text', '')
                nested_is_valid, nested_reason = validate_entity_length(nested_text, "nested")
                
                if nested_is_valid:
                    valid_nested.append(nested_entity)
                else:
                    if chunk_index is not None:
                        st.warning(f"Chunk {chunk_index}: Filtered out overly long nested entity: '{nested_text[:30]}...' ({nested_reason})")
                    else:
                        st.warning(f"Filtered out overly long nested entity: '{nested_text[:30]}...' ({nested_reason})")
            
            # Update the entity with filtered nested entities
            entity_copy = entity.copy()
            entity_copy['nested_entities'] = valid_nested
            filtered_entities.append(entity_copy)
        else:
            filtered_entities.append(entity)
    
    return filtered_entities, filtered_count
