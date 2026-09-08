import re
import html
import urllib.parse
from collections import OrderedDict

import requests
import streamlit as st
from bs4 import BeautifulSoup

st.set_page_config(
    page_title="Learning Path AI",
    page_icon="🎓",
    layout="wide",
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 Chrome/139.0 Safari/537.36"
}


# -----------------------------
# Course outline processing
# -----------------------------
def clean_text(text):
    text = re.sub(r"\s+", " ", text or "").strip()
    return text


def extract_topics(outline):
    """
    Converts a pasted course outline into a reasonably clean list of topics.
    It supports numbered outlines, bullets, headings and comma-separated items.
    """
    lines = [clean_text(x) for x in outline.splitlines() if clean_text(x)]
    topics = []

    for line in lines:
        # Remove common numbering/bullet prefixes.
        item = re.sub(
            r"^(?:[-*•▪◦]|\(?\d+(?:\.\d+)*\)?[.)-]?|[A-Za-z][.)])\s*",
            "",
            line,
        ).strip()

        # Ignore very long paragraph-like lines; they are usually descriptions.
        if item and len(item) <= 180:
            topics.append(item)

    # If the user pasted a paragraph rather than an outline, split on semicolons.
    if len(topics) <= 1 and ";" in outline:
        topics = [clean_text(x) for x in outline.split(";") if clean_text(x)]

    # Remove duplicates while preserving order.
    return list(OrderedDict.fromkeys(topics))


def normalize_topic_name(topic):
    return re.sub(r"\s+", " ", topic).strip(" .:-")


def make_subtopics(topic):
    """
    Generates useful subtopic buckets without requiring an LLM/API key.
    This makes the app deployable with zero AI credentials.
    """
    t = normalize_topic_name(topic)
    lower = t.lower()

    templates = [
        f"{t}: fundamentals and key concepts",
        f"{t}: terminology and core components",
        f"{t}: how it works / workflow",
        f"{t}: practical examples",
        f"{t}: common mistakes and best practices",
        f"{t}: hands-on practice",
        f"{t}: mini project / real-world application",
        f"{t}: revision questions and assessment",
    ]

    # Add a small domain-aware improvement.
    if any(k in lower for k in ["python", "programming", "coding", "java", "javascript"]):
        templates.insert(2, f"{t}: syntax, patterns and code structure")
        templates.insert(5, f"{t}: debugging and problem solving")

    if any(k in lower for k in ["machine learning", "deep learning", "ai", "data science"]):
        templates.insert(3, f"{t}: datasets, features and evaluation")
        templates.insert(5, f"{t}: implementation with a small dataset")

    if any(k in lower for k in ["database", "sql"]):
        templates.insert(3, f"{t}: queries, filtering and aggregation")
        templates.insert(5, f"{t}: schema design and practical exercises")

    return list(OrderedDict.fromkeys(templates))


# -----------------------------
# Web/resource discovery
# -----------------------------
def ddg_search(query, max_results=6):
    """
    Uses DuckDuckGo's public HTML search endpoint.
    No API key is required.
    """
    url = "https://html.duckduckgo.com/html/"
    try:
        response = requests.get(
            url,
            params={"q": query},
            headers=HEADERS,
            timeout=12,
        )
        response.raise_for_status()
    except requests.RequestException:
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    for result in soup.select(".result"):
        a = result.select_one(".result__a")
        snippet = result.select_one(".result__snippet")
        if not a:
            continue

        title = clean_text(a.get_text(" ", strip=True))
        href = a.get("href", "")
        description = clean_text(snippet.get_text(" ", strip=True)) if snippet else ""

        if href:
            results.append({
                "title": title,
                "url": href,
                "description": description,
            })

        if len(results) >= max_results:
            break

    return results


def youtube_search_url(query):
    return "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(query)


def discover_resources(subtopic, max_web=5):
    web_results = ddg_search(f"{subtopic} tutorial course documentation", max_web)

    # Prefer common educational domains when possible.
    preferred_domains = [
        "w3schools.com",
        "developer.mozilla.org",
        "docs.python.org",
        "geeksforgeeks.org",
        "freecodecamp.org",
        "khanacademy.org",
        "coursera.org",
        "edx.org",
        "tutorialspoint.com",
        "datacamp.com",
        "realpython.com",
    ]

    def score(item):
        url = item["url"].lower()
        return sum(1 for d in preferred_domains if d in url)

    web_results.sort(key=score, reverse=True)

    return {
        "youtube": youtube_search_url(subtopic + " tutorial"),
        "web": web_results[:max_web],
    }


def build_assignments(topic, subtopic):
    return [
        f"Explain {subtopic} in your own words in 5–8 sentences.",
        f"Find one real-world use case of {subtopic} and describe how it is applied.",
        f"Create a small hands-on exercise demonstrating {subtopic}. Record your steps and result.",
        f"Write 5 quiz questions about {subtopic}, then answer them without looking at your notes.",
        f"Complete one mini-project that uses {subtopic} and document what worked, what failed, and what you learned.",
    ]


# -----------------------------
# UI
# -----------------------------
st.title("🎓 Learning Path AI")
st.caption(
    "Turn a course outline into a topic-by-topic learning path with subtopics, "
    "web resources, YouTube searches and hands-on assignments."
)

with st.sidebar:
    st.header("Settings")
    max_topics = st.slider("Topics to process", 1, 12, 6)
    resources_per_topic = st.slider("Web resources per subtopic", 1, 5, 3)
    st.info(
        "This version does not require an AI/API key. "
        "Topic decomposition uses a built-in learning framework, while resources "
        "are discovered through public web search."
    )

outline = st.text_area(
    "1. Paste your course outline",
    height=220,
    placeholder=(
        "Example:\n"
        "1. Python Programming\n"
        "2. Object Oriented Programming\n"
        "3. SQL and Databases\n"
        "4. Data Analysis\n"
        "5. Machine Learning"
    ),
)

selected_topic = st.text_input(
    "2. Which topic do you want to learn?",
    placeholder="Example: Machine Learning",
)

if st.button("🚀 Build My Learning Path", type="primary"):
    if not outline.strip():
        st.error("Please paste a course outline.")
        st.stop()

    topics = extract_topics(outline)
    if not topics:
        st.error("I could not detect topics. Try a numbered or bullet-point outline.")
        st.stop()

    if selected_topic.strip():
        requested = normalize_topic_name(selected_topic)
        matching = [t for t in topics if requested.lower() in t.lower()]
        if matching:
            topics_to_process = [matching[0]]
        else:
            # Allow a topic that is not explicitly listed in the outline.
            topics_to_process = [requested]
    else:
        topics_to_process = topics[:max_topics]

    st.session_state["learning_path"] = []

    progress = st.progress(0)
    for i, topic in enumerate(topics_to_process):
        subtopics = make_subtopics(topic)
        topic_data = {
            "topic": topic,
            "subtopics": [],
        }

        for subtopic in subtopics:
            resources = discover_resources(subtopic, resources_per_topic)
            assignments = build_assignments(topic, subtopic)

            topic_data["subtopics"].append({
                "name": subtopic,
                "resources": resources,
                "assignments": assignments,
            })

        st.session_state["learning_path"].append(topic_data)
        progress.progress((i + 1) / len(topics_to_process))

    st.success("Learning path created!")

if "learning_path" in st.session_state and st.session_state["learning_path"]:
    st.divider()
    st.header("📚 Your Learning Path")

    for topic_data in st.session_state["learning_path"]:
        with st.expander(f"📘 {topic_data['topic']}", expanded=True):
            for idx, item in enumerate(topic_data["subtopics"], 1):
                st.subheader(f"{idx}. {item['name']}")

                st.markdown("**🎥 YouTube resource**")
                st.markdown(
                    f"[Search YouTube for this subtopic]({item['resources']['youtube']})"
                )

                st.markdown("**🌐 Web resources**")
                if item["resources"]["web"]:
                    for r in item["resources"]["web"]:
                        title = html.escape(r["title"])
                        desc = html.escape(r["description"])
                        st.markdown(f"- [{title}]({r['url']})")
                        if desc:
                            st.caption(desc)
                else:
                    st.info("No web results were returned. Try again or use the YouTube search.")

                st.markdown("**📝 Hands-on assignments**")
                for a in item["assignments"]:
                    st.markdown(f"- {a}")

                st.markdown("---")

    # Download a simple text copy of the generated plan.
    lines = ["LEARNING PATH AI", "=" * 60, ""]
    for topic_data in st.session_state["learning_path"]:
        lines.append(f"TOPIC: {topic_data['topic']}")
        lines.append("-" * 60)
        for item in topic_data["subtopics"]:
            lines.append(f"SUBTOPIC: {item['name']}")
            lines.append(f"YouTube: {item['resources']['youtube']}")
            lines.append("Web resources:")
            for r in item["resources"]["web"]:
                lines.append(f"- {r['title']}: {r['url']}")
            lines.append("Assignments:")
            for a in item["assignments"]:
                lines.append(f"- {a}")
            lines.append("")

    st.download_button(
        "⬇️ Download learning plan",
        data="\n".join(lines),
        file_name="learning_plan.txt",
        mime="text/plain",
    )

st.divider()
st.caption(
    "Tip: For the best results, use a course outline with one topic per line."
)
