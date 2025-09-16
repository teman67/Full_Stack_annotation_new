# prompts.py

def build_annotation_prompt(tag_df, text_chunk):
    """
    Build prompt for flat (traditional) annotation.
    """
    tag_definitions = []
    for _, row in tag_df.iterrows():
        tag_name = row['tag_name']
        definition = row['definition']
        examples = row['examples']
        tag_definitions.append(f"- **{tag_name}**: {definition}\n  Examples: {examples}")
    
    tag_section = "\n".join(tag_definitions)
    
    prompt = f"""You are an expert scientific text annotator. Your task is to identify and extract entities from the given text according to the provided tag definitions.

## Tag Definitions:
{tag_section}

## Instructions:
1. Read the text carefully and identify all entities that match the provided tag definitions
2. Focus on specific terms, names, and concepts - NOT full sentences or phrases
3. Entities should typically be 1-8 words long (e.g., "protein", "DNA polymerase", "cell cycle regulation")
4. Avoid annotating complete sentences, long phrases, or descriptive text as single entities
5. **NEVER annotate common words like**: 'and', 'or', 'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', punctuation marks ('!', '?', ','), or single letters
6. For each entity, provide the exact character positions (start_char, end_char)
7. Extract the exact text span for each entity
8. Assign the most appropriate tag label

## Entity Length Guidelines:
- Single terms: "protein", "DNA", "temperature"
- Compound terms: "DNA polymerase", "cell membrane", "molecular weight"
- Named entities: "BRCA1", "p53 protein", "E. coli"
- Avoid: Full sentences, long descriptive phrases, text longer than ~50 characters, common English words (and, or, the, etc.), and punctuation marks

## Text to Annotate:
{text_chunk}

## Output Format:
Return your annotations as a JSON array with the following structure:
[
  {{
    "start_char": <integer>,
    "end_char": <integer>,
    "text": "<exact text span>",
    "label": "<tag_name>",
  }}
]

Make sure to:
- Use exact character positions from the original text
- Include only entities that clearly match the tag definitions
- Return valid JSON format only, no additional text

JSON Array:"""

    return prompt

def build_nested_annotation_prompt(tag_df, text_chunk):
    """
    Build prompt for nested annotation, where entities can contain other entities.
    """
    tag_definitions = []
    for _, row in tag_df.iterrows():
        tag_name = row['tag_name']
        definition = row['definition']
        examples = row['examples']
        tag_definitions.append(f"- **{tag_name}**: {definition}\n  Examples: {examples}")
    
    tag_section = "\n".join(tag_definitions)
    
    prompt = f"""You are an expert scientific text annotator specializing in hierarchical entity recognition. Your task is to identify and extract entities from the given text, including nested relationships where smaller entities exist within larger ones.

## Tag Definitions:
{tag_section}

## Instructions:
1. Read the text carefully and identify all entities that match the provided tag definitions
2. Focus on specific terms, names, and concepts - NOT full sentences or phrases
3. Entities should typically be 1-8 words long (e.g., "protein", "DNA polymerase", "cell cycle regulation")
4. Avoid annotating complete sentences, long phrases, or descriptive text as single entities
5. **NEVER annotate common words like**: 'and', 'or', 'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', punctuation marks ('!', '?', ','), or single letters
6. Look for hierarchical relationships where one entity contains another (e.g., a protein name within a protein complex description)
7. For each main entity, identify any nested entities within its boundaries
8. Provide exact character positions for both main and nested entities

## Entity Length Guidelines:
- Single terms: "protein", "DNA", "temperature"
- Compound terms: "DNA polymerase", "cell membrane", "molecular weight"
- Named entities: "BRCA1", "p53 protein", "E. coli"
- Avoid: Full sentences, long descriptive phrases, text longer than ~50 characters, common English words (and, or, the, etc.), and punctuation marks

## Nested Entity Rules:
- A nested entity must be completely contained within the boundaries of its parent entity
- Nested entities should have clear semantic relationships with their parents
- Common patterns include:
  * Gene names within gene complex descriptions (e.g., "BRCA1" in "BRCA1 gene complex")
  * Protein names within protein family descriptions (e.g., "p53" in "p53 tumor suppressor protein")
  * Chemical compounds within mixture descriptions (e.g., "glucose" in "glucose solution")
  * Specific terms within general category descriptions
- A single parent can contain multiple nested entities
- Keep nesting to reasonable levels (avoid over-segmentation)
- Only create nested entities when there's a clear semantic parent-child relationship
- Nested entities must have valid, non-overlapping character positions within the parent

## Text to Annotate:
{text_chunk}

## Output Format:
Return your annotations as a JSON array with the following structure:
[
  {{
    "start_char": <integer>,
    "end_char": <integer>,
    "text": "<exact text span>",
    "label": "<tag_name>",
    "nested_entities": [
      {{
        "start_char": <integer>,
        "end_char": <integer>,
        "text": "<exact nested text span>",
        "label": "<tag_name>",
      }}
    ]
  }}
]

## Example Structure:

**Example 1:** Single nested entity
Text: "The BRCA1 protein complex contains multiple domains"
- "BRCA1 protein complex" is a PROTEIN_COMPLEX (characters 4-27) ✓ Good length
- "BRCA1" is a PROTEIN_NAME (characters 4-9) ✓ Good length

**AVOID:** "The BRCA1 protein complex contains multiple domains that are essential for DNA repair function" ✗ Too long, this is a sentence

Output:
[
  {{
    "start_char": 4,
    "end_char": 27,
    "text": "BRCA1 protein complex",
    "label": "PROTEIN_COMPLEX",
    "nested_entities": [
      {{
        "start_char": 4,
        "end_char": 9,
        "text": "BRCA1",
        "label": "PROTEIN_NAME"
      }}
    ]
  }}
]

**Example 2:** Multiple nested entities
Text: "p53 and MDM2 proteins interact"
- "p53 and MDM2 proteins" is a PROTEIN_GROUP (characters 0-19)
- "p53" is a PROTEIN_NAME (characters 0-3)
- "MDM2" is a PROTEIN_NAME (characters 8-12)

Output:
[
  {{
    "start_char": 0,
    "end_char": 19,
    "text": "p53 and MDM2 proteins",
    "label": "PROTEIN_GROUP",
    "nested_entities": [
      {{
        "start_char": 0,
        "end_char": 3,
        "text": "p53",
        "label": "PROTEIN_NAME"
      }},
      {{
        "start_char": 8,
        "end_char": 12,
        "text": "MDM2",
        "label": "PROTEIN_NAME"
      }}
    ]
  }}
]

**Example 3:** No nested entities
Text: "DNA replication occurs"
- "DNA" is a MOLECULE (characters 0-3)

Output:
[
  {{
    "start_char": 0,
    "end_char": 3,
    "text": "DNA",
    "label": "MOLECULE",
    "nested_entities": []
  }}
]

Make sure to:
- Use exact character positions from the original text
- Ensure nested entities are within parent boundaries
- Include empty nested_entities array if no nesting exists
- Return valid JSON format only, no additional text

JSON Array:"""

    return prompt

def build_custom_prompt(tag_df, text_chunk, custom_instructions=""):
    """
    Build a custom prompt with additional user-specified instructions.
    """
    base_prompt = build_annotation_prompt(tag_df, text_chunk)
    
    if custom_instructions:
        # Insert custom instructions before the output format section
        sections = base_prompt.split("## Output Format:")
        enhanced_prompt = f"{sections[0]}\n## Additional Instructions:\n{custom_instructions}\n\n## Output Format:{sections[1]}"
        return enhanced_prompt
    
    return base_prompt

def build_few_shot_prompt(tag_df, text_chunk, examples=None):
    """
    Build a few-shot prompt with examples to improve annotation quality.
    """
    tag_definitions = []
    for _, row in tag_df.iterrows():
        tag_name = row['tag_name']
        definition = row['definition']
        examples = row['examples']
        tag_definitions.append(f"- **{tag_name}**: {definition}\n  Examples: {examples}")
    
    tag_section = "\n".join(tag_definitions)
    
    # Default examples if none provided
    if examples is None:
        examples = [
            {
                "text": "The p53 protein regulates cell cycle progression.",
                "annotations": [
                    {
                        "start_char": 4,
                        "end_char": 7,
                        "text": "p53",
                        "label": "PROTEIN_NAME",
                        
                    },
                    {
                        "start_char": 4,
                        "end_char": 15,
                        "text": "p53 protein",
                        "label": "PROTEIN",
                  
                    }
                ]
            }
        ]
    
    example_section = ""
    for i, example in enumerate(examples, 1):
        example_section += f"\n### Example {i}:\nText: \"{example['text']}\"\nAnnotations: {example['annotations']}\n"
    
    prompt = f"""You are an expert scientific text annotator. Your task is to identify and extract entities from the given text according to the provided tag definitions.

## Tag Definitions:
{tag_section}

## Examples:
{example_section}

## Instructions:
1. Read the text carefully and identify all entities that match the provided tag definitions
2. Follow the annotation style shown in the examples above
3. For each entity, provide the exact character positions (start_char, end_char)
4. Extract the exact text span for each entity
5. Assign the most appropriate tag label

## Text to Annotate:
{text_chunk}

## Output Format:
Return your annotations as a JSON array with the following structure:
[
  {{
    "start_char": <integer>,
    "end_char": <integer>,
    "text": "<exact text span>",
    "label": "<tag_name>",
  }}
]

Make sure to:
- Use exact character positions from the original text
- Include only entities that clearly match the tag definitions
- Return valid JSON format only, no additional text

JSON Array:"""

    return prompt