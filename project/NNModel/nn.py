"""Module docstring"""
import json

import keras
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import OneHotEncoder, LabelEncoder


class NLPModel:
    """
    Keras neural network model, created to being aply for online learning.
    To create model with main model branch:
    NLP_model("./model_configs/config.json","./model_weights/model1_weights.hdf5").
    To train: model.train(text,emotion)
    To predict: model.predict(text)
    """

    def __init__(self, config_path, weights_path=False):
        """
        Create sequatial neural network model with config from file config_path.
        Load weights from weights_path.
        If weights_path is False, then new weights will be initialized
        """
        with open(config_path, "r") as file:
            config = json.JSONDecoder().decode(file.read())
        #creating Keras model with architecture from config file.
        self.model = keras.Sequential.from_config(config)
        if weights_path:
            self.model.load_weights(weights_path, by_name=False)
        phrases = pd.read_csv("./datasets/Emotion Phrases.csv", names=["emotion", "text"])

        self.config_path = config_path
        self.weights_path = weights_path
        self.tokenizer = CountVectorizer()
        self.tokenizer.fit(phrases.text)
        self.label_encoder = LabelEncoder()
        self.one_hot_encoder = OneHotEncoder()
        temp_labels = self.label_encoder.fit_transform(phrases.emotion).reshape(-1, 1)

        self.one_hot_encoder.fit(temp_labels)
        self.emotions = ["anger", "disgust", "fear", "guilt", "joy", "sadness", "shame"]
        del phrases, temp_labels
        sgd = keras.optimizers.SGD(lr=1.7)
        self.model.compile(optimizer=sgd, loss="categorical_crossentropy", metrics=["accuracy"])
        print("Initialized model.\n Config:{}".format(config))


    def train(self, text, emotion):
        """Train neural network for instance text with given emotion.
         Text is any-length string."""
        label = self.label_encoder.transform([emotion]).reshape(-1, 1)
        label = self.one_hot_encoder.transform(label)
        label = csr_matrix.todense(label)
        instance = self.__preprocess(text)
        print("Instance shape:", instance.shape)
        print("Label shape:", label.shape)
        self.model.fit(instance, label, epochs=1)
        print("Success: Trained on this example")
        self.save()
        return True


    def save(self, config_path=False, weights_path=False):
        "Saving current model to config,weights_path."
        if config_path:
            self.config_path = config_path
        if weights_path:
            self.weights_path = weights_path
        cfg = self.model.get_config()
        cfg_json = json.JSONEncoder().encode(cfg)
        with open(self.config_path, "w") as file:
            file.write(cfg_json)
        self.model.save_weights(self.weights_path)
        print("Success: Created Checkpoint")



    def predict(self, text):
        """Predicting emotion by text. Input text must be the string"""
        instance = self.__preprocess(text)
        predicted_value = int(self.model.predict_classes(instance)[0])
        predicted_emotion = self.emotions[predicted_value]
        print("Successfully predicted emotion for this text")
        return predicted_emotion

    def __preprocess(self, text):
        """Apply CountVectorizer for text"""
        instance = [text]
        instance = self.tokenizer.transform(instance)
        return csr_matrix.todense(instance)





def test():
    """Testing NLPModel"""
    nlp = NLPModel("./model_configs/config.json", "./model_weights/model1_weights.hdf5")
    nlp.train("Dima is a pretty one man, who like Putin as president and attack on aftertimes miron, but yariks loves huis to suck and be a stupid one ", "fear")
    del nlp

def main():
    """Main docstring"""
    test()
    pass



if __name__ == "__main__":
    main()
