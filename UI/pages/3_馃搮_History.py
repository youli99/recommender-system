import streamlit as st
from utils.BookInfoGetter import BookInfoGetter
from utils.HistoryGetter import HistoryGetter

bookinfo = BookInfoGetter()
history_getter = HistoryGetter()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None


def login_page():
    st.title("🕑 Log in to the borrowing records system")

    user_id = st.number_input(
        "Please enter your user ID", min_value=0, step=1, key="user_input"
    )
    if st.button("Login", type="primary", use_container_width=True):
        st.session_state.user_id = user_id
        st.session_state.logged_in = True
        st.rerun()


def history_page():
    st.title("📅 History")
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
            st.rerun()

    history_items = history_getter.get_user_history(st.session_state.user_id)

    for item in history_items:
        book_id = item.get("i", None)
        time_str = item.get("time_str", None)
        if book_id is None:
            continue

        book_info = bookinfo.get_book_info(book_id)
        cover_url = (
            bookinfo.get_book_cover(book_id) or "UI/data/book-cover-placeholder.png"
        )

        with st.container(border=True):
            cols = st.columns([1, 3])
            with cols[0]:
                st.image(cover_url, width=120)
            with cols[1]:
                st.markdown(
                    f"""
                        <div style='
                            background-color: #e0f0ff;
                            padding: 8px 16px;
                            border-radius: 8px;
                            font-size: 16px;
                            font-weight: bold;
                            color: #1a4f7a;
                            text-align: center;
                            margin-bottom: 10px;
                        '>
                            🗓️ Borrowed on: {time_str}
                        </div>
                    """,
                    unsafe_allow_html=True,
                )
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
    history_page()
else:
    login_page()
