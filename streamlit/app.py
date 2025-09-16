import streamlit as st
import pandas as pd
import json
import traceback
import streamlit as st
import pandas as pd
from helper import (
    display_processing_summary,  # Function to show processing summary
    generate_label_colors,  # Function to generate colors for labels
    get_token_recommendations,  # Function to get token recommendations based on chunk size
    validate_annotations_streamlit,  # Function to validate annotations
    correct_annotation_positions,  # Enhanced function to correct annotation positions
    debug_annotation_positions,  # Debug function for position analysis
    run_annotation_pipeline,  # Function to run the annotation pipeline
    clear_all_previous_data,  # Function to clear all previous data
    evaluate_annotations_with_llm,  # Function to evaluate annotations with LLM
    apply_evaluation_recommendations, # Function to apply evaluation recommendations
    display_annotated_entities_with_selection,
    create_annotations_for_similar_words,  # Function to auto-detect similar words
    auto_detect_similar_words_for_llm_annotations,  # Function to auto-detect similar words for LLM annotations
    create_conll_export_data,  # Function to create CoNLL export data with metadata
    identify_duplicate_llm_annotations,  # Function to identify which LLM annotations to delete
)
from enhanced_validation import validate_annotations_enhanced, auto_fix_annotations  # Enhanced validation with phantom detection
from llm_clients import LLMClient


# ----- Page Setup -----
st.set_page_config(page_title="LLM-based Scientific Text Annotator", layout="wide")

# ----- Title and Description -----
st.title("🔬 Scientific Text Annotator with LLMs")
st.markdown("Use OpenAI or Claude models to annotate scientific text with custom tag definitions.")

# ----- Session State Setup -----
if 'text_data' not in st.session_state:
    st.session_state.text_data = ""
if 'tag_df' not in st.session_state:
    st.session_state.tag_df = None
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'model_provider' not in st.session_state:
    st.session_state.model_provider = "OpenAI"
if 'annotated_entities' not in st.session_state:
    st.session_state.annotated_entities = []
if 'annotation_complete' not in st.session_state:
    st.session_state.annotation_complete = False
if 'evaluation_results' not in st.session_state:
    st.session_state.evaluation_results = []
if 'evaluation_complete' not in st.session_state:
    st.session_state.evaluation_complete = False
if 'evaluation_summary' not in st.session_state:
    st.session_state.evaluation_summary = {}
if 'manual_annotations' not in st.session_state:
    st.session_state.manual_annotations = []
if 'selected_text_for_annotation' not in st.session_state:
    st.session_state.selected_text_for_annotation = ""
if 'selected_start_pos' not in st.session_state:
    st.session_state.selected_start_pos = -1
if 'selected_end_pos' not in st.session_state:
    st.session_state.selected_end_pos = -1
if 'annotation_mode' not in st.session_state:
    st.session_state.annotation_mode = "Nested (Hierarchical)"
if 'auto_similar_words' not in st.session_state:
    st.session_state.auto_similar_words = True
if 'auto_detected_entities' not in st.session_state:
    st.session_state.auto_detected_entities = []

st.sidebar.header("🔐 API Configuration")

api_key = st.sidebar.text_input("Paste your API key", type="password")
model_provider = st.sidebar.selectbox("Choose LLM provider", ["OpenAI", "Claude"])

st.session_state.api_key = api_key
st.session_state.model_provider = model_provider

if model_provider == "OpenAI":
    model = st.sidebar.selectbox("OpenAI model", ["gpt-4o-mini", "gpt-4o", "gpt-4", "gpt-3.5-turbo"])
else:
    model = st.sidebar.selectbox("Claude model", ["claude-3-7-sonnet-20250219", "claude-3-5-haiku-20241022"])

st.sidebar.markdown("---")
st.sidebar.subheader("🔧 Processing Parameters")

# Add annotation mode selection
annotation_mode = st.sidebar.selectbox(
    "Annotation Mode", 
    ["Flat (Traditional)", "Nested (Hierarchical)"],
    index=1,  # Default to nested
    help="Flat: Non-overlapping entities only. Nested: Allows entities within entities (e.g., 'BRCA1' within 'BRCA1 protein complex')"
)

st.session_state.annotation_mode = annotation_mode

# Auto-detect similar words feature
auto_similar_words = st.sidebar.checkbox(
    "Auto-detect similar words", 
    value=True,
    help="Automatically find and annotate all similar words when LLM finds an entity (case-insensitive matching)"
)

st.session_state.auto_similar_words = auto_similar_words

temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.1, step=0.05, 
                                help="Lower = more consistent, Higher = more creative")

chunk_size = st.sidebar.slider("Chunk size (characters)", 200, 4000, 1000, step=100,
                              help="Size of text chunks to process separately")


min_tokens, max_tokens_limit, default_tokens = get_token_recommendations(chunk_size)

max_tokens = st.sidebar.slider(
    "Max tokens per response", 
    min_tokens, 
    max_tokens_limit, 
    default_tokens, 
    step=50,
    help=f"Recommended: {default_tokens} tokens for {chunk_size} character chunks"
)

# Show the relationship
st.sidebar.info(f"""
**Current Settings:**
- Chunk: {chunk_size:,} chars (~{chunk_size//4:,} tokens input)
- Response: {max_tokens:,} tokens max output
- Ratio: {max_tokens/(chunk_size//4):.1f}x output/input
""")

# Warning if settings seem problematic
if max_tokens > chunk_size // 2:
    st.sidebar.warning("⚠️ Max tokens seems very high for this chunk size")
elif max_tokens < chunk_size // 20:
    st.sidebar.warning("⚠️ Max tokens might be too low - responses may get cut off")

st.sidebar.markdown("---")
clean_text = st.sidebar.checkbox("Clean text input (remove weird characters)", value=True)

# ----- GitHub Repository and Developer Info -----
st.sidebar.markdown("---")
st.sidebar.markdown("### 👨‍💻 About")
st.sidebar.markdown("""
**Developer:** Amirhossein Bayani  
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/amirhosseinbayani/)

**GitHub Repository:**  
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=flat&logo=github&logoColor=white)](https://github.com/teman67/Annotation_NER_LLM)

This app enables AI-powered scientific text annotation with support for manual editing, auto-detection of similar entities, and export to various formats.
""")

st.sidebar.markdown("---")
st.sidebar.markdown("💡 **Features:**")
st.sidebar.markdown("""
- 🤖 LLM-powered entity recognition
- 🔍 Auto-detection of similar words
- ✏️ Manual annotation editing
- 📊 Quality evaluation
- 📋 JSON & CoNLL export
- 🔧 Position validation & fixing
""")

st.sidebar.markdown("---")
st.sidebar.markdown("⭐ **Star the repo if you find it useful!**")

# ----- File Upload -----
st.header("📄 Upload Scientific Text")
uploaded_text = st.file_uploader("Upload a `.txt` file or paste below", type=["txt"])

if uploaded_text:
    text = uploaded_text.read().decode("utf-8", errors="ignore")
    if clean_text:
        text = ''.join(c for c in text if c.isprintable())
    st.session_state.text_data = text

text_area_input = st.text_area("Or paste text here:", st.session_state.text_data, height=200)

if text_area_input:
    st.session_state.text_data = text_area_input

# ----- CSV Tag Upload -----
st.header("🏷️ Tag Set Configuration")

# Option to choose between uploading or using local file
csv_option = st.radio(
    "Choose tag set source:",
    ["Upload your own CSV file", "Use reference example (scientific annotations)"],
    help="You can either upload your own CSV file or use the built-in scientific annotation reference example"
)

if csv_option == "Upload your own CSV file":
    uploaded_csv = st.file_uploader("Upload a `.csv` file with `tag_name`, `definition`, and `examples` columns", type=["csv"])
    
    if uploaded_csv:
        try:
            tag_df = pd.read_csv(uploaded_csv)
            required_cols = {"tag_name", "definition", "examples"}
            if not required_cols.issubset(tag_df.columns):
                st.error("CSV file must include columns: tag_name, definition, examples.")
            else:
                st.session_state.tag_df = tag_df
                st.success("✅ Custom tag file loaded successfully!")
                st.dataframe(tag_df)
                st.session_state.label_colors = generate_label_colors(tag_df['tag_name'].unique())
        except Exception as e:
            st.error(f"❌ Failed to read CSV: {e}")

elif csv_option == "Use reference example (scientific annotations)":
    try:
        import os
        reference_csv_path = os.path.join("TagSets", "reference_example_utf8_cleaned.csv")
        if os.path.exists(reference_csv_path):
            tag_df = pd.read_csv(reference_csv_path)
            st.session_state.tag_df = tag_df
            st.success("✅ Reference tag set loaded successfully!")
            # st.info("📖 Using scientific annotation reference example with predefined tags for biological entities, materials, and methods.")
            
            # Show expandable preview of the reference tags
            with st.expander("🔍 Preview Reference Tags", expanded=True):
                st.dataframe(tag_df)
            
            st.session_state.label_colors = generate_label_colors(tag_df['tag_name'].unique())
        else:
            st.error("❌ Reference CSV file not found. Please upload your own CSV file.")
    except Exception as e:
        st.error(f"❌ Failed to load reference CSV: {e}")

# ----- Input Validation -----
st.header("🧠 Ready to Annotate?")


# === Show Processing Summary ===
if st.session_state.text_data and st.session_state.tag_df is not None:
    display_processing_summary(
        st.session_state.text_data, 
        st.session_state.tag_df, 
        chunk_size, 
        temperature, 
        max_tokens, 
        model_provider, 
        model
    )

# === Streamlit UI ===
if st.button("🔍 Run Annotation", key="run_annotation_btn"):
    if not st.session_state.api_key:
        st.error("❌ API key missing")
    elif not st.session_state.text_data:
        st.error("❌ Text missing")
    elif st.session_state.tag_df is None:
        st.error("❌ Tag CSV missing")
    else:
        try:
            # Clear ALL previous data when starting new annotation
            clear_all_previous_data()  # This function we defined in step 3
            
            st.markdown("### 🚀 Starting Annotation Process")
            
            client = LLMClient(
                api_key=st.session_state.api_key,
                provider=st.session_state.model_provider,
                model=model,
            )
            entities = run_annotation_pipeline(
                text=st.session_state.text_data,
                tag_df=st.session_state.tag_df,
                client=client,
                temperature=temperature,
                max_tokens=max_tokens,
                chunk_size=chunk_size,
            )
            
            # Store results in session state
            st.session_state.annotated_entities = entities
            st.session_state.annotation_complete = True

            # Auto-detect similar words if enabled
            if st.session_state.auto_similar_words and entities:
                # st.markdown("### 🔍 Auto-detecting Similar Words")
                # st.info("Looking for similar words to automatically annotate with the same labels...")
                
                auto_detected, auto_stats = auto_detect_similar_words_for_llm_annotations(
                    st.session_state.text_data, 
                    entities
                )
                
                st.session_state.auto_detected_entities = auto_detected
                
                # Show summary of auto-detection results
                if auto_detected:
                    st.success(f"🎯 Auto-detected {len(auto_detected)} similar words from {auto_stats['entities_with_similar_words']} unique entities!")
                    
                    # Show detailed statistics
                    with st.expander("📊 Auto-detection Summary", expanded=False):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("LLM Entities", auto_stats['total_llm_entities'])
                        with col2:
                            st.metric("Entities with Similar Words", auto_stats['entities_with_similar_words'])
                        with col3:
                            st.metric("Total Similar Words Found", auto_stats['total_similar_words_found'])
                        
                        if auto_stats['by_label']:
                            st.subheader("By Label:")
                            for label, label_stats in auto_stats['by_label'].items():
                                st.write(f"**{label}**: {label_stats['original_entities']} original → {label_stats['similar_words_found']} similar words found")
                # else:
                #     st.info("ℹ️ No similar words found for auto-detection")
            else:
                # Clear auto-detected entities if feature is disabled
                st.session_state.auto_detected_entities = []

            # DEBUG: Add comprehensive debugging (keep your existing debug code)
            st.markdown("### 🔍 Annotation Information")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("LLM Entities", len(st.session_state.annotated_entities))
            with col2:
                st.metric("Auto-detected Similar", len(st.session_state.auto_detected_entities))
            with col3:
                total_entities = len(st.session_state.annotated_entities) + len(st.session_state.auto_detected_entities)
                st.metric("Total Entities", total_entities)
            with col4:
                # Check for invalid entities
                valid_entities = [e for e in st.session_state.annotated_entities 
                                if all(key in e for key in ['start_char', 'end_char', 'text', 'label'])]
                st.metric("Valid LLM Entities", len(valid_entities))

            # Show problematic entities (keep your existing debug code)
            problematic_entities = [e for e in st.session_state.annotated_entities 
                                if not all(key in e for key in ['start_char', 'end_char', 'text', 'label'])]

            if problematic_entities:
                with st.expander("⚠️ Problematic Entities (missing required fields)", expanded=True):
                    st.json(problematic_entities[:5])  # Show first 5

            # Check for entities with invalid positions (keep your existing debug code)
            invalid_pos_entities = []
            text_length = len(st.session_state.text_data)
            for e in st.session_state.annotated_entities:
                start = e.get('start_char', 0)
                end = e.get('end_char', 0)
                if start < 0 or end > text_length or start >= end:
                    invalid_pos_entities.append(e)

            if invalid_pos_entities:
                with st.expander("⚠️ Entities with Invalid Positions", expanded=True):
                    st.json(invalid_pos_entities[:5])

            # Show entity distribution by label (include all entities)
            all_entities_for_debug = st.session_state.annotated_entities + st.session_state.auto_detected_entities
            if all_entities_for_debug:
                entity_df_debug = pd.DataFrame(all_entities_for_debug)
                label_counts = entity_df_debug['label'].value_counts()
                
                with st.expander("📊 Entity Distribution by Label (LLM + Auto-detected)", expanded=False):
                    st.bar_chart(label_counts)
                    
                    # Show breakdown by source
                    st.subheader("Breakdown by Source:")
                    llm_count = len(st.session_state.annotated_entities)
                    auto_count = len(st.session_state.auto_detected_entities)
                    st.write(f"🤖 **LLM entities**: {llm_count}")
                    st.write(f"🤖🔍 **Auto-detected**: {auto_count}")
                    st.write(f"**Total**: {llm_count + auto_count}")
            
            total_entities = len(entities) + len(st.session_state.auto_detected_entities)
            st.success(f"🎯 Annotation completed! Found {len(entities)} LLM entities + {len(st.session_state.auto_detected_entities)} auto-detected = {total_entities} total entities.")

        except Exception as e:
            st.error(f"❌ Annotation failed: {e}")

# === Visual Highlight ===
st.subheader("🔍 Annotated Text Preview")

if st.session_state.get("annotation_complete"):
    # Combine annotations for display - use cleaned annotations if available
    combined_entities = []
    
    # Use cleaned annotations if phantom removal was performed
    if st.session_state.get('cleaned_annotations'):
        st.info("🧹 Displaying cleaned annotations (phantoms removed)")
        for entity in st.session_state.cleaned_annotations:
            entity_copy = entity.copy()
            # The cleaned annotations already have proper source tracking
            if 'source' not in entity_copy:
                entity_copy['source'] = 'cleaned'
            combined_entities.append(entity_copy)
    else:
        # Use original annotations
        # Add LLM annotations with source flag
        for entity in st.session_state.annotated_entities:
            entity_copy = entity.copy()
            entity_copy['source'] = 'llm'
            combined_entities.append(entity_copy)
        
        # Add auto-detected similar words with source flag
        for auto_entity in st.session_state.auto_detected_entities:
            auto_entity_copy = auto_entity.copy()
            auto_entity_copy['source'] = 'auto_detected'
            combined_entities.append(auto_entity_copy)
        
        # Add manual annotations with source flag
        for manual_entity in st.session_state.manual_annotations:
            manual_entity_copy = manual_entity.copy()
            manual_entity_copy['source'] = 'manual'
            combined_entities.append(manual_entity_copy)
    
    if combined_entities:
        # Display combined annotations
        display_annotated_entities_with_selection(combined_entities)
        
        # Add legend for annotation styles
        if combined_entities:
            # st.markdown("---")  # Removed to reduce spacing
            st.markdown("<div style='margin-top: -40px;'></div>", unsafe_allow_html=True)
            st.markdown("**📖 Legend:**")
            
            is_nested_mode = st.session_state.get('annotation_mode', 'Nested (Hierarchical)') == "Nested (Hierarchical)"
            
            if is_nested_mode:
                legend_col1, legend_col3, legend_col4 = st.columns(3)
                
                with legend_col1:
                    st.markdown("🤖 **LLM Parent**: <span style='background-color: #e0e0e0; padding: 2px 4px; border-radius: 3px; border: 2px solid #e0e0e0;'>Tag-based colors</span>", unsafe_allow_html=True)
                
                # with legend_col2:
                #     st.markdown("↳ **LLM Nested**: <span style='background-color: #e0e0e0; padding: 2px 4px; border-radius: 3px; border: 2px dotted #666;'>↳ Tag colors + dotted border</span>", unsafe_allow_html=True)
                
                with legend_col3:
                    st.markdown("✏️ **Manual**: <span style='background-color: #ffeb3b; padding: 2px 4px; border-radius: 3px; border: 2px solid #f57f17;'>Yellow with solid border</span>", unsafe_allow_html=True)
                
                with legend_col4:
                    st.markdown("🔍 **Auto Detected**: <span style='background-color: #ff9800; padding: 2px 4px; border-radius: 3px; border: 2px dashed #e65100;'>Orange with dashed border</span>", unsafe_allow_html=True)
                
                # with legend_col5:
                #     st.markdown("🤖🔍 **Auto from LLM**: <span style='background-color: #4caf50; padding: 2px 4px; border-radius: 3px; border: 2px dashed #2e7d32;'>Green with dashed border</span>", unsafe_allow_html=True)
            else:
                legend_col1, legend_col2, legend_col3, legend_col4 = st.columns(4)
                
                with legend_col1:
                    st.markdown("🤖 **LLM Annotations**: Tag-based colored highlighting")
                
                with legend_col2:
                    st.markdown("✏️ **Manual**: <span style='background-color: #ffeb3b; padding: 2px 4px; border-radius: 3px; border: 2px solid #f57f17;'>Yellow with solid border</span>", unsafe_allow_html=True)
                
                with legend_col3:
                    st.markdown("🔍 **Auto from Manual**: <span style='background-color: #ff9800; padding: 2px 4px; border-radius: 3px; border: 2px dashed #e65100;'>Orange with dashed border</span>", unsafe_allow_html=True)
                
                with legend_col4:
                    st.markdown("🤖🔍 **Auto from LLM**: <span style='background-color: #4caf50; padding: 2px 4px; border-radius: 3px; border: 2px dashed #2e7d32;'>Green with dashed border</span>", unsafe_allow_html=True)
    
    # Manual annotation interface
    st.markdown("---")
    st.subheader("✏️ Manual Annotation")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Text input for manual selection (read-only display)
        # selected_text = st.text_input(
        #     "Selected Text:",
        #     value=st.session_state.get('selected_text_for_annotation', ''),
        #     disabled=True,
        #     key="display_selected_text"
        # )
        
        # Manual text input as fallback
        manual_text_input = st.text_input(
            "Type text manually:",
            key="manual_text_input",
            help="You can also type the text you want to annotate manually"
        )
    
    with col2:
        if st.session_state.tag_df is not None:
            # Auto-detect similar words option
            auto_detect_similar = st.checkbox(
                "🔍 Auto-detect similar words",
                value=True,
                help="Automatically find and annotate all similar words (case-insensitive) when you manually annotate a word. Example: annotating 'pH' will also find 'PH', 'Ph', etc."
            )
            
            # Tag selection dropdown
            tag_options = st.session_state.tag_df['tag_name'].tolist()
            selected_tag = st.selectbox(
                "Select Tag:",
                options=tag_options,
                key="manual_tag_selection"
            )
            
            # Apply button
            if st.button("✅ Add Manual Annotation", key="add_manual_annotation"):
                # Determine which text to use
                text_to_annotate = ""
                if manual_text_input.strip():
                    text_to_annotate = manual_text_input.strip()
                elif st.session_state.get('selected_text_for_annotation', '').strip():
                    text_to_annotate = st.session_state.selected_text_for_annotation.strip()
                
                if text_to_annotate and selected_tag:
                    # Find the text in the original document
                    start_pos = st.session_state.text_data.find(text_to_annotate)
                    
                    if start_pos != -1:
                        end_pos = start_pos + len(text_to_annotate)
                        
                        # Check for overlaps with existing annotations (only in flat mode)
                        overlap_found = False
                        all_existing = st.session_state.annotated_entities + st.session_state.manual_annotations + st.session_state.auto_detected_entities
                        
                        if st.session_state.annotation_mode == "Flat (Traditional)":
                            # In flat mode, prevent any overlaps
                            for existing in all_existing:
                                existing_start = existing.get('start_char', 0)
                                existing_end = existing.get('end_char', 0)
                                
                                # Check for overlap
                                if (start_pos < existing_end and end_pos > existing_start):
                                    overlap_found = True
                                    break
                        else:
                            # In nested mode, only prevent identical annotations
                            for existing in all_existing:
                                existing_start = existing.get('start_char', 0)
                                existing_end = existing.get('end_char', 0)
                                
                                # Only prevent exact duplicates
                                if (start_pos == existing_start and end_pos == existing_end and 
                                    selected_tag == existing.get('label', '')):
                                    overlap_found = True
                                    break
                        
                        if not overlap_found:
                            # Create manual annotation for the first occurrence
                            manual_annotation = {
                                'start_char': start_pos,
                                'end_char': end_pos,
                                'text': text_to_annotate,
                                'label': selected_tag,
                                'source': 'manual'
                            }
                            
                            # Add to manual annotations
                            st.session_state.manual_annotations.append(manual_annotation)
                            
                            # Auto-detect similar words if enabled
                            similar_annotations_added = 0
                            if auto_detect_similar:
                                # Get all current annotations to check for overlaps
                                all_current = st.session_state.annotated_entities + st.session_state.manual_annotations + st.session_state.auto_detected_entities
                                
                                # Find and create annotations for similar words
                                similar_annotations = create_annotations_for_similar_words(
                                    st.session_state.text_data,
                                    text_to_annotate,
                                    selected_tag,
                                    all_current
                                )
                                
                                # Add similar annotations, respecting annotation mode
                                for similar_annotation in similar_annotations:
                                    sim_start = similar_annotation['start_char']
                                    sim_end = similar_annotation['end_char']
                                    
                                    # Check overlaps based on annotation mode
                                    sim_overlap_found = False
                                    
                                    if st.session_state.annotation_mode == "Flat (Traditional)":
                                        # In flat mode, prevent any overlaps
                                        for existing in all_current:
                                            existing_start = existing.get('start_char', 0)
                                            existing_end = existing.get('end_char', 0)
                                            
                                            if (sim_start < existing_end and sim_end > existing_start):
                                                sim_overlap_found = True
                                                break
                                    else:
                                        # In nested mode, only prevent exact duplicates
                                        for existing in all_current:
                                            existing_start = existing.get('start_char', 0)
                                            existing_end = existing.get('end_char', 0)
                                            
                                            if (sim_start == existing_start and sim_end == existing_end and 
                                                selected_tag == existing.get('label', '')):
                                                sim_overlap_found = True
                                                break
                                    
                                    if not sim_overlap_found:
                                        st.session_state.manual_annotations.append(similar_annotation)
                                        all_current.append(similar_annotation)  # Update current list for next iteration
                                        similar_annotations_added += 1
                            
                            # Clear selection
                            st.session_state.selected_text_for_annotation = ""
                            st.session_state.selected_start_pos = -1
                            st.session_state.selected_end_pos = -1
                            
                            if similar_annotations_added > 0:
                                st.success(f"✅ Added manual annotation: '{text_to_annotate}' → {selected_tag}")
                                st.info(f"🔍 Auto-detected and added {similar_annotations_added} similar word(s)")
                            else:
                                st.success(f"✅ Added manual annotation: '{text_to_annotate}' → {selected_tag}")
                            
                            st.rerun()
                        else:
                            if st.session_state.annotation_mode == "Flat (Traditional)":
                                st.error("❌ Selected text overlaps with existing annotation. Switch to Nested mode to allow overlapping annotations.")
                            else:
                                st.error("❌ This exact annotation already exists")
                    else:
                        st.error("❌ Selected text not found in document")
                else:
                    st.warning("⚠️ Please select/enter text and choose a tag")
        else:
            st.warning("⚠️ Please upload tag CSV first")
    
    # Show manual annotations count
    if st.session_state.manual_annotations:
        manual_count = len([a for a in st.session_state.manual_annotations if a.get('source') == 'manual'])
        auto_count = len([a for a in st.session_state.manual_annotations if a.get('source') == 'manual_auto'])
        total_count = len(st.session_state.manual_annotations)
        
        if auto_count > 0:
            st.info(f"📝 Manual annotations: {total_count} total ({manual_count} manual + {auto_count} auto-detected)")
        else:
            st.info(f"📝 Manual annotations: {manual_count}")

else:
    st.info("Run annotation first to see results and enable manual annotation.")

    
if st.session_state.get("annotation_complete"):
    st.header("📝 Edit Annotations")

    # Combine all annotations for editing
    all_annotations = []
    
    # Add LLM annotations
    for entity in st.session_state.annotated_entities:
        entity_copy = entity.copy()
        entity_copy['source'] = 'LLM'
        all_annotations.append(entity_copy)
    
    # Add auto-detected annotations from LLM
    for auto_entity in st.session_state.auto_detected_entities:
        auto_entity_copy = auto_entity.copy()
        auto_entity_copy['source'] = 'Auto-detected from LLM'
        all_annotations.append(auto_entity_copy)
    
    # Add manual annotations
    for manual_entity in st.session_state.manual_annotations:
        manual_entity_copy = manual_entity.copy()
        # Preserve the source type (manual or manual_auto) but capitalize for display
        if manual_entity_copy.get('source') == 'manual_auto':
            manual_entity_copy['source'] = 'Auto-detected from Manual'
        else:
            manual_entity_copy['source'] = 'Manual'
        all_annotations.append(manual_entity_copy)

    # Check if there are any annotations to display
    if not all_annotations:
        st.info("📭 No annotations available. All annotations have been deleted or none were created yet.")
        st.markdown("💡 **Tip**: You can run LLM annotation again or add manual annotations using the text selection tool above.")
    else:
        # Initialize or reload dataframe from session state, including ID column
        # Check if we need to recreate the dataframe
        should_recreate_df = (
            "editable_entities_df" not in st.session_state or 
            st.session_state.editable_entities_df.empty or
            len(all_annotations) != len(st.session_state.editable_entities_df)
        )
        
        if should_recreate_df:
            # Filter out invalid entities before creating DataFrame
            valid_entities = []
            for e in all_annotations:
                # Check if entity has all required fields
                required_fields = ['start_char', 'end_char', 'text', 'label']
                if all(field in e and e[field] is not None for field in required_fields):
                    # Additional validation
                    if (isinstance(e['start_char'], (int, float)) and 
                        isinstance(e['end_char'], (int, float)) and
                        e['start_char'] >= 0 and 
                        e['end_char'] > e['start_char'] and
                        isinstance(e['text'], str) and 
                        len(e['text'].strip()) > 0):
                        
                        # Clean entity - remove nested_entities and parent_entity fields
                        clean_entity = e.copy()
                        clean_entity.pop('nested_entities', None)
                        clean_entity.pop('parent_entity', None)
                        valid_entities.append(clean_entity)
                    # else:
                    #     # st.warning(f"Filtered out invalid entity: {e}")
                # else:
                #     st.warning(f"Filtered out entity missing required fields: {e}")
            
            # if len(valid_entities) != len(all_annotations):
            #     st.warning(f"⚠️ Filtered out {len(all_annotations) - len(valid_entities)} invalid entities")
            
            try:
                df_entities = pd.DataFrame(valid_entities)
                if not df_entities.empty:
                    df_entities.insert(0, "ID", range(len(df_entities)))
                    st.session_state.editable_entities_df = df_entities
                    st.success(f"✅ Created DataFrame with {len(df_entities)} valid entities ({len([e for e in valid_entities if e.get('source') == 'LLM'])} LLM + {len([e for e in valid_entities if e.get('source') == 'Auto-detected from LLM'])} Auto-detected + {len([e for e in valid_entities if e.get('source') in ['Manual', 'Auto-detected from Manual']])} Manual)")
                else:
                    st.error("❌ No valid entities to display")
                    st.session_state.editable_entities_df = pd.DataFrame()
            except Exception as e:
                st.error(f"Error creating DataFrame: {e}")
                st.session_state.editable_entities_df = pd.DataFrame()
        else:
            df_entities = st.session_state.editable_entities_df

        # Show editable table, disabled ID column
        if not df_entities.empty:
            # Prepare display dataframe - remove nesting columns
            display_df = df_entities.copy()
            
            # Remove any nesting-related columns if they exist
            columns_to_remove = ['parent_entity', 'nested_entities', 'Nesting']
            for col in columns_to_remove:
                if col in display_df.columns:
                    display_df = display_df.drop(columns=[col])
            
            edited_df = st.data_editor(
                display_df,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "ID": st.column_config.NumberColumn("ID", disabled=True),
                    "start_char": st.column_config.NumberColumn("Start", width="small"),
                    "end_char": st.column_config.NumberColumn("End", width="small"),
                    "text": st.column_config.TextColumn("Text", width="large"),
                    "label": st.column_config.TextColumn("Label", width="medium"),
                    "source": st.column_config.SelectboxColumn(
                        "Source",
                        options=["LLM", "Manual", "Auto-detected from LLM", "Auto-detected from Manual"],
                        disabled=True,
                        width="small"
                    ),
                },
                key="annotation_data_editor",
                disabled=["ID", "source"],
                hide_index=True,
            )

            # Save edits back to session state (except ID column)
            st.session_state.editable_entities_df = edited_df

            # Update the original annotations based on edits
            if not edited_df.equals(display_df):
                # Separate back into LLM, auto-detected, and manual annotations
                llm_annotations = []
                auto_detected_annotations = []
                manual_annotations = []
                
                for _, row in edited_df.iterrows():
                    # Remove display-only columns that exist
                    columns_to_drop = ['ID']
                    
                    row_dict = row.drop(columns_to_drop).to_dict()
                    # Clean NaN values and remove any nesting-related fields
                    row_dict = {k: v for k, v in row_dict.items() if pd.notna(v)}
                    # Ensure no nesting fields are included
                    row_dict.pop('nested_entities', None)
                    row_dict.pop('parent_entity', None)
                    row_dict.pop('Nesting', None)
                    
                    if row_dict.get('source') == 'LLM':
                        row_dict.pop('source', None)
                        llm_annotations.append(row_dict)
                    elif row_dict.get('source') == 'Auto-detected from LLM':
                        row_dict['source'] = 'auto_detected'
                        auto_detected_annotations.append(row_dict)
                    elif row_dict.get('source') in ['Manual', 'Auto-detected from Manual']:
                        # Restore original source type for manual annotations
                        original_source = 'manual' if row_dict.get('source') == 'Manual' else 'manual_auto'
                        row_dict['source'] = original_source
                        manual_annotations.append(row_dict)
                
                st.session_state.annotated_entities = llm_annotations
                st.session_state.auto_detected_entities = auto_detected_annotations
                st.session_state.manual_annotations = manual_annotations

            # Multiselect options from current df
            to_delete_ids = st.multiselect(
                "Select annotation ID(s) to remove:",
                options=edited_df["ID"].tolist() if not edited_df.empty else [],
                key="delete_selected_ids"
            )

            if st.button("🗑 Remove Selected Annotations"):
                if to_delete_ids:
                    # Filter out rows to delete
                    filtered_df = edited_df[~edited_df["ID"].isin(to_delete_ids)].reset_index(drop=True)
                    # Re-assign ID sequentially
                    filtered_df["ID"] = range(len(filtered_df))

                    # Update session state dataframe
                    st.session_state.editable_entities_df = filtered_df
                    
                    # If all annotations were deleted, handle this special case
                    if filtered_df.empty:
                        st.session_state.annotated_entities = []
                        st.session_state.auto_detected_entities = []
                        st.session_state.manual_annotations = []
                        # Don't clear annotation_complete as we still want to show the UI
                        st.success(f"All annotations have been removed.")
                        st.rerun()
                    
                    # Separate back into LLM, auto-detected, and manual annotations
                    llm_annotations = []
                    auto_detected_annotations = []
                    manual_annotations = []
                    
                    for _, row in filtered_df.iterrows():
                        # Remove display-only columns that exist
                        columns_to_drop = ['ID']
                        
                        row_dict = row.drop(columns_to_drop).to_dict()
                        # Clean NaN values and remove any nesting-related fields
                        row_dict = {k: v for k, v in row_dict.items() if pd.notna(v)}
                        # Ensure no nesting fields are included
                        row_dict.pop('nested_entities', None)
                        row_dict.pop('parent_entity', None)
                        row_dict.pop('Nesting', None)
                        
                        if row_dict.get('source') == 'LLM':
                            row_dict.pop('source', None)
                            llm_annotations.append(row_dict)
                        elif row_dict.get('source') == 'Auto-detected from LLM':
                            row_dict['source'] = 'auto_detected'
                            auto_detected_annotations.append(row_dict)
                        elif row_dict.get('source') in ['Manual', 'Auto-detected from Manual']:
                            # Restore original source type for manual annotations
                            original_source = 'manual' if row_dict.get('source') == 'Manual' else 'manual_auto'
                            row_dict['source'] = original_source
                            manual_annotations.append(row_dict)
                    
                    st.session_state.annotated_entities = llm_annotations
                    st.session_state.auto_detected_entities = auto_detected_annotations
                    st.session_state.manual_annotations = manual_annotations

                    # IMPORTANT: Clean up evaluation results after manual deletion
                    # We need to properly update evaluation results indices after deletions
                    if st.session_state.get('evaluation_results'):
                        # Create a mapping from entity indices to new indices
                        # In our case, entity_index in evaluation_results is equal to the ID in the dataframe
                        entity_index_to_new_index = {}
                        deleted_indices = set(to_delete_ids)
                        
                        # We need to track which entity indices (that were used in evaluation_results)
                        # will map to which new positions after deletion
                        
                        # Map old entity indices to their positions after deletion
                        # This is what we need: for each entity_index in evaluation_results,
                        # if it wasn't deleted, what's its new position?
                        deleted_entity_indices = []
                        kept_entity_indices = []
                        
                        # Map IDs to their positions in the sequence
                        for old_id in to_delete_ids:
                            deleted_entity_indices.append(old_id)
                        
                        # Get the IDs that remain, in order
                        all_ids_in_order = edited_df["ID"].tolist()
                        
                        # Map remaining entities to their new positions
                        new_index = 0
                        for old_id in all_ids_in_order:
                            if old_id not in deleted_indices:
                                entity_index_to_new_index[old_id] = new_index
                                kept_entity_indices.append(old_id)
                                new_index += 1
                        
                        # Update evaluation results to use new indices
                        updated_evaluation_results = []
                        
                        for eval_result in st.session_state.evaluation_results:
                            entity_idx = eval_result.get('entity_index', -1)
                            
                            # If the entity still exists in our mapping, update its index
                            if entity_idx in entity_index_to_new_index:
                                # Update to the new position
                                eval_result['entity_index'] = entity_index_to_new_index[entity_idx]
                                updated_evaluation_results.append(eval_result)
                        
                        # Log what's happening
                        st.session_state.debug_mapping = {
                            "deleted_ids": list(deleted_indices),
                            "original_ids": all_ids_in_order,
                            "new_mapping": entity_index_to_new_index,
                            "eval_results_before": len(st.session_state.evaluation_results),
                            "eval_results_after": len(updated_evaluation_results)
                        }
                                
                        # Update the evaluation results with the new indices
                        st.session_state.evaluation_results = updated_evaluation_results
                        
                        # Update evaluation complete flag only if we still have results
                        if len(updated_evaluation_results) > 0:
                            st.session_state.evaluation_complete = True
                        
                        # Update the summary if it exists
                        if 'evaluation_summary' in st.session_state and st.session_state.evaluation_summary:
                            # Update the counts in the summary
                            st.session_state.evaluation_summary['total_entities'] = len(filtered_df)
                            st.session_state.evaluation_summary['evaluated_entities'] = len(updated_evaluation_results)
                        
                        if len(updated_evaluation_results) > 0:
                            # Show debug information to help diagnose the issue
                            with st.expander("🔧 Debug: Evaluation Index Mapping", expanded=False):
                                st.write("### Evaluation Index Mapping")
                                st.write(f"Deleted IDs: {list(deleted_indices)}")
                                st.write(f"Original IDs: {all_ids_in_order}")
                                st.write(f"New Mapping: {entity_index_to_new_index}")
                                st.write(f"Evaluation Results Before: {len(st.session_state.evaluation_results)}")
                                st.write(f"Evaluation Results After: {len(updated_evaluation_results)}")
                                
                                # Sample before and after
                                if len(st.session_state.evaluation_results) > 0:
                                    st.write("### Sample Before:")
                                    st.write(st.session_state.evaluation_results[0])
                                if len(updated_evaluation_results) > 0:
                                    st.write("### Sample After:")
                                    st.write(updated_evaluation_results[0])
                            
                            st.info(f"🔄 Evaluation results have been updated to reflect the deleted annotations.")
                        else:
                            st.info("🔄 All evaluated annotations were deleted. Please re-run evaluation if needed.")

                    st.success(f"Removed {len(to_delete_ids)} annotation(s).")
                    # Store a flag in the session state to indicate we've just deleted annotations
                    st.session_state.just_deleted_annotations = True
                    # Force a rerun to update all UI components
                    st.rerun()
                    
                    # Force recreation of the editable dataframe on next render
                    if 'editable_entities_df' in st.session_state:
                        del st.session_state.editable_entities_df
                    
                    st.rerun()
                else:
                    st.warning("Please select annotation ID(s) to remove.")

            # Add button to delete duplicate LLM annotations (smart deletion)
            st.markdown("#### 🤖 Bulk Actions")
            col1, col2 = st.columns([1, 3])
            
            with col1:
                # Count LLM annotations and analyze duplicates
                llm_count = len(edited_df[edited_df['source'] == 'LLM']) if not edited_df.empty else 0
                
                if llm_count > 0:
                    # Get current entities to analyze
                    llm_entities = st.session_state.get('annotated_entities', [])
                    auto_detected_entities = st.session_state.get('auto_detected_entities', [])
                    
                    # Analyze which LLM annotations have duplicates
                    entities_to_delete, entities_to_keep, stats = identify_duplicate_llm_annotations(
                        llm_entities, auto_detected_entities
                    )
                    
                    duplicate_count = stats['has_duplicates']
                    unique_count = stats['unique_kept']
                    
                    # Smart delete button - only deletes LLM annotations that have auto-detected duplicates
                    if st.button(f"🗑 Delete Duplicate LLM Annotations ({duplicate_count})", 
                               disabled=duplicate_count == 0,
                               help=f"Remove {duplicate_count} LLM annotations that have auto-detected duplicates. Will keep {unique_count} unique LLM annotations that don't appear elsewhere."):
                        if duplicate_count > 0:
                            # Keep only the LLM annotations that don't have duplicates
                            st.session_state.annotated_entities = entities_to_keep
                            
                            # Filter the dataframe to remove the deleted LLM annotations
                            # Create a set of (start, end, text, label) tuples for entities to delete
                            delete_signatures = set()
                            for entity in entities_to_delete:
                                signature = (
                                    entity.get('start_char'), 
                                    entity.get('end_char'), 
                                    entity.get('text', '').strip(), 
                                    entity.get('label', '')
                                )
                                delete_signatures.add(signature)
                            
                            # Filter the dataframe
                            def should_keep_row(row):
                                if row['source'] != 'LLM':
                                    return True  # Keep all non-LLM annotations
                                
                                # For LLM annotations, check if this one should be deleted
                                row_signature = (
                                    row.get('start_char'), 
                                    row.get('end_char'), 
                                    str(row.get('text', '')).strip(), 
                                    row.get('label', '')
                                )
                                return row_signature not in delete_signatures
                            
                            filtered_df = edited_df[edited_df.apply(should_keep_row, axis=1)].reset_index(drop=True)
                            # Re-assign ID sequentially
                            filtered_df["ID"] = range(len(filtered_df))
                            
                            # Update session state dataframe
                            st.session_state.editable_entities_df = filtered_df
                            
                            # Clear evaluation results since they included deleted LLM annotations
                            if st.session_state.get('evaluation_results'):
                                st.session_state.evaluation_results = []
                                st.session_state.evaluation_complete = False
                                st.session_state.evaluation_summary = None
                            
                            st.success(f"✅ Deleted {duplicate_count} duplicate LLM annotations. Kept {unique_count} unique LLM annotations + all auto-detected and manual annotations.")
                            if duplicate_count > 0:
                                st.info("ℹ️ Evaluation results have been cleared. Please re-run evaluation if needed.")
                            
                            # Force a rerun to update all UI components
                            st.rerun()
                    
                    # Also provide the old "delete all" option for users who want it
                    if st.button(f"⚠️ Delete ALL LLM Annotations ({llm_count})", 
                               help="Delete ALL LLM annotations regardless of duplicates. Use with caution!"):
                        # Original delete all logic
                        filtered_df = edited_df[edited_df['source'] != 'LLM'].reset_index(drop=True)
                        filtered_df["ID"] = range(len(filtered_df))
                        st.session_state.editable_entities_df = filtered_df
                        
                        # Clear LLM annotations completely
                        st.session_state.annotated_entities = []
                        
                        # Clear evaluation results
                        if st.session_state.get('evaluation_results'):
                            st.session_state.evaluation_results = []
                            st.session_state.evaluation_complete = False
                            st.session_state.evaluation_summary = None
                        
                        st.success(f"✅ Deleted ALL {llm_count} LLM annotations. Auto-detected and manual annotations preserved.")
                        st.info("ℹ️ Evaluation results have been cleared. Please re-run evaluation if needed.")
                        st.rerun()
                        
                else:
                    st.info("No LLM annotations to delete")
            
            with col2:
                if llm_count > 0:
                    # Get analysis for display
                    llm_entities = st.session_state.get('annotated_entities', [])
                    auto_detected_entities = st.session_state.get('auto_detected_entities', [])
                    entities_to_delete, entities_to_keep, stats = identify_duplicate_llm_annotations(
                        llm_entities, auto_detected_entities
                    )
                    
                    st.markdown(f"""
                    **Smart Deletion Analysis:**
                    - 🔍 **{stats['has_duplicates']} LLM annotations** have auto-detected duplicates (will be deleted)
                    - 💎 **{stats['unique_kept']} LLM annotations** are unique (will be kept)
                    - 📊 **Total LLM annotations:** {stats['total_llm']}
                    
                    **Recommendation:** Use 'Delete Duplicate LLM Annotations' to keep unique scientific terms while removing redundant annotations.
                    """)
                else:
                    st.markdown("**Note:** Smart deletion will preserve unique LLM annotations while removing only those that have auto-detected duplicates elsewhere in the text.")
        
        else:
            st.info("📋 No annotations to display in the table.")
                
st.markdown("---")
# Download annotated JSON (outside of button click)
if st.session_state.get("annotation_complete"):    
    
    # Add validation and fixing section
    st.subheader("🔍 Validate & Fix Annotations Position")
    
    # Add validation mode selection
    validation_mode = st.radio(
        "Select Validation Mode:",
        ["Standard Validation", "Enhanced Validation (with Phantom Detection)"],
        help="Enhanced validation can detect LLM hallucinations and phantom annotations"
    )
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔍 Validate Annotations", key="validate_btn"):
            with st.spinner("Validating annotations..."):
                # Combine all annotations for validation
                all_annotations = st.session_state.annotated_entities + st.session_state.manual_annotations + st.session_state.auto_detected_entities
                
                if validation_mode == "Enhanced Validation (with Phantom Detection)":
                    validation_results = validate_annotations_enhanced(
                        st.session_state.text_data, 
                        all_annotations
                    )
                    st.session_state.validation_mode = "enhanced"
                else:
                    validation_results = validate_annotations_streamlit(
                        st.session_state.text_data, 
                        all_annotations
                    )
                    st.session_state.validation_mode = "standard"
                
                # Store validation results in session state
                st.session_state.validation_results = validation_results
    
    with col2:
        if st.button("🔧 Auto-Fix Annotations", key="auto_fix_btn"):
            if st.session_state.get('validation_results') and st.session_state.get('validation_mode') == "enhanced":
                with st.spinner("Auto-fixing annotations..."):
                    all_annotations = st.session_state.annotated_entities + st.session_state.manual_annotations + st.session_state.auto_detected_entities
                    
                    fixed_annotations, fix_summary = auto_fix_annotations(
                        st.session_state.text_data,
                        all_annotations,
                        st.session_state.validation_results
                    )
                    
                    # Update session state with fixed annotations
                    # Note: This updates all annotations - you might want to separate by type
                    st.session_state.fixed_annotations = fixed_annotations
                    st.session_state.fix_summary = fix_summary
                    
                    st.success(f"✅ Auto-fix completed! Fixed {fix_summary['total_fixed']} annotations, flagged {fix_summary['phantoms_flagged']} phantoms")
            else:
                st.warning("⚠️ Run Enhanced Validation first to enable auto-fix")
    
    with col3:
        if st.button("🐛 Debug Positions", key="debug_btn"):
            with st.spinner("Debugging annotation positions..."):
                # Combine all annotations for debugging
                all_annotations = st.session_state.annotated_entities + st.session_state.manual_annotations + st.session_state.auto_detected_entities
                
                debug_results = debug_annotation_positions(
                    st.session_state.text_data, 
                    all_annotations,
                    verbose=True
                )
                
                # Store debug results in session state
                st.session_state.debug_results = debug_results
    
    with col4:
        if st.button("🧹 Remove Phantoms", key="remove_phantoms_btn"):
            if st.session_state.get('validation_results') and st.session_state.get('validation_mode') == "enhanced":
                phantom_annotations = st.session_state.validation_results.get('phantom_annotations', [])
                phantom_count = len(phantom_annotations)
                
                if phantom_count > 0:
                    # Get phantom entity indices
                    phantom_indices = {ann['entity_index'] for ann in phantom_annotations}
                    
                    # Create combined list with source tracking
                    all_annotations = []
                    current_index = 0
                    
                    # Add LLM annotations with tracking
                    llm_start_index = current_index
                    for ann in st.session_state.annotated_entities:
                        ann['_source_type'] = 'llm'
                        ann['_original_index'] = current_index
                        all_annotations.append(ann)
                        current_index += 1
                    llm_end_index = current_index
                    
                    # Add manual annotations with tracking
                    manual_start_index = current_index
                    for ann in st.session_state.manual_annotations:
                        ann['_source_type'] = 'manual'
                        ann['_original_index'] = current_index
                        all_annotations.append(ann)
                        current_index += 1
                    manual_end_index = current_index
                    
                    # Add auto-detected annotations with tracking
                    auto_start_index = current_index
                    for ann in st.session_state.auto_detected_entities:
                        ann['_source_type'] = 'auto'
                        ann['_original_index'] = current_index
                        all_annotations.append(ann)
                        current_index += 1
                    auto_end_index = current_index
                    
                    # Remove phantom annotations
                    cleaned_annotations = [
                        ann for i, ann in enumerate(all_annotations)
                        if i not in phantom_indices
                    ]
                    
                    # Separate back into original lists
                    new_llm_annotations = []
                    new_manual_annotations = []
                    new_auto_annotations = []
                    
                    for ann in cleaned_annotations:
                        # Clean up tracking fields
                        source_type = ann.pop('_source_type', 'unknown')
                        ann.pop('_original_index', None)
                        
                        if source_type == 'llm':
                            new_llm_annotations.append(ann)
                        elif source_type == 'manual':
                            new_manual_annotations.append(ann)
                        elif source_type == 'auto':
                            new_auto_annotations.append(ann)
                    
                    # Update session state
                    original_llm_count = len(st.session_state.annotated_entities)
                    original_manual_count = len(st.session_state.manual_annotations)
                    original_auto_count = len(st.session_state.auto_detected_entities)
                    
                    st.session_state.annotated_entities = new_llm_annotations
                    st.session_state.manual_annotations = new_manual_annotations
                    st.session_state.auto_detected_entities = new_auto_annotations
                    
                    # Calculate removal counts by type
                    llm_removed = original_llm_count - len(new_llm_annotations)
                    manual_removed = original_manual_count - len(new_manual_annotations)
                    auto_removed = original_auto_count - len(new_auto_annotations)
                    
                    # Store cleaned annotations for reference
                    st.session_state.cleaned_annotations = cleaned_annotations
                    
                    # Success message with details
                    st.success(f"🧹 Removed {phantom_count} phantom annotations!")
                    
                    if llm_removed > 0 or manual_removed > 0 or auto_removed > 0:
                        st.info(f"📊 Removed: {llm_removed} LLM, {manual_removed} Manual, {auto_removed} Auto-detected")
                    
                    # Force refresh of displays
                    st.rerun()
                    
                else:
                    st.info("ℹ️ No phantom annotations detected")
            else:
                st.warning("⚠️ Run Enhanced Validation first to detect phantoms")
    
    # Display validation results if they exist (outside the button click)
    if st.session_state.get('validation_results'):
        validation_results = st.session_state.validation_results
        
        # Display validation summary
        st.markdown("### 📊 Validation Results")
        
        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            st.metric("Total Entities", validation_results['total_entities'])
        with col_b:
            # Calculate percentage safely to avoid division by zero
            if validation_results['total_entities'] > 0:
                accuracy_pct = validation_results['correct_entities']/validation_results['total_entities']*100
                delta_str = f"{accuracy_pct:.1f}%"
            else:
                delta_str = "0.0%"
            
            st.metric("Correct", validation_results['correct_entities'], delta=delta_str)
        with col_c:
            st.metric("Errors", len(validation_results['errors']))
        with col_d:
            st.metric("Warnings", len(validation_results['warnings']))
        
        # Show errors if any
        if validation_results['errors']:
            st.error(f"❌ Found {len(validation_results['errors'])} annotation errors!")
            
            with st.expander("📋 View Error Details", expanded=False):
                error_data = []
                for error in validation_results['errors'][:100]:  # Show first 100 errors
                    error_data.append({
                        "Index": error['entity_index'],
                        "Expected Text": error['expected_text'],
                        "Actual Text": error.get('actual_text', 'N/A'),
                        "Position": f"[{error['start_char']}:{error['end_char']}]",
                        "Label": error['label'],
                        "Error": error.get('error', 'Text mismatch')
                    })
                
                if error_data:
                    st.dataframe(pd.DataFrame(error_data), use_container_width=True)
                
                if len(validation_results['errors']) > 100:
                    st.info(f"Showing first 100 of {len(validation_results['errors'])} errors.")
        
        # Show warnings if any
        if validation_results['warnings']:
            st.warning(f"⚠️ Found {len(validation_results['warnings'])} warnings!")
    
            with st.expander("⚠️ View Warning Details", expanded=False):
                for i, warning in enumerate(validation_results['warnings']):
                    if warning.get('type') == 'overlap':
                        st.write(f"**Overlap {i+1}:**")
                        st.write(f"- Entity 1: '{warning['entity1']['text']}' [{warning['entity1']['start_char']}:{warning['entity1']['end_char']}]")
                        st.write(f"- Entity 2: '{warning['entity2']['text']}' [{warning['entity2']['start_char']}:{warning['entity2']['end_char']}]")
                    else:
                        st.write(f"**Zero-length annotation {i+1}:** {warning}")
                
        if not validation_results['errors']:
            st.success("✅ All position of the annotations are valid!")
    
    with col3:
        # Only show fix button if validation has been run and there are errors
        if (st.session_state.get('validation_results') and 
            st.session_state.validation_results.get('errors')):
            
            fix_strategy = st.selectbox(
                "Fix Strategy", 
                ["closest" , "first"],
                help="closest: Choose position closest to original | first: Use first occurrence found"
            )
            
            if st.button("🔧 Fix Annotations", key="fix_btn"):
                with st.spinner("Fixing annotations..."):
                    # Combine all annotations for fixing
                    all_annotations = st.session_state.annotated_entities + st.session_state.manual_annotations + st.session_state.auto_detected_entities
                    
                    # Use the enhanced correction function
                    corrected_entities = correct_annotation_positions(
                        st.session_state.text_data, 
                        all_annotations, 
                        verbose=True
                    )
                    
                    # Separate corrected entities back into LLM, auto-detected, and manual
                    num_llm_entities = len(st.session_state.annotated_entities)
                    num_auto_detected_entities = len(st.session_state.auto_detected_entities)
                    
                    fixed_llm = []
                    fixed_auto_detected = []
                    fixed_manual = []
                    
                    for i, entity in enumerate(corrected_entities):
                        # Remove source field for storage
                        entity_copy = entity.copy()
                        entity_copy.pop('source', None)
                        
                        if i < num_llm_entities:
                            # This was originally an LLM entity
                            fixed_llm.append(entity_copy)
                        elif i < num_llm_entities + num_auto_detected_entities:
                            # This was originally an auto-detected entity
                            entity_copy['source'] = 'auto_detected'  # Preserve auto-detected source
                            fixed_auto_detected.append(entity_copy)
                        else:
                            # This was originally a manual entity
                            fixed_manual.append(entity_copy)
                    
                    # Update session state with corrected entities
                    st.session_state.annotated_entities = fixed_llm
                    st.session_state.auto_detected_entities = fixed_auto_detected
                    st.session_state.manual_annotations = fixed_manual
                    
                    # Update the editable dataframe if it exists
                    if 'editable_entities_df' in st.session_state:
                        try:
                            # Combine for dataframe display
                            combined_for_df = []
                            for entity in fixed_llm:
                                entity_copy = entity.copy()
                                entity_copy['source'] = 'LLM'
                                combined_for_df.append(entity_copy)
                            for entity in fixed_auto_detected:
                                entity_copy = entity.copy()
                                entity_copy['source'] = 'Auto-detected from LLM'
                                combined_for_df.append(entity_copy)
                            for entity in fixed_manual:
                                entity_copy = entity.copy()
                                entity_copy['source'] = 'Manual'
                                combined_for_df.append(entity_copy)
                            
                            if combined_for_df:
                                df_fixed = pd.DataFrame(combined_for_df)
                                df_fixed.insert(0, "ID", range(len(df_fixed)))
                                st.session_state.editable_entities_df = df_fixed
                            else:
                                st.session_state.editable_entities_df = pd.DataFrame()
                        except:
                            pass  # If DataFrame creation fails, just skip
                    
                    # Clear validation results to allow re-validation
                    if 'validation_results' in st.session_state:
                        del st.session_state.validation_results
                    
                    st.success("✅ Annotation positions have been corrected! Please re-validate to see the results.")
    
    # Optional: Display fix results information
    st.info("💡 After fixing annotations, please re-validate to check if all issues were resolved!")

# === LLM Evaluation Section ===
if st.session_state.get("annotation_complete"):
    st.markdown("---")
    st.subheader("🤖 LLM Evaluation & Suggestions")
    
    col1, col2 = st.columns([2, 2])
    
    with col1:
        st.write("Use LLM to evaluate whether annotated entities match their tag definitions and get suggestions for improvements.")
    
    with col2:
        if st.button("🤖 Evaluate Annotations", key="evaluate_annotations_btn"):
            if not st.session_state.api_key:
                st.error("❌ API key missing for evaluation")
            elif not (st.session_state.annotated_entities or st.session_state.manual_annotations or st.session_state.auto_detected_entities):  # Check all annotation types
                st.error("❌ No annotations to evaluate")
            elif st.session_state.tag_df is None:
                st.error("❌ Tag definitions missing")
            else:
                with st.spinner("🤖 LLM is evaluating your annotations..."):
                    try:
                        # Create LLM client
                        client = LLMClient(
                            api_key=st.session_state.api_key,
                            provider=st.session_state.model_provider,
                            model=model,
                        )
                        
                        # FIXED: Combine ALL annotations for evaluation (LLM + auto-detected + manual)
                        all_annotations_for_eval = (st.session_state.annotated_entities + 
                                                   st.session_state.get("auto_detected_entities", []) + 
                                                   st.session_state.get("manual_annotations", []))
                        
                        # Run evaluation on ALL annotations
                        evaluations = evaluate_annotations_with_llm(
                            all_annotations_for_eval,  # FIXED: Use combined annotations
                            st.session_state.tag_df,
                            client,
                            temperature=0.1,  # Low temperature for consistent evaluation
                            max_tokens=2000
                        )
                        
                        # Store results in session state
                        st.session_state.evaluation_results = evaluations
                        st.session_state.evaluation_complete = True
                        
                        # Calculate summary statistics - FIXED: Use all annotations
                        total_entities = len(all_annotations_for_eval)
                        correct_count = sum(1 for eval_result in evaluations if eval_result.get('is_correct', False))
                        change_recommendations = sum(1 for eval_result in evaluations if eval_result.get('recommendation') == 'change_label')
                        delete_recommendations = sum(1 for eval_result in evaluations if eval_result.get('recommendation') == 'delete')
                        
                        st.session_state.evaluation_summary = {
                            'total_entities': total_entities,
                            'evaluated_entities': len(evaluations),
                            'correct_count': correct_count,
                            'change_recommendations': change_recommendations,
                            'delete_recommendations': delete_recommendations
                        }
                        
                        st.success(f"✅ Evaluation completed! Analyzed {len(evaluations)} entities.")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Evaluation failed: {e}")

# Display evaluation results if they exist (outside the button click)
# CHANGE 1: Replace the LLM Evaluation button section with this fixed version

# CHANGE 2: Replace the evaluation results display section with this fixed version

# Display evaluation results if they exist (outside the button click)
if st.session_state.get('evaluation_results') or st.session_state.get('evaluation_complete'):
    # First, check if there are any evaluation results after deletions
    if len(st.session_state.evaluation_results) == 0:
        st.info("⚠️ No evaluation results available. All evaluated entities have been deleted or removed.")
        
        # Option to clear evaluation state entirely
        if st.button("🔄 Reset Evaluation State", key="reset_eval_after_delete"):
            st.session_state.evaluation_complete = False
            st.session_state.evaluation_summary = {}
            st.rerun()
    else:
        # Display evaluation summary
        st.markdown("### 📊 Evaluation Summary")
        
        summary = st.session_state.evaluation_summary
        col_a, col_b, col_c, col_d = st.columns(4)
    
    # FIXED: Use all annotations (LLM + Auto-detected + Manual) for metrics
    all_current_annotations = (st.session_state.annotated_entities + 
                              st.session_state.get("auto_detected_entities", []) + 
                              st.session_state.get("manual_annotations", []))
    
    with col_a:
        st.metric("Total Entities", len(all_current_annotations))  # FIXED: Use combined count
    with col_b:
        # Recalculate accuracy based on current entities and evaluation results
        current_correct = 0
        valid_evaluations = 0
        for eval_result in st.session_state.evaluation_results:
            entity_idx = eval_result.get('entity_index', -1)
            if 0 <= entity_idx < len(all_current_annotations):  # FIXED: Check against all annotations
                valid_evaluations += 1
                if eval_result.get('is_correct', False):
                    current_correct += 1
        
        accuracy = current_correct / valid_evaluations * 100 if valid_evaluations > 0 else 0
        st.metric("Correct", current_correct, delta=f"{accuracy:.1f}%")
    with col_c:
        # Count remaining change recommendations
        remaining_changes = sum(1 for eval_result in st.session_state.evaluation_results 
                               if eval_result.get('recommendation') == 'change_label' and 
                               0 <= eval_result.get('entity_index', -1) < len(all_current_annotations))  # FIXED
        st.metric("Remaining Changes", remaining_changes)
    with col_d:
        # Count remaining delete recommendations
        remaining_deletes = sum(1 for eval_result in st.session_state.evaluation_results 
                               if eval_result.get('recommendation') == 'delete' and 
                               0 <= eval_result.get('entity_index', -1) < len(all_current_annotations))  # FIXED
        st.metric("Remaining Deletions", remaining_deletes)
    
    # Display evaluation results table - FIXED VERSION
    st.markdown("### 📋 Evaluation Results & Recommendations")
    
    # Convert evaluation results to DataFrame for display - FIXED TO INCLUDE ALL ENTITIES
    eval_df_display = []
    
    # Create a mapping of all entities with their evaluation results
    entity_evaluation_map = {}
    for eval_result in st.session_state.evaluation_results:
        entity_idx = eval_result.get('entity_index', -1)
        if 0 <= entity_idx < len(all_current_annotations):  # FIXED: Use all annotations
            entity_evaluation_map[entity_idx] = eval_result
    
    # Process ALL entities in the current combined annotations list - FIXED
    for current_idx, entity in enumerate(all_current_annotations):
        current_text = entity.get('text', '')
        current_label = entity.get('label', '')
        
        # Check if we have evaluation results for this entity
        if current_idx in entity_evaluation_map:
            eval_result = entity_evaluation_map[current_idx]
            
            # Check if this recommendation was already applied
            recommendation = eval_result.get('recommendation', '')
            is_applied = False
            
            if recommendation == 'change_label':
                suggested_label = eval_result.get('suggested_label', '')
                # If current label matches suggested label, recommendation was applied
                is_applied = (current_label == suggested_label)
            elif recommendation == 'delete':
                # If we're here, entity wasn't deleted, so not applied
                is_applied = False
            
            # Determine correctness - if recommendation was applied and it was change_label, now it's correct
            is_correct = eval_result.get('is_correct', False)
            if is_applied and recommendation == 'change_label':
                is_correct = True
            
            status = ''
            if is_applied:
                status = '✅ Applied'
            elif not is_correct:
                status = '❌ Needs Action'
            else:
                status = '✅ Correct'
            
            eval_df_display.append({
                'ID': current_idx,
                'Text': current_text,
                'Current Label': current_label,
                'Status': status,
                'Recommendation': recommendation if not is_applied else 'Applied ✅',
                'Suggested Label': eval_result.get('suggested_label', '') or 'N/A',
                'Reasoning': eval_result.get('reasoning', '')[:300] + '...' if len(eval_result.get('reasoning', '')) > 300 else eval_result.get('reasoning', '')
            })
        else:
            # Entity has no evaluation result - this might happen if evaluation was incomplete
            eval_df_display.append({
                'ID': current_idx,
                'Text': current_text,
                'Current Label': current_label,
                'Status': '⚠️ Not Evaluated',
                'Recommendation': 'N/A',
                'Suggested Label': 'N/A',
                'Reasoning': 'No evaluation data available'
            })
    
    if eval_df_display:
        eval_display_df = pd.DataFrame(eval_df_display)
        
        # Show evaluation table
        st.dataframe(eval_display_df, use_container_width=True, height=400)
        
        # Show debug information
        with st.expander("🔍 Debug Information", expanded=False):
            st.write(f"**Total LLM entities:** {len(st.session_state.annotated_entities)}")
            st.write(f"**Total manual entities:** {len(st.session_state.get('manual_annotations', []))}")
            st.write(f"**Total combined entities:** {len(all_current_annotations)}")  # FIXED
            st.write(f"**Total evaluation results:** {len(st.session_state.evaluation_results)}")
            st.write(f"**Entities displayed in table:** {len(eval_df_display)}")
            
            # Show entity indices in evaluation results
            eval_indices = [eval_result.get('entity_index', -1) for eval_result in st.session_state.evaluation_results]
            st.write(f"**Entity indices in evaluation results:** {sorted(eval_indices)}")
            
            # Show which entities have no evaluation
            evaluated_indices = set(eval_indices)
            all_indices = set(range(len(all_current_annotations)))  # FIXED
            missing_indices = all_indices - evaluated_indices
            if missing_indices:
                st.write(f"**Entities missing evaluation:** {sorted(missing_indices)}")
            else:
                st.write("**All entities have evaluation results**")
        
        # Filter for actionable recommendations (NOT YET APPLIED) - FIXED
        actionable_evals = []
        for eval_result in st.session_state.evaluation_results:
            entity_idx = eval_result.get('entity_index', -1)
            
            # Skip if entity index is invalid - FIXED: Check against all annotations
            if not (0 <= entity_idx < len(all_current_annotations)):
                continue
                
            recommendation = eval_result.get('recommendation', '')
            
            if recommendation == 'delete':
                # Delete recommendations are always actionable if entity exists
                actionable_evals.append(eval_result)
            elif recommendation == 'change_label':
                # Change recommendations are actionable if not already applied
                current_entity = all_current_annotations[entity_idx]  # FIXED: Use all annotations
                current_label = current_entity.get('label', '')
                suggested_label = eval_result.get('suggested_label', '')
                
                # Only actionable if current label != suggested label
                if current_label != suggested_label:
                    actionable_evals.append(eval_result)
        
        if actionable_evals:
            st.markdown("### 🔧 Apply Recommendations")
            
            # Create selection options for REMAINING recommendations only
            selection_options = []
            
            for eval_result in actionable_evals:
                entity_idx = eval_result.get('entity_index', -1)
                # Find the evaluation index for this eval_result
                eval_idx = next((i for i, er in enumerate(st.session_state.evaluation_results) if er == eval_result), -1)
                
                if 0 <= entity_idx < len(all_current_annotations):  # FIXED: Use all annotations
                    current_entity = all_current_annotations[entity_idx]  # FIXED
                    current_text = current_entity.get('text', eval_result.get('current_text', ''))
                    
                    if eval_result.get('recommendation') == 'delete':
                        action = "DELETE" 
                    else:
                        action = f"CHANGE to '{eval_result.get('suggested_label')}'"
                    
                    option_text = f"[Entity {entity_idx}] '{current_text}' → {action}"
                    selection_options.append((eval_idx, option_text))
            
            # Multiselect for recommendations to apply
            selected_recommendations = st.multiselect(
                "Select recommendations to apply:",
                options=[idx for idx, _ in selection_options],
                format_func=lambda x: next(text for idx, text in selection_options if idx == x),
                key="selected_eval_recommendations"
            )
            
            col1, col2 = st.columns([1, 3])
            
            with col1:
                if st.button("✅ Apply Selected", disabled=not selected_recommendations, key="apply_recommendations_btn"):
                    if selected_recommendations:
                        try:
                            # FIXED: Combine all annotations for applying recommendations (same as evaluation)
                            all_annotations_for_apply = (st.session_state.annotated_entities + 
                                                        st.session_state.get("auto_detected_entities", []) + 
                                                        st.session_state.get("manual_annotations", []))
                            
                            # Apply recommendations (including automatic deletions)
                            updated_entities, changes_made = apply_evaluation_recommendations(
                                all_annotations_for_apply,
                                st.session_state.evaluation_results,
                                selected_recommendations
                            )
                            
                            # FIXED: Split updated entities back into LLM, auto-detected, and manual annotations
                            num_llm_entities = len(st.session_state.annotated_entities)
                            num_auto_detected_entities = len(st.session_state.get("auto_detected_entities", []))
                            
                            # Update LLM entities
                            updated_llm_entities = []
                            updated_auto_detected_entities = []
                            updated_manual_entities = []
                            
                            for i, entity in enumerate(updated_entities):
                                if i < num_llm_entities:
                                    # This was originally an LLM entity
                                    updated_llm_entities.append(entity)
                                elif i < num_llm_entities + num_auto_detected_entities:
                                    # This was originally an auto-detected entity
                                    updated_auto_detected_entities.append(entity)
                                else:
                                    # This was originally a manual entity
                                    updated_manual_entities.append(entity)
                            
                            # Update session state
                            st.session_state.annotated_entities = updated_llm_entities
                            st.session_state.auto_detected_entities = updated_auto_detected_entities
                            if updated_manual_entities or st.session_state.get("manual_annotations"):
                                st.session_state.manual_annotations = updated_manual_entities
                            
                            # Update editable dataframe if it exists
                            if 'editable_entities_df' in st.session_state:
                                try:
                                    # FIXED: Use all updated entities (LLM + auto-detected + manual) for dataframe
                                    all_updated_entities = updated_llm_entities + updated_auto_detected_entities + updated_manual_entities
                                    df_updated = pd.DataFrame(all_updated_entities)
                                    if not df_updated.empty:
                                        df_updated.insert(0, "ID", range(len(df_updated)))
                                        st.session_state.editable_entities_df = df_updated
                                    else:
                                        st.session_state.editable_entities_df = pd.DataFrame()
                                except Exception as df_error:
                                    st.warning(f"Could not update editable dataframe: {df_error}")
                            
                            # Update evaluation results to reflect the changes
                            # Remove evaluation results for deleted entities and update indices
                            remaining_evaluation_results = []
                            entity_index_mapping = {}  # old_index -> new_index
                            
                            # FIXED: Use the original total entity count (LLM + manual)
                            original_total_entities = len(all_annotations_for_apply)
                            
                            # Create mapping for entities that weren't deleted
                            new_idx = 0
                            for old_idx in range(original_total_entities):
                                # Check if this entity was deleted
                                was_deleted = any(
                                    st.session_state.evaluation_results[sel_idx].get('entity_index') == old_idx and 
                                    st.session_state.evaluation_results[sel_idx].get('recommendation') == 'delete'
                                    for sel_idx in selected_recommendations
                                    if sel_idx < len(st.session_state.evaluation_results)
                                )
                                
                                if not was_deleted:
                                    entity_index_mapping[old_idx] = new_idx
                                    new_idx += 1
                            
                            # Update evaluation results with new indices
                            for eval_result in st.session_state.evaluation_results:
                                old_entity_idx = eval_result.get('entity_index', -1)
                                if old_entity_idx in entity_index_mapping:
                                    eval_result['entity_index'] = entity_index_mapping[old_entity_idx]
                                    remaining_evaluation_results.append(eval_result)
                                # If not in mapping, entity was deleted, so don't include this evaluation result
                            
                            st.session_state.evaluation_results = remaining_evaluation_results
                            
                            # Update evaluation_complete flag
                            if len(remaining_evaluation_results) > 0:
                                st.session_state.evaluation_complete = True
                            
                            # Update the summary if it exists
                            if 'evaluation_summary' in st.session_state and st.session_state.evaluation_summary:
                                # Update the counts in the summary
                                st.session_state.evaluation_summary['total_entities'] = len(updated_entities)
                                st.session_state.evaluation_summary['evaluated_entities'] = len(remaining_evaluation_results)
                            
                            # Show success message with changes
                            st.success(f"✅ Applied {len(selected_recommendations)} recommendations!")
                            
                            if changes_made:
                                with st.expander("📝 Changes Made", expanded=True):
                                    for change in changes_made:
                                        st.write(f"• {change}")
                            
                            # Clear the selection to avoid re-applying
                            if 'selected_eval_recommendations' in st.session_state:
                                del st.session_state['selected_eval_recommendations']
                            
                            # Rerun to refresh the display
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Failed to apply recommendations: {e}")
                            import traceback
                            st.error(traceback.format_exc())  # For debugging
            
            with col2:
                if selected_recommendations:
                    st.info(f"💡 {len(selected_recommendations)} recommendation(s) selected for application.")
                else:
                    st.info("💡 Select recommendations above to apply them.")
        
        else:
            st.success("🎉 All recommendations have been applied or no actionable recommendations remain!")
    
    else:
        st.info("ℹ️ No evaluation results to display (all entities may have been processed).")

# Option to clear evaluation results
if st.button("🧹 Clear Evaluation Results", key="clear_eval_results_btn"):
    st.session_state.evaluation_results = []
    st.session_state.evaluation_complete = False
    st.session_state.evaluation_summary = {}
    if 'selected_eval_recommendations' in st.session_state:
        del st.session_state['selected_eval_recommendations']
    st.rerun()


if st.session_state.get("annotation_complete"):
    st.markdown("---")
    st.header("💾 Export Results")
    
    # Check if there are any annotations to export
    # Calculate total annotations - use cleaned if available
    if st.session_state.get('cleaned_annotations'):
        total_annotations = len(st.session_state.cleaned_annotations)
        st.info("📝 Using cleaned annotations (phantoms removed) for export")
    else:
        total_annotations = (len(st.session_state.annotated_entities) + 
                            len(st.session_state.get("auto_detected_entities", [])) + 
                            len(st.session_state.get("manual_annotations", [])))
    
    if total_annotations == 0:
        st.info("📭 No annotations to export. All annotations have been deleted or none were created yet.")
        st.markdown("💡 **Tip**: You can run LLM annotation again or add manual annotations to have something to export.")
    else:
        # FIXED: Combine all annotations for export while preserving structure based on annotation mode
        all_combined_annotations = []
        is_nested_mode = st.session_state.get("annotation_mode", "Nested (Hierarchical)") == "Nested (Hierarchical)"

        # Use cleaned annotations if available (after phantom removal)
        if st.session_state.get('cleaned_annotations'):
            st.markdown("✨ **Exporting cleaned annotations** (phantom annotations have been removed)")
            for entity in st.session_state.cleaned_annotations:
                clean_entity = entity.copy()
                clean_entity.pop('source', None)  # Remove source if it exists
                clean_entity.pop('validation_flag', None)  # Remove validation flags
                clean_entity.pop('phantom_reason', None)  # Remove phantom analysis data
                
                if not is_nested_mode:
                    # In flat mode, remove nested structure fields
                    clean_entity.pop('nested_entities', None)
                    clean_entity.pop('parent_entity', None)
                # In nested mode, preserve nested_entities and parent_entity fields
                
                all_combined_annotations.append(clean_entity)
        else:
            # Use original annotations
            # Add LLM annotations 
            for entity in st.session_state.annotated_entities:
                clean_entity = entity.copy()
                clean_entity.pop('source', None)  # Remove source if it exists
                
                if not is_nested_mode:
                    # In flat mode, remove nested structure fields
                    clean_entity.pop('nested_entities', None)
                    clean_entity.pop('parent_entity', None)
                # In nested mode, preserve nested_entities and parent_entity fields
                
                all_combined_annotations.append(clean_entity)

            # Add auto-detected annotations from LLM
            for entity in st.session_state.get("auto_detected_entities", []):
                clean_entity = entity.copy()
                clean_entity.pop('source', None)  # Remove source if it exists
                
                if not is_nested_mode:
                    # In flat mode, remove nested structure fields  
                    clean_entity.pop('nested_entities', None)
                    clean_entity.pop('parent_entity', None)
                # In nested mode, preserve nested_entities and parent_entity fields
                
                all_combined_annotations.append(clean_entity)

            # Add manual annotations 
            for entity in st.session_state.get("manual_annotations", []):
                clean_entity = entity.copy()
                clean_entity.pop('source', None)  # Remove source if it exists
                
                if not is_nested_mode:
                    # In flat mode, remove nested structure fields  
                    clean_entity.pop('nested_entities', None)
                    clean_entity.pop('parent_entity', None)
                # In nested mode, preserve nested_entities and parent_entity fields
                
                all_combined_annotations.append(clean_entity)

        # Create appropriate export structure based on annotation mode
        if is_nested_mode:
            # For nested mode, preserve hierarchical structure
            def organize_nested_entities(entities):
                """Organize entities into hierarchical structure preserving nesting"""
                organized_entities = []
                
                for entity in entities:
                    # Keep the entity as-is with nested_entities preserved
                    if isinstance(entity, dict):
                        organized_entities.append(entity)
                
                return organized_entities

            organized_entities = organize_nested_entities(all_combined_annotations)
            
            # Create nested JSON structure
            output_json = {
                "text": st.session_state.get("text_data", ""),
                "entities": organized_entities,
                # "annotation_mode": "nested",
                # "nested_structure_preserved": True
            }
        else:
            # For flat mode, use original flat structure
            def organize_flat_entities(entities):
                """Organize entities into flat structure without nested hierarchies"""
                flat_entities = []
                
                for entity in entities:
                    # Ensure entity is a dictionary before processing
                    if not isinstance(entity, dict):
                        continue
                    clean_entity = {k: v for k, v in entity.items() if k not in ['source', 'confidence', 'nested_entities', 'parent_entity']}
                    flat_entities.append(clean_entity)
                
                return flat_entities

            organized_entities = organize_flat_entities(all_combined_annotations)
            
            # Create flat JSON structure
            output_json = {
                "text": st.session_state.get("text_data", ""),
                "entities": organized_entities,
                "annotation_mode": "flat"
            }

        # Create comprehensive export with metadata
        comprehensive_output_json = {
            "text": st.session_state.get("text_data", ""),
            "entities": organized_entities,
            "annotation_mode": "nested" if is_nested_mode else "flat",
            "llm_entities": [
                {k: v for k, v in entity.items() if k not in ['source', 'confidence'] + ([] if is_nested_mode else ['nested_entities', 'parent_entity'])} 
                for entity in st.session_state.annotated_entities
            ],
            "manual_entities": [
                {k: v for k, v in entity.items() if k not in ['source', 'confidence'] + ([] if is_nested_mode else ['nested_entities', 'parent_entity'])} 
                for entity in st.session_state.get("manual_annotations", [])
            ],
            "metadata": {
                "total_llm_entities": len(st.session_state.annotated_entities),
                "total_manual_entities": len(st.session_state.get("manual_annotations", [])),
                "total_entities": len(all_combined_annotations),
                # "annotation_mode": st.session_state.get("annotation_mode", "Nested (Hierarchical)"),
                # "nested_structure_preserved": is_nested_mode,
                "annotation_timestamp": pd.Timestamp.now().isoformat(),
                "model_provider": st.session_state.get("model_provider", ""),
                "model": model if 'model' in locals() else "",
                "processing_parameters": {
                    "temperature": temperature if 'temperature' in locals() else 0.1,
                    "chunk_size": chunk_size if 'chunk_size' in locals() else 1000,
                    "max_tokens": max_tokens if 'max_tokens' in locals() else 1000
                }
            }
        }
        
        # Add evaluation data if available
        if st.session_state.get('evaluation_complete') and st.session_state.get('evaluation_results'):
            comprehensive_output_json["evaluation"] = {
                "evaluation_results": st.session_state.evaluation_results,
                "evaluation_summary": st.session_state.evaluation_summary,
                "evaluation_timestamp": pd.Timestamp.now().isoformat()
            }
        
        # Add validation data if available
        if st.session_state.get('validation_results'):
            comprehensive_output_json["validation"] = {
                "validation_results": st.session_state.validation_results,
                "validation_timestamp": pd.Timestamp.now().isoformat()
            }
            st.info("✅ Export includes validation results.")
        
        # Add fix data if available
        if st.session_state.get('fix_results'):
            comprehensive_output_json["position_fixes"] = {
                "fix_results": st.session_state.fix_results,
                "fix_timestamp": pd.Timestamp.now().isoformat()
            }
        
        
        # Convert to JSON strings
        simple_json_str = json.dumps(output_json, indent=2, ensure_ascii=False)
        comprehensive_json_str = json.dumps(comprehensive_output_json, indent=2, ensure_ascii=False)
        
        # Define annotation mode string for exports
        annotation_mode_str = "nested" if is_nested_mode else "flat"
        
        # Create CoNLL format export
        conll_export_data = create_conll_export_data(
            st.session_state.get("text_data", ""),
            organized_entities,
            annotation_mode_str
        )
        conll_content = conll_export_data["conll_content"]
        conll_metadata = conll_export_data["metadata"]
        
        # Export buttons
        st.subheader("📥 Download Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.download_button(
                f"📥 Download JSON", 
                data=simple_json_str, 
                file_name=f"annotations_{annotation_mode_str}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json", 
                mime="application/json",
                key="download_simple_json_btn",
                help=f"Download annotations in {annotation_mode_str} structure {'preserving nesting' if is_nested_mode else 'without nesting'}"
            )
            
        with col2:
            st.download_button(
                f"📥 Download CoNLL", 
                data=conll_content, 
                file_name=f"annotations_{annotation_mode_str}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.conll", 
                mime="text/plain",
                key="download_conll_btn",
                help=f"Download annotations in CoNLL format for NER model training ({annotation_mode_str} mode)"
            )
            
        with col3:
            st.download_button(
                "📥 Comprehensive Export", 
                data=comprehensive_json_str, 
                file_name=f"annotations_comprehensive_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json", 
                mime="application/json",
                key="download_comprehensive_json_btn",
                help="Download with detailed metadata, evaluation results, and validation data"
            )
            
        # Show CoNLL format information and preview
        st.markdown("---")
        st.subheader("📊 CoNLL Format Information")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Entities", conll_metadata["total_entities"])
            st.metric("Approximate Tokens", conll_metadata["total_tokens"])
        
        with col2:
            st.write("**Label Distribution:**")
            for label, count in conll_metadata["label_distribution"].items():
                st.write(f"• {label}: {count}")
        
        with st.expander("👁️ Preview CoNLL Format", expanded=False):
            st.markdown("**Format Explanation:**")
            st.markdown("""
            - Each token is on a separate line with its corresponding label
            - Labels use IOB format: B-LABEL (Beginning), I-LABEL (Inside), O (Outside)
            - Empty lines separate sentences
            - Perfect for training NER models with libraries like spaCy, Transformers, etc.
            """)
            
            # Show first 20 lines of CoNLL output as preview
            conll_lines = conll_content.split('\n')
            preview_lines = conll_lines[:20]
            if len(conll_lines) > 20:
                preview_lines.append("...")
                preview_lines.append(f"[{len(conll_lines) - 20} more lines]")
            
            st.code('\n'.join(preview_lines), language='text')
            
        # Show preview of nested structure if there are nested entities
        # nested_count = len([e for e in organized_entities if 'nested_entities' in e and e['nested_entities']])
        # if nested_count > 0:
        #     st.info(f"🔗 Found {nested_count} entities with nested children in the dataset")
            
        #     with st.expander("👁️ Preview Nested Structure", expanded=False):
        #         for entity in organized_entities[:3]:  # Show first 3 entities
        #             if 'nested_entities' in entity and entity['nested_entities']:
        #                 st.write(f"**Parent:** {entity['text']} ({entity['label']})")
        #                 for child in entity['nested_entities']:
        #                     # Ensure child is a dictionary, not a string
        #                     if isinstance(child, dict) and 'text' in child and 'label' in child:
        #                         st.write(f"  ↳ **Child:** {child['text']} ({child['label']})")
        #                     else:
        #                         st.write(f"  ↳ **Child:** {str(child)} (unknown type)")
        #                 st.write("---")

        st.markdown("---")

        # Optional clear all button
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🧹 Clear All Annotations"):
                st.session_state.annotated_entities = []
                st.session_state.manual_annotations = []
                st.session_state.editable_entities_df = pd.DataFrame()
                st.session_state.annotation_complete = False
                st.session_state.selected_text_for_annotation = ""
                st.session_state.selected_start_pos = -1
                st.session_state.selected_end_pos = -1
                st.rerun()
        
        with col2:
            if st.button("🔧 Clean Nested Data", help="Remove any nested_entities or parent_entity fields from existing annotations"):
                # Clean LLM annotations
                cleaned_llm = []
                for entity in st.session_state.annotated_entities:
                    clean_entity = {k: v for k, v in entity.items() if k not in ['nested_entities', 'parent_entity']}
                    cleaned_llm.append(clean_entity)
                st.session_state.annotated_entities = cleaned_llm
                
                # Clean manual annotations
                cleaned_manual = []
                for entity in st.session_state.get("manual_annotations", []):
                    clean_entity = {k: v for k, v in entity.items() if k not in ['nested_entities', 'parent_entity']}
                    cleaned_manual.append(clean_entity)
                st.session_state.manual_annotations = cleaned_manual
                
                # Reset editable dataframe to force recreation
                if 'editable_entities_df' in st.session_state:
                    del st.session_state.editable_entities_df
                
                st.success("✅ Cleaned all nested data from annotations!")
                st.rerun()