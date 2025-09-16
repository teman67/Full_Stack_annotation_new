import streamlit as st
import pandas as pd
import json
import streamlit as st
import pandas as pd
from prompts_nested import build_annotation_prompt, build_nested_annotation_prompt
from evaluation_prompt import build_evaluation_prompt
from entity_length_validator import validate_entity_length, filter_entities_by_length
import time
import streamlit.components.v1 as components
import colorsys
import html
import re

def calculate_dynamic_height(text):
    """
    Calculate dynamic height based on text length.
    Base height of 200px + additional height based on text length.
    """
    base_height = -40
    text_length = len(text)
    
    # Add height based on text length (roughly 1px per 2 characters)
    additional_height = max(200, min(text_length // 2, 500))  # Min 50px, max 300px additional
    
    return base_height + additional_height

def display_annotated_entities_with_selection(entities_list):
    """
    Display annotated entities with highlighting, tooltips, and text selection capability.
    
    Args:
        entities_list: List of entities with 'source' field indicating 'llm' or 'manual'
    """
    import streamlit as st
    import streamlit.components.v1 as components
    
    if entities_list:
        highlighted_html = highlight_text_with_entities_and_selection(
            st.session_state.text_data,
            entities_list,
            st.session_state.label_colors
        )
        
        # Create a complete HTML document with inline CSS and JavaScript for selection
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                .annotation-container {{
                    font-family: Arial, sans-serif;
                    font-size: 16px;
                    line-height: 1.7;
                    padding: 20px;
                    background-color: #f9f9f9;
                    border-radius: 8px;
                    border: 1px solid #e0e0e0;
                    margin-top: 30px;
                    
                    user-select: text;
                    -webkit-user-select: text;
                    -moz-user-select: text;
                    -ms-user-select: text;
                }}
               
                .annotation-container span[data-tooltip] {{
                    position: relative;
                    cursor: help;
                    transition: all 0.2s ease;
                }}
                
                .manual-annotation {{
                    background-color: #ffeb3b !important;
                    border: 2px solid #f57f17 !important;
                }}
                
                .auto-detected {{
                    background-color: #ff9800 !important;
                    border: 2px solid #e65100 !important;
                    border-style: dashed !important;
                }}
                
                .nested-entity {{
                    border: 2px dotted #666 !important;
                    position: relative;
                }}
                
                .nested-entity::before {{
                    content: "↳";
                    position: absolute;
                    left: -8px;
                    top: -2px;
                    font-size: 10px;
                    color: #666;
                }}
                
                .parent-entity {{
                    /* Parent entities use their tag-based colors */
                }}
               
                .annotation-container span[data-tooltip]:hover {{
                    transform: translateY(-1px);
                    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
                }}
               
                .tooltip {{
                    visibility: hidden;
                    position: absolute;
                    bottom: 125%;
                    left: 50%;
                    transform: translateX(-50%);
                    background-color: #333;
                    color: white;
                    padding: 8px 12px;
                    border-radius: 6px;
                    font-size: 14px;
                    font-weight: normal;
                    white-space: nowrap;
                    z-index: 1000;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                    opacity: 0;
                    transition: opacity 0.3s, visibility 0.3s;
                }}
               
                .tooltip::after {{
                    content: '';
                    position: absolute;
                    top: 100%;
                    left: 50%;
                    margin-left: -6px;
                    border-width: 6px;
                    border-style: solid;
                    border-color: #333 transparent transparent transparent;
                }}
               
                .annotation-container span[data-tooltip]:hover .tooltip {{
                    visibility: visible;
                    opacity: 1;
                }}
                
                .selection-info {{
                    margin-top: 10px;
                    padding: 10px;
                    background-color: #e3f2fd;
                    border-radius: 4px;
                    border-left: 4px solid #2196f3;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="annotation-container" id="textContainer">
                {highlighted_html}
            </div>
            <div id="selectionInfo" class="selection-info" style="display: none;">
                <strong>Selected text:</strong> <span id="selectedText"></span>
            </div>
           
            <script>
                document.addEventListener('DOMContentLoaded', function() {{
                    const spans = document.querySelectorAll('span[data-tooltip]');
                    spans.forEach(span => {{
                        const tooltip = span.querySelector('.tooltip');
                        if (tooltip) {{
                            const label = span.getAttribute('data-tooltip');
                            const source = span.getAttribute('data-source') || 'LLM';
                            tooltip.textContent = label + ' (' + source + ')';
                        }}
                    }});
                    
                    // Text selection handling - FIXED VERSION
                    const container = document.getElementById('textContainer');
                    const selectionInfo = document.getElementById('selectionInfo');
                    const selectedTextSpan = document.getElementById('selectedText');
                    
                    document.addEventListener('mouseup', function() {{
                        const selection = window.getSelection();
                        if (selection.toString().trim().length > 0) {{
                            const selectedText = selection.toString().trim();
                            selectedTextSpan.textContent = selectedText;
                            selectionInfo.style.display = 'block';
                            
                            // FIXED: Proper message format for Streamlit
                            const message = {{
                                selectedText: selectedText,
                                timestamp: Date.now()
                            }};
                            
                            // Send to parent window (Streamlit)
                            window.parent.postMessage(message, '*');
                            
                        }} else {{
                            selectionInfo.style.display = 'none';
                        }}
                    }});
                }});
            </script>
        </body>
        </html>
        """
       
        # Calculate dynamic height based on text length
        dynamic_height = calculate_dynamic_height(st.session_state.text_data)
        
        # Use Streamlit's HTML component to render the complete HTML - FIXED KEY
        selection_result = components.html(
            full_html, 
            height=dynamic_height, 
            scrolling=True,
              # FIXED: Added unique key
        )
        
        # FIXED: Handle selection result properly
        if selection_result:
            if isinstance(selection_result, dict) and 'selectedText' in selection_result:
                selected_text = selection_result.get('selectedText', '').strip()
                if selected_text and selected_text != st.session_state.get('selected_text_for_annotation', ''):
                    st.session_state.selected_text_for_annotation = selected_text
                    st.rerun()  # Force rerun to update the input field
            elif isinstance(selection_result, str):
                # Sometimes the result comes as a string
                try:
                    import json
                    result_dict = json.loads(selection_result)
                    selected_text = result_dict.get('selectedText', '').strip()
                    if selected_text and selected_text != st.session_state.get('selected_text_for_annotation', ''):
                        st.session_state.selected_text_for_annotation = selected_text
                        st.rerun()
                except:
                    pass  # Ignore parsing errors


def highlight_text_with_entities_and_selection(text: str, entities: list, label_colors: dict) -> str:
    """
    Enhanced version that handles both LLM and manual annotations with different styling.
    Also properly handles nested entities when in nested mode.
    Uses character positions instead of text search for accuracy.
    """
    import html
    used_positions = set()
    highlighted = []
    last_pos = 0
    
    # Check annotation mode to determine how to handle entities
    is_nested_mode = st.session_state.get('annotation_mode', 'Nested (Hierarchical)') == "Nested (Hierarchical)"

    # Filter entities that have valid character positions and sort by start position
    valid_entities = []
    
    if is_nested_mode:
        # In nested mode, flatten the entities for display but preserve structure info
        for ent in entities:
            start_char = ent.get("start_char")
            end_char = ent.get("end_char")
            if start_char is not None and end_char is not None and start_char >= 0 and end_char <= len(text):
                # Verify that the position actually matches the expected text
                actual_text = text[start_char:end_char]
                expected_text = ent.get("text", "")
                if actual_text == expected_text:
                    # Add main entity
                    valid_entities.append(ent)
                    
                    # Add nested entities as separate entities for display
                    nested_entities = ent.get('nested_entities', [])
                    for nested_ent in nested_entities:
                        nested_start = nested_ent.get("start_char")
                        nested_end = nested_ent.get("end_char")
                        if nested_start is not None and nested_end is not None and nested_start >= 0 and nested_end <= len(text):
                            # Verify nested entity position
                            nested_actual = text[nested_start:nested_end]
                            nested_expected = nested_ent.get("text", "")
                            if nested_actual == nested_expected:
                                # Create display entity for nested item
                                display_nested = nested_ent.copy()
                                display_nested['source'] = ent.get('source', 'llm')
                                display_nested['is_nested'] = True
                                display_nested['parent_text'] = ent.get('text', '')
                                valid_entities.append(display_nested)
                else:
                    # Try to find the correct position for this text
                    corrected_positions = find_correct_position(text, expected_text, start_char)
                    if corrected_positions:
                        ent_copy = ent.copy()
                        ent_copy["start_char"] = corrected_positions[0]
                        ent_copy["end_char"] = corrected_positions[1]
                        valid_entities.append(ent_copy)
    else:
        # In flat mode, use entities as-is (original behavior)
        for ent in entities:
            start_char = ent.get("start_char")
            end_char = ent.get("end_char")
            if start_char is not None and end_char is not None and start_char >= 0 and end_char <= len(text):
                # Verify that the position actually matches the expected text
                actual_text = text[start_char:end_char]
                expected_text = ent.get("text", "")
                if actual_text == expected_text:
                    valid_entities.append(ent)
                else:
                    # Try to find the correct position for this text
                    corrected_positions = find_correct_position(text, expected_text, start_char)
                    if corrected_positions:
                        ent_copy = ent.copy()
                        ent_copy["start_char"] = corrected_positions[0]
                        ent_copy["end_char"] = corrected_positions[1]
                        valid_entities.append(ent_copy)

    sorted_entities = sorted(valid_entities, key=lambda x: x.get("start_char", 0))

    for ent in sorted_entities:
        start_char = ent["start_char"]
        end_char = ent["end_char"]
        span = ent["text"]
        label = ent["label"]
        source = ent.get("source", "llm")
        is_nested = ent.get("is_nested", False)
        color = label_colors.get(label, "#e0e0e0")  # fallback if missing

        # Check for overlapping positions
        if any(i in used_positions for i in range(start_char, end_char)):
            continue

        # Add text before this entity
        highlighted.append(html.escape(text[last_pos:start_char]))
        
        # Different styling for different types of annotations
        additional_class = ""
        border_style = ""
        
        if source == "manual":
            additional_class = "manual-annotation"
            manual_color = "#ffeb3b"  # Yellow for manual
            border_style = "2px solid #f57f17"
        elif source == "manual_auto":
            additional_class = "manual-annotation auto-detected"
            manual_color = "#ff9800"  # Orange for auto-detected from manual
            border_style = "2px dashed #e65100"
        elif source == "auto_detected":
            additional_class = "llm-annotation auto-detected"
            manual_color = "#4caf50"  # Green for auto-detected from LLM
            border_style = "2px dashed #2e7d32"
        else:
            # LLM annotations - use tag-based colors and differentiate nested vs parent
            manual_color = color  # Use the tag-based color from label_colors
            if is_nested:
                additional_class = "nested-entity"
                border_style = "2px dotted #666"
            else:
                additional_class = "parent-entity"
                border_style = f"2px solid {color}"
        
        # Create tooltip text with additional info
        tooltip_text = label
        if is_nested:
            parent_text = ent.get('parent_text', 'Unknown')
            tooltip_text += f" (nested in: {parent_text[:30]}...)" if len(parent_text) > 30 else f" (nested in: {parent_text})"
        elif source == "manual":
            tooltip_text += " (Manual)"
        elif source == "manual_auto":
            tooltip_text += " (Auto-detected from manual)"
        elif source == "auto_detected":
            tooltip_text += " (Auto-detected from LLM)"
        
        # Add the highlighted entity
        highlighted.append(
            f'<span class="{additional_class}" style="background-color: {manual_color}; font-weight: bold; padding: 2px 4px; '
            f'border-radius: 3px; cursor: help; display: inline-block; '
            f'border: {border_style};" '
            f'data-tooltip="{html.escape(tooltip_text)}" data-source="{source.upper()}">'
            f'{html.escape(span)}<span class="tooltip"></span></span>'
        )
        
        used_positions.update(range(start_char, end_char))
        last_pos = end_char

    # Append any remaining text after all entities
    highlighted.append(html.escape(text[last_pos:]))

    return ''.join(highlighted)

def generate_label_colors(tag_list):
    """
    Generate visually distinct colors for each tag using hashing and HSL spacing.
    """
    label_colors = {}
    num_tags = len(tag_list)

    for i, tag in enumerate(sorted(tag_list)):
        # Generate hue spaced around the color wheel
        hue = i / num_tags
        lightness = 0.7
        saturation = 0.6
        rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
        # Convert to hex
        color = '#{:02x}{:02x}{:02x}'.format(
            int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)
        )
        label_colors[tag] = color
    return label_colors

def estimate_tokens(text):
    """
    Rough token estimation (1 token ≈ 4 characters for English text)
    """
    return len(text) // 4

def display_processing_summary(text, tag_df, chunk_size, temperature, max_tokens, model_provider, model):
    """
    Display a comprehensive summary of processing parameters
    """
    # Use overlapping chunks for processing
    chunks_with_overlap = chunk_text(text, chunk_size)
    simple_chunks = chunk_text_simple(text, chunk_size)
    
    # Calculate overlap statistics
    overlap_size = max(50, chunk_size // 10)
    total_chunk_chars = sum(len(chunk[0]) for chunk in chunks_with_overlap)
    overlap_chars = total_chunk_chars - len(text) if total_chunk_chars > len(text) else 0
    
    st.markdown("### 📊 Processing Summary")
    
    # Create metrics columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Text Length", f"{len(text):,} chars", help="Total number of characters in the input text")
        st.metric("Estimated Tokens", f"{estimate_tokens(text):,}", help="Approximate number of tokens (1 token ≈ 4 characters)")
    
    with col2:
        st.metric("Number of Chunks", len(chunks_with_overlap), help="Text will be split into this many overlapping chunks")
        st.metric("Chunk Size", f"{chunk_size:,} chars", help="Target characters per chunk")
    
    with col3:
        st.metric("Overlap Size", f"{overlap_size:,} chars", help="Characters overlapping between adjacent chunks")
        st.metric("Total Tags", len(tag_df), help="Number of annotation tags available")
    
    with col4:
        st.metric("Temperature", temperature, help="LLM creativity setting (0=deterministic, 1=creative)")
        st.metric("Max Tokens/Response", max_tokens, help="Maximum tokens the LLM can generate per chunk")
    
    # Second row of metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Model", f"{model_provider}: {model}", help="Selected language model")
    
    with col2:
        if overlap_chars > 0:
            st.metric("Overlap Coverage", f"{(overlap_chars/total_chunk_chars)*100:.1f}%", help="Percentage of text appearing in multiple chunks")
        else:
            st.metric("Overlap Coverage", "0%", help="No overlap detected")
    
    with col3:
        st.metric("Processing Mode", "🔗 Overlapping", help="Using overlapping chunks to improve entity detection")
    
    with col4:
        redundancy = overlap_chars / len(text) * 100 if len(text) > 0 else 0
        st.metric("Text Redundancy", f"{redundancy:.1f}%", help="Extra text processed due to overlapping")

    # Display chunk information in an expandable section
    with st.expander("📋 Chunk Details", expanded=False):
        chunk_data = []
        for i, (chunk_text_content, start_offset, end_offset) in enumerate(chunks_with_overlap):
            chunk_data.append({
                "Chunk #": i + 1,
                "Start": start_offset,
                "End": end_offset,
                "Characters": len(chunk_text_content),
                "Est. Tokens": estimate_tokens(chunk_text_content),
                "Preview": chunk_text_content[:100] + "..." if len(chunk_text_content) > 100 else chunk_text_content
            })
        
        chunk_df = pd.DataFrame(chunk_data)
        st.dataframe(chunk_df, use_container_width=True)
        
        # Show overlap analysis
        if len(chunks_with_overlap) > 1:
            st.markdown("**🔗 Chunk Overlap Analysis:**")
            overlap_info = []
            for i in range(len(chunks_with_overlap) - 1):
                current_chunk = chunks_with_overlap[i]
                next_chunk = chunks_with_overlap[i + 1]
                
                current_end = current_chunk[2]
                next_start = next_chunk[1]
                
                if current_end > next_start:
                    overlap_amount = current_end - next_start
                    overlap_text = text[next_start:current_end]
                    overlap_info.append({
                        "Between Chunks": f"{i+1} → {i+2}",
                        "Overlap Chars": overlap_amount,
                        "Overlap Text": overlap_text[:60] + "..." if len(overlap_text) > 60 else overlap_text
                    })
            
            if overlap_info:
                overlap_df = pd.DataFrame(overlap_info)
                st.dataframe(overlap_df, use_container_width=True)
                st.success(f"✅ Found {len(overlap_info)} overlapping regions to improve entity detection at chunk boundaries")
            else:
                st.warning("⚠️ No overlaps detected - this might indicate chunking issues")

    # Display tag information
    # with st.expander("🏷️ Tag Configuration", expanded=False):
    #     st.dataframe(tag_df[['tag_name', 'definition']], use_container_width=True)
    
    st.markdown("---")

def display_chunk_progress(current_chunk, total_chunks, chunk_text, start_time=None):
    """
    Display attractive progress information for current chunk processing
    """
    # Progress bar
    progress = current_chunk / total_chunks
    st.progress(progress)
    
    # Progress info
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"**Processing Chunk {current_chunk}/{total_chunks}**")
        if start_time:
            elapsed = time.time() - start_time
            estimated_total = elapsed / progress if progress > 0 else 0
            remaining = estimated_total - elapsed
            st.caption(f"⏱️ Elapsed: {elapsed:.1f}s | Estimated remaining: {remaining:.1f}s")
    
    with col2:
        st.metric("Progress", f"{progress:.1%}")
    
    with col3:
        st.metric("Chunk Size", f"{len(chunk_text):,} chars")
        
    # Show chunk preview
    preview = chunk_text[:200] + "..." if len(chunk_text) > 200 else chunk_text
    st.caption(f"📝 **Chunk Preview:** {preview}")

def display_chunk_progress_with_overlap(current_chunk, total_chunks, chunk_text, start_offset, end_offset, start_time=None):
    """
    Display attractive progress information for overlapping chunk processing
    """
    # Progress bar
    progress = current_chunk / total_chunks
    st.progress(progress)
    
    # Progress info
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        st.markdown(f"**Processing Chunk {current_chunk}/{total_chunks}**")
        if start_time:
            elapsed = time.time() - start_time
            estimated_total = elapsed / progress if progress > 0 else 0
            remaining = estimated_total - elapsed
            st.caption(f"⏱️ Elapsed: {elapsed:.1f}s | Estimated remaining: {remaining:.1f}s")
    
    with col2:
        st.metric("Progress", f"{progress:.1%}")
    
    with col3:
        st.metric("Position", f"{start_offset:,}-{end_offset:,}")
    
    with col4:
        st.metric("Chunk Size", f"{len(chunk_text):,} chars")
        
    # Show chunk preview
    preview = chunk_text[:200] + "..." if len(chunk_text) > 200 else chunk_text
    st.caption(f"📝 **Chunk Preview:** {preview}")

def remove_overlapping_duplicates(all_entities, processed_chunks):
    """
    Remove duplicate entities that appear in overlapping regions between chunks.
    
    Args:
        all_entities (list): All entities from all chunks
        processed_chunks (list): Information about each processed chunk
    
    Returns:
        list: Deduplicated entities
    """
    if len(processed_chunks) <= 1:
        return all_entities
    
    deduplicated = []
    seen_entities = set()
    
    # Sort entities by start position for consistent processing
    sorted_entities = sorted(all_entities, key=lambda x: (x.get('start_char', 0), x.get('end_char', 0)))
    
    for entity in sorted_entities:
        start_char = entity.get('start_char', 0)
        end_char = entity.get('end_char', 0)
        text = entity.get('text', '').strip().lower()
        label = entity.get('label', '')
        
        # Create a unique identifier for this entity
        entity_id = (start_char, end_char, text, label)
        
        # Skip if we've already seen this exact entity
        if entity_id in seen_entities:
            continue
        
        # Check for near-duplicate entities (same text and label, very close positions)
        is_duplicate = False
        for seen_start, seen_end, seen_text, seen_label in seen_entities:
            if (text == seen_text and label == seen_label and
                abs(start_char - seen_start) <= 5 and abs(end_char - seen_end) <= 5):
                is_duplicate = True
                break
        
        if not is_duplicate:
            deduplicated.append(entity)
            seen_entities.add(entity_id)
    
    return deduplicated


# Dynamic token calculation based on chunk size
def get_token_recommendations(chunk_size):
    if chunk_size <= 500:
        return 200, 800, 300
    elif chunk_size <= 1000:
        return 300, 1200, 400
    elif chunk_size <= 2000:
        return 500, 1800, 1000
    elif chunk_size <= 3000:
        return 700, 2500, 1400
    else:
        return 1000, 3000, 1800
    
def chunk_text(text: str, chunk_size: int, overlap_size: int = None):
    """
    Splits text into chunks of approximately chunk_size characters with optional overlap.
    Tries to split on newline or space to avoid cutting words abruptly.
    
    Args:
        text (str): Text to chunk
        chunk_size (int): Target size for each chunk
        overlap_size (int): Number of characters to overlap between chunks (default: 10% of chunk_size)
    
    Returns:
        list: List of tuples (chunk_text, start_offset, end_offset)
    """
    if overlap_size is None:
        overlap_size = max(50, chunk_size // 10)  # Default: 10% overlap, minimum 50 chars
    
    chunks = []
    start = 0
    length = len(text)
    
    while start < length:
        end = start + chunk_size
        if end >= length:
            # Last chunk - no overlap needed
            chunks.append((text[start:], start, length))
            break
            
        # Try to split on last newline before end
        split_pos = text.rfind('\n', start, end)
        if split_pos == -1 or split_pos <= start:
            split_pos = text.rfind(' ', start, end)
        if split_pos == -1 or split_pos <= start:
            split_pos = end  # fallback hard cut

        chunk_text = text[start:split_pos].strip()
        chunks.append((chunk_text, start, split_pos))
        
        # FIXED: Next chunk starts with overlap, but ensure we advance by a reasonable amount
        next_start = split_pos - overlap_size
        
        # Ensure we advance by at least 25% of chunk_size to prevent infinite loops
        min_advance = max(chunk_size // 4, 100)
        if next_start <= start + min_advance:
            next_start = start + min_advance
        
        start = next_start
    
    return chunks

def chunk_text_simple(text: str, chunk_size: int):
    """
    Legacy simple chunking function for backward compatibility.
    Splits text into chunks without overlap.
    """
    chunks = []
    start = 0
    length = len(text)
    while start < length:
        end = start + chunk_size
        if end >= length:
            chunks.append(text[start:])
            break
        # Try to split on last newline before end
        split_pos = text.rfind('\n', start, end)
        if split_pos == -1 or split_pos <= start:
            split_pos = text.rfind(' ', start, end)
        if split_pos == -1 or split_pos <= start:
            split_pos = end  # fallback hard cut

        chunks.append(text[start:split_pos].strip())
        start = split_pos
    return chunks

def aggregate_entities(all_entities, offset):
    """
    Adjust entity character positions by offset (chunk start position in full text).
    """
    for ent in all_entities:
        ent['start_char'] += offset
        ent['end_char'] += offset
    return all_entities

def find_correct_position(text, expected_text, approximate_start):
    """
    Find the correct position of expected_text in the text, starting near approximate_start.
    
    Args:
        text (str): The full text to search in
        expected_text (str): The text we're looking for
        approximate_start (int): The approximate starting position
    
    Returns:
        tuple: (start_char, end_char) if found, None otherwise
    """
    # First try exact match at the approximate position
    if (approximate_start >= 0 and 
        approximate_start + len(expected_text) <= len(text) and
        text[approximate_start:approximate_start + len(expected_text)] == expected_text):
        return (approximate_start, approximate_start + len(expected_text))
    
    # Search in a window around the approximate position
    search_window = 50  # Look 50 characters before and after
    start_search = max(0, approximate_start - search_window)
    end_search = min(len(text), approximate_start + len(expected_text) + search_window)
    
    search_text = text[start_search:end_search]
    found_pos = search_text.find(expected_text)
    
    if found_pos != -1:
        actual_start = start_search + found_pos
        actual_end = actual_start + len(expected_text)
        return (actual_start, actual_end)
    
    # If not found in window, try finding all occurrences and pick the closest
    all_positions = find_all_occurrences(text, expected_text)
    if all_positions:
        # Find the position closest to the approximate start
        closest_pos = min(all_positions, key=lambda x: abs(x[0] - approximate_start))
        return closest_pos
    
    return None

def highlight_text_with_entities(text: str, entities: list, label_colors: dict) -> str:
    import html
    used_positions = set()
    highlighted = []
    last_pos = 0

    # Filter entities that have valid character positions and sort by start position
    valid_entities = []
    for ent in entities:
        start_char = ent.get("start_char")
        end_char = ent.get("end_char")
        if start_char is not None and end_char is not None and start_char >= 0 and end_char <= len(text):
            # Verify that the position actually matches the expected text
            actual_text = text[start_char:end_char]
            expected_text = ent.get("text", "")
            if actual_text == expected_text:
                valid_entities.append(ent)
            else:
                # Try to find the correct position for this text
                corrected_positions = find_correct_position(text, expected_text, start_char)
                if corrected_positions:
                    ent_copy = ent.copy()
                    ent_copy["start_char"] = corrected_positions[0]
                    ent_copy["end_char"] = corrected_positions[1]
                    valid_entities.append(ent_copy)

    sorted_entities = sorted(valid_entities, key=lambda x: x.get("start_char", 0))

    for ent in sorted_entities:
        start_char = ent["start_char"]
        end_char = ent["end_char"]
        span = ent["text"]
        label = ent["label"]
        color = label_colors.get(label, "#e0e0e0")  # fallback if missing

        # Check for overlapping positions
        if any(i in used_positions for i in range(start_char, end_char)):
            continue

        # Add text before this entity
        highlighted.append(html.escape(text[last_pos:start_char]))
        
        # Add the highlighted entity
        highlighted.append(
            f'<span style="background-color: {color}; font-weight: bold; padding: 2px 4px; '
            f'border-radius: 3px; cursor: help; display: inline-block; '
            f'border: 1px solid {color};" '
            f'data-tooltip="{html.escape(label)}">'
            f'{html.escape(span)}</span>'
        )
        
        used_positions.update(range(start_char, end_char))
        last_pos = end_char

    # Append any remaining text after all entities
    highlighted.append(html.escape(text[last_pos:]))

    return ''.join(highlighted)

def display_annotated_entities():
    """
    Display annotated entities with highlighting and tooltips if they exist in session state.
    
    This function checks for annotated entities in Streamlit session state and renders
    them as an interactive HTML component with hover tooltips showing entity labels.
    """
    if 'annotated_entities' in st.session_state and st.session_state.annotated_entities:
        highlighted_html = highlight_text_with_entities(
            st.session_state.text_data,
            st.session_state.annotated_entities,
            st.session_state.label_colors
        )
        
        # Create a complete HTML document with inline CSS and JavaScript
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                .annotation-container {{
                    font-family: Arial, sans-serif;
                    font-size: 16px;
                    line-height: 1.7;
                    padding: 20px;
                    background-color: #f9f9f9;
                    border-radius: 8px;
                    border: 1px solid #e0e0e0;
                    margin: 10px 0 -30px 0;
                }}
               
                .annotation-container span[data-tooltip] {{
                    position: relative;
                    cursor: help;
                    transition: all 0.2s ease;
                }}
               
                .annotation-container span[data-tooltip]:hover {{
                    transform: translateY(-1px);
                    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
                }}
               
                .tooltip {{
                    visibility: hidden;
                    position: absolute;
                    bottom: 125%;
                    left: 50%;
                    transform: translateX(-50%);
                    background-color: #333;
                    color: white;
                    padding: 8px 12px;
                    border-radius: 6px;
                    font-size: 14px;
                    font-weight: normal;
                    white-space: nowrap;
                    z-index: 1000;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                    opacity: 0;
                    transition: opacity 0.3s, visibility 0.3s;
                }}
               
                .tooltip::after {{
                    content: '';
                    position: absolute;
                    top: 100%;
                    left: 50%;
                    margin-left: -6px;
                    border-width: 6px;
                    border-style: solid;
                    border-color: #333 transparent transparent transparent;
                }}
               
                .annotation-container span[data-tooltip]:hover .tooltip {{
                    visibility: visible;
                    opacity: 1;
                }}
            </style>
        </head>
        <body>
            <div class="annotation-container">
                {highlighted_html.replace('data-tooltip="', 'data-tooltip="').replace('">', '"><span class="tooltip"></span>')}
            </div>
           
            <script>
                document.addEventListener('DOMContentLoaded', function() {{
                    const spans = document.querySelectorAll('span[data-tooltip]');
                    spans.forEach(span => {{
                        const tooltip = span.querySelector('.tooltip');
                        if (tooltip) {{
                            tooltip.textContent = span.getAttribute('data-tooltip');
                        }}
                    }});
                }});
            </script>
        </body>
        </html>
        """
       
        # Calculate dynamic height based on text length
        dynamic_height = calculate_dynamic_height(st.session_state.text_data)
        
        # Use Streamlit's HTML component to render the complete HTML
        components.html(full_html, height=dynamic_height, scrolling=True)

def validate_annotations_streamlit(text, entities):
    """
    Validate that start_char and end_char positions in annotations match the actual text.
    Enhanced version with detailed error reporting and correction suggestions.
    
    Args:
        text (str): The source text
        entities (list): List of entity dictionaries
    
    Returns:
        dict: Validation results with errors and statistics
    """
    
    validation_results = {
        'total_entities': len(entities),
        'correct_entities': 0,
        'errors': [],
        'warnings': [],
        'detailed_analysis': []
    }
    
    st.write(f"🔍 Validating {len(entities)} annotations...")
    
    # Create a progress bar for validation
    validation_progress = st.progress(0)
    validation_status = st.empty()
    
    for i, entity in enumerate(entities):
        # Update progress
        validation_progress.progress((i + 1) / len(entities))
        validation_status.text(f"Validating entity {i+1}/{len(entities)}: '{entity.get('text', 'N/A')}'")
        
        start_char = entity.get('start_char')
        end_char = entity.get('end_char')
        expected_text = entity.get('text')
        
        analysis = {
            'entity_index': i,
            'expected_text': expected_text,
            'start_char': start_char,
            'end_char': end_char,
            'label': entity.get('label', 'Unknown'),
            'status': 'unknown'
        }
        
        # Skip entities with missing required fields
        if None in [start_char, end_char, expected_text]:
            error_info = {
                'entity_index': i,
                'expected_text': expected_text,
                'start_char': start_char,
                'end_char': end_char,
                'error': 'Missing required fields',
                'label': entity.get('label', 'Unknown')
            }
            validation_results['errors'].append(error_info)
            analysis['status'] = 'missing_fields'
            analysis['error'] = 'Missing required fields'
            validation_results['detailed_analysis'].append(analysis)
            continue
        
        # Extract actual text from the source using the character positions
        try:
            if start_char < 0 or end_char > len(text) or start_char >= end_char:
                analysis['status'] = 'invalid_range'
                analysis['error'] = f'Invalid position range: [{start_char}:{end_char}]'
                validation_results['errors'].append({
                    'entity_index': i,
                    'expected_text': expected_text,
                    'start_char': start_char,
                    'end_char': end_char,
                    'error': 'Invalid position range',
                    'label': entity.get('label', 'Unknown')
                })
                validation_results['detailed_analysis'].append(analysis)
                continue
                
            actual_text = text[start_char:end_char]
            analysis['actual_text'] = actual_text
            
            # Check if texts match exactly
            if actual_text == expected_text:
                validation_results['correct_entities'] += 1
                analysis['status'] = 'correct'
                validation_results['detailed_analysis'].append(analysis)
            else:
                # Find where the expected text actually appears
                correct_positions = find_all_occurrences(text, expected_text)
                analysis['found_positions'] = correct_positions
                
                if correct_positions:
                    closest_pos = min(correct_positions, key=lambda x: abs(x[0] - start_char))
                    analysis['suggested_position'] = closest_pos
                    analysis['position_offset'] = closest_pos[0] - start_char
                
                error_info = {
                    'entity_index': i,
                    'expected_text': expected_text,
                    'actual_text': actual_text,
                    'start_char': start_char,
                    'end_char': end_char,
                    'label': entity.get('label', 'Unknown'),
                    'found_positions': correct_positions,
                    'suggested_correction': closest_pos if correct_positions else None
                }
                validation_results['errors'].append(error_info)
                analysis['status'] = 'position_mismatch'
                analysis['error'] = f'Text mismatch: expected "{expected_text}", got "{actual_text}"'
                validation_results['detailed_analysis'].append(analysis)
                
        except IndexError:
            error_info = {
                'entity_index': i,
                'expected_text': expected_text,
                'start_char': start_char,
                'end_char': end_char,
                'error': 'Index out of range',
                'label': entity.get('label', 'Unknown')
            }
            validation_results['errors'].append(error_info)
            analysis['status'] = 'index_error'
            analysis['error'] = 'Index out of range'
            validation_results['detailed_analysis'].append(analysis)
    
    # Clear progress indicators
    validation_progress.empty()
    validation_status.empty()
    
    # Display detailed results
    if validation_results['errors']:
        st.error(f"❌ Found {len(validation_results['errors'])} annotation errors")
        
        # Show examples of errors
        st.subheader("🔍 Error Analysis")
        for error in validation_results['errors'][:5]:  # Show first 5 errors
            with st.expander(f"Error: '{error['expected_text'][:50]}...'"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Expected:**", error['expected_text'])
                    st.write("**Position:**", f"{error['start_char']}-{error['end_char']}")
                    st.write("**Label:**", error['label'])
                
                with col2:
                    if 'actual_text' in error:
                        st.write("**Actually extracted:**", error['actual_text'])
                    if 'suggested_correction' in error and error['suggested_correction']:
                        st.write("**Suggested position:**", f"{error['suggested_correction'][0]}-{error['suggested_correction'][1]}")
                        
        if len(validation_results['errors']) > 5:
            st.info(f"... and {len(validation_results['errors']) - 5} more errors")
    else:
        st.success("✅ All annotations have correct character positions!")
    
    # Additional checks (overlaps, duplicates, etc.) - keep existing logic
    if st.session_state.annotation_mode == "Flat (Traditional)":
        sorted_entities = sorted([e for e in entities if all(k in e for k in ['start_char', 'end_char'])], 
                               key=lambda x: x['start_char'])
        
        for i in range(len(sorted_entities) - 1):
            current = sorted_entities[i]
            next_entity = sorted_entities[i + 1]
            
            if current['end_char'] > next_entity['start_char']:
                warning = {
                    'type': 'overlap',
                    'entity1': current,
                    'entity2': next_entity
                }
                validation_results['warnings'].append(warning)
    else:
        # In nested mode, check for exact duplicates instead
        sorted_entities = sorted([e for e in entities if all(k in e for k in ['start_char', 'end_char'])], 
                               key=lambda x: (x['start_char'], x['end_char']))
        
        for i in range(len(sorted_entities) - 1):
            current = sorted_entities[i]
            next_entity = sorted_entities[i + 1]
            
            if (current['start_char'] == next_entity['start_char'] and 
                current['end_char'] == next_entity['end_char'] and
                current.get('label') == next_entity.get('label')):
                warning = {
                    'type': 'duplicate',
                    'entity1': current,
                    'entity2': next_entity
                }
                validation_results['warnings'].append(warning)
    
    # Check for zero-length annotations
    zero_length = [e for e in entities if e.get('start_char') == e.get('end_char')]
    if zero_length:
        validation_results['warnings'].extend(zero_length)
    
    return validation_results

def find_all_occurrences(text, pattern):
    """Find all occurrences of pattern in text with enhanced matching"""
    positions = []
    start = 0
    
    # Strategy 1: Exact match
    while True:
        pos = text.find(pattern, start)
        if pos == -1:
            break
        positions.append((pos, pos + len(pattern)))
        start = pos + 1
    
    # Strategy 2: If no exact matches, try case-insensitive
    if not positions:
        text_lower = text.lower()
        pattern_lower = pattern.lower()
        start = 0
        while True:
            pos = text_lower.find(pattern_lower, start)
            if pos == -1:
                break
            positions.append((pos, pos + len(pattern)))
            start = pos + 1
    
    # Strategy 3: If still no matches, try normalized whitespace
    if not positions:
        normalized_pattern = ' '.join(pattern.split())
        normalized_text = ' '.join(text.split())
        start = 0
        while True:
            pos = normalized_text.find(normalized_pattern, start)
            if pos == -1:
                break
            # Convert back to original text positions (approximate)
            positions.append((pos, pos + len(normalized_pattern)))
            start = pos + 1
    
    return positions

def find_similar_words_case_insensitive(text, pattern):
    """
    Find all occurrences of pattern in text, case-insensitive.
    Uses word boundaries to avoid matching substrings within larger words.
    Returns list of tuples with (start_char, end_char, actual_text_found).
    """
    import re
    
    # Escape special regex characters in the pattern
    escaped_pattern = re.escape(pattern)
    
    # For very short patterns (1-3 characters), be more strict about word boundaries
    # This prevents matching substrings within larger words
    if len(pattern.strip()) <= 3:
        # For short patterns like "pH", "CO", "UV", etc., use strict word boundaries
        # Also check that we're not matching within larger alphabetic sequences
        regex_pattern = re.compile(r'(?<![a-zA-Z])' + escaped_pattern + r'(?![a-zA-Z])', re.IGNORECASE)
    else:
        # For longer patterns, check if it looks like a compound word or phrase
        if '-' in pattern or ' ' in pattern:
            # For hyphenated words or phrases, don't require strict word boundaries
            # but ensure we're not matching within words
            regex_pattern = re.compile(r'(?<!\w)' + escaped_pattern + r'(?!\w)', re.IGNORECASE)
        else:
            # For regular single words, use word boundaries
            regex_pattern = re.compile(r'\b' + escaped_pattern + r'\b', re.IGNORECASE)
    
    matches = []
    for match in regex_pattern.finditer(text):
        start_pos = match.start()
        end_pos = match.end()
        matched_text = text[start_pos:end_pos]
        
        # Additional validation for short patterns to avoid false positives
        if len(pattern.strip()) <= 3:
            # Check if this looks like a standalone scientific term
            # by examining the surrounding context
            before_char = text[start_pos - 1] if start_pos > 0 else ' '
            after_char = text[end_pos] if end_pos < len(text) else ' '
            
            # Allow if surrounded by whitespace, punctuation, or string boundaries
            if (before_char.isspace() or before_char in '.,;:!?()[]{}"\'-=' or start_pos == 0) and \
               (after_char.isspace() or after_char in '.,;:!?()[]{}"\'-=' or end_pos == len(text)):
                matches.append((start_pos, end_pos, matched_text))
        else:
            matches.append((start_pos, end_pos, matched_text))
    
    return matches

def create_annotations_for_similar_words(text, word_to_find, label, existing_annotations=None, source_type='manual_auto'):
    """
    Create annotations for all similar words (case-insensitive) found in text.
    
    Args:
        text (str): The source text to search in
        word_to_find (str): The word/phrase to find similar instances of
        label (str): The label to assign to all found instances
        existing_annotations (list): List of existing annotations to avoid duplicates
        source_type (str): Source type for new annotations ('auto_detected' or 'manual_auto')
    
    Returns:
        list: List of new annotation dictionaries
    """
    if existing_annotations is None:
        existing_annotations = []
    
    # Find all similar words (case-insensitive)
    similar_matches = find_similar_words_case_insensitive(text, word_to_find)
    
    new_annotations = []
    
    for start_pos, end_pos, matched_text in similar_matches:
        # Check if this position already has an annotation
        overlap_found = False
        for existing in existing_annotations:
            existing_start = existing.get('start_char', 0)
            existing_end = existing.get('end_char', 0)
            existing_label = existing.get('label', '')
            existing_text = existing.get('text', '')
            
            # Check for exact duplicate (same position, label, and text)
            if (start_pos == existing_start and end_pos == existing_end and 
                label == existing_label and matched_text.lower() == existing_text.lower()):
                overlap_found = True
                break
                
        if not overlap_found:
            annotation = {
                'start_char': start_pos,
                'end_char': end_pos,
                'text': matched_text,  # Use the actual text found (preserves original case)
                'label': label,
                'source': source_type  # Use the specified source type
            }
            new_annotations.append(annotation)
    
    return new_annotations

def auto_detect_similar_words_for_llm_annotations(text, llm_entities):
    """
    Automatically detect and create annotations for similar words based on LLM annotations.
    
    Args:
        text (str): The source text
        llm_entities (list): List of entities found by LLM
    
    Returns:
        tuple: (auto_detected_entities, summary_stats)
    """
    if not llm_entities:
        return [], {}
    
    auto_detected = []
    stats = {
        'total_llm_entities': len(llm_entities),
        'entities_with_similar_words': 0,
        'total_similar_words_found': 0,
        'by_label': {}
    }
    
    # Process each LLM entity to find similar words
    with st.status("🔍 Auto-detecting similar words...", expanded=False) as status:
        for i, entity in enumerate(llm_entities):
            if not isinstance(entity, dict):
                continue
                
            entity_text = entity.get('text', '').strip()
            entity_label = entity.get('label', '')
            
            if not entity_text or not entity_label:
                continue
            
            # st.write(f"Searching for words similar to: '{entity_text}' ({entity_label})")
            
            # Get all current annotations (LLM + any existing auto-detected)
            all_existing = llm_entities + auto_detected
            
            # Find similar words for this entity
            similar_annotations = create_annotations_for_similar_words(
                text, entity_text, entity_label, all_existing, 'auto_detected'
            )
            
            if similar_annotations:
                auto_detected.extend(similar_annotations)
                stats['entities_with_similar_words'] += 1
                stats['total_similar_words_found'] += len(similar_annotations)
                
                # Update label statistics
                if entity_label not in stats['by_label']:
                    stats['by_label'][entity_label] = {
                        'original_entities': 0,
                        'similar_words_found': 0
                    }
                stats['by_label'][entity_label]['original_entities'] += 1
                stats['by_label'][entity_label]['similar_words_found'] += len(similar_annotations)
                
                # st.write(f"  ✅ Found {len(similar_annotations)} similar words")
                
                # Show the similar words found
                similar_texts = [ann['text'] for ann in similar_annotations]
                # if len(similar_texts) <= 5:
                #     st.write(f"  📝 Similar words: {', '.join(similar_texts)}")
            #     else:
            #         st.write(f"  📝 Similar words: {', '.join(similar_texts[:5])}, ... and {len(similar_texts)-5} more")
            # else:
            #     st.write(f"  ➖ No similar words found")
        
        # status.update(label=f"✅ Auto-detection complete! Found {len(auto_detected)} similar words", state="complete")
    
    # Additional safeguard: Remove any duplicates that might have slipped through
    # This ensures no entity appears in both LLM and auto-detected lists
    filtered_auto_detected = []
    for auto_entity in auto_detected:
        is_duplicate = False
        for llm_entity in llm_entities:
            if (auto_entity['start_char'] == llm_entity['start_char'] and 
                auto_entity['end_char'] == llm_entity['end_char'] and
                auto_entity['label'] == llm_entity['label'] and
                auto_entity['text'].lower() == llm_entity['text'].lower()):
                is_duplicate = True
                break
        
        if not is_duplicate:
            filtered_auto_detected.append(auto_entity)
    
    if len(filtered_auto_detected) != len(auto_detected):
        removed_count = len(auto_detected) - len(filtered_auto_detected)
        st.warning(f"⚠️ Removed {removed_count} duplicate auto-detected entities that matched original LLM entities")
    
    return filtered_auto_detected, stats

def try_fuzzy_fix(text, expected_text, original_start, original_end):
    """Try to fix common annotation errors"""
    # Try removing/adding whitespace
    variations = [
        expected_text.strip(),
        expected_text.lstrip(),
        expected_text.rstrip(),
        ' ' + expected_text,
        expected_text + ' ',
        ' ' + expected_text + ' '
    ]
    
    for variation in variations:
        positions = find_all_occurrences(text, variation)
        if positions:
            # Return the closest match to original position
            closest = min(positions, key=lambda x: abs(x[0] - original_start))
            return closest
    
    # Try case variations
    case_variations = [
        expected_text.lower(),
        expected_text.upper(),
        expected_text.capitalize()
    ]
    
    for variation in case_variations:
        positions = find_all_occurrences(text, variation)
        if positions:
            closest = min(positions, key=lambda x: abs(x[0] - original_start))
            return closest
    
    return None

def correct_annotation_positions(text, entities, verbose=False):
    """
    Comprehensive function to correct annotation positions.
    
    This function addresses the core issue where character positions don't match the actual text.
    It uses multiple strategies to find the correct positions.
    
    Args:
        text (str): The full source text
        entities (list): List of entity dictionaries with potentially incorrect positions
        verbose (bool): Whether to print detailed information about corrections
    
    Returns:
        list: Corrected entities with accurate start_char and end_char
    """
    corrected_entities = []
    correction_stats = {
        'total': len(entities),
        'already_correct': 0,
        'corrected': 0,
        'failed': 0
    }
    
    if verbose:
        st.write(f"🔧 Correcting positions for {len(entities)} annotations...")
        progress_bar = st.progress(0)
        status_text = st.empty()
    
    for i, entity in enumerate(entities):
        if verbose:
            progress_bar.progress((i + 1) / len(entities))
            status_text.text(f"Processing: {entity.get('text', 'N/A')[:50]}...")
        
        expected_text = entity.get('text', '')
        start_char = entity.get('start_char')
        end_char = entity.get('end_char')
        
        if not expected_text or start_char is None or end_char is None:
            if verbose:
                st.warning(f"Skipping entity with missing data: {entity}")
            corrected_entities.append(entity)
            correction_stats['failed'] += 1
            continue
        
        # Strategy 1: Check if current position is already correct
        if (start_char >= 0 and end_char <= len(text) and 
            start_char < end_char and text[start_char:end_char] == expected_text):
            corrected_entities.append(entity)
            correction_stats['already_correct'] += 1
            continue
        
        # Strategy 2: Search for exact text match
        correct_position = find_best_position_match(text, expected_text, start_char)
        
        if correct_position:
            corrected_entity = entity.copy()
            corrected_entity['start_char'] = correct_position[0]
            corrected_entity['end_char'] = correct_position[1]
            corrected_entities.append(corrected_entity)
            correction_stats['corrected'] += 1
            
            if verbose:
                st.info(f"✅ Corrected '{expected_text}': {start_char}-{end_char} → {correct_position[0]}-{correct_position[1]}")
        else:
            # Keep original if we can't find a better position
            corrected_entities.append(entity)
            correction_stats['failed'] += 1
            
            if verbose:
                st.error(f"❌ Could not correct '{expected_text}' at position {start_char}-{end_char}")
    
    if verbose:
        progress_bar.empty()
        status_text.empty()
        
        # Display correction statistics
        st.success(f"✅ Correction complete!")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total", correction_stats['total'])
        col2.metric("Already Correct", correction_stats['already_correct'])
        col3.metric("Corrected", correction_stats['corrected'])
        col4.metric("Failed", correction_stats['failed'])
    
    return corrected_entities

def find_best_position_match(text, expected_text, approximate_start):
    """
    Find the best matching position for expected_text in the source text.
    
    Args:
        text (str): The full source text
        expected_text (str): The text we're looking for
        approximate_start (int): The approximate starting position from annotation
    
    Returns:
        tuple: (start, end) positions if found, None otherwise
    """
    # Strategy 1: Exact match near the approximate position
    window_size = 100  # Search within 100 characters of the original position
    search_start = max(0, approximate_start - window_size)
    search_end = min(len(text), approximate_start + len(expected_text) + window_size)
    
    search_region = text[search_start:search_end]
    found_pos = search_region.find(expected_text)
    
    if found_pos != -1:
        actual_start = search_start + found_pos
        actual_end = actual_start + len(expected_text)
        return (actual_start, actual_end)
    
    # Strategy 2: Find all occurrences and pick the closest to approximate_start
    all_positions = find_all_occurrences(text, expected_text)
    if all_positions:
        closest = min(all_positions, key=lambda pos: abs(pos[0] - approximate_start))
        return closest
    
    # Strategy 3: Try fuzzy matching (handle whitespace issues, etc.)
    fuzzy_match = try_advanced_fuzzy_match(text, expected_text, approximate_start)
    if fuzzy_match:
        return fuzzy_match
    
    return None

def debug_annotation_positions(text, entities, verbose=True):
    """
    Debug function to analyze annotation position issues in detail.
    This helps identify exactly what's wrong with positions.
    
    Args:
        text (str): The full source text
        entities (list): List of entity dictionaries
        verbose (bool): Whether to print detailed debug information
    
    Returns:
        dict: Detailed debugging information
    """
    debug_results = {
        'total_entities': len(entities),
        'issues_found': [],
        'detailed_analysis': []
    }
    
    for i, entity in enumerate(entities):
        analysis = {
            'entity_index': i,
            'entity': entity,
            'issues': []
        }
        
        expected_text = entity.get('text', '')
        start_char = entity.get('start_char')
        end_char = entity.get('end_char')
        
        if verbose:
            print(f"\n--- Debugging Entity {i+1}: '{expected_text[:50]}...' ---")
        
        # Check 1: Missing fields
        if not expected_text or start_char is None or end_char is None:
            analysis['issues'].append('missing_fields')
            if verbose:
                print("❌ Missing required fields")
            continue
        
        # Check 2: Invalid range
        if start_char < 0 or end_char > len(text) or start_char >= end_char:
            analysis['issues'].append('invalid_range')
            if verbose:
                print(f"❌ Invalid range: [{start_char}:{end_char}] for text length {len(text)}")
            continue
        
        # Check 3: Extract text at given position
        try:
            actual_text = text[start_char:end_char]
            analysis['actual_text'] = actual_text
            
            if verbose:
                print(f"Expected: '{expected_text}'")
                print(f"Actual:   '{actual_text}'")
                print(f"Position: [{start_char}:{end_char}]")
            
            # Check 4: Exact match
            if actual_text == expected_text:
                if verbose:
                    print("✅ Exact match")
                continue
            else:
                analysis['issues'].append('text_mismatch')
                
                # Check 5: Character-by-character comparison
                if verbose:
                    print("❌ Text mismatch - Character analysis:")
                    min_len = min(len(expected_text), len(actual_text))
                    for j in range(min_len):
                        if expected_text[j] != actual_text[j]:
                            print(f"   Diff at pos {j}: expected '{repr(expected_text[j])}' got '{repr(actual_text[j])}'")
                            break
                    
                    if len(expected_text) != len(actual_text):
                        print(f"   Length diff: expected {len(expected_text)}, got {len(actual_text)}")
                
                # Check 6: Find where text actually appears
                all_occurrences = find_all_occurrences(text, expected_text)
                analysis['actual_occurrences'] = all_occurrences
                
                if verbose:
                    if all_occurrences:
                        print(f"   Text found at positions: {all_occurrences}")
                        closest = min(all_occurrences, key=lambda x: abs(x[0] - start_char))
                        offset = closest[0] - start_char
                        print(f"   Closest correct position: {closest} (offset: {offset})")
                    else:
                        print("   ❌ Text not found anywhere in document")
                
                # Check 7: Try fuzzy matching
                fuzzy_result = try_advanced_fuzzy_match(text, expected_text, start_char)
                if fuzzy_result and verbose:
                    print(f"   Fuzzy match found at: {fuzzy_result}")
        
        except Exception as e:
            analysis['issues'].append('extraction_error')
            if verbose:
                print(f"❌ Error extracting text: {e}")
        
        debug_results['detailed_analysis'].append(analysis)
        if analysis['issues']:
            debug_results['issues_found'].extend(analysis['issues'])
    
    # Summary
    if verbose:
        print(f"\n{'='*60}")
        print(f"DEBUG SUMMARY:")
        print(f"Total entities: {debug_results['total_entities']}")
        print(f"Issues found: {len(debug_results['issues_found'])}")
        issue_counts = {}
        for issue in debug_results['issues_found']:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
        for issue, count in issue_counts.items():
            print(f"  {issue}: {count}")
    
    return debug_results

def try_advanced_fuzzy_match(text, expected_text, approximate_start):
    """
    Advanced fuzzy matching to handle common annotation issues.
    Enhanced to detect LLM hallucinations and phantom annotations.
    """
    # Check if this might be a phantom annotation (words exist but not as contiguous text)
    words = expected_text.split()
    if len(words) > 1:
        # Check if all words exist in text but not as a contiguous phrase
        all_words_exist = all(word in text for word in words)
        contiguous_exists = expected_text in text
        
        if all_words_exist and not contiguous_exists:
            # This is likely a phantom annotation - LLM combined separate concepts
            return None
    
    # Remove extra whitespace and try again
    normalized_expected = ' '.join(expected_text.split())
    
    # Try variations with different whitespace handling
    variations = [
        expected_text.strip(),
        normalized_expected,
        expected_text.replace('\n', ' '),
        expected_text.replace('\t', ' '),
    ]
    
    window_size = 200
    search_start = max(0, approximate_start - window_size)
    search_end = min(len(text), approximate_start + len(expected_text) + window_size)
    search_region = text[search_start:search_end]
    
    for variation in variations:
        if variation and variation != expected_text:
            found_pos = search_region.find(variation)
            if found_pos != -1:
                actual_start = search_start + found_pos
                actual_end = actual_start + len(variation)
                # Update the expected text to match what we actually found
                return (actual_start, actual_end)
    
    return None

def detect_phantom_annotations(text, entities):
    """
    Detect phantom annotations - cases where LLM created compound phrases 
    that don't exist as contiguous text.
    
    Args:
        text (str): Source text
        entities (list): List of entity annotations
    
    Returns:
        dict: Analysis of phantom annotations
    """
    phantom_analysis = {
        'total_entities': len(entities),
        'phantom_annotations': [],
        'valid_annotations': [],
        'suspicious_patterns': []
    }
    
    for i, entity in enumerate(entities):
        expected_text = entity.get('text', '').strip()
        if not expected_text:
            continue
        
        # Check if the exact text exists in source
        if expected_text in text:
            phantom_analysis['valid_annotations'].append({
                'index': i,
                'entity': entity,
                'status': 'valid'
            })
            continue
        
        # Analyze if this might be a phantom annotation
        words = expected_text.split()
        
        analysis = {
            'index': i,
            'entity': entity,
            'expected_text': expected_text,
            'issues': []
        }
        
        # Check 1: All words exist but not contiguously
        if len(words) > 1:
            words_in_text = [word for word in words if word in text]
            if len(words_in_text) == len(words):
                analysis['issues'].append('words_exist_separately')
                analysis['status'] = 'phantom_combination'
        
        # Check 2: Very long compound phrases (likely hallucinated)
        if len(words) > 6:
            analysis['issues'].append('overly_long_phrase')
            analysis['status'] = 'likely_hallucination'
        
        # Check 3: Unusual combinations of technical terms
        if any(combo in expected_text.lower() for combo in [
            'drug delivery system', 'magnetic incorporated', 'phase change',
            'release system', 'force response'
        ]):
            # Check if these appear separately in text
            parts_exist_separately = False
            for combo in ['drug delivery', 'magnetic', 'phase change', 'release system']:
                if combo in expected_text.lower() and combo in text.lower():
                    parts_exist_separately = True
                    break
            
            if parts_exist_separately:
                analysis['issues'].append('technical_term_combination')
                analysis['status'] = 'phantom_technical_phrase'
        
        # Determine final status
        if analysis.get('issues'):
            phantom_analysis['phantom_annotations'].append(analysis)
            
            # Add to suspicious patterns
            for issue in analysis['issues']:
                if issue not in [p['pattern'] for p in phantom_analysis['suspicious_patterns']]:
                    phantom_analysis['suspicious_patterns'].append({
                        'pattern': issue,
                        'count': 1,
                        'examples': [expected_text]
                    })
                else:
                    # Update existing pattern
                    for pattern in phantom_analysis['suspicious_patterns']:
                        if pattern['pattern'] == issue:
                            pattern['count'] += 1
                            if expected_text not in pattern['examples']:
                                pattern['examples'].append(expected_text)
        else:
            # Might be a position error rather than phantom
            phantom_analysis['valid_annotations'].append({
                'index': i,
                'entity': entity,
                'status': 'position_error'
            })
    
    return phantom_analysis

def fix_annotation_positions_streamlit(text, entities, strategy='closest'):
    """
    Automatically fix annotation positions by searching for the text.
    Modified for Streamlit integration.
    
    Args:
        text (str): The source text
        entities (list): List of entity dictionaries
        strategy (str): Strategy for handling multiple matches ('closest', 'first')
    
    Returns:
        tuple: (fixed_entities, stats)
    """
    
    fixed_entities = []
    stats = {
        'total': len(entities),
        'already_correct': 0,
        'fixed': 0,
        'unfixable': 0,
        'multiple_matches': 0
    }
    
    st.write(f"🔧 Attempting to fix {len(entities)} annotations...")
    
    # Create progress bar for fixing
    fix_progress = st.progress(0)
    fix_status = st.empty()
    
    for i, entity in enumerate(entities):
        # Update progress
        fix_progress.progress((i + 1) / len(entities))
        fix_status.text(f"Processing entity {i+1}/{len(entities)}: '{entity.get('text', 'N/A')}'")
        
        expected_text = entity.get('text')
        start_char = entity.get('start_char')
        end_char = entity.get('end_char')
        
        # Skip entities with missing required fields
        if None in [expected_text, start_char, end_char]:
            fixed_entities.append(entity)
            stats['unfixable'] += 1
            continue
        
        # Check if current position is correct
        try:
            if start_char >= 0 and end_char <= len(text) and text[start_char:end_char] == expected_text:
                fixed_entities.append(entity)
                stats['already_correct'] += 1
                continue
        except:
            pass
        
        # Try to find the text in the document
        found_positions = find_all_occurrences(text, expected_text)
        
        if not found_positions:
            # Try fuzzy matching for common issues
            fixed_pos = try_fuzzy_fix(text, expected_text, start_char, end_char)
            if fixed_pos:
                entity_copy = entity.copy()
                entity_copy['start_char'] = fixed_pos[0]
                entity_copy['end_char'] = fixed_pos[1]
                fixed_entities.append(entity_copy)
                stats['fixed'] += 1
            else:
                # Text not found, keep original but mark as unfixable
                fixed_entities.append(entity)
                stats['unfixable'] += 1
        elif len(found_positions) == 1:
            # Only one match found, use it
            new_start, new_end = found_positions[0]
            entity_copy = entity.copy()
            entity_copy['start_char'] = new_start
            entity_copy['end_char'] = new_end
            fixed_entities.append(entity_copy)
            stats['fixed'] += 1
        else:
            # Multiple matches found
            stats['multiple_matches'] += 1
            
            if strategy == 'closest':
                # Choose the closest to original position
                closest_pos = min(found_positions, key=lambda x: abs(x[0] - start_char))
                entity_copy = entity.copy()
                entity_copy['start_char'] = closest_pos[0]
                entity_copy['end_char'] = closest_pos[1]
                fixed_entities.append(entity_copy)
                stats['fixed'] += 1
            elif strategy == 'first':
                # Use the first occurrence
                first_pos = found_positions[0]
                entity_copy = entity.copy()
                entity_copy['start_char'] = first_pos[0]
                entity_copy['end_char'] = first_pos[1]
                fixed_entities.append(entity_copy)
                stats['fixed'] += 1
    
    # Clear progress indicators
    fix_progress.empty()
    fix_status.empty()
    
    return fixed_entities, stats


def evaluate_annotations_with_llm(entities, tag_df, client, temperature=0.1, max_tokens=2000):
    """
    Use LLM to evaluate whether annotations match their label definitions.
    FIXED VERSION with proper evaluation prompt and entity tracking.
    """
    if not entities:
        st.warning("No entities to evaluate")
        return []
        
    # Split entities into batches if too many (to avoid token limits)
    batch_size = 20  # REDUCED from 50 to ensure better processing
    all_evaluations = []
    
    entity_batches = [entities[i:i + batch_size] for i in range(0, len(entities), batch_size)]
    
    st.write(f"📊 Processing {len(entities)} entities in {len(entity_batches)} batches...")
    
    for batch_idx, entity_batch in enumerate(entity_batches):
        st.write(f"🤖 Evaluating batch {batch_idx + 1}/{len(entity_batches)} ({len(entity_batch)} entities)...")
        
        try:
            # Build evaluation prompt
            prompt = build_evaluation_prompt(tag_df, entity_batch)
            
            # Call LLM for evaluation
            response = client.generate(prompt, temperature=temperature, max_tokens=max_tokens)
            
            # Parse evaluation results
            batch_evaluations = parse_evaluation_response(response, batch_idx + 1)
            
            # Add batch offset to entity indices
            for eval_result in batch_evaluations:
                if 'entity_index' in eval_result:
                    eval_result['entity_index'] = batch_idx * batch_size + eval_result['entity_index']
            
            all_evaluations.extend(batch_evaluations)
            st.success(f"✅ Batch {batch_idx + 1} completed! Processed {len(batch_evaluations)} evaluations.")
                
        except Exception as e:
            st.error(f"❌ Batch {batch_idx + 1} failed: {e}")
            
            # Create default evaluations for failed batch
            for i, entity in enumerate(entity_batch):
                global_entity_idx = batch_idx * batch_size + i
                default_eval = {
                    'entity_index': global_entity_idx,
                    'current_text': entity.get('text', ''),
                    'current_label': entity.get('label', ''),
                    'is_correct': True,
                    'recommendation': 'keep',
                    'reasoning': f'Batch evaluation failed: {str(e)}',
                    'suggested_label': entity.get('label', ''),
                    'confidence': 0.5
                }
                all_evaluations.append(default_eval)
            
            st.warning(f"Created {len(entity_batch)} default evaluations for failed batch")
    
    # FINAL VERIFICATION: Ensure we have evaluation for every entity
    if len(all_evaluations) != len(entities):
        st.error(f"❌ CRITICAL: Expected {len(entities)} evaluations, got {len(all_evaluations)}")
        
        # Find missing entities and create default evaluations
        evaluated_indices = set(eval_result.get('entity_index', -1) for eval_result in all_evaluations)
        missing_indices = set(range(len(entities))) - evaluated_indices
        
        if missing_indices:
            st.warning(f"Creating default evaluations for {len(missing_indices)} missing entities: {sorted(missing_indices)}")
            
            for entity_idx in missing_indices:
                if entity_idx < len(entities):
                    entity = entities[entity_idx]
                    default_eval = {
                        'entity_index': entity_idx,
                        'current_text': entity.get('text', ''),
                        'current_label': entity.get('label', ''),
                        'is_correct': False,
                        'recommendation': 'manual_review',
                        'reasoning': 'Missing from LLM evaluation - requires manual review',
                        'suggested_label': entity.get('label', ''),
                        'confidence': 0.0
                    }
                    all_evaluations.append(default_eval)
        
        # Sort evaluations by entity_index to maintain order
        all_evaluations.sort(key=lambda x: x.get('entity_index', 0))
    
    st.success(f"🎉 Evaluation completed! Generated {len(all_evaluations)} evaluations for {len(entities)} entities.")
    return all_evaluations


def parse_evaluation_response(response_text: str, batch_idx: int = None) -> list:
    """
    Parse the evaluation JSON response from LLM.
    ENHANCED VERSION with better error handling and recovery.
    """
    if not response_text or response_text.strip() == "":
        st.warning(f"⚠️ Empty evaluation response from LLM for batch {batch_idx if batch_idx is not None else 'unknown'}")
        return []
    
    response_text = response_text.strip()
    
    try:
        # Method 1: Try direct JSON parsing first
        evaluations = json.loads(response_text)
        if isinstance(evaluations, list):
            valid_evaluations = validate_evaluation_structure(evaluations)
            if valid_evaluations:
                return valid_evaluations
        else:
            st.warning(f"Evaluation response is not a list: {type(evaluations)}")
            
    except json.JSONDecodeError:
        pass
    
    # Method 2: Try to extract JSON from markdown code blocks
    try:
        import re
        
        # Look for JSON content between ```json and ``` or ``` and ```
        json_patterns = [
            r'```json\s*(\[.*?\])\s*```',
            r'```\s*(\[.*?\])\s*```',
            r'(\[(?:[^[\]]*|\[[^[\]]*\])*\])'  # Find any JSON array
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, response_text, re.DOTALL)
            for match in matches:
                try:
                    evaluations = json.loads(match.strip())
                    if isinstance(evaluations, list):
                        valid_evaluations = validate_evaluation_structure(evaluations)
                        if valid_evaluations:
                            st.info(f"Recovered {len(valid_evaluations)} evaluations using pattern matching")
                            return valid_evaluations
                except json.JSONDecodeError:
                    continue
                    
    except Exception as e:
        st.warning(f"Pattern matching failed: {e}")
    
    # Method 3: Try to find and parse individual JSON objects
    try:
        import re
        json_objects = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text)
        entities = []
        for obj_str in json_objects:
            try:
                obj = json.loads(obj_str)
                if is_valid_evaluation_object(obj):
                    entities.append(obj)
            except:
                continue
        
        if entities:
            st.info(f"Recovered {len(entities)} evaluations from individual JSON objects")
            return entities
                
    except Exception:
        pass
    
    # Final fallback: Log error and return empty
    st.error(f"❌ Failed to parse evaluation response for batch {batch_idx if batch_idx is not None else 'unknown'}")
    
    # Show debugging info
    with st.expander(f"🔍 Debug Response Content (Batch {batch_idx})", expanded=False):
        st.text("Full raw response:")
        st.code(response_text, language="text")
        st.text(f"Response length: {len(response_text)} characters")
        st.text(f"First 200 chars: {repr(response_text[:200])}")
    
    return []


def validate_evaluation_structure(evaluations: list) -> list:
    """
    Validate and clean evaluation results structure.
    """
    valid_evaluations = []
    required_fields = ["entity_index", "current_text", "current_label", "is_correct", "recommendation"]
    
    for i, eval_result in enumerate(evaluations):
        if not isinstance(eval_result, dict):
            st.warning(f"Evaluation {i} is not a dictionary: {type(eval_result)}")
            continue
            
        # Check required fields
        missing_fields = [field for field in required_fields if field not in eval_result]
        if missing_fields:
            st.warning(f"Evaluation {i} missing fields: {missing_fields}")
            
            # Try to fill missing fields with defaults
            if 'entity_index' not in eval_result:
                eval_result['entity_index'] = i
            if 'current_text' not in eval_result:
                eval_result['current_text'] = 'Unknown'
            if 'current_label' not in eval_result:
                eval_result['current_label'] = 'Unknown'
            if 'is_correct' not in eval_result:
                eval_result['is_correct'] = False
            if 'recommendation' not in eval_result:
                eval_result['recommendation'] = 'manual_review'
        
        # Ensure proper data types
        try:
            eval_result['entity_index'] = int(eval_result.get('entity_index', i))
            eval_result['is_correct'] = bool(eval_result.get('is_correct', False))
        except (ValueError, TypeError):
            st.warning(f"Data type issues in evaluation {i}, using defaults")
            eval_result['entity_index'] = i
            eval_result['is_correct'] = False
        
        valid_evaluations.append(eval_result)
    
    return valid_evaluations


def is_valid_evaluation_object(obj: dict) -> bool:
    """
    Check if an object has the minimum required fields for an evaluation.
    """
    required_fields = ["entity_index", "current_text", "current_label", "is_correct", "recommendation"]
    return all(field in obj for field in required_fields)

def identify_duplicate_llm_annotations(llm_entities, auto_detected_entities):
    """
    Identify which LLM annotations have auto-detected duplicates and should be removed.
    
    Args:
        llm_entities (list): List of LLM annotation entities
        auto_detected_entities (list): List of auto-detected entities
    
    Returns:
        tuple: (entities_to_delete, entities_to_keep, stats)
    """
    entities_to_delete = []
    entities_to_keep = []
    
    stats = {
        'total_llm': len(llm_entities),
        'has_duplicates': 0,
        'unique_kept': 0
    }
    
    for llm_entity in llm_entities:
        llm_text = llm_entity.get('text', '').strip().lower()
        llm_label = llm_entity.get('label', '')
        
        # Check if this LLM entity has an auto-detected counterpart
        has_auto_detected = False
        for auto_entity in auto_detected_entities:
            auto_text = auto_entity.get('text', '').strip().lower()
            auto_label = auto_entity.get('label', '')
            
            # Match by text and label (case-insensitive text comparison)
            if llm_text == auto_text and llm_label == auto_label:
                has_auto_detected = True
                break
        
        if has_auto_detected:
            entities_to_delete.append(llm_entity)
            stats['has_duplicates'] += 1
        else:
            entities_to_keep.append(llm_entity)
            stats['unique_kept'] += 1
    
    return entities_to_delete, entities_to_keep, stats

def clear_all_previous_data():
    """Clear all previous annotation and evaluation data when starting new annotation."""
    # Clear annotation data
    st.session_state.annotated_entities = []
    st.session_state.auto_detected_entities = []  # Clear auto-detected entities
    st.session_state.annotation_complete = False
    if 'editable_entities_df' in st.session_state:
        del st.session_state.editable_entities_df

    # Clear validation and fix results
    if 'validation_results' in st.session_state:
        del st.session_state.validation_results
    if 'fix_results' in st.session_state:
        del st.session_state.fix_results
    
    # Clear evaluation data (NEW)
    st.session_state.evaluation_results = []
    st.session_state.evaluation_complete = False
    st.session_state.evaluation_summary = {}

def apply_evaluation_recommendations(entities, evaluations, selected_indices):
    """
    Apply selected evaluation recommendations to entities.
    Returns updated entities and list of changes made.
    """
    if not entities:
        return [], ["No entities to process"]
   
    if not evaluations:
        return entities, ["No evaluations available"]
   
    updated_entities = entities.copy()
    changes_made = []
    entities_to_delete = []  # Use list to maintain order
   
    # Process all recommendations first (for label changes and mark deletions)
    for eval_idx in selected_indices:
        if eval_idx < len(evaluations):
            evaluation = evaluations[eval_idx]
            entity_idx = evaluation.get('entity_index')
           
            if entity_idx is None or entity_idx >= len(updated_entities):
                changes_made.append(f"Warning: Invalid entity index {entity_idx}")
                continue
               
            recommendation = evaluation.get('recommendation', '')
            current_text = updated_entities[entity_idx].get('text', 'Unknown')
           
            if recommendation == 'change_label' and evaluation.get('suggested_label'):
                # Change the label
                old_label = updated_entities[entity_idx].get('label', 'Unknown')
                new_label = evaluation['suggested_label']
                updated_entities[entity_idx]['label'] = new_label
                changes_made.append(f"Changed '{current_text}' from '{old_label}' to '{new_label}'")
               
            elif recommendation == 'delete':
                # Mark for deletion (will delete later)
                entities_to_delete.append(entity_idx)
                changes_made.append(f"Marked '{current_text}' for deletion")
   
    # Delete entities (in reverse order to maintain indices)
    if entities_to_delete:
        for entity_idx in sorted(set(entities_to_delete), reverse=True):
            if entity_idx < len(updated_entities):
                deleted_text = updated_entities[entity_idx].get('text', 'Unknown')
                deleted_label = updated_entities[entity_idx].get('label', 'Unknown')
                updated_entities.pop(entity_idx)
                changes_made.append(f"Deleted entity: '{deleted_text}' (label: '{deleted_label}')")
   
    return updated_entities, changes_made


def parse_llm_response(response_text: str, chunk_index: int = None):
    """
    Parse the JSON returned by LLM with improved error handling.
    Returns list of entities preserving nested structure when annotation_mode is nested.
    Includes validation to filter out overly long entities.
    """
    # Define maximum entity length (in characters) to prevent over-annotation
    MAX_ENTITY_LENGTH = 100  # Reasonable limit for scientific entities
    MAX_WORD_COUNT = 10      # Maximum number of words in an entity
    
    # Log the raw response for debugging
    if chunk_index is not None:
        st.write(f"**Debug - Chunk {chunk_index} Raw Response:**")
        with st.expander(f"Raw Response Content (Chunk {chunk_index})", expanded=False):
            st.text(repr(response_text))  # Use repr to show exact content including whitespace
    
    # Check if response is empty or None
    if not response_text or response_text.strip() == "":
        st.warning(f"⚠️ Empty response from LLM for chunk {chunk_index if chunk_index else 'unknown'}")
        return []
    
    # Clean the response text
    response_text = response_text.strip()
    
    def validate_entity_length(entity_text, entity_type="main"):
        """Validate entity length and word count"""
        if not entity_text:
            return False, "Empty text"
        
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
        
        return True, "Valid"
    
    try:
        # Method 1: Try direct JSON parsing first
        entities = json.loads(response_text)
        if isinstance(entities, list):
            # Apply entity length filtering to prevent over-annotation
            filtered_entities, filtered_count = filter_entities_by_length(entities, chunk_index)
            
            if filtered_count > 0:
                st.info(f"Filtered out {filtered_count} overly long entities that appeared to be sentences or phrases")
            
            # Check annotation mode to determine processing strategy
            is_nested_mode = st.session_state.get('annotation_mode', 'Nested (Hierarchical)') == "Nested (Hierarchical)"
            
            if is_nested_mode:
                # Preserve nested structure for nested mode AND create separate entities for nested items
                valid_entities = []
                for ent in filtered_entities:
                    if isinstance(ent, dict) and all(key in ent for key in ["start_char", "end_char", "text", "label"]):
                        # Add the main entity with preserved nested structure
                        main_entity = {
                            'start_char': ent['start_char'],
                            'end_char': ent['end_char'],
                            'text': ent['text'],
                            'label': ent['label'],
                            'source': 'llm'
                        }
                        
                        # Preserve nested entities if they exist
                        if 'nested_entities' in ent and isinstance(ent['nested_entities'], list):
                            valid_nested = []
                            for nested_ent in ent['nested_entities']:
                                if isinstance(nested_ent, dict) and all(key in nested_ent for key in ["start_char", "end_char", "text", "label"]):
                                    # Validate that nested entity is within parent boundaries
                                    if (nested_ent['start_char'] >= main_entity['start_char'] and 
                                        nested_ent['end_char'] <= main_entity['end_char'] and
                                        nested_ent['start_char'] < nested_ent['end_char']):
                                        
                                        # Add nested entity info to parent
                                        valid_nested.append({
                                            'start_char': nested_ent['start_char'],
                                            'end_char': nested_ent['end_char'],
                                            'text': nested_ent['text'],
                                            'label': nested_ent['label']
                                        })
                                        
                                        # ALSO create a separate entity for the nested item
                                        nested_entity = {
                                            'start_char': nested_ent['start_char'],
                                            'end_char': nested_ent['end_char'],
                                            'text': nested_ent['text'],
                                            'label': nested_ent['label'],
                                            'source': 'llm',
                                            'parent_entity': main_entity['text'],
                                            'is_nested': True
                                        }
                                        valid_entities.append(nested_entity)
                                #     else:
                                #         st.warning(f"Skipped nested entity outside parent boundaries: {nested_ent['text']} not within {main_entity['text']}")
                                # else:
                                #     st.warning(f"Invalid nested entity structure: {nested_ent}")
                            
                            if valid_nested:
                                main_entity['nested_entities'] = valid_nested
                            else:
                                main_entity['nested_entities'] = []
                        else:
                            main_entity['nested_entities'] = []
                        
                        valid_entities.append(main_entity)
                    else:
                        st.warning(f"Invalid entity structure: {ent}")
                return valid_entities
            else:
                # Flatten entities for flat mode (original behavior)
                valid_entities = []
                for ent in filtered_entities:
                    if isinstance(ent, dict) and all(key in ent for key in ["start_char", "end_char", "text", "label"]):
                        # Add the main entity
                        main_entity = {
                            'start_char': ent['start_char'],
                            'end_char': ent['end_char'],
                            'text': ent['text'],
                            'label': ent['label'],
                            'source': 'llm'
                        }
                        valid_entities.append(main_entity)
                        
                        # Process nested entities as separate flat entities
                        if 'nested_entities' in ent and isinstance(ent['nested_entities'], list):
                            for nested_ent in ent['nested_entities']:
                                if isinstance(nested_ent, dict) and all(key in nested_ent for key in ["start_char", "end_char", "text", "label"]):
                                    # Validate that nested entity is within parent boundaries
                                    if (nested_ent['start_char'] >= main_entity['start_char'] and 
                                        nested_ent['end_char'] <= main_entity['end_char'] and
                                        nested_ent['start_char'] < nested_ent['end_char']):
                                        
                                        nested_entity = {
                                            'start_char': nested_ent['start_char'],
                                            'end_char': nested_ent['end_char'],
                                            'text': nested_ent['text'],
                                            'label': nested_ent['label'],
                                            'source': 'llm',
                                            'parent_entity': main_entity['text']  # Reference to parent
                                        }
                                        valid_entities.append(nested_entity)
                                #     else:
                                #         st.warning(f"Skipped nested entity outside parent boundaries: {nested_ent['text']} not within {main_entity['text']}")
                                # else:
                                #     st.warning(f"Invalid nested entity structure: {nested_ent}")
                    # else:
                    #     st.warning(f"Invalid entity structure: {ent}")
                return valid_entities
        else:
            st.warning(f"Response is not a list: {type(entities)}")
            return []
            
    except json.JSONDecodeError:
        # Method 2: Try to extract JSON array from text
        try:
            first_bracket = response_text.find('[')
            last_bracket = response_text.rfind(']')
            
            if first_bracket == -1 or last_bracket == -1 or first_bracket >= last_bracket:
                raise ValueError("No valid JSON array found")
                
            json_str = response_text[first_bracket:last_bracket+1]
            entities = json.loads(json_str)
            
            # Apply entity length filtering to prevent over-annotation
            filtered_entities, filtered_count = filter_entities_by_length(entities, chunk_index)
            
            if filtered_count > 0:
                st.info(f"Filtered out {filtered_count} overly long entities that appeared to be sentences or phrases")
            
            # Check annotation mode for processing strategy
            is_nested_mode = st.session_state.get('annotation_mode', 'Nested (Hierarchical)') == "Nested (Hierarchical)"
            
            if is_nested_mode:
                # Preserve nested structure for nested mode AND create separate entities for nested items
                valid_entities = []
                for ent in filtered_entities:
                    if isinstance(ent, dict) and all(key in ent for key in ["start_char", "end_char", "text", "label"]):
                        # Add the main entity with preserved nested structure
                        main_entity = {
                            'start_char': ent['start_char'],
                            'end_char': ent['end_char'],
                            'text': ent['text'],
                            'label': ent['label'],
                            'source': 'llm'
                        }
                        
                        # Preserve nested entities if they exist
                        if 'nested_entities' in ent and isinstance(ent['nested_entities'], list):
                            valid_nested = []
                            for nested_ent in ent['nested_entities']:
                                if isinstance(nested_ent, dict) and all(key in nested_ent for key in ["start_char", "end_char", "text", "label"]):
                                    # Validate that nested entity is within parent boundaries
                                    if (nested_ent['start_char'] >= main_entity['start_char'] and 
                                        nested_ent['end_char'] <= main_entity['end_char'] and
                                        nested_ent['start_char'] < nested_ent['end_char']):
                                        
                                        # Add nested entity info to parent
                                        valid_nested.append({
                                            'start_char': nested_ent['start_char'],
                                            'end_char': nested_ent['end_char'],
                                            'text': nested_ent['text'],
                                            'label': nested_ent['label']
                                        })
                                        
                                        # ALSO create a separate entity for the nested item
                                        nested_entity = {
                                            'start_char': nested_ent['start_char'],
                                            'end_char': nested_ent['end_char'],
                                            'text': nested_ent['text'],
                                            'label': nested_ent['label'],
                                            'source': 'llm',
                                            'parent_entity': main_entity['text'],
                                            'is_nested': True
                                        }
                                        valid_entities.append(nested_entity)
                                #     else:
                                #         st.warning(f"Skipped nested entity outside parent boundaries: {nested_ent['text']} not within {main_entity['text']}")
                                # else:
                                #     st.warning(f"Invalid nested entity structure: {nested_ent}")
                            
                            if valid_nested:
                                main_entity['nested_entities'] = valid_nested
                            else:
                                main_entity['nested_entities'] = []
                        else:
                            main_entity['nested_entities'] = []
                        
                        valid_entities.append(main_entity)
                    else:
                        st.warning(f"Invalid entity structure: {ent}")
                return valid_entities
            else:
                # Flatten entities for flat mode
                valid_entities = []
                for ent in filtered_entities:
                    if isinstance(ent, dict) and all(key in ent for key in ["start_char", "end_char", "text", "label"]):
                        # Add the main entity
                        main_entity = {
                            'start_char': ent['start_char'],
                            'end_char': ent['end_char'],
                            'text': ent['text'],
                            'label': ent['label'],
                            'source': 'llm'
                        }
                        valid_entities.append(main_entity)
                        
                        # Process nested entities as separate flat entities
                        if 'nested_entities' in ent and isinstance(ent['nested_entities'], list):
                            for nested_ent in ent['nested_entities']:
                                if isinstance(nested_ent, dict) and all(key in nested_ent for key in ["start_char", "end_char", "text", "label"]):
                                    # Validate that nested entity is within parent boundaries
                                    if (nested_ent['start_char'] >= main_entity['start_char'] and 
                                        nested_ent['end_char'] <= main_entity['end_char'] and
                                        nested_ent['start_char'] < nested_ent['end_char']):
                                        
                                        nested_entity = {
                                            'start_char': nested_ent['start_char'],
                                            'end_char': nested_ent['end_char'],
                                            'text': nested_ent['text'],
                                            'label': nested_ent['label'],
                                            'source': 'llm',
                                            'parent_entity': main_entity['text']  # Reference to parent
                                        }
                                        valid_entities.append(nested_entity)
                                    else:
                                        st.warning(f"Skipped nested entity outside parent boundaries: {nested_ent['text']} not within {main_entity['text']}")
                                else:
                                    st.warning(f"Invalid nested entity structure: {nested_ent}")
                    else:
                        st.warning(f"Invalid entity structure: {ent}")
                
                if len(valid_entities) != len(entities):
                    st.warning(f"Some entities were invalid and filtered out")
                
                return valid_entities
            
        except (json.JSONDecodeError, ValueError) as e:
            # Method 3: Try to find and parse multiple JSON objects
            try:
                # Look for individual JSON objects
                import re
                json_objects = re.findall(r'\{[^{}]*\}', response_text)
                entities = []
                for obj_str in json_objects:
                    try:
                        obj = json.loads(obj_str)
                        if all(key in obj for key in ["start_char", "end_char", "text", "label"]):
                            entities.append(obj)
                    except:
                        continue
                
                if entities:
                    st.info(f"Recovered {len(entities)} entities from malformed response")
                    return entities
                    
            except Exception:
                pass
            
            # Final fallback: Log error and return empty
            st.error(f"Failed to parse LLM output JSON for chunk {chunk_index if chunk_index else 'unknown'}: {e}")
            st.error(f"Raw response preview: {response_text[:200]}...")
            return []



def run_annotation_pipeline(text, tag_df, client, temperature, max_tokens, chunk_size):
    """
    1. Chunk the text with overlap
    2. For each chunk, generate prompt and call LLM
    3. Parse and adjust entities with offset
    4. Remove duplicates from overlapping regions
    5. Aggregate and return full list of entities
    """
    chunks_with_overlap = chunk_text(text, chunk_size)
    all_entities = []
    processed_chunks = []
    
    # Create a container for progress updates
    progress_container = st.container()
    
    start_time = time.time()
    
    # st.info(f"🔗 Processing {len(chunks_with_overlap)} overlapping chunks to improve entity detection at boundaries...")
    
    for i, (chunk_text_content, start_offset, end_offset) in enumerate(chunks_with_overlap):
        with progress_container:
            # Clear previous progress display
            progress_container.empty()
            
            # Show current progress with overlap info
            display_chunk_progress_with_overlap(i + 1, len(chunks_with_overlap), chunk_text_content, start_offset, end_offset, start_time)
            
            # Process the chunk
            with st.spinner(f"🤖 Calling {st.session_state.model_provider} API..."):
                # Use appropriate prompt based on annotation mode
                if st.session_state.annotation_mode == "Nested (Hierarchical)":
                    prompt = build_nested_annotation_prompt(tag_df, chunk_text_content)
                else:
                    prompt = build_annotation_prompt(tag_df, chunk_text_content)
                    
                response = client.generate(prompt, temperature=temperature, max_tokens=max_tokens)
                entities = parse_llm_response(response, i + 1)  # Pass chunk index for debugging
                
                # Adjust entities with the actual start offset
                entities = aggregate_entities(entities, start_offset)
                
                # Store chunk information for overlap detection
                processed_chunks.append({
                    'chunk_index': i,
                    'start_offset': start_offset,
                    'end_offset': end_offset,
                    'entities': entities,
                    'chunk_text': chunk_text_content
                })
                
                all_entities.extend(entities)
                
                # Show chunk results with overlap info
                overlap_msg = ""
                if i > 0:
                    prev_chunk = processed_chunks[i-1]
                    if start_offset < prev_chunk['end_offset']:
                        overlap_chars = prev_chunk['end_offset'] - start_offset
                        overlap_msg = f" | 🔗 {overlap_chars} chars overlap with previous chunk"
                
                # Show chunk results with nested entity info
                if st.session_state.annotation_mode == "Nested (Hierarchical)":
                    # Count entities with nesting
                    entities_with_nesting = len([e for e in entities if e.get('nested_entities')])
                    total_nested_children = sum(len(e.get('nested_entities', [])) for e in entities)
                    
                    if entities_with_nesting > 0:
                        st.success(f"✅ Chunk {i+1} completed! Found {len(entities)} entities ({entities_with_nesting} with nested children, {total_nested_children} total nested entities){overlap_msg}")
                    else:
                        st.success(f"✅ Chunk {i+1} completed! Found {len(entities)} entities (no nesting found in this chunk){overlap_msg}")
                else:
                    # Flat mode - count parent and child entities separately
                    parent_count = len([e for e in entities if 'parent_entity' not in e])
                    nested_count = len([e for e in entities if 'parent_entity' in e])
                    st.success(f"✅ Chunk {i+1} completed! Found {len(entities)} entities ({parent_count} main, {nested_count} nested as separate entities){overlap_msg}")
    
    # Remove duplicates from overlapping regions
    # st.info("🔍 Removing duplicate entities from overlapping regions...")
    deduplicated_entities = remove_overlapping_duplicates(all_entities, processed_chunks)
    
    removed_count = len(all_entities) - len(deduplicated_entities)
    # if removed_count > 0:
    #     st.success(f"✅ Removed {removed_count} duplicate entities from overlapping regions")
    # else:
    #     st.info("ℹ️ No duplicate entities found in overlapping regions")
    
    # Final summary
    total_time = time.time() - start_time
    
    # Show detailed summary for nested mode
    if st.session_state.annotation_mode == "Nested (Hierarchical)":
        # Count entities with nested structure in deduplicated results
        entities_with_nesting = len([e for e in deduplicated_entities if e.get('nested_entities')])
        total_nested_children = sum(len(e.get('nested_entities', [])) for e in deduplicated_entities)
        
        st.balloons()
        st.success(f"🎉 All overlapping chunks processed in {total_time:.1f} seconds!")
        # st.info(f"📊 Final Results: {len(deduplicated_entities)} total entities (after deduplication)")
        
        if entities_with_nesting > 0:
            # st.info(f"🔗 Nesting Statistics: {entities_with_nesting} entities contain {total_nested_children} nested children")
            nesting_ratio = (total_nested_children / (len(deduplicated_entities) + total_nested_children)) * 100
            # st.info(f"📈 Nesting Coverage: {nesting_ratio:.1f}% of all entities are nested within parents")
        # else:
        #     st.info("ℹ️ No nested entities were found - all entities are at the top level")
    else:
        # Flat mode - entities are already flattened
        total_parent = len([e for e in deduplicated_entities if 'parent_entity' not in e])
        total_nested = len([e for e in deduplicated_entities if 'parent_entity' in e])
        
        st.balloons()
        st.success(f"🎉 All overlapping chunks processed in {total_time:.1f} seconds!")
        # st.info(f"📊 Final Results: {len(deduplicated_entities)} total entities (after deduplication)")
        st.info(f"📈 Breakdown: {total_parent} main entities, {total_nested} nested entities")
        
        # if total_nested > 0:
        #     st.info(f"🔗 Nesting Statistics: {total_nested} entities were originally nested but are now flattened")
    
    # Show overlap processing summary
    total_chars_processed = sum(len(chunk[0]) for chunk in chunks_with_overlap)
    overlap_efficiency = (total_chars_processed - len(text)) / len(text) * 100 if len(text) > 0 else 0
    
    with st.expander("🔗 Overlap Processing Summary", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Original Text", f"{len(text):,} chars")
        with col2:
            st.metric("Total Processed", f"{total_chars_processed:,} chars")
        with col3:
            st.metric("Overlap Redundancy", f"{overlap_efficiency:.1f}%")
        
        st.info(f"📈 Processing efficiency: Overlapping chunks helped ensure entities at chunk boundaries are properly detected")
        if removed_count > 0:
            st.success(f"🎯 Successfully identified and removed {removed_count} duplicate entities from overlapping regions")
    
    return deduplicated_entities


def flatten_entities_for_conll(entities):
    """
    Flatten nested entities structure for CoNLL format export.
    
    Args:
        entities (list): List of entities that may contain nested_entities
    
    Returns:
        list: Flat list of entities with start, end, label, text fields
    """
    flattened_entities = []
    
    def extract_flat_entity(entity):
        """Extract basic entity information for CoNLL format."""
        if not isinstance(entity, dict):
            return None
            
        # Handle different field naming conventions
        start_field = None
        end_field = None
        
        # Check for different start/end field names
        if 'start' in entity and 'end' in entity:
            start_field = 'start'
            end_field = 'end'
        elif 'start_char' in entity and 'end_char' in entity:
            start_field = 'start_char'
            end_field = 'end_char'
        else:
            # Check if entity has required fields
            return None
            
        if 'label' not in entity:
            return None
            
        # Create basic entity structure for CoNLL
        flat_entity = {
            'start': entity[start_field],
            'end': entity[end_field],
            'label': entity['label'],
            'text': entity.get('text', '')
        }
        
        return flat_entity
    
    def process_entity_recursively(entity):
        """Recursively process entity and its nested entities."""
        # Add the main entity
        flat_entity = extract_flat_entity(entity)
        if flat_entity:
            flattened_entities.append(flat_entity)
        
        # Process nested entities if they exist
        nested_entities = entity.get('nested_entities', [])
        if isinstance(nested_entities, list):
            for nested_entity in nested_entities:
                if isinstance(nested_entity, dict):
                    process_entity_recursively(nested_entity)
    
    # Process all entities
    for entity in entities:
        if isinstance(entity, dict):
            process_entity_recursively(entity)
    
    return flattened_entities


def convert_to_conll_format(text, entities, annotation_mode="flat"):
    """
    Convert text and annotations to CoNLL format for NER training.
    Uses spaCy tokenization and improved entity matching algorithm.
    
    Args:
        text (str): The original text
        entities (list): List of entity dictionaries with 'start', 'end', 'label', 'text'
        annotation_mode (str): "flat" or "nested" - determines how to handle overlapping entities
    
    Returns:
        str: Text in CoNLL format (token per line with IOB tags)
    """
    from spacy.lang.en import English
    
    if not text or not entities:
        return ""
    
    # Use a lightweight tokenizer
    nlp = English()
    nlp.add_pipe("sentencizer")
    
    # Flatten nested entities structure for CoNLL format
    flattened_entities = flatten_entities_for_conll(entities)
    
    # Remove duplicate entities (same start/end/label)
    unique_entities = []
    seen = set()
    for entity in flattened_entities:
        if (isinstance(entity, dict) and 
            'start' in entity and 'end' in entity and 'label' in entity and
            0 <= entity['start'] < entity['end'] <= len(text)):
            key = (entity['start'], entity['end'], entity['label'])
            if key not in seen:
                unique_entities.append(entity)
                seen.add(key)
    
    # Build list of spans (start, end, label) and sort by start position
    spans = [(ent['start'], ent['end'], ent['label']) for ent in unique_entities]
    spans.sort()  # Sort by start position to handle overlaps better
    
    # Tokenize text using spaCy
    doc = nlp(text)
    conll_lines = []
    
    for token in doc:
        start, end = token.idx, token.idx + len(token.text)
        label = "O"
        
        # Find the entity this token belongs to
        # Priority: exact match > partial overlap, longer spans > shorter spans
        best_match = None
        best_score = 0
        
        for ent_start, ent_end, ent_label in spans:
            # Check if token overlaps with entity
            if start < ent_end and end > ent_start:
                # Calculate overlap score (prefer complete containment)
                if start >= ent_start and end <= ent_end:
                    # Token completely inside entity
                    score = 100 + (ent_end - ent_start)  # Prefer longer entities
                else:
                    # Partial overlap
                    overlap = min(end, ent_end) - max(start, ent_start)
                    score = overlap
                
                if score > best_score:
                    best_score = score
                    best_match = (ent_start, ent_end, ent_label)
        
        if best_match:
            ent_start, ent_end, ent_label = best_match
            # Determine if this is the beginning of the entity
            if start == ent_start:
                label = f"B-{ent_label.strip().upper()}"
            else:
                label = f"I-{ent_label.strip().upper()}"
        
        conll_lines.append(f"{token.text}\t{label}")
    
    # Add sentence breaks (empty lines) after sentence-ending punctuation
    final_lines = []
    for line in conll_lines:
        final_lines.append(line)
        # Add empty line after sentence-ending punctuation
        if line.split('\t')[0] in ['.', '!', '?']:
            final_lines.append("")
    
    return '\n'.join(final_lines)


def create_conll_export_data(text, entities, annotation_mode="flat"):
    """
    Create CoNLL format export data with metadata.
    
    Args:
        text (str): The original text
        entities (list): List of entity dictionaries
        annotation_mode (str): "flat" or "nested"
    
    Returns:
        dict: Dictionary containing CoNLL data and metadata
    """
    conll_content = convert_to_conll_format(text, entities, annotation_mode)
    
    # Flatten entities for accurate counting
    flattened_entities = flatten_entities_for_conll(entities)
    
    # Count entities by label
    label_counts = {}
    for entity in flattened_entities:
        label = entity.get('label', 'ENTITY')
        label_counts[label] = label_counts.get(label, 0) + 1
    
    # Calculate accurate token count from CoNLL content
    conll_lines = conll_content.split('\n')
    total_tokens = len([line for line in conll_lines if line.strip() and '\t' in line])
    
    # Create metadata
    metadata = {
        "format": "CoNLL",
        "annotation_mode": annotation_mode,
        "total_entities": len(flattened_entities),
        "total_tokens": total_tokens,
        "label_distribution": label_counts,
        "export_timestamp": pd.Timestamp.now().isoformat()
    }
    
    return {
        "conll_content": conll_content,
        "metadata": metadata
    }