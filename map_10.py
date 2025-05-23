import numpy as np
import pandas as pd


def print_map_10(test_df, prediction, n_users, n_items, top_k=10):
    ground_truth = test_df.groupby("u")["i"].apply(list).to_dict()

    user_ids = np.array(range(n_users))
    item_ids = np.array(range(n_items))

    top10_preds = {}

    for idx, user in enumerate(user_ids):
        scores = prediction[idx]
        top_indices = np.argsort(scores)[::-1][:top_k]
        top_items = item_ids[top_indices]
        top10_preds[user] = top_items.tolist()

    def average_precision_at_k(predicted, actual, k=10):
        if not actual:
            return 0.0
        score = 0.0
        num_hits = 0
        for i, p in enumerate(predicted[:k]):
            if p in actual:
                num_hits += 1
                score += num_hits / (i + 1)
        return score / min(len(actual), k)

    ap_scores = [
        average_precision_at_k(top10_preds[user], ground_truth[user], k=10)
        for user in user_ids
        if user in top10_preds
    ]

    map10 = np.mean(ap_scores)
    print(f"MAP@10: {map10:.4f}")
    return map10


def print_map_10_from_csv(test_df: pd.DataFrame, submission_df: pd.DataFrame) -> float:
    ground_truth = test_df.groupby("u")["i"].apply(list).to_dict()

    predictions = (
        submission_df.set_index("user_id")["recommendation"]
        .apply(lambda x: list(map(int, x.strip().split()[:10])))
        .to_dict()
    )

    def average_precision_at_k(predicted, actual, k=10):
        if not actual:
            return 0.0
        score = 0.0
        num_hits = 0
        for i, p in enumerate(predicted[:k]):
            if p in actual:
                num_hits += 1
                score += num_hits / (i + 1)
        return score / min(len(actual), k)

    ap_scores = []
    for user, actual_items in ground_truth.items():
        if user in predictions:
            predicted_items = predictions[user]
            ap = average_precision_at_k(predicted_items, actual_items, k=10)
            ap_scores.append(ap)

    map_10 = np.mean(ap_scores)
    print(f"MAP@10: {map_10:.4f}")
    return map_10
