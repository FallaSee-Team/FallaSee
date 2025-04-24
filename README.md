# FallaSee
## Detecting Logical Fallacies

**Authors:**

[Maren Bormann](https://www.linkedin.com/in/maren-bormann/), [Aylin Hanne](https://www.linkedin.com/in/aylin-hanne/), [Parya Tavaloki-Tehrani](https://www.linkedin.com/in/parya-tavakoli-tehrani/),
[Katharina Baumgartner](https://www.linkedin.com/in/katharina-baumgartner-b80057261/)

## About the Project

This project began as part of our Capstone Phase at [neuefische GmbH](https://www.neuefische.de). Our idea was to train an NLP Model to detect logical fallacies in sentences and build a web application where users can enter their own sentences.

Logical fallacies are a common phenomenon and are also associated with the spread of disinformation. A logical fallacy is a shortcut that sounds clever but doesn't really make sense when you look closer. It is an error in reasoning that weakens an argument. 
Being aware of logical fallacies is a good idea, but sometimes tricky. Even for AI! The AI needs to understand the underlying logical structure of the argument. 

We created a web application that can detect 5 common logical fallacies in a sentence. It also explains the different fallacies and provides a small game to beat the AI at recognising logical fallacies.


### Datasets Sources
We have merged our dataset from the following datasets:
1) [Jin et al. (2022)](https://arxiv.org/pdf/2202.13758). Dataset:
[LogicClimate](https://github.com/causalNLP/logical-fallacy/tree/main/data) 

2) Midhun Kandan. *Logical Fallacy Classification*. 2004. Dataset: [Hugging Face Dataset](https://huggingface.co/datasets/MidhunKanadan/logical-fallacy-classification)

3) [Yeh et al. (2024)](https://arxiv.org/pdf/2410.03457v1). Dataset:
[CoCoLoFa](https://github.com/Crowd-AI-Lab/cocolofa) 

4) [Chaves et al. (2025)](https://hal.science/hal-04834405/document). Dataset:
[FALCON](https://github.com/m-chaves/falcon-fallacy-classification) 

5) [Alhindi et al. (2022)](https://aclanthology.org/2022.emnlp-main.560.pdf). Dataset:
[Datasets](https://github.com/Tariq60/fallacy-detection) 

6) [Helwe et al. (2024)](https://arxiv.org/pdf/2311.09761). Dataset:
[MAFALDA](https://github.com/ChadiHelwe/MAFALDA) 

7) [Goffredo et al. (2023)](https://aclanthology.org/2023.emnlp-main.684.pdf). Dataset:
[ElecDeb60to20](https://github.com/pierpaologoffredo/ElecDeb60to20) 


### Categories of Logical Fallacies
After cleaning the data, we trained our model on the five most common fallacies present in the dataset, as well as on sentences that do not contain any logical fallacies.

Categories used for training:

| Category  |  Definition |
|---|---|
| Ad Hominem  |  This fallacy occurs when the speaker is attacking the other person or some aspect of them rather than addressing the argument itself. |
|Appeal to Authority | This fallacy occurs when an argument relies on the opinion or endorsement of an authority figure who may not have relevant expertise or whose expertise is questionable.| 
| Appeal to Emotion | This fallacy occurs when an emotion is used to support an argument, such as pity, fear, anger, etc..  |
| False Dilemma | This fallacy occurs when only two options are presented in an argument, even though more options may exist. A case of "either this or that".|
|None | There are no fallacies in the text.|
| Slippery Slope | This fallacy occurs when someone argues that a event will trigger a series of events that lead to an extreme outcome without demonstrating any causal connections between the events.|

<br>

*Please note*: The definitions of the fallacies were taken from the research papers cited above or adjusted by us as needed.


### Model Evaluation

After training and fine-tuning different models, we got the following results:

| Model        | Macro F1 |
|------------|----------|
Logistic Regression | 0.65 |
DeepSeek | 0.53 |
DistilBERT | 0.71 |
Deberta  | 0.76  |

Our model used in the webapp is Deberta, you can find [here](https://huggingface.co/kathixx/fallacy-deberta-model).


### Web Application

The Webapp has been build using Flask and Vue.js.  It only runs locally at the moment.


## Repo Structure:
- **backend**
    - **additional**: additional files, which where not used in the final product but may be useful, e. g. build pipelines with different models
    - **data**: folder created to store the datasets, which will be created in the eda notebooks
    - **eda**: cleaning different datasets, combining datasets and creating final datasets to train, includes also notebooks for plots and wordclouds
    - **modeling**: main folder with files for different models: training, testing, evaluating
    - **model**: folder to store models locally
    - **app.py**: main flask file, which handels the incoming requestes, predicts the inputs and send the result to the frontend
- **frontend**: Vue.js App
- **research**: Notes about the different models we used

## Run

### Backend
_in your backend folder, in different terminal tabs_

**1. Flask App:**
```bash
source .venv/bin/activate
python app.py # should run on http://127.0.0.1:5000
```

**2. for training: MLFlow:**
```bash
source .venv/bin/activate
mlflow ui --port 5001 #should run on http://127.0.0.1:5001
```



<!-- **3. Ruff:** _(optional)_
```bash
source .venv/bin/activate
ruff check --watch
```

**more helpful commands from ruff:**
- `ruff rule F821`: more detailed explanation about the error message
- `ruff check --fix`: fix all errors, whith a fix-flag [*]
- `ruff format`: format the files -->

### Frontend
_in your frontend folder, in a new terminal tab_

**1. VueApp**
```bash
npm run dev # app should run on http://localhost:5173/
```


<!-- 

## Initial Setup

### Backend
_in the backend folder_


**1. Virtuell Environment, Install requirements**

```BASH
pyenv local 3.11.3
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```
<!-- 

**2. MLFlow**

create a `mlflow_uri` file in the backend folder

```BASH
echo http://127.0.0.1:5001/ > .mlflow_uri
```

Handle errors:

```bash
# MLFlow server already running
pkill -f gunicorn
``` 
<!-- 
### Frontend
_everything will be installed globally, it's not importend in which folder you're right now_

**1. Node & NPM**: check if you have already node and npm installed

```bash
node -v # v23.7.0
npm -v # 11.2.0

# update if necessary
npm install -g npm@11.2.0
```
**2. VueCLI & Vite**
```bash
npm install -g @vue/cli
npm install vite
```

**3. Axios**
```bash
npm install axios
```
 --> 
