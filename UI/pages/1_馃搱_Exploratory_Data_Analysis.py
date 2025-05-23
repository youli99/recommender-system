import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd

st.header("Exploratory Data Analysis")

interactions = pd.read_csv(f"UI/data/interactions_train.csv")
interactions.sort_values(by=["u", "t"], inplace=True)
interactions.t = pd.to_datetime(interactions.t, unit="s")
interactions = interactions.rename(columns={"u": "User ID", "i": "Item ID", "t": "Time"})

items = pd.read_csv(f"UI/data/items_cleaned.csv")

st.subheader("Basic Stats")
st.markdown(
    "Below are some basic statistics about the dataset, including the number of unique users, items, and total interactions. "
    "These metrics provide an overview of the dataset's scale and density."
)
st.write(f"**Unique Users:** {interactions['User ID'].nunique()}")
st.write(f"**Unique Items:** {items['i'].nunique()}")
st.write(f"**Total Interactions:** {len(interactions)}")


st.subheader("User Activity")
st.markdown(
    "This chart shows the top 20 most active users based on the number of interactions. "
    "These users demonstrate the highest engagement to the library."
)
user_activity = interactions["User ID"].value_counts().reset_index()
user_activity.columns = ["User ID", "Interaction Count"]
st.write(user_activity.head())
st.bar_chart(user_activity.head(20), x="User ID", y="Interaction Count")


st.subheader("Popular Items")
st.markdown(
    "The chart below presents the top 20 most popular items based on interaction counts. "
    "These items are the most frequently interacted with and may indicate trending or highly relevant content."
)
item_popularity = interactions["Item ID"].value_counts().reset_index()
item_popularity.columns = ["Item ID", "Interaction Count"]
st.write(item_popularity.head())
st.bar_chart(item_popularity.head(20), x="Item ID", y="Interaction Count")


st.subheader("Interactions Over Time")
st.markdown(
    "This line chart displays the total number of user interactions per day. "
)
interactions['Date'] = interactions['Time'].dt.date
daily_interactions = interactions.groupby("Date").size().reset_index(name="Count")
daily_interactions = daily_interactions.set_index("Date")
st.line_chart(daily_interactions)

st.subheader("User-Item Interaction Heatmap (Sampled)")

top_users = interactions["User ID"].value_counts().head(50).index
top_items = interactions["Item ID"].value_counts().head(50).index
sample = interactions[interactions["User ID"].isin(top_users) & interactions["Item ID"].isin(top_items)]
interaction_matrix = sample.groupby(["User ID", "Item ID"]).size().unstack(fill_value=0)
fig, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(interaction_matrix, cmap="Blues", linewidths=0.5, annot=True, fmt="d", ax=ax)
ax.set_title("Sampled User-Item Interaction Heatmap")
st.pyplot(fig)

st.markdown(
    "This heatmap shows a sampled user-item interaction matrix, including the top 20 users and top 20 items based on interaction frequency. "
    "The result clearly illustrates the sparsity of interactions, which is a common characteristic in recommender system datasets."
)