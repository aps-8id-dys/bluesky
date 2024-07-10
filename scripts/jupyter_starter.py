# ~/my_repo/create_and_open_notebook.py
import os
import nbformat as nbf
from jupyter import notebookapp
import webbrowser

# Define the notebook content
notebook_content = nbf.v4.new_notebook()
notebook_content.cells.append(nbf.v4.new_code_cell("%run bluesky_interactive_startup.ipy"))

# Write the notebook to a file
notebook_path = os.path.expanduser("~/my_repo/auto_run_notebook.ipynb")
with open(notebook_path, "w") as f:
    nbf.write(notebook_content, f)

# Start Jupyter Lab
os.system(f"jupyter lab {notebook_path}")

# Open the notebook in the browser
servers = list(notebookapp.list_running_servers())
if servers:
    server = servers[0]
    notebook_url = server['url'] + 'lab/tree/' + notebook_path
    webbrowser.open(notebook_url)
