import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
import logging 


from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder
from sklearn.utils.class_weight import compute_class_weight
from sklearn.preprocessing import LabelBinarizer
from scipy.special import softmax
import numpy as np

from torch import nn


# os.environ["TOKENIZERS_PARALLELISM"] = "false"  # This tells Hugging Face: “Don’t use parallel tokenization — avoid possible deadlocks.”

from torch.utils.data import Dataset, DataLoader
import torch

from transformers import TrainingArguments, Trainer, AutoModelForSequenceClassification, AutoModel, AutoTokenizer, AutoConfig


from logging import getLogger
logger = getLogger(__name__)

import nltk


def tokenize(texts, model_path):
    logger.info('create tokenizer & load model')
    # tokenization after train test split to prevent data leakage
    #added use_fast=False to prevent tokenization error (might happen when using fast tokenization)
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    return tokenizer(
        texts,
        padding="max_length", #ensures that all tokenized sequences are padded to the same length, padding adds special tokens to shorter sequeces so they match the maximum length
        truncation=True, #if sequence exceeds max, it will be trucated
        max_length=512, #for most transformer models, 512 is a common limit for maximum length
        return_tensors="pt" #converts the output to pytorch tensors
    )




#object oriented programming (class is the object), with class you can do different things, such as calling functions
class TextDataset(Dataset):  # Inherits from PyTorch's Dataset class
    def __init__(self, encodings, labels):
        self.input_ids = encodings['input_ids']       # Token IDs from tokenizer
        self.attention_mask = encodings['attention_mask']  # Mask for padding
        self.labels = torch.tensor(labels)  # Convert labels to tensors
    def __getitem__(self, idx):
        return {
            'input_ids': self.input_ids[idx],       # Token IDs for one sample
            'attention_mask': self.attention_mask[idx],  # Mask for one sample
            'labels': self.labels[idx]              # Label for one sample
        }
    def __len__(self):
        return len(self.labels)  # Total number of samples


def get_encode_tokenize_data(problem, path, model_path):
    logger = getLogger(__name__)

    logger.info("Loading data...")
    df = pd.read_csv(path)
    
    # Determine target column based on problem type
    target_column = "two_class_target" if problem == "binary" else "logical_fallacies"
    y = df[target_column]
    
    X = df[["dataset", "text"]]
    logger.info("Train test split, test-size 0.3")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, stratify=y, test_size=0.30, random_state=42
    )

    logging.info("Create encoded dataframes")
    encoded_train_dataset = X_train.copy()
    encoded_test_dataset = X_test.copy()
    
    encoded_train_dataset[target_column] = y_train
    encoded_test_dataset[target_column] = y_test
    
    X_train = X_train["text"]
    X_test = X_test["text"]

    logging.info("Encode the label column")
    le = LabelEncoder()
    y_train = le.fit_transform(y_train)
    y_test = le.transform(y_test)

    logging.info("Tokenize")
    train_encodings = tokenize(X_train.to_list(), model_path)
    test_encodings = tokenize(X_test.to_list(), model_path)

    logging.info("Create TextDatasets (train & test)")
    train_dataset = TextDataset(train_encodings, y_train)
    test_dataset = TextDataset(test_encodings, y_test)

    return train_dataset, test_dataset, encoded_train_dataset, encoded_test_dataset, le
class WeightedLossTrainer(Trainer):
    def __init__(self, class_weights=None, **kwargs):
        super().__init__(**kwargs)
        self.class_weights = class_weights
        if self.class_weights is not None:
            # Move weights to device after model initialization
            self._move_weights_to_device()
    
    def _move_weights_to_device(self):
        self.class_weights = self.class_weights.to(self.model.device)

    def compute_loss(
        self, 
        model, 
        inputs, 
        return_outputs=False, 
        num_items_in_batch=None  # Add this parameter
    ):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits
        loss_fct = nn.CrossEntropyLoss(weight=self.class_weights)
        loss = loss_fct(logits.view(-1, self.model.config.num_labels), 
                       labels.view(-1))
        return (loss, outputs) if return_outputs else loss
        

def createTrainer(
    model,
    train_dataset,
    test_dataset,
    output_dir,
    y_train, 
    class_weight=False, 
    epochs=3, 
    learning_rate=5e-5, 
    weight_decay = 0, 
    train_batch_size = 4, 
    eval_batch_size=8
    ):
    logging.info('defining training arguments')
    training_args = TrainingArguments(
            output_dir=output_dir, # to save results and checkpoints
            num_train_epochs=epochs,
            per_device_train_batch_size=train_batch_size, #small to save memory
            per_device_eval_batch_size=eval_batch_size, #small to save memory
            learning_rate=learning_rate, #standard for deberta; maybe try 6e-6
            weight_decay=weight_decay,
            eval_strategy="epoch",
            logging_steps=50,
            save_strategy="epoch",
            load_best_model_at_end=True,
            report_to= [] #set to empty to prevent the mlflow from logging too many parameters
        )

    computed_class_weights = compute_class_weight(class_weight='balanced', classes=np.unique(y_train), y=y_train)
    # Convert class weights to tensor
    computed_class_weights_tensor = torch.tensor(computed_class_weights, dtype=torch.float32)

    def compute_metrics(p):
        preds = p.predictions.argmax(-1)
        return {'accuracy': accuracy_score(p.label_ids, preds)}

    if class_weight==False:
        logging.info('get normal trainer')
        return Trainer(
                model=model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=test_dataset,
                compute_metrics=compute_metrics
            )
    else:
        logging.info('get weighted loss trainer')
        return WeightedLossTrainer(
                model=model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=test_dataset,
                compute_metrics=compute_metrics,
                class_weights=computed_class_weights_tensor
            )

def get_eval_metrics(output, le):
    logger.info('get evaluation metrics')

    y_pred = np.argmax(output.predictions, axis=1)
    y_true = output.label_ids
    logits = output.predictions
    proba = softmax(logits, axis=1)

    logger.info('classification_report')
    classification_report_dict = classification_report(y_true, y_pred, target_names=le.classes_, output_dict=True)
    print(classification_report(y_true, y_pred, target_names=le.classes_))

    logger.info('confusion_matrix')
    cm = (confusion_matrix(y_true, y_pred))
    # print(cm)

    labels = sorted(set(y_true) | set(y_pred))

    logger.info('heatmap')
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Greens', xticklabels=le.classes_, yticklabels=le.classes_)
    plt.title("Confusion Matrix Heatmap")
    plt.xlabel("Predicted Labels")
    plt.ylabel("True Labels")
    plt.show()

    logger.info('brier score')
    # 1. One-hot encode the true labels (y_test)
    lb = LabelBinarizer()
    y_true_onehot = lb.fit_transform(y_true)  # Shape: (n_samples, n_classes)

    # 2. Compute Brier score for multiclass
    brier_score = np.mean(np.sum((proba - y_true_onehot) ** 2, axis=1))
    print("Multiclass Brier score:", brier_score)

    return classification_report_dict, brier_score


def get_error_analysis(output, encoded_df):
    y_pred = np.argmax(output.predictions, axis=1)

    y_true = output.label_ids

    encoded_df = encoded_df.reset_index()

    text = []
    dataset  = []
    true_label = []
    pred_label = []

    for i, (true, pred) in enumerate(zip(y_true, y_pred)):
        if true != pred:
            text.append(encoded_df['text'][i])
            dataset.append(encoded_df['dataset'][i])
            true_label.append(true)
            pred_label.append(pred)
            
    df = pd.DataFrame({'text': text, 'dataset': dataset, 'true_label': true_label, 'pred_label': pred_label})
    df['text_char_length'] = df['text'].map(lambda x : len(x))
    df['text_word_length'] = df['text'].str.split().str.len()
    return df

def print_error_df (df):
    for i, row in df.iterrows():
        print(f"Example {i}:")
        print(f"Text: {row['text']}")
        print(f"True Label: {row['true_label']}, Predicted Label: {row['pred_label']}")





#functions for baseline models

def get_preprocess_data(data_path):
    df = pd.read_csv(data_path, index_col=0)

    # Change text to lower cases
    df['text'] = df['text'].apply(lambda x: x.lower())
    return df

def lemmatize_text(text):
    lemmatize = nltk.WordNetLemmatizer()
    return ' '.join([lemmatize.lemmatize(word) for word in text.split()])

def get_lemmatized_data(df):
    df['text'] = df['text'].apply(lemmatize_text)
    return df

def get_metrics(y_true, y_pred):
    logger.info('classification_report')
    classification_report_dict = classification_report(y_true, y_pred, output_dict=True)
    print(classification_report(y_true, y_pred))

    logger.info('confusion_matrix')
    cm = (confusion_matrix(y_true, y_pred))
    print(cm)

    labels = sorted(set(y_true) | set(y_pred))

    logger.info('heatmap')
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Greens', xticklabels=labels, yticklabels=labels)
    plt.title("Confusion Matrix Heatmap")
    plt.xlabel("Predicted Labels")
    plt.ylabel("True Labels")
    plt.show()

    return classification_report_dict
  