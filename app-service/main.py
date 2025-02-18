import json
import os

import streamlit as st
from confluent_kafka import Consumer

st.set_page_config(page_title="Semantic Score Dashboard", layout="wide")

if "semantic_score" not in st.session_state:
    st.session_state["semantic_score"] = []
if "comment_count" not in st.session_state:
    st.session_state["comment_count"] = []

bootstrap_servers = os.getenv("BOOTSTRAP_SERVERS", "localhost:9095")
topic = os.getenv("TOPIC", "broadcast_data")

conf = {"bootstrap.servers": bootstrap_servers, "group.id": topic}

consumer = Consumer(conf)
consumer.subscribe([topic])

st.title("Semantic Score Dashboard")

col1 = st.empty()
col2 = st.empty()
chart_holder1 = st.empty()
chart_holder2 = st.empty()

while True:
    message = consumer.poll(1.0)
    if message is not None:
        data = json.loads(message.value().decode("utf-8"))
        print(data)

        st.session_state["semantic_score"].append(data["semantic_score"])
        st.session_state["comment_count"].append(data["comment_count"])

        with chart_holder1:
            chart_holder1.line_chart(
                st.session_state["semantic_score"],
                use_container_width=True,
                x_label="Semantic score",
            )

        with chart_holder2:
            chart_holder2.line_chart(
                st.session_state["comment_count"],
                use_container_width=True,
                x_label="Count comment",
            )

        with col1:
            st.metric(
                label="Current Semantic Score",
                value=st.session_state["semantic_score"][-1]
                if st.session_state["semantic_score"]
                else 0,
            )

        with col2:
            st.metric(
                label="Total Comments",
                value=st.session_state["comment_count"][-1]
                if st.session_state["comment_count"]
                else 0,
            )
