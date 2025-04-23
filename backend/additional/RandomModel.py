from logging import getLogger
import random 
import warnings
import mlflow
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix



from modeling.config import TRACKING_URI, EXPERIMENT_NAME

warnings.filterwarnings("ignore")
logger = getLogger(__name__)

DATA_PATH = "data/data_dropped_duplicates_small.csv"

def get_data():
    logger.info("Getting the data")
    # load the data
    df = pd.read_csv(DATA_PATH)

    # define target and features 
    y = df["logical_fallacies"]
    X = df["text"]

    # splitting into train and test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.30, random_state=42
    )

    return X_train, X_test, y_train, y_test


def get_metrics(y_true, y_pred):
    logger.info('classification_report')
    classification_report_dict = classification_report(y_true, y_pred, output_dict=True)
    print(classification_report(y_true, y_pred))

    logger.info('confusion_matrix')
    print(confusion_matrix(y_true, y_pred))

    return classification_report_dict


def log_metrics(cr, split):

    for key, value in cr.items():
        if (key == "accuracy"):
                # print(f"{split}_{key}", round(value,2))
                mlflow.log_metric(f"{split}_{key}", value)
        else:
            for metric in value:
                mlflow.log_metric(f"{split}_{key}_{metric}", value.get(metric))
                # print(f"{split}_{key}_{metric}", round(value.get(metri


def run_training():
    logger.info("Getting the data")
    X_train, X_test, y_train, y_test = get_data()

    logger.info("Training baseline model and tracking with MLFlow")
    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)

    logger.info("Running the baseline model")
    with mlflow.start_run():
        # predict y randomly 
        y_train_list = y_train.tolist()
        y_train_pred = random.choices(y_train_list, k=len(y_train))
        y_test_pred = random.choices(y_train_list, k=len(y_test))

        # in mlFlow a tag has a name (like 'modelX') and a corresponding value (here: true).
        mlflow.set_tag("mlflow.runName", "baseline_model")
        mlflow.set_tag("baseline_model", "True")

        logger.info("Evaluating the baseline model: Train dataset")
        classification_report_train = get_metrics(y_train, y_train_pred)
        log_metrics(classification_report_train, "train")
        
        logger.info("Evaluating the baseline model: Test dataset")
        classification_report_test = get_metrics(y_test, y_test_pred)
        log_metrics(classification_report_train, "test")


if __name__ == "__main__":
    import logging

    logger = logging.getLogger()
    logging.basicConfig(format="%(asctime)s: %(message)s")
    logging.getLogger("pyhive").setLevel(logging.CRITICAL)  # avoid excessive logs
    logger.setLevel(logging.INFO)

    run_training()