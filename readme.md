# Library Recommender Competition

Github Repo: https://github.com/youli99/recommender-system (Video link inside the repo readme)

## 1. Exploratory Data Analysis

Before developing the recommender system, I performed an exploratory data analysis (EDA) to better understand the structure, scale, and dynamics of the dataset. The dataset includes user-item interaction records, which are essential for collaborative filtering and other recommendation strategies.

### Basic Statistics

The dataset consists of:

- Unique Users: 7,838
- Unique Items: 15,291
- Total Interactions: 87,047

These figures suggest a reasonably sparse interaction matrix, which is a typical characteristic of recommender system datasets.

### User Activity

I examined the distribution of interactions across users. The top 20 most active users recorded substantially more interactions, with the most active user reaching 385 interactions. This suggests that a small portion of users are responsible for a large share of the activity.

The accompanying bar chart illustrates this imbalance clearly, revealing a skewed distribution where the majority of users have relatively few interactions.

### Item Popularity

Similarly, item popularity was analyzed based on interaction frequency. The most popular item had 380 interactions, while the rest followed a gradual decline. This indicates potential trends or universally appealing items within the dataset. Such patterns are useful for implementing hybrid recommender models, where the semantic information of the books can be used.

### Temporal Interaction Patterns

A line chart was plotted to show the total number of interactions per day. The data reveals clear temporal trends, including noticeable peaks and a gradual decline in activity over time. While these trends may not be directly leveraged in our final model, they highlight the potential value of incorporating temporal features during the modeling process.

## 2. Data augmentation

The dataset provides metadata for each book, including the title, author, ISBN, publisher, and subjects. Incorporating this metadata into the recommender model introduces useful semantic information, which can theoretically enhance recommendation quality.

However, upon closer inspection, I found that not all metadata fields contribute meaningful semantic value. For example, the author, ISBN, and publisher fields lack descriptive information about the book's content. In contrast, the title and subjects contain the most relevant semantic information.

To extract semantic embeddings for each book, one could apply traditional methods such as TF-IDF or machine learning approaches like Word2Vec. However, these techniques often fall short in capturing the true meaning of the text and tend to overlook synonyms and nuanced language.

I also observed that the subject field is poorly structured and introduces considerable noise. Moreover, both the title and subjects are in French, adding an additional layer of complexity.

To address these challenges, I chose to use OpenAI's API for semantic enrichment. Specifically, I used the GPT-4.1-mini model and prompted it as follows:

```
You are a professional book metadata assistant.

Given a JSON with:
• "title": French book title
• "subjects": list of French keywords

Return only a JSON with:

"Semantic_Tags": up to 3 concise English nouns/phrases
"Genre": 1 top-level English genre
"Subgenre": 1 specific English subgenre
"Themes": up to 2 high-level English themes
"Tone_Mood": up to 3 English descriptors (tone or style)
"Target_Audience": English phrase, ≤10 words
"Short_Summary": 1–2 English sentences, max 20 words
Output only valid JSON. No explanations or extra text.
```

The model generates structured semantic information—tags, genre, subgenre, themes, tone/mood, target audience, and a short summary—based solely on the title and subjects, which I found to be the most informative fields.

These structured tags can be displayed in the user interface to improve user experience. To incorporate them into the model, I use OpenAI's ``text-embedding-3-large model`` to generate embeddings for each field. I exclude genres from embedding due to the limited number of categories, which makes vectorization less informative.

As a result, I obtain six sets of embeddings per book, each carrying real semantic meaning and ready for use in the recommender model.

##### Original Book Metadata for Book 1
| Key       | Value                                                                                      |
| --------- | ------------------------------------------------------------------------------------------ |
| Title     | Les interactions dans l'enseignement des langues : agir professoral et pratiques de classe |
| Author    | Cicurel, Francine                                                                          |
| ISBN      | 9782278058327; 2278058320                                                                  |
| Publisher | Didier                                                                                     |
| Subject   | didactique--langue étrangère - enseignement; didactique--langue - enseignement             |

##### AI Processed Book Metadata for Book 1
| Key             | Value                                                                          |
| --------------- | ------------------------------------------------------------------------------ |
| Semantic Tags   | Language Teaching, Classroom Interaction, Educational Practices                |
| Genre           | Non-fiction                                                                    |
| Subgenre        | Educational Theory                                                             |
| Themes          | Language Education, Teaching Methods                                           |
| Tone Mood       | Analytical, Informative, Academic                                              |
| Target Audience | Language educators and researchers                                             |
| Short Summary   | Explores teacher actions and classroom practices in foreign language teaching. |

## 3. Models

### Baseline -- Pure CF or Embedding

As a baseline, I implemented traditional collaborative filtering (CF) models, as well as a pure content-based model that recommends items based on the similarity of their embedding vectors.

In the content-based model, I first calculated the cosine similarity between each books, and then I use **the sum of similarity scores of all the books in the user's borrowing history against one book** (semantic aggregation) to create a prediction score matrix:

$$ Score_{m \times n} = I_{m \times n} S_{n \times n} $$

where $I_{m \times n}$ is the interaction matrix of m users and n books, with each element as 1 or 0 to represent an interaction, and $S_{n \times n}$ is the cosine similarity matrix between books.

### CF with Rating

Building on the basic CF model, I developed an enhanced CF model by incorporating a custom rating score for each user-book pair. During the EDA phase, I observed a potential temporal pattern in user interactions, which inspired me to integrate temporal information into the CF model.

Instead of representing interactions with a binary 0–1 value, I grouped the interaction data by user and item to calculate two features: the frequency of interactions and the most recent interaction timestamp ($t_{max}$) for each user-book pair. I normalized the timestamps across the entire dataset to ensure comparability. I introduced a temporal weighting assumption: the more recent a borrowing event, the more it reflects the user's current interest. Specifically, I used a temporal amplification term:

$$
e^{2t_{\text{max}}}
$$

where $t_{\text{max}}$ is the normalized timestamp of the latest interaction.

The final rating for each user-book pair was then computed using the following formula:

$$ 100 \times \log(e^{2t_{max}} \times \text{Count} + 1) $$

where the temporal amplification term is multiplied with the borrowed times of the book (Count). This formulation amplifies the influence of both interaction frequency and recency, assigning higher ratings to frequently and recently interacted books.

### Hybrid Model

Next, I developed a hybrid model that combines the enhanced collaborative filtering (CF) model—based on custom ratings—with semantic embeddings to capture both user behavior and content-based features.

To improve the semantic component, I introduced a temporal weighting assumption: the more recent a borrowing event, the more it reflects the user's current interest. I modified the interaction matrix ($I_{m \times n}$) by assigning each entry the value of the temoral amplification term introduced before. To further emphasize time relevance, I limited the semantic aggregation to only the most recent 30% of each user's interaction history.

The final hybrid prediction score for each user-book pair is calculated using the following weighted formula:

$$
\text{Hybrid Score} = 0.92 \times \log(1 + \text{CF Score}) + 0.20 \times \text{Semantic Tags Score} + 0.80 \times \log(1 + \text{Summary Score}) + 0.01 \times \log(1 + \text{Themes Score})
$$

This approach balances collaborative and content signals while amplifying recency, aiming to generate recommendations that are both personalized and timely.

### Sequencial pattern

In addition, I observed a sequential pattern in user interactions, indicating that the order in which books are read may carry predictive information. To capture this behavior, I trained a transformer-based model designed to learn sequencial dependencies from user histories.

Based on this, I developed a final model that integrates both the hybrid model and the sequential model, aiming to fully leverage both semantic features and sequential reading patterns. For the first 1,200 users, the system recommends 2 books based on the sequential model and the remaining 8 using the hybrid model. For all other users, recommendations are generated solely using the hybrid model.

### Results

The given dataset was first sorted by user and timestamp. The first 80\% of the interactions were allocated to the training set, and the remaining 20\% to the test set. All evaluation metrics reported below are based on models trained on the training set and evaluated on the test set accordingly.

|              | User-user CF | Item-item CF | CF with rating | Pure semantic embedding | Hybrid | Hybrid with sequencial |
| ------------ | ------------ | ------------ | -------------- | ----------------------- | ------ | ---------------------- |
| Precision@10 | 0.0565       | 0.0556       | 0.0612         | 0.0391                  | 0.0636 | 0.0704                 |
| Recall@10    | 0.2907       | 0.2640       | 0.2955         | 0.2290                  | 0.3180 | 0.3469                 |
| MAP@10       | 0.1576       | 0.1443       | 0.1681         | 0.1320                  | 0.1772 | 0.1958                 |
| Kaggle Score | 0.1241       | --           | --             | 0.0166                  | 0.1674 | 0.1964                 |
