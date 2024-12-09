import json
import glob

def merge_json_files(file_patterns):
    merged_data = []
    
    for pattern, source in file_patterns:
        for file_path in glob.glob(pattern):
            with open(file_path, 'r') as file:
                data = json.load(file)
                for item in data:
                    item['source'] = source
                merged_data.extend(data)
    
    return merged_data

# Define file patterns and their sources
file_patterns = [
    ('json_events/actividades.json', 'actividad'),
    ('json_events/conferencias.json', 'conferencia'),
    ('json_events/exposiciones.json', 'exhibicion'),
    ('json_events/planetario.json', 'planetario')
]

# Merge the files
merged_data = merge_json_files(file_patterns)

# Write the merged data to a new JSON file
with open('merged_events.json', 'w') as outfile:
    json.dump(merged_data, outfile, indent=2)

print("Merged data written to 'merged_events.json'")