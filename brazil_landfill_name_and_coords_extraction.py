# works for a single file, yay!
import pandas as pd
from dotenv import load_dotenv
import os
from openai import OpenAI
import json

_ = load_dotenv(r'C:\Users\andre.scheinwald\OneDrive - RMI\Documents\env files\openapi.env')

#client = OpenAI(api_key=os.getenv('work_account_key'))
client = OpenAI(api_key=os.getenv('key'))

assistant = client.beta.assistants.create(
  name="Document Reader Assistant",
  instructions="""Read the uploaded documents and answer questions about them. Do not use any outside knowledge to answer questions.
                    Cite what page the relevant information is on.""",
  model="gpt-4o-mini",
  tools=[{"type": "file_search"}],
)

# Create a vector store called "Financial Statements"
vector_store = client.beta.vector_stores.create(name="CDM docs")

# Ready the files for upload to OpenAI
#file_paths = [r'C:\Users\andre.scheinwald\Downloads\brazil_test.pdf']
file_paths = [r'C:\Users\andre.scheinwald\Downloads\cdm_files\10257_PDD.pdf']
file_streams = [open(path, "rb") for path in file_paths]
  
file_paths = []
for dirpath, dirnames, filenames in os.walk(r'C:\Users\andre.scheinwald\Downloads\cdm_files'):
    for filename in filenames:
        full_path = os.path.join(dirpath, filename)
        file_paths.append(full_path)

# Use the upload and poll SDK helper to upload the files, add them to the vector store,
# and poll the status of the file batch for completion.
file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
  vector_store_id=vector_store.id, files=file_streams
)

# You can print the status and the file counts of the batch to see the result of this operation.
print(file_batch.status)
print(file_batch.file_counts)

assistant = client.beta.assistants.update(
  assistant_id=assistant.id,
  tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)



# Upload the user provided file to OpenAI
for files in file_paths:
  message_file = client.files.create(
    file=open(files, "rb"), purpose="assistants"
  )

  # Create a thread and attach the file to the message
  thread = client.beta.threads.create(
    messages=[
      {
        "role": "user",
        "content": """Please review the attached file and answer the following questions: What is the landfill name, location (region, city, and country), coordinates, and filename of the uploaded file referenced?
                    Coordinates should be in decimal format with positive or negative values for cardinal direction. Return a response in JSON format.
                    Do not add formatting such as \n or tabs.""",
        # Attach the new file to the message.
        "attachments": [
          { "file_id": message_file.id, "tools": [{"type": "file_search"}] }
        ],
      }
    ]
  )

  # The thread now has a vector store with that file in its tool resources.
  print(thread.tool_resources.file_search)

  # Use the create and poll SDK helper to create a run and poll the status of
  # the run until it's in a terminal state.

  run = client.beta.threads.runs.create_and_poll(
      thread_id=thread.id, assistant_id=assistant.id
  )

  messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

  message_content = messages[0].content[0].text
  annotations = message_content.annotations
  #citations = []
  for index, annotation in enumerate(annotations):
      message_content.value = message_content.value.replace(annotation.text, f"[{index}]")
      if file_citation := getattr(annotation, "file_citation", None):
          cited_file = client.files.retrieve(file_citation.file_id)
          #citations.append(f"[{index}] {cited_file.filename}")

  print(message_content.value)
  #print("\n".join(citations))
  cleaned_response_str = message_content.value.replace('\n', '').replace('  ', '')
  data = json.loads(cleaned_response_str)
  test = []
  test.append(data)

df = pd.json_normalize(data)


vector_stores = client.beta.vector_stores.list()

for store in vector_stores.data:
    vector_store_id = store.id
    print(f"Deleting vector store: {store.name} (ID: {store.id})")
    client.beta.vector_stores.delete(vector_store_id=vector_store_id)



# this WAS working for multiple files. But once again just spits out the same results for 1 file, twice.
import pandas as pd
from dotenv import load_dotenv
import os
from openai import OpenAI
import json

_ = load_dotenv(r'C:\Users\andre.scheinwald\OneDrive - RMI\Documents\env files\openapi.env')

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('key'))

assistant = client.beta.assistants.create(
  name="Document Reader Assistant",
  instructions="""Read the uploaded documents and answer questions about them. Do not use any outside knowledge to answer questions.
                    Cite what page the relevant information is on.""",
  model="gpt-4o-mini",
  tools=[{"type": "file_search"}],
)

# Create a vector store called "Financial Statements"
vector_store = client.beta.vector_stores.create(name="CDM docs")

# Specify the folder to search for files
folder_path = r'C:\Users\andre.scheinwald\Downloads\cdm_files'

# Get the full filenames including directory info
file_paths = []
for dirpath, dirnames, filenames in os.walk(folder_path):
    for filename in filenames:
        full_path = os.path.join(dirpath, filename)
        file_paths.append(full_path)

# Print the full filenames
for file_path in file_paths:
    print(file_path)

# Process files in batches
batch_size = 10  # Adjust the batch size as needed
for i in range(0, len(file_paths), batch_size):
    batch_file_paths = file_paths[i:i + batch_size]
    file_streams = [open(path, "rb") for path in batch_file_paths]

    # Use the upload and poll SDK helper to upload the files, add them to the vector store,
    # and poll the status of the file batch for completion.
    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
      vector_store_id=vector_store.id, files=file_streams
    )

    # You can print the status and the file counts of the batch to see the result of this operation.
    print(file_batch.status)
    print(file_batch.file_counts)

    # Close the file streams after use
    for stream in file_streams:
        stream.close()

assistant = client.beta.assistants.update(
  assistant_id=assistant.id,
  tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)

test = []
# Upload the user provided file to OpenAI
for file_path in file_paths:
  message_file = client.files.create(
    file=open(file_path, "rb"), purpose="assistants"
  )

  print(f'file_path: {file_path}')
  print(f'message_file_id: {message_file.id}')


  # Create a thread and attach the file to the message
  thread = client.beta.threads.create(
    messages=[
      {
        "role": "user",
        "content": """Please review the attached file and answer the following questions: What is the landfill name, location (region, city, and country), coordinates, and filename of the uploaded file referenced?
                    Coordinates should be in decimal format with positive or negative values for cardinal direction. Return a response in JSON format.
                    Do not add formatting such as \n or tabs.""",
        # Attach the new file to the message.
        "attachments": [
          { "file_id": message_file.id, "tools": [{"type": "file_search"}] }
        ],
      }
    ]
  )

  # The thread now has a vector store with that file in its tool resources.
  print(thread.tool_resources.file_search)

  # Use the create and poll SDK helper to create a run and poll the status of
  # the run until it's in a terminal state.

  run = client.beta.threads.runs.create_and_poll(
      thread_id=thread.id, assistant_id=assistant.id
  )

  messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

  message_content = messages[0].content[0].text
  annotations = message_content.annotations

  for index, annotation in enumerate(annotations):
      message_content.value = message_content.value.replace(annotation.text, f"[{index}]")
      if file_citation := getattr(annotation, "file_citation", None):
          cited_file = client.files.retrieve(file_citation.file_id)

  print(message_content.value)

  cleaned_response_str = message_content.value.replace('\n', '').replace('  ', '')
  data = json.loads(cleaned_response_str)
  test.append(data)

df = pd.json_normalize(test)

# List and delete all vector stores
vector_stores = client.beta.vector_stores.list()

for store in vector_stores.data:
    vector_store_id = store.id
    print(f"Deleting vector store: {store.name} (ID: {store.id})")
    client.beta.vector_stores.delete(vector_store_id=vector_store_id)




# this WAS working for multiple files. But once again just spits out the same results for 1 file, twice.
import pandas as pd
from dotenv import load_dotenv
import os
from openai import OpenAI
import json

_ = load_dotenv(r'C:\Users\andre.scheinwald\OneDrive - RMI\Documents\env files\openapi.env')

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('key'))

assistant = client.beta.assistants.create(
  name="Document Reader Assistant",
  instructions="""Read the uploaded documents and answer questions about them. Do not use any outside knowledge to answer questions.
                    Cite what page the relevant information is on.""",
  model="gpt-4o-mini",
  tools=[{"type": "file_search"}],
)

# Create a vector store called "Financial Statements"
#vector_store = client.beta.vector_stores.create(name="CDM docs")

# Specify the folder to search for files
#folder_path = r'C:\Users\andre.scheinwald\Downloads\cdm_files'
folder_path = r'C:\Users\andre.scheinwald\OneDrive - RMI\Documents\Python Scripts\cdm_scraping\downloads'

# Get the full filenames including directory info
file_paths = []
for dirpath, dirnames, filenames in os.walk(folder_path):
    for filename in filenames:
        full_path = os.path.join(dirpath, filename)
        file_paths.append(full_path)

# Print the full filenames
for file_path in file_paths:
    print(file_path)

test = []
errors = []
# Upload the user provided file to OpenAI
for file_path in file_paths:
  message_file = client.files.create(
    file=open(file_path, "rb"), purpose="assistants"
  )

  print(f'file_path: {file_path}')
  print(f'message_file_id: {message_file.id}')


  # Create a thread and attach the file to the message
  thread = client.beta.threads.create(
    messages=[
      {
        "role": "user",
        "content": """Please review all files and answer the following questions for every single file: What is the landfill name, location (region, city, and country),
        gas_capture (True or False), gas_flare (True or False), gas_to_energy_project (True or False, coordinates, project title, and filename of the uploaded file referenced?
                    Coordinates should be in decimal format with positive or negative values for cardinal direction. Return a response in JSON format.
                    Do not add formatting such as \n or tabs. Name each json response 'landfills'. Do not use any other name.
                    Do not include any text outside the json response. This includes coding markup.
                    The format should look like this: {'landfills': [{'landfill_name': 'Dois Arcos Landfill',
   'location': {'region': 'Rio de Janeiro State',
    'city': 'São Pedro da Aldeia',
    'country': 'Brazil'},
   'gas_capture': True,
   'gas_flare': True,
   'gas_to_energy_project': True,
   'coordinates': {'latitude': -22.82601389, 'longitude': -42.05100556},
   'project_title': 'Dois Arcos Landfill Gas Project Activity',
   'filename': '10257_PDD.pdf'}]}""",
        # Attach the new file to the message.
        "attachments": [
          { "file_id": message_file.id, "tools": [{"type": "file_search"}] }
        ],
      }
    ]
  )

  # The thread now has a vector store with that file in its tool resources.
  print(thread.tool_resources.file_search)

  # Use the create and poll SDK helper to create a run and poll the status of
  # the run until it's in a terminal state.

  run = client.beta.threads.runs.create_and_poll(
      thread_id=thread.id, assistant_id=assistant.id
  )

  messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

  message_content = messages[0].content[0].text
  annotations = message_content.annotations

  for index, annotation in enumerate(annotations):
      message_content.value = message_content.value.replace(annotation.text, f"[{index}]")
      if file_citation := getattr(annotation, "file_citation", None):
          cited_file = client.files.retrieve(file_citation.file_id)

  print(message_content.value)

  cleaned_response_str = message_content.value.replace('\n', '').replace('  ', '').replace('json', '').replace("```", "")

  try:
    data = json.loads(cleaned_response_str)
    test.append(data)
  except json.JSONDecodeError as e:
      print(f"JSONDecodeError: {e}")
      print(f"Problematic JSON string: {cleaned_response_str}")
      errors.append(cleaned_response_str)

# Ensure 'landfills' is always a list in the 'test' list
for entry in test:
    if 'landfills' in entry and isinstance(entry['landfills'], dict):
        entry['landfills'] = [entry['landfills']]


df = pd.json_normalize(test, record_path = 'landfills')

fixed_errors = []
for entry in errors:
    # Replace single quotes with double quotes and fix boolean values
    entry = entry.replace("'", '"').replace('True', 'true').replace('False', 'false')
    fixed_entries = json.loads(entry)
    fixed_errors.append(fixed_entries)

df2 = pd.json_normalize(fixed_errors, record_path='landfills')

df3 = pd.concat([df, df2], ignore_index=True)

df3.to_csv(r'C:\Users\andre.scheinwald\OneDrive - RMI\Documents\Python Scripts\cdm_scraping\brazil_landfill_name_and_coords_extraction.csv', index=False)

# List and delete all vector stores
vector_stores = client.beta.vector_stores.list()

while vector_stores.has_more:
  for store in vector_stores.data:
    vector_store_id = store.id
    print(f"Deleting vector store: {store.name} (ID: {store.id})")
    client.beta.vector_stores.delete(vector_store_id=vector_store_id)
  vector_stores = client.beta.vector_stores.list()