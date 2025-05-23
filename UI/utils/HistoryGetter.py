import pandas as pd


class HistoryGetter(object):
    def __init__(self, max_length=10):
        self._max_length = max_length
        self._interactions = pd.read_csv("UI/data/interactions_train.csv")

    def get_user_history(self, user_id):
        user_history = self._interactions[self._interactions.u == user_id].copy()
        user_history["time_str"] = (
            pd.to_datetime(user_history.t, unit="s", utc=True)
            .dt.tz_convert("Europe/Zurich")
            .dt.strftime("%d.%m.%Y %H:%M:%S")
        )
        user_history = (
            user_history.sort_values(["u", "t"], ascending=[True, False])
            .reset_index(drop=True)
            .head(self._max_length)
        )

        return user_history.to_dict(orient="records")
