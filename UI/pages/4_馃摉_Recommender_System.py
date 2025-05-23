import streamlit as st
from utils.Recommender import Recommender
from utils.BookInfoGetter import BookInfoGetter

recommender = Recommender()
bookinfo = BookInfoGetter()


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "model" not in st.session_state:
    st.session_state.model = None
if "recommend_start_pos" not in st.session_state:
    st.session_state.recommend_start_pos = 0


def login_page():
    st.title("📚 Log in to the recommender system")

    user_id = st.number_input(
        "Please enter your user ID", min_value=0, step=1, key="user_input"
    )
    if st.button("Login", type="primary", use_container_width=True):
        st.session_state.user_id = user_id
        st.session_state.logged_in = True
        st.rerun()


def recommendation_page():
    st.title("🎯 Recommender System")
    st.subheader(f"👋 Welcome, **User {st.session_state.user_id}**!")

    with st.expander("Want to login with another account?"):
        user_id = st.number_input(
            "Want to login with another account?",
            min_value=0,
            value=None,
            step=1,
            key="user_input",
            placeholder="Please enter your user ID",
            label_visibility="collapsed",
        )

        if st.button("Login", use_container_width=True):
            st.session_state.user_id = user_id
            st.session_state.logged_in = True
            st.session_state.recommend_start_pos = 0
            st.rerun()

    model_options = {
        "Collaborative Filtering": 0,
        "Semantic Embedding": 1,
        "Hybrid": 2,
        "Hybrid with Sequence": 3,
    }

    st.session_state.model = st.selectbox(
        "Please select the recommender model:",
        [
            "Collaborative Filtering",
            "Semantic Embedding",
            "Hybrid",
            "Hybrid with Sequence",
        ],
        key="model_selection",
        index=model_options.get(st.session_state.model, 0),
        on_change=lambda: st.session_state.update({"recommend_start_pos": 0}),
    )

    if st.button("Refresh", use_container_width=True):
        st.session_state.recommend_start_pos += 10
        st.rerun()

    recommender.set_config(st.session_state.model, st.session_state.user_id)

    recommended_book_ids = recommender.get_recommendations(
        st.session_state.recommend_start_pos
    )

    for book_id in recommended_book_ids:
        book_info = bookinfo.get_book_info(book_id)
        cover_url = (
            bookinfo.get_book_cover(book_id) or "UI/data/book-cover-placeholder.png"
        )

        with st.container(border=True):
            cols = st.columns([1, 3])
            with cols[0]:
                st.image(cover_url, width=120)
            with cols[1]:
                st.markdown(f"**📖 Title:** {book_info.get('title', 'Unknown')}")
                st.markdown(f"**👤 Author:** {book_info.get('author', 'Unknown')}")
                st.markdown(
                    f"**🏢 Publisher:** {book_info.get('publisher', 'Unknown')}"
                )
                st.markdown(f"**🔢 ISBN:** {book_info.get('isbn', 'Unknown')}")
                with st.expander("🔍 More info"):
                    tags = book_info.get("tags", {})
                    st.markdown(f"**Genre:** {tags.get('genre', 'Unknown')}")
                    st.markdown(f"**Sub-genre:** {tags.get('subgenre', 'Unknown')}")
                    st.markdown(
                        f"**Themes:** {', '.join(tags.get('themes', 'Unknown'))}"
                    )
                    st.markdown(
                        f"**Tone/Mood:** {', '.join(tags.get('tone_mood', 'Unknown'))}"
                    )
                    st.markdown(
                        f"**Target audience:** {tags.get('target_audience', 'Unknown')}"
                    )
                    st.markdown(
                        f"**Short summary:** {tags.get('short_summary', 'Unknown')}"
                    )

    if st.button("Log out"):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.rerun()


if st.session_state.logged_in:
    recommendation_page()
else:
    login_page()
