import pandas as pd
import numpy as np


class Recommender(object):
    def __init__(self):
        self._model = None
        self._user_id = None
        self._score_matrix = None
        self._recommendations = []

    def set_config(self, model, user_id):
        self._model = model
        self._user_id = user_id

    def get_recommendations(self, start_pos):
        if self._model == "Hybrid with Sequence":
            path = "UI/data/score_hybrid_full.npy"
            self.load_recommendation_matrix(path)
            self.recommend_seq(start_pos)
            return self._recommendations

        if self._model == "Collaborative Filtering":
            path = "UI/data/score_cf_normalized.npy"
        elif self._model == "Semantic Embedding":
            path = "UI/data/score_semantic_normalized.npy"
        elif self._model == "Hybrid":
            path = "UI/data/score_hybrid_full.npy"
        else:
            raise ValueError("Invalid model type")

        self.load_recommendation_matrix(path)
        self.recommend(start_pos)
        return self._recommendations

    def load_recommendation_matrix(self, path):
        self._score_matrix = np.load(path)

    def recommend(self, start_pos):
        if self._score_matrix is None:
            raise ValueError("Recommendation matrix not loaded")
        if self._user_id is None:
            raise ValueError("User ID not set")

        sorted_indices = np.argsort(self._score_matrix[self._user_id, :])

        self._recommendations = sorted_indices[
            -(start_pos + 10) : -start_pos if start_pos > 0 else None
        ][::-1]

    def recommend_seq(self, start_pos):
        if self._score_matrix is None:
            raise ValueError("Recommendation matrix not loaded")
        if self._user_id is None:
            raise ValueError("User ID not set")

        sorted_indices = np.argsort(self._score_matrix[self._user_id, :])

        if start_pos == 0:
            if self._user_id < 1200:
                result_seq_df = pd.read_csv("UI/data/seq_pred.csv")
                result_seq = result_seq_df.loc[
                    result_seq_df["user_id"] == self._user_id, "recommendation"
                ].iloc[0]
                result_seq = eval(result_seq)

                self._recommendations = result_seq + sorted_indices[-8:][::-1].tolist()
            else:
                self._recommendations = sorted_indices[
                    -(start_pos + 10) : -start_pos if start_pos > 0 else None
                ][::-1]
        else:
            self._recommendations = sorted_indices[
                -(start_pos + 10) : -start_pos if start_pos > 0 else None
            ][::-1]
