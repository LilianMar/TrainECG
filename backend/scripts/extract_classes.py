import json

# Read the notebook
notebook_path = 'backend/scripts/Voting_final.ipynb'
with open(notebook_path, 'r') as f:
    notebook = json.load(f)

# Extract the code cell
if notebook['cells']:
    cell = notebook['cells'][0]
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source'])
        lines = source.split('\n')
        
        # Find all class definitions
        classes_to_extract = [
            'AttentionLayer',
            'SpatialAttentionLayer',
            'SimpleECGModel',
            'ImprovedCNNModel',
            'LSTMWithAttentionModel',
            'HybridCNNLSTMWithAttentionModel',
            'ResNet50WithSpatialAttention'
        ]
        
        class_locations = {}
        
        # Find locations
        for class_name in classes_to_extract:
            for i, line in enumerate(lines):
                if f'class {class_name}' in line:
                    class_locations[class_name] = i
                    print(f"Found {class_name} at line {i+1}")
                    break
        
        # Extract each class
        print("\n" + "="*80)
        print("EXTRACTING CLASSES:")
        print("="*80 + "\n")
        
        for class_name in classes_to_extract:
            if class_name not in class_locations:
                print(f"WARNING: {class_name} not found\n")
                continue
            
            start_idx = class_locations[class_name]
            indent_level = len(lines[start_idx]) - len(lines[start_idx].lstrip())
            
            # Find the end of the class
            end_idx = len(lines)
            for i in range(start_idx + 1, len(lines)):
                current_line = lines[i]
                if current_line.strip() == '':
                    continue
                current_indent = len(current_line) - len(current_line.lstrip())
                # Check if we've hit another top-level definition
                if current_indent == indent_level and (current_line.strip().startswith('class ') or (current_line.strip().startswith('def ') and indent_level == 0)):
                    end_idx = i
                    break
            
            class_code = '\n'.join(lines[start_idx:end_idx]).rstrip()
            print(f"# ============= {class_name} =============\n")
            print(class_code)
            print("\n\n")
