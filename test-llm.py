import torch
from transformers import AutoTokenizer, GPTJForCausalLM

model = GPTJForCausalLM.from_pretrained("EleutherAI/gpt-j-6B", torch_dtype=torch.float16)
tokenizer = AutoTokenizer.from_pretrained("EleutherAI/gpt-j-6B")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

def generate_text(prompt, max_length=100):
    input_ids = tokenizer.encode(prompt, return_tensors="pt").to(device)
    output = model.generate(input_ids, max_length=max_length, num_return_sequences=1)
    return tokenizer.decode(output[0], skip_special_tokens=True)

def parse_media_filename(filename, prompt):
    full_prompt = f"""
    Filename: {filename}
    Task: {prompt}
    Parsed result:
    """
    response = generate_text(full_prompt, max_length=200)
    return response.split("Parsed result:")[-1].strip()

filename = "Breaking Bad (2008) - S01E01 - Pilot (1080p BluRay x265 Silence).mkv"
prompt = "Extract the show name, season and episode number (e.g. S01E02), and episode name. Return as string in the format: show_name episode_number episode_name.extension"

parsed_result = parse_media_filename(filename, prompt)
print("Parsed filename:", parsed_result)
