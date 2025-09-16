"""
Enhanced validation system with phantom annotation detection.
This module provides improved validation capabilities for LLM-generated annotations.
"""

import streamlit as st
from helper import find_all_occurrences, try_advanced_fuzzy_match, detect_phantom_annotations

def validate_annotations_enhanced(text, entities):
    """
    Enhanced validation with phantom annotation detection.
    
    Args:
        text (str): The source text
        entities (list): List of entity dictionaries
    
    Returns:
        dict: Enhanced validation results with phantom detection
    """
    
    validation_results = {
        'total_entities': len(entities),
        'correct_entities': 0,
        'errors': [],
        'warnings': [],
        'phantom_annotations': [],
        'detailed_analysis': [],
        'phantom_analysis': None
    }
    
    st.write(f"🔍 Enhanced validation of {len(entities)} annotations...")
    
    # Step 1: Run phantom detection analysis
    st.write("🕵️ Detecting phantom annotations...")
    phantom_analysis = detect_phantom_annotations(text, entities)
    validation_results['phantom_analysis'] = phantom_analysis
    
    phantom_indices = {item['index'] for item in phantom_analysis['phantom_annotations']}
    
    # Display phantom detection results
    if phantom_analysis['phantom_annotations']:
        st.warning(f"⚠️ Detected {len(phantom_analysis['phantom_annotations'])} potential phantom annotations")
        
        with st.expander("🔍 Phantom Annotation Analysis"):
            for phantom in phantom_analysis['phantom_annotations'][:3]:  # Show first 3
                st.write(f"**Text:** {phantom['expected_text']}")
                st.write(f"**Issues:** {', '.join(phantom['issues'])}")
                st.write(f"**Status:** {phantom.get('status', 'unknown')}")
                st.write("---")
                
            if len(phantom_analysis['phantom_annotations']) > 3:
                st.info(f"... and {len(phantom_analysis['phantom_annotations']) - 3} more phantom annotations")
    
    # Step 2: Regular validation with phantom awareness
    validation_progress = st.progress(0)
    validation_status = st.empty()
    
    for i, entity in enumerate(entities):
        validation_progress.progress((i + 1) / len(entities))
        validation_status.text(f"Validating entity {i+1}/{len(entities)}: '{entity.get('text', 'N/A')[:30]}...'")
        
        start_char = entity.get('start_char')
        end_char = entity.get('end_char')
        expected_text = entity.get('text')
        
        analysis = {
            'entity_index': i,
            'expected_text': expected_text,
            'start_char': start_char,
            'end_char': end_char,
            'label': entity.get('label', 'Unknown'),
            'status': 'unknown',
            'is_phantom': i in phantom_indices
        }
        
        # Handle phantom annotations
        if i in phantom_indices:
            phantom_info = next((p for p in phantom_analysis['phantom_annotations'] if p['index'] == i), {})
            analysis['status'] = 'phantom'
            analysis['phantom_reason'] = phantom_info.get('issues', [])
            analysis['phantom_type'] = phantom_info.get('status', 'unknown')
            
            validation_results['phantom_annotations'].append({
                'entity_index': i,
                'expected_text': expected_text,
                'start_char': start_char,
                'end_char': end_char,
                'label': entity.get('label', 'Unknown'),
                'phantom_reason': phantom_info.get('issues', []),
                'phantom_type': phantom_info.get('status', 'unknown')
            })
            
            validation_results['detailed_analysis'].append(analysis)
            continue
        
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
        
        # Extract actual text and validate
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
                    analysis['status'] = 'position_fixable'
                else:
                    # Try advanced fuzzy matching
                    fuzzy_result = try_advanced_fuzzy_match(text, expected_text, start_char)
                    if fuzzy_result:
                        analysis['suggested_position'] = fuzzy_result
                        analysis['position_offset'] = fuzzy_result[0] - start_char
                        analysis['status'] = 'fuzzy_fixable'
                    else:
                        analysis['status'] = 'unfixable'
                
                error_info = {
                    'entity_index': i,
                    'expected_text': expected_text,
                    'actual_text': actual_text,
                    'start_char': start_char,
                    'end_char': end_char,
                    'label': entity.get('label', 'Unknown'),
                    'found_positions': correct_positions,
                    'suggested_correction': analysis.get('suggested_position'),
                    'status': analysis['status']
                }
                validation_results['errors'].append(error_info)
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
    
    # Display enhanced results
    display_enhanced_results(validation_results)
    
    return validation_results

def display_enhanced_results(validation_results):
    """Display enhanced validation results with phantom annotation details."""
    
    total = validation_results['total_entities']
    correct = validation_results['correct_entities']
    phantom_count = len(validation_results['phantom_annotations'])
    error_count = len(validation_results['errors'])
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Annotations", total)
    with col2:
        st.metric("Correct", correct, f"{correct/total*100:.1f}%" if total > 0 else "0%")
    with col3:
        st.metric("Phantom Detected", phantom_count, f"{phantom_count/total*100:.1f}%" if total > 0 else "0%")
    with col4:
        st.metric("Position Errors", error_count - phantom_count, f"{(error_count-phantom_count)/total*100:.1f}%" if total > 0 else "0%")
    
    # Detailed analysis
    if phantom_count > 0:
        st.subheader("🕵️ Phantom Annotation Analysis")
        
        phantom_analysis = validation_results['phantom_analysis']
        
        if phantom_analysis['suspicious_patterns']:
            st.write("**Detected Patterns:**")
            for pattern in phantom_analysis['suspicious_patterns']:
                st.write(f"- **{pattern['pattern'].replace('_', ' ').title()}**: {pattern['count']} cases")
                if len(pattern['examples']) <= 2:
                    for example in pattern['examples']:
                        st.write(f"  - \"{example}\"")
                else:
                    st.write(f"  - \"{pattern['examples'][0]}\"")
                    st.write(f"  - \"{pattern['examples'][1]}\"")
                    st.write(f"  - ... and {len(pattern['examples']) - 2} more")
        
        with st.expander("🔍 Detailed Phantom Annotations"):
            for phantom in validation_results['phantom_annotations']:
                st.write(f"**Text:** {phantom['expected_text']}")
                st.write(f"**Reason:** {', '.join(phantom['phantom_reason'])}")
                st.write(f"**Type:** {phantom['phantom_type']}")
                st.write(f"**Label:** {phantom['label']}")
                st.write("---")
    
    if error_count > phantom_count:
        st.subheader("🔧 Position Errors (Fixable)")
        
        fixable_errors = [e for e in validation_results['errors'] 
                         if e.get('status') in ['position_fixable', 'fuzzy_fixable']]
        unfixable_errors = [e for e in validation_results['errors'] 
                           if e.get('status') == 'unfixable']
        
        if fixable_errors:
            st.success(f"✅ {len(fixable_errors)} errors can be automatically fixed")
            
        if unfixable_errors:
            st.error(f"❌ {len(unfixable_errors)} errors cannot be fixed (likely phantom annotations)")
            
            with st.expander("🔍 Unfixable Errors Details"):
                for error in unfixable_errors[:5]:
                    st.write(f"**Expected:** {error['expected_text']}")
                    st.write(f"**Actually extracted:** {error.get('actual_text', 'N/A')}")
                    st.write(f"**Position:** {error['start_char']}-{error['end_char']}")
                    st.write("---")
                
                if len(unfixable_errors) > 5:
                    st.info(f"... and {len(unfixable_errors) - 5} more unfixable errors")
    
    if validation_results['correct_entities'] == total:
        st.success("✅ All annotations have correct positions!")

def auto_fix_annotations(text, entities, validation_results):
    """
    Automatically fix annotations based on validation results.
    
    Args:
        text (str): Source text
        entities (list): Original entities
        validation_results (dict): Results from enhanced validation
    
    Returns:
        tuple: (fixed_entities, fix_summary)
    """
    fixed_entities = []
    fix_summary = {
        'total_fixed': 0,
        'position_fixes': 0,
        'fuzzy_fixes': 0,
        'phantoms_flagged': 0,
        'unfixable': 0
    }
    
    for entity in entities:
        entity_index = entities.index(entity)
        
        # Find corresponding analysis
        analysis = next((a for a in validation_results['detailed_analysis'] 
                        if a['entity_index'] == entity_index), {})
        
        if analysis.get('status') == 'correct':
            fixed_entities.append(entity)
        elif analysis.get('status') == 'phantom':
            # Flag phantom but keep for user review
            phantom_entity = entity.copy()
            phantom_entity['validation_flag'] = 'PHANTOM'
            phantom_entity['phantom_reason'] = analysis.get('phantom_reason', [])
            fixed_entities.append(phantom_entity)
            fix_summary['phantoms_flagged'] += 1
        elif analysis.get('status') in ['position_fixable', 'fuzzy_fixable']:
            # Fix position
            fixed_entity = entity.copy()
            suggested_pos = analysis.get('suggested_position')
            if suggested_pos:
                fixed_entity['start_char'] = suggested_pos[0]
                fixed_entity['end_char'] = suggested_pos[1]
                fixed_entity['validation_flag'] = 'AUTO_FIXED'
                fixed_entities.append(fixed_entity)
                fix_summary['total_fixed'] += 1
                if analysis.get('status') == 'position_fixable':
                    fix_summary['position_fixes'] += 1
                else:
                    fix_summary['fuzzy_fixes'] += 1
            else:
                # Keep original but flag as unfixable
                unfixable_entity = entity.copy()
                unfixable_entity['validation_flag'] = 'UNFIXABLE'
                fixed_entities.append(unfixable_entity)
                fix_summary['unfixable'] += 1
        else:
            # Keep original but flag as problematic
            problem_entity = entity.copy()
            problem_entity['validation_flag'] = 'NEEDS_REVIEW'
            fixed_entities.append(problem_entity)
            fix_summary['unfixable'] += 1
    
    return fixed_entities, fix_summary
