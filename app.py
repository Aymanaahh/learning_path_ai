import re
import html
import hashlib
import urllib.parse
from collections import OrderedDict

import requests
import streamlit as st
from bs4 import BeautifulSoup


# ============================================================
# CONFIGURATION
# ============================================================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/139.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

REQUEST_TIMEOUT = 15


# ============================================================
# CURATED AUTHORITATIVE RESOURCES
# ============================================================

CURATED_RESOURCES = {
    "machine_learning": [
        {
            "title": "Google Machine Learning",
            "url": "https://developers.google.com/machine-learning",
            "description": "Google's machine learning learning resources and courses.",
        },
        {
            "title": "Scikit-learn User Guide",
            "url": "https://scikit-learn.org/stable/user_guide.html",
            "description": "Official documentation and examples for machine learning with Scikit-learn.",
        },
        {
            "title": "TensorFlow Tutorials",
            "url": "https://www.tensorflow.org/tutorials",
            "description": "Official TensorFlow tutorials covering machine learning and deep learning.",
        },
        {
            "title": "PyTorch Tutorials",
            "url": "https://docs.pytorch.org/tutorials/",
            "description": "Official PyTorch tutorials and examples.",
        },
    ],

    "programming": [
        {
            "title": "Python Documentation",
            "url": "https://docs.python.org/3/",
            "description": "Official Python documentation, tutorials, and language reference.",
        },
        {
            "title": "Real Python",
            "url": "https://realpython.com/",
            "description": "Python tutorials, projects, and practical programming guides.",
        },
        {
            "title": "W3Schools Python",
            "url": "https://www.w3schools.com/python/",
            "description": "Beginner-friendly Python tutorials and examples.",
        },
        {
            "title": "freeCodeCamp",
            "url": "https://www.freecodecamp.org/",
            "description": "Free programming courses and practical coding exercises.",
        },
    ],

    "database": [
        {
            "title": "PostgreSQL Documentation",
            "url": "https://www.postgresql.org/docs/",
            "description": "Official PostgreSQL documentation and SQL reference.",
        },
        {
            "title": "MongoDB Documentation",
            "url": "https://www.mongodb.com/docs/",
            "description": "Official MongoDB documentation and database tutorials.",
        },
        {
            "title": "MySQL Documentation",
            "url": "https://dev.mysql.com/doc/",
            "description": "Official MySQL documentation and reference material.",
        },
        {
            "title": "W3Schools SQL",
            "url": "https://www.w3schools.com/sql/",
            "description": "SQL tutorials and interactive examples.",
        },
    ],

    "data_analysis": [
        {
            "title": "Pandas Documentation",
            "url": "https://pandas.pydata.org/docs/",
            "description": "Official Pandas documentation for data analysis with Python.",
        },
        {
            "title": "NumPy Documentation",
            "url": "https://numpy.org/doc/",
            "description": "Official NumPy documentation for numerical computing.",
        },
        {
            "title": "Matplotlib Documentation",
            "url": "https://matplotlib.org/stable/",
            "description": "Official Matplotlib documentation for data visualization.",
        },
        {
            "title": "Kaggle Learn",
            "url": "https://www.kaggle.com/learn",
            "description": "Short practical courses covering Python, data analysis, machine learning, and more.",
        },
    ],

    "web_development": [
        {
            "title": "MDN Web Docs",
            "url": "https://developer.mozilla.org/",
            "description": "Comprehensive documentation for HTML, CSS, JavaScript, and web APIs.",
        },
        {
            "title": "W3Schools Web Development",
            "url": "https://www.w3schools.com/",
            "description": "Beginner-friendly tutorials for web technologies.",
        },
        {
            "title": "freeCodeCamp Web Development",
            "url": "https://www.freecodecamp.org/learn/",
            "description": "Free web development courses and coding projects.",
        },
    ],

    "networking": [
        {
            "title": "Cloudflare Learning Center",
            "url": "https://www.cloudflare.com/learning/",
            "description": "Easy-to-understand explanations of networking, security, DNS, HTTP, and the Internet.",
        },
        {
            "title": "Cisco Networking Academy",
            "url": "https://www.netacad.com/",
            "description": "Networking and IT learning resources from Cisco.",
        },
        {
            "title": "MDN HTTP Documentation",
            "url": "https://developer.mozilla.org/en-US/docs/Web/HTTP",
            "description": "Detailed documentation about HTTP and web networking.",
        },
    ],

    "cybersecurity": [
        {
            "title": "OWASP",
            "url": "https://owasp.org/",
            "description": "Open-source cybersecurity resources and application security guidance.",
        },
        {
            "title": "NIST Cybersecurity",
            "url": "https://www.nist.gov/cybersecurity",
            "description": "Cybersecurity standards, frameworks, and guidance from NIST.",
        },
        {
            "title": "Cisco Cybersecurity",
            "url": "https://www.cisco.com/c/en/us/products/security/what-is-cybersecurity.html",
            "description": "Cybersecurity concepts and learning material from Cisco.",
        },
    ],

    "software_engineering": [
        {
            "title": "Git Documentation",
            "url": "https://git-scm.com/doc",
            "description": "Official Git documentation and reference material.",
        },
        {
            "title": "GitHub Docs",
            "url": "https://docs.github.com/",
            "description": "Documentation covering GitHub, repositories, collaboration, and development workflows.",
        },
        {
            "title": "Atlassian Git Tutorials",
            "url": "https://www.atlassian.com/git/tutorials",
            "description": "Practical Git and version-control tutorials.",
        },
    ],

    "general": [
        {
            "title": "Khan Academy",
            "url": "https://www.khanacademy.org/",
            "description": "Free educational courses and learning resources.",
        },
        {
            "title": "Coursera",
            "url": "https://www.coursera.org/",
            "description": "Online courses and learning resources from universities and organizations.",
        },
        {
            "title": "edX",
            "url": "https://www.edx.org/",
            "description": "Online courses from universities and institutions.",
        },
    ],
}


PREFERRED_DOMAINS = [
    "developer.mozilla.org",
    "docs.python.org",
    "scikit-learn.org",
    "tensorflow.org",
    "pytorch.org",
    "pandas.pydata.org",
    "numpy.org",
    "matplotlib.org",
    "postgresql.org",
    "mongodb.com",
    "dev.mysql.com",
    "owasp.org",
    "nist.gov",
    "cloudflare.com",
    "cisco.com",
    "github.com",
    "kaggle.com",
    "freecodecamp.org",
    "w3schools.com",
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_text(text):
    """Clean HTML entities and extra whitespace."""
    if not text:
        return ""

    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_topic_name(topic):
    """Normalize topic text for comparisons."""
    topic = topic.lower().strip()
    topic = re.sub(r"[^a-z0-9\s]", " ", topic)
    topic = re.sub(r"\s+", " ", topic)
    return topic


def unique_items(items, key="url"):
    """Remove duplicate dictionaries while preserving order."""
    seen = set()
    output = []

    for item in items:
        value = item.get(key, "")

        if value and value not in seen:
            seen.add(value)
            output.append(item)

    return output


# ============================================================
# STABLE STREAMLIT WIDGET KEYS
# ============================================================

def stable_key(prefix, *parts):
    """Create deterministic widget keys that survive Streamlit reruns."""
    raw = "||".join(str(part) for part in parts)
    digest = hashlib.md5(raw.encode("utf-8")).hexdigest()
    return f"{prefix}_{digest}"


# ============================================================
# COURSE OUTLINE PROCESSING
# ============================================================

def extract_topics(outline):
    """Extract meaningful topic lines from a course outline."""

    if not outline:
        return []

    lines = outline.splitlines()
    topics = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Remove common numbering/bullets
        cleaned = re.sub(
            r"^(?:\d+(?:\.\d+)*[\.\)\-:]?\s*|[-*•]\s*)",
            "",
            line,
        ).strip()

        if len(cleaned) < 2:
            continue

        topics.append(cleaned)

    return unique_items(
        [{"topic": topic} for topic in topics],
        key="topic",
    )


# ============================================================
# DOMAIN DETECTION
# ============================================================

def detect_domain(topic):
    """Detect the most likely educational domain."""

    t = normalize_topic_name(topic)

    if any(
        word in t
        for word in [
            "machine learning",
            "deep learning",
            "neural network",
            "classification",
            "regression",
            "clustering",
            "supervised learning",
            "unsupervised learning",
            "reinforcement learning",
        ]
    ):
        return "machine_learning"

    if any(
        word in t
        for word in [
            "python",
            "programming",
            "javascript",
            "java ",
            "c++",
            "c programming",
            "coding",
            "algorithm",
            "data structure",
        ]
    ):
        return "programming"

    if any(
        word in t
        for word in [
            "sql",
            "database",
            "mysql",
            "postgresql",
            "mongodb",
            "nosql",
            "query",
            "relational database",
        ]
    ):
        return "database"

    if any(
        word in t
        for word in [
            "data analysis",
            "pandas",
            "numpy",
            "matplotlib",
            "visualization",
            "data science",
            "statistics",
        ]
    ):
        return "data_analysis"

    if any(
        word in t
        for word in [
            "web development",
            "html",
            "css",
            "javascript",
            "frontend",
            "backend",
            "react",
            "website",
            "web application",
        ]
    ):
        return "web_development"

    if any(
        word in t
        for word in [
            "network",
            "networking",
            "tcp",
            "ip",
            "dns",
            "http",
            "routing",
            "switching",
        ]
    ):
        return "networking"

    if any(
        word in t
        for word in [
            "cybersecurity",
            "cyber security",
            "security",
            "ethical hacking",
            "penetration testing",
            "owasp",
            "cryptography",
        ]
    ):
        return "cybersecurity"

    if any(
        word in t
        for word in [
            "software engineering",
            "software development",
            "git",
            "github",
            "version control",
            "testing",
            "agile",
            "devops",
        ]
    ):
        return "software_engineering"

    return "general"


# ============================================================
# SUBTOPIC GENERATION
# ============================================================

def make_subtopics(topic, learning_level):
    """Create a structured learning roadmap."""

    domain = detect_domain(topic)

    base = [
        (
            "Foundation and Core Concepts",
            "Understand the fundamental ideas, terminology, and purpose of the topic.",
        ),
        (
            "Key Components and Techniques",
            "Learn the important components, methods, and techniques used in this topic.",
        ),
        (
            "Practical Implementation",
            "Apply the concepts through examples and hands-on implementation.",
        ),
        (
            "Real-World Applications",
            "Understand how the topic is used in practical projects and industry.",
        ),
        (
            "Practice and Problem Solving",
            "Solve practical problems to strengthen understanding.",
        ),
    ]

    domain_additions = {
        "machine_learning": [
            (
                "Data Preparation",
                "Learn how data is collected, cleaned, transformed, and prepared.",
            ),
            (
                "Model Training and Evaluation",
                "Understand training, validation, testing, and model evaluation.",
            ),
            (
                "Model Improvement",
                "Explore feature engineering, hyperparameter tuning, and optimization.",
            ),
        ],
        "programming": [
            (
                "Syntax and Fundamentals",
                "Learn the syntax, variables, data types, operators, and basic constructs.",
            ),
            (
                "Functions and Modular Programming",
                "Learn how to organize reusable code using functions and modules.",
            ),
            (
                "Debugging and Error Handling",
                "Learn how to identify, understand, and fix programming errors.",
            ),
        ],
        "database": [
            (
                "Database Concepts",
                "Understand tables, records, keys, relationships, and database design.",
            ),
            (
                "Queries and Data Manipulation",
                "Practice retrieving, inserting, updating, and deleting data.",
            ),
            (
                "Database Design",
                "Learn normalization, relationships, constraints, and schema design.",
            ),
        ],
        "data_analysis": [
            (
                "Data Cleaning",
                "Learn how to handle missing values, duplicates, and inconsistent data.",
            ),
            (
                "Exploratory Data Analysis",
                "Analyze datasets using descriptive statistics and visualizations.",
            ),
            (
                "Data Visualization",
                "Create meaningful charts and communicate insights from data.",
            ),
        ],
        "web_development": [
            (
                "Frontend Fundamentals",
                "Understand the structure and presentation of web pages.",
            ),
            (
                "Web Interaction",
                "Learn how JavaScript and web APIs create interactive experiences.",
            ),
            (
                "Building a Web Project",
                "Combine concepts into a functional web application.",
            ),
        ],
        "networking": [
            (
                "Networking Fundamentals",
                "Understand devices, protocols, addresses, and network models.",
            ),
            (
                "Protocols and Communication",
                "Study important networking protocols and communication methods.",
            ),
            (
                "Troubleshooting",
                "Practice identifying and solving common networking problems.",
            ),
        ],
        "cybersecurity": [
            (
                "Security Fundamentals",
                "Understand threats, vulnerabilities, risks, and security principles.",
            ),
            (
                "Security Controls",
                "Explore authentication, authorization, encryption, and defensive techniques.",
            ),
            (
                "Security Testing",
                "Learn how security weaknesses can be identified and assessed safely.",
            ),
        ],
        "software_engineering": [
            (
                "Development Workflow",
                "Understand planning, coding, testing, version control, and deployment.",
            ),
            (
                "Software Testing",
                "Learn testing concepts and techniques for reliable software.",
            ),
            (
                "Version Control",
                "Practice Git-based workflows for managing software projects.",
            ),
        ],
    }

    selected = domain_additions.get(domain, []) + base

    # Remove duplicates while keeping order
    seen = set()
    selected = [
        item
        for item in selected
        if not (item[0] in seen or seen.add(item[0]))
    ]

    if learning_level == "Beginner":
        selected = selected[:6]

    elif learning_level == "Intermediate":
        selected = selected[:7]

    else:
        selected = selected[:8]

    result = []

    for index, (name, objective) in enumerate(selected, start=1):
        result.append(
            {
                "name": f"{topic}: {name}",
                "objective": objective,
                "level": learning_level,
                "estimated_time": f"{30 + index * 10} minutes",
            }
        )

    return result


# ============================================================
# ROBUST DUCKDUCKGO SEARCH
# ============================================================

def decode_ddg_url(href):
    """Convert DuckDuckGo redirect URLs into real URLs."""

    if not href:
        return ""

    href = html.unescape(href)

    # Protocol-relative URL
    if href.startswith("//"):
        href = "https:" + href

    # DuckDuckGo redirect
    if "duckduckgo.com/l/" in href:
        try:
            parsed = urllib.parse.urlparse(href)
            params = urllib.parse.parse_qs(parsed.query)

            if "uddg" in params:
                return urllib.parse.unquote(params["uddg"][0])
        except Exception:
            pass

    return href


def is_valid_external_url(url):
    """Check whether a URL is useful for the user."""

    if not url:
        return False

    lower = url.lower()

    if not lower.startswith(("http://", "https://")):
        return False

    # Do not return DuckDuckGo internal URLs
    if "duckduckgo.com" in lower:
        return False

    # Ignore obvious advertisements/tracking links
    blocked_terms = [
        "ad_domain=",
        "ad_provider=",
        "ad_type=",
        "utm_source=bing",
        "utm_medium=cpc",
        "msclkid=",
    ]

    if any(term in lower for term in blocked_terms):
        return False

    return True


def ddg_search(query, max_results=6):
    """
    Search DuckDuckGo HTML and return useful external resources.

    This function:
    - uses browser-like headers
    - decodes DuckDuckGo redirects
    - filters advertisements
    - filters internal DuckDuckGo URLs
    - de-duplicates results
    """

    search_url = "https://html.duckduckgo.com/html/"

    try:
        response = requests.get(
            search_url,
            params={"q": query},
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

    except requests.RequestException:
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    results = []

    for result in soup.select(".result"):

        anchor = result.select_one(".result__a")
        snippet = result.select_one(".result__snippet")

        if not anchor:
            continue

        title = clean_text(anchor.get_text(" ", strip=True))

        href = decode_ddg_url(
            anchor.get("href", "")
        )

        if not is_valid_external_url(href):
            continue

        description = ""

        if snippet:
            description = clean_text(
                snippet.get_text(" ", strip=True)
            )

        results.append(
            {
                "title": title,
                "url": href,
                "description": description,
            }
        )

        if len(results) >= max_results:
            break

    return unique_items(results, key="url")


# ============================================================
# RESOURCE SCORING
# ============================================================

def score_resource(resource, topic):
    """Give higher scores to authoritative educational resources."""

    url = resource.get("url", "").lower()
    title = resource.get("title", "").lower()

    score = 0

    for domain in PREFERRED_DOMAINS:
        if domain in url:
            score += 10

    educational_words = [
        "tutorial",
        "documentation",
        "guide",
        "course",
        "learn",
        "learning",
        "reference",
        "examples",
    ]

    for word in educational_words:
        if word in title:
            score += 2

    topic_words = normalize_topic_name(topic).split()

    for word in topic_words:
        if len(word) > 3 and word in title:
            score += 1

    return score


# ============================================================
# RELIABLE WEB RESOURCE DISCOVERY
# ============================================================

def discover_resources(topic, max_web=6):
    """
    Discover reliable web resources using multiple fallback layers.

    Layer 1:
        DuckDuckGo direct search.

    Layer 2:
        Curated authoritative resources based on domain.

    Layer 3:
        Google search link for additional exploration.
    """

    domain = detect_domain(topic)

    resources = []

    # --------------------------------------------------------
    # LAYER 1: Direct DuckDuckGo searches
    # --------------------------------------------------------

    queries = [
        f"{topic} tutorial",
        f"{topic} documentation",
        f"{topic} examples",
    ]

    for query in queries:

        results = ddg_search(
            query,
            max_results=5,
        )

        resources.extend(results)

        # Avoid too many requests
        if len(resources) >= max_web * 2:
            break

    # --------------------------------------------------------
    # LAYER 2: Curated authoritative resources
    # --------------------------------------------------------

    curated = CURATED_RESOURCES.get(
        domain,
        CURATED_RESOURCES["general"],
    )

    # Put curated resources into the pool
    resources.extend(curated)

    # --------------------------------------------------------
    # Remove duplicate URLs
    # --------------------------------------------------------

    resources = unique_items(
        resources,
        key="url",
    )

    # --------------------------------------------------------
    # Score resources
    # --------------------------------------------------------

    scored = []

    for resource in resources:
        score = score_resource(
            resource,
            topic,
        )

        scored.append(
            (
                score,
                resource,
            )
        )

    # Higher score first
    scored.sort(
        key=lambda x: x[0],
        reverse=True,
    )

    final_resources = []

    for _, resource in scored:

        if resource["url"] not in [
            r["url"] for r in final_resources
        ]:
            final_resources.append(resource)

        if len(final_resources) >= max_web:
            break

    # --------------------------------------------------------
    # LAYER 3: Guaranteed Google search fallback
    # --------------------------------------------------------

    google_url = google_search_url(
        f"{topic} tutorial learning"
    )

    if google_url:
        final_resources.append(
            {
                "title": f"More web resources for: {topic}",
                "url": google_url,
                "description": (
                    "Search Google for additional tutorials, "
                    "documentation, examples, and learning resources."
                ),
            }
        )

    return final_resources


# ============================================================
# YOUTUBE
# ============================================================

def youtube_search_url(query):
    """Generate a YouTube search URL."""

    encoded = urllib.parse.quote_plus(
        query
    )

    return (
        "https://www.youtube.com/results?search_query="
        + encoded
    )


def google_search_url(query):
    """Generate a Google search URL."""

    encoded = urllib.parse.quote_plus(
        query
    )

    return (
        "https://www.google.com/search?q="
        + encoded
    )


# ============================================================
# ASSIGNMENTS
# ============================================================

def build_assignments(topic):
    """Generate hands-on assignments based on the domain."""

    domain = detect_domain(topic)

    assignments = {
        "machine_learning": [
            f"Find a small dataset related to {topic} and identify its important features.",
            f"Implement a simple machine learning model related to {topic}.",
            f"Evaluate your model using at least two suitable evaluation metrics.",
            f"Experiment with changing one parameter and compare the results.",
        ],

        "programming": [
            f"Write a small program demonstrating the core concepts of {topic}.",
            f"Create at least three test cases for your program.",
            f"Identify and fix three possible errors or edge cases.",
            f"Extend your program with one additional feature.",
        ],

        "database": [
            f"Design a small database related to {topic}.",
            f"Create tables and define suitable keys and relationships.",
            f"Write SQL queries to insert, retrieve, update, and delete data.",
            f"Write at least five queries that answer useful questions about your data.",
        ],

        "data_analysis": [
            f"Find a dataset related to {topic}.",
            f"Clean the dataset and document the cleaning steps.",
            f"Perform exploratory data analysis.",
            f"Create at least three visualizations and explain the insights.",
        ],

        "web_development": [
            f"Create a small web page demonstrating {topic}.",
            f"Add interactive functionality related to the topic.",
            f"Make the page responsive for different screen sizes.",
            f"Deploy or locally test the completed web project.",
        ],

        "networking": [
            f"Draw a network diagram demonstrating {topic}.",
            f"Explain the role of the main protocols or components involved.",
            f"Perform a safe local networking experiment.",
            f"Document a troubleshooting procedure for a common problem.",
        ],

        "cybersecurity": [
            f"Research common security risks associated with {topic}.",
            f"Create a security checklist for a small application.",
            f"Study a relevant OWASP security concept.",
            f"Perform a safe security assessment in a controlled local environment.",
        ],

        "software_engineering": [
            f"Create a small project demonstrating {topic}.",
            f"Initialize a Git repository and make meaningful commits.",
            f"Write tests for important parts of the project.",
            f"Document the development workflow and lessons learned.",
        ],

        "general": [
            f"Research the fundamental concepts of {topic}.",
            f"Create a practical example demonstrating {topic}.",
            f"Prepare a short summary of the most important concepts.",
            f"Build a small project applying what you learned about {topic}.",
        ],
    }

    return assignments.get(
        domain,
        assignments["general"],
    )


# ============================================================
# MINI PROJECT
# ============================================================

def build_mini_project(topic):
    return {
        "title": f"Mini Project: {topic}",
        "description": (
            f"Build a small practical project that demonstrates "
            f"the important concepts of {topic}. "
            f"The project should include a clear objective, "
            f"implementation, testing, and documentation."
        ),
        "deliverables": [
            "Project source code",
            "README/documentation",
            "Example input and output",
            "Short explanation of the concepts used",
        ],
    }


# ============================================================
# QUIZ
# ============================================================

def build_quiz(topic):
    return [
        f"What is {topic} and why is it important?",
        f"What are the main concepts associated with {topic}?",
        f"Give one practical example of {topic}.",
        f"What are some common challenges when working with {topic}?",
        f"How could you apply {topic} in a real-world project?",
    ]


# ============================================================
# RESOURCE CATEGORIES
# ============================================================

def get_resource_categories(topic):
    """Return YouTube and Google exploration links."""

    return [
        {
            "title": f"YouTube: {topic} Tutorial",
            "url": youtube_search_url(
                f"{topic} tutorial"
            ),
        },
        {
            "title": f"YouTube: {topic} Full Course",
            "url": youtube_search_url(
                f"{topic} full course"
            ),
        },
        {
            "title": f"YouTube: {topic} Practical Examples",
            "url": youtube_search_url(
                f"{topic} practical examples"
            ),
        },
        {
            "title": f"Google: {topic} Resources",
            "url": google_search_url(
                f"{topic} tutorial documentation examples"
            ),
        },
    ]


# ============================================================
# BUILD LEARNING PATH
# ============================================================

def build_learning_path(
    outline,
    selected_topic,
    learning_level,
    max_web,
):
    """Build the complete learning path."""

    outline_topics = extract_topics(
        outline
    )

    if selected_topic.strip():

        topics = [
            selected_topic.strip()
        ]

    else:

        topics = [
            item["topic"]
            for item in outline_topics
        ]

    learning_path = []

    for topic in topics:

        subtopics = make_subtopics(
            topic,
            learning_level,
        )

        topic_resources = discover_resources(
            topic,
            max_web=max_web,
        )

        assignments = build_assignments(
            topic
        )

        quiz = build_quiz(
            topic
        )

        mini_project = build_mini_project(
            topic
        )

        resource_categories = (
            get_resource_categories(topic)
        )

        learning_path.append(
            {
                "topic": topic,
                "domain": detect_domain(topic),
                "subtopics": subtopics,
                "web_resources": topic_resources,
                "video_resources": resource_categories,
                "assignments": assignments,
                "quiz": quiz,
                "mini_project": mini_project,
            }
        )

    return learning_path


# ============================================================
# DOWNLOAD TEXT
# ============================================================

def create_download_text(learning_path):
    """Create a plain-text learning plan."""

    lines = []

    lines.append(
        "=" * 70
    )

    lines.append(
        "PERSONALIZED LEARNING PATH"
    )

    lines.append(
        "=" * 70
    )

    lines.append("")

    for topic_data in learning_path:

        topic = topic_data["topic"]

        lines.append(
            f"TOPIC: {topic}"
        )

        lines.append(
            f"DOMAIN: {topic_data['domain']}"
        )

        lines.append("")

        lines.append(
            "SUBTOPICS"
        )

        lines.append(
            "-" * 50
        )

        for item in topic_data["subtopics"]:

            lines.append(
                f"- {item['name']}"
            )

            lines.append(
                f"  Objective: {item['objective']}"
            )

            lines.append(
                f"  Level: {item['level']}"
            )

            lines.append(
                f"  Estimated time: {item['estimated_time']}"
            )

        lines.append("")

        lines.append(
            "WEB RESOURCES"
        )

        lines.append(
            "-" * 50
        )

        for resource in topic_data[
            "web_resources"
        ]:

            lines.append(
                f"- {resource['title']}"
            )

            lines.append(
                f"  {resource['url']}"
            )

            if resource["description"]:
                lines.append(
                    f"  {resource['description']}"
                )

        lines.append("")

        lines.append(
            "YOUTUBE RESOURCES"
        )

        lines.append(
            "-" * 50
        )

        for video in topic_data[
            "video_resources"
        ]:

            lines.append(
                f"- {video['title']}"
            )

            lines.append(
                f"  {video['url']}"
            )

        lines.append("")

        lines.append(
            "ASSIGNMENTS"
        )

        lines.append(
            "-" * 50
        )

        for assignment in topic_data[
            "assignments"
        ]:

            lines.append(
                f"- {assignment}"
            )

        lines.append("")

        lines.append(
            "QUIZ"
        )

        lines.append(
            "-" * 50
        )

        for question in topic_data[
            "quiz"
        ]:

            lines.append(
                f"- {question}"
            )

        lines.append("")

        lines.append(
            "MINI PROJECT"
        )

        lines.append(
            "-" * 50
        )

        project = topic_data[
            "mini_project"
        ]

        lines.append(
            f"Title: {project['title']}"
        )

        lines.append(
            f"Description: {project['description']}"
        )

        for deliverable in project[
            "deliverables"
        ]:

            lines.append(
                f"- {deliverable}"
            )

        lines.append("")

        lines.append(
            "=" * 70
        )

        lines.append("")

    return "\n".join(lines)


# ============================================================
# STREAMLIT UI
# ============================================================

st.set_page_config(
    page_title="Learning Path AI",
    page_icon="📚",
    layout="wide",
)


st.title(
    "📚 Learning Path AI"
)

st.write(
    "Transform a course outline into a structured learning path "
    "with subtopics, YouTube resources, reliable web resources, "
    "hands-on assignments, quizzes, and a mini project."
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header(
        "⚙️ Learning Settings"
    )

    learning_level = st.selectbox(
        "Learning level",
        [
            "Beginner",
            "Intermediate",
            "Advanced",
        ],
        index=0,
    )

    max_web = st.slider(
        "Web resources per topic",
        min_value=3,
        max_value=10,
        value=6,
    )

    st.info(
        "Web resources use direct search plus curated "
        "educational sources. No API key is required."
    )


# ============================================================
# INPUT
# ============================================================

st.subheader(
    "1. Enter Course Outline"
)

outline = st.text_area(
    "Paste your course outline here:",
    height=220,
    placeholder=(
        "Example:\n"
        "1. Python Programming\n"
        "2. Data Structures\n"
        "3. Machine Learning\n"
        "4. Databases"
    ),
)


st.subheader(
    "2. Specify a Topic"
)

selected_topic = st.text_input(
    "Enter the topic you want to study:",
    placeholder=(
        "Example: Machine Learning"
    ),
)


generate = st.button(
    "🚀 Generate Learning Path",
    type="primary",
    use_container_width=True,
)


# ============================================================
# GENERATE
# ============================================================

# ============================================================
# SESSION STATE
# ============================================================

if "learning_path" not in st.session_state:
    st.session_state.learning_path = None

if "generated" not in st.session_state:
    st.session_state.generated = False


if generate:

    if not outline.strip() and not selected_topic.strip():

        st.error(
            "Please enter a course outline or specify a topic."
        )

        st.stop()

    with st.spinner(
        "Building your personalized learning path..."
    ):

        st.session_state.learning_path = build_learning_path(
            outline=outline,
            selected_topic=selected_topic,
            learning_level=learning_level,
            max_web=max_web,
        )

    st.session_state.generated = True

    st.success(
        "Learning path generated successfully!"
    )


    # ========================================================

# ============================================================
# DISPLAY SAVED LEARNING PATH
# ============================================================

learning_path = st.session_state.learning_path

if learning_path:

    for topic_index, topic_data in enumerate(
        learning_path,
        start=1,
    ):

        topic = topic_data["topic"]

        st.header(
            f"📖 {topic_index}. {topic}"
        )

        st.caption(
            f"Detected domain: {topic_data['domain']}"
        )


        # ----------------------------------------------------
        # SUBTOPICS
        # ----------------------------------------------------

        with st.expander(
            "📌 Subtopics and Learning Objectives",
            expanded=True,
        ):

            for item in topic_data[
                "subtopics"
            ]:

                st.markdown(
                    f"### {item['name']}"
                )

                st.write(
                    item["objective"]
                )

                col1, col2 = st.columns(2)

                with col1:
                    st.caption(
                        f"Level: {item['level']}"
                    )

                with col2:
                    st.caption(
                        f"Estimated time: {item['estimated_time']}"
                    )


        # ----------------------------------------------------
        # YOUTUBE
        # ----------------------------------------------------

        with st.expander(
            "🎥 YouTube Learning Resources",
            expanded=True,
        ):

            st.write(
                "Use these searches to find relevant tutorials, "
                "full courses, and practical demonstrations."
            )

            for video in topic_data[
                "video_resources"
            ]:

                st.markdown(
                    f"🔗 [{video['title']}]({video['url']})"
                )


        # ----------------------------------------------------
        # WEB RESOURCES
        # ----------------------------------------------------

        with st.expander(
            "🌐 Web Learning Resources",
            expanded=True,
        ):

            resources = topic_data[
                "web_resources"
            ]

            if resources:

                for resource in resources:

                    st.markdown(
                        f"### 🔗 [{resource['title']}]"
                        f"({resource['url']})"
                    )

                    if resource[
                        "description"
                    ]:

                        st.write(
                            resource[
                                "description"
                            ]
                        )

            else:

                st.warning(
                    "No direct web resources were returned. "
                    "Use the Google search link below to explore "
                    "resources for this topic."
                )

                fallback_url = google_search_url(
                    f"{topic} tutorial documentation"
                )

                st.markdown(
                    f"🔎 [Search web resources for "
                    f"{topic}]({fallback_url})"
                )


        # ----------------------------------------------------
        # ASSIGNMENTS
        # ----------------------------------------------------

        with st.expander(
            "🛠️ Hands-on Assignments",
            expanded=True,
        ):

            st.write(
                "Complete these activities to apply what you learned."
            )

            for assignment_index, assignment in enumerate(
                topic_data["assignments"],
                start=1,
            ):

                st.checkbox(
                    assignment,
                    key=stable_key(
                        "assignment",
                        topic,
                        assignment_index,
                        assignment,
                    ),
                )


        # ----------------------------------------------------
        # QUIZ
        # ----------------------------------------------------

        with st.expander(
            "🧠 Self-Assessment Quiz",
            expanded=False,
        ):

            for question_index, question in enumerate(
                topic_data["quiz"],
                start=1,
            ):

                st.markdown(
                    f"**Q{question_index}. {question}**"
                )

                st.text_area(
                    "Your answer:",
                    key=stable_key(
                        "quiz",
                        topic,
                        question_index,
                        question,
                    ),
                    height=80,
                )


        # ----------------------------------------------------
        # MINI PROJECT
        # ----------------------------------------------------

        with st.expander(
            "🚀 Mini Project",
            expanded=False,
        ):

            project = topic_data[
                "mini_project"
            ]

            st.subheader(
                project["title"]
            )

            st.write(
                project["description"]
            )

            st.write(
                "**Suggested deliverables:**"
            )

            for deliverable in project[
                "deliverables"
            ]:

                st.write(
                    f"• {deliverable}"
                )


    # ========================================================
    # DOWNLOAD
    # ========================================================

    st.divider()

    st.subheader(
        "📥 Download Your Learning Path"
    )

    download_text = create_download_text(
        learning_path
    )

    st.download_button(
        label="📄 Download Learning Path",
        data=download_text,
        file_name="learning_path.txt",
        mime="text/plain",
        use_container_width=True,
    )
