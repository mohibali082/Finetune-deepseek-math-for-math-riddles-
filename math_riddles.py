# -*- coding: utf-8 -*-
"""math_riddles.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1o_A2s5fahhTJx1M22F69esRTOJWhNodw
"""

!pip install transformers datasets torch
!pip install unsloth
!pip install peft

import json
import torch
from transformers import AutoTokenizer, Trainer, TrainingArguments
from datasets import Dataset
from huggingface_hub import login
from unsloth import FastLanguageModel
from peft import LoraConfig, get_peft_model

# Log in to Hugging Face Hub to save the fine-tuned model
login()

from datasets import Dataset

# Dataset: Incorrect math memes and their corrected versions
dataset = [
    {"riddle": "8 ÷ 2(2+2) = 1?", "solution": "8 ÷ 2 × (4) = 4 × 4 = 16"},
    {"riddle": "52 = 10?", "solution": "5² = 25"},
    {"riddle": "6 ÷ 2(1+2) = 1?", "solution": "6 ÷ 2 × (3) = 3 × 3 = 9"},
    {"riddle": "0.999... = 0?", "solution": "0.999... = 1 (Mathematical proof: Limit approach)"},
    {"riddle": "2 + 3 × 4 = 20?", "solution": "2 + (3 × 4) = 2 + 12 = 14"},
    {"riddle": "100 - 50 ÷ 2 = 25?", "solution": "100 - (50 ÷ 2) = 100 - 25 = 75"},
    {"riddle": "1 + 1 = 3 (common meme)?", "solution": "1 + 1 = 2 (Basic arithmetic)"},
    {"riddle": "10 ÷ 5 ÷ 2 = 1?", "solution": "(10 ÷ 5) ÷ 2 = 2 ÷ 2 = 1"},
    {"riddle": "25% of 200 = 100?", "solution": "25% of 200 = (25/100) × 200 = 50"},
    {"riddle": "1/2 + 1/2 = 1/4?", "solution": "1/2 + 1/2 = 1"},
    {"riddle": "√-1 = 1?", "solution": "√-1 = i (Imaginary unit in complex numbers)"},
    {"riddle": "10² = 20?", "solution": "10² = 100"},
    {"riddle": "9 - 3 ÷ 1/3 + 1 = 1?", "solution": "9 - 3 ÷ (1/3) + 1 = 9 - 9 + 1 = 1"},
    {"riddle": "2⁴ ÷ 2² = 8?", "solution": "2⁴ ÷ 2² = 16 ÷ 4 = 4"},
    {"riddle": "3(2+2) = 3×2+2?", "solution": "3(2+2) = 3×4 = 12 (not 3×2+2 = 6+2 = 8)"},
    {"riddle": "7 + 7 ÷ 7 + 7 × 7 - 7 = 0?", "solution": "7 + (7 ÷ 7) + (7 × 7) - 7 = 7 + 1 + 49 - 7 = 50"},
    {"riddle": "4 ÷ 2(2+2) = 2?", "solution": "4 ÷ 2 × (4) = 2 × 4 = 8"},
    {"riddle": "50 - 10 × 5 + 10 = 200?", "solution": "50 - (10 × 5) + 10 = 50 - 50 + 10 = 10"},
    {"riddle": "√4 + √4 = 4?", "solution": "√4 + √4 = 2 + 2 = 4"},
    {"riddle": "60 ÷ 5(7 - 5) = 30?", "solution": "60 ÷ 5 × (7 - 5) = 60 ÷ 5 × 2 = 12 × 2 = 24"},
]

# Convert the dataset into a Hugging Face Dataset
dataset = Dataset.from_dict({
    "riddle": [item["riddle"] for item in dataset],
    "solution": [item["solution"] for item in dataset]
})

# Load the pre-trained model and tokenizer with Unsloth
model_name = "deepseek-ai/deepseek-math-7b-instruct"  # Replace with the correct model name
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=model_name,
    max_seq_length=512,
    dtype=None,
    load_in_4bit=True,
)

# Tokenize the riddle dataset
def preprocess_function(examples):
    # Tokenize the riddles (inputs)
    model_inputs = tokenizer(examples["riddle"], truncation=True, padding="max_length", max_length=512)

    # Tokenize the solutions (labels)
    labels = tokenizer(examples["solution"], truncation=True, padding="max_length", max_length=512)

    # Add the labels to the model inputs
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

tokenized_dataset = more_dataset.map(preprocess_function, batched=True)

# Check the first example
print(tokenized_dataset[0])

# Decode the input IDs to verify the tokenization
decoded_input = tokenizer.decode(tokenized_dataset[0]["input_ids"])
decoded_labels = tokenizer.decode(tokenized_dataset[0]["labels"])

print(f"Decoded input: {decoded_input}")
print(f"Decoded labels: {decoded_labels}")

# Define training arguments
training_args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    num_train_epochs=10,
    weight_decay=0.01,
    save_total_limit=2,
    save_steps=500,
    logging_dir="./logs",
    logging_steps=10,
    fp16=True,  # Enable mixed precision training to save memory
)

# Define training arguments
training_args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    num_train_epochs=50,
    weight_decay=0.01,
    save_total_limit=2,
    save_steps=500,
    logging_dir="./logs",
    logging_steps=10,
    fp16=True,  # Enable mixed precision training to save memory
)

!pip install peft

# Define LoRA configuration for PEFT
lora_config = LoraConfig(
    r=16,  # Rank of the low-rank adaptation
    lora_alpha=32,  # Scaling factor
    target_modules=["q_proj", "v_proj"],  # Target modules for LoRA
    lora_dropout=0.05,  # Dropout for LoRA
    bias="none",  # No bias
    task_type="SEQ_2_SEQ_LM",  # Task type for sequence-to-sequence models
)

# Wrap the model with PEFT
model = get_peft_model(model, lora_config)

# Define the Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    eval_dataset=tokenized_dataset,
)

trainer.train()

# Save the model and tokenizer locally
model.save_pretrained("./fine-tuned-deepseek-math")
tokenizer.save_pretrained("./fine-tuned-deepseek-math")

prompt = "Riddle: What number becomes zero when you subtract 15 from half of it ?\nSolution:"

# Tokenize the prompt
inputs = tokenizer(prompt, return_tensors="pt")  # `return_tensors="pt"` returns PyTorch tensors

# Move inputs to the same device as the model
inputs = {key: value.to("cuda") for key, value in inputs.items()}

# Generate a response
outputs = model.generate(**inputs, max_length=50)  # `max_length` controls the maximum length of the output

response = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(response)