def build_evaluation_prompt(tag_df, entities_batch):
    """
    Build a prompt for evaluating whether annotations match their tag definitions.
    """
    tag_definitions = []
    for _, row in tag_df.iterrows():
        tag_name = row['tag_name']
        definition = row['definition']
        examples = row['examples']
        tag_definitions.append(f"- **{tag_name}**: {definition}\n  Examples: {examples}")
    
    tag_section = "\n".join(tag_definitions)
    
    # Format entities for evaluation
    entities_text = ""
    for i, entity in enumerate(entities_batch):
        entities_text += f"{i}. Text: \"{entity.get('text', '')}\" | Label: {entity.get('label', '')} | Position: [{entity.get('start_char', 0)}:{entity.get('end_char', 0)}]\n"
    
    prompt = f"""You are an expert scientific text annotator evaluating the quality of entity annotations. Your task is to determine if each annotation correctly matches its assigned label definition.

## Tag Definitions:
{tag_section}

## Entities to Evaluate:
{entities_text}

## Instructions:
For each entity, evaluate:
1. Does the annotated text match the definition of its assigned label?
2. Is the label assignment appropriate and accurate?
3. Should the annotation be kept, changed to a different label, or deleted?

## Evaluation Criteria:
- **Correct**: The text clearly matches the label definition
- **Change Label**: The text represents a valid entity but has the wrong label
- **Delete**: The text doesn't represent any valid entity or is incorrectly annotated

## Output Format:
Return your evaluation as a JSON array with the following structure:
[
  {{
    "entity_index": 0,
    "current_text": "annotated text",
    "current_label": "assigned label",
    "is_correct": true/false,
    "recommendation": "keep" | "change_label" | "delete",
    "suggested_label": "new label if recommending change",
    "reasoning": "brief explanation of your decision",
    "confidence": 0.0-1.0
  }}
]

## Examples:

**Example 1 - Correct:**
Entity: "p53" labeled as PROTEIN_NAME
Evaluation: "p53" is a well-known tumor suppressor protein name
Result: {{"entity_index": 0, "current_text": "p53", "current_label": "PROTEIN_NAME", "is_correct": true, "recommendation": "keep", "suggested_label": "", "reasoning": "p53 is a well-known protein name", "confidence": 0.95}}

**Example 2 - Wrong Label:**
Entity: "glucose" labeled as PROTEIN_NAME
Evaluation: "glucose" is a chemical/molecule, not a protein
Result: {{"entity_index": 1, "current_text": "glucose", "current_label": "PROTEIN_NAME", "is_correct": false, "recommendation": "change_label", "suggested_label": "CHEMICAL", "reasoning": "glucose is a sugar molecule, not a protein", "confidence": 0.9}}

**Example 3 - Should Delete (Stop Word):**
Entity: "and" labeled as BIOLOGICAL_PROCESS
Evaluation: "and" is a common conjunction, not a biological entity
Result: {{"entity_index": 2, "current_text": "and", "current_label": "BIOLOGICAL_PROCESS", "is_correct": false, "recommendation": "delete", "suggested_label": "", "reasoning": "and is a common conjunction word, not a scientific entity", "confidence": 0.99}}

**Example 4 - Should Delete (Punctuation):**
Entity: "!" labeled as CHEMICAL_NOTATION
Evaluation: "!" is punctuation, not a chemical notation
Result: {{"entity_index": 3, "current_text": "!", "current_label": "CHEMICAL_NOTATION", "is_correct": false, "recommendation": "delete", "suggested_label": "", "reasoning": "exclamation mark is punctuation, not a chemical entity", "confidence": 0.99}}

**Common words that should always be deleted:**
- Articles: "the", "a", "an"
- Conjunctions: "and", "or", "but"  
- Prepositions: "in", "on", "at", "to", "for", "of", "with", "by"
- Punctuation: "!", "?", ",", ".", ";", ":"
- Single letters (unless chemical elements): "x", "y", "z"

Evaluate each entity carefully and return valid JSON only.

JSON Array:"""

    return prompt
