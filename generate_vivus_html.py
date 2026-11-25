import os
import argparse

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Vivus SVG Animation Grid</title>
  <script src="https://cdn.jsdelivr.net/npm/vivus@0.4.4/dist/vivus.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/vivus@0.4.4/src/pathformer.js"></script>
  <script src="/js/vivusObserver.js"></script>
  <style>
    body {{
      background: grey;
      color: white;
      font-family: sans-serif;
      margin: 0;
      padding: 0;
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
    }}
    .itemWrapper {{
        display: flex;
        flex-direction: column;
        ustify-content: center;
        align-items: center;
    }}
    .svgContainer {{
      width: 300px;
      max-width: 100%;
      margin: 20px;
      border: 2px solid white;
      padding: 10px;
      text-align: center;
    }}
    h2 {{
      color: white;
      font-size: 18px;
      margin-bottom: 10px;
      text-align: center;
    }}
    svg {{
      width: 100%;
      height: auto;
      display: block;
    }}
  </style>
</head>
<body>
{svg_sections}

<script>
  document.addEventListener('DOMContentLoaded', function() {{
    const shapes = [
{shape_objects}
    ];
    initGlobalStaggerObserver(shapes, 0.5, true);
  }});
</script>
</body>
</html>
"""

SVG_SECTION_TEMPLATE = """
  <div class="itemWrapper">
    <h2>{file_name}</h2>
    <div id="{container_id}" class="svgContainer">
    </div>
  </div>
"""

SHAPE_OBJECT_TEMPLATE = """      {{
        containerId: '{container_id}',
        svgUrl: '{svg_path}',
        vivusOptions: {{ type: 'scenario-sync', duration: 36 }},
        vivusInstance: null,
        isAnimated: false
      }},"""

def generate_html(svgs, output_file):
    svg_sections = ""
    shape_objects = ""
    
    for svg in svgs:
        file_name = os.path.basename(svg)
        container_id = os.path.splitext(file_name)[0] + "Container"
        
        # Add the SVG section and shape object data
        svg_sections += SVG_SECTION_TEMPLATE.format(container_id=container_id, file_name=file_name)
        shape_objects += SHAPE_OBJECT_TEMPLATE.format(container_id=container_id, svg_path=svg) + "\n"
    
    # Create the final HTML by filling the placeholders
    final_html = HTML_TEMPLATE.format(svg_sections=svg_sections.strip(), shape_objects=shape_objects.strip())
    
    # Write the HTML file
    with open(output_file, 'w') as f:
        f.write(final_html)
    print(f"HTML generated at {output_file}")

def find_svgs(directory):
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.svg')]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Vivus SVG animation page.")
    parser.add_argument('--svg-dir', required=True, help="Directory containing SVG files.")
    parser.add_argument('--output', required=True, help="Output HTML file path.")

    args = parser.parse_args()

    svg_files = find_svgs(args.svg_dir)
    if not svg_files:
        print("No SVG files found in the specified directory.")
    else:
        generate_html(svg_files, args.output)