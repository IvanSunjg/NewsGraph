"""
Module Description: 
"""
import functools
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from fairseq.data.data_utils import collate_tokens
import torch
from torch.utils.data import Dataset, DataLoader
import torch
from tqdm import tqdm

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def init_model():
    """
    Initialise the NLI model.
    """
    nli_tokenizer = AutoTokenizer.from_pretrained('roberta-large-mnli')
    nli_model = AutoModelForSequenceClassification.from_pretrained('roberta-large-mnli')
    if device is not None:
        nli_model.to(device)
    return nli_tokenizer, nli_model

# pylint: disable=missing-class-docstring
class NLIDataset(Dataset):
    def __init__(self, nli_data):
        super().__init__()
        self.data = nli_data

    def __getitem__(self, idx):
        return self.data[idx]

    def __len__(self):
        return len(self.data)

def collate_nli(xs, tokenizer):
    """
    Collect and Combine
    """
    result = []
    for p,h in xs:
        result.append(
            tokenizer.encode(
                f"{p}", f"{h}",
                return_tensors='pt',
                truncation='only_first',
                padding='max_length',
                max_length=128
            )
        )
    result = torch.cat(result, dim=0)
    return result

def classify_nli(pairs, nli_tokenizer, nli_model):
    """
    Classify the NLI
    """
    dataset = NLIDataset(pairs)
    collator = functools.partial(collate_nli, tokenizer=nli_tokenizer)
    dataloader = DataLoader(dataset, collate_fn=collator, batch_size=8, shuffle=False)
    logit_results = []
    with torch.no_grad():
        for b in tqdm(dataloader):
            inputs = b
            outputs = nli_model(inputs.to(device))[0].cpu()
            logit_results.append(outputs)
    combined_results = torch.cat(logit_results, dim=0)
    class_probability = torch.nn.Softmax(dim=1)(combined_results)
    return class_probability
