import re


# ============================================================
# TECHNOLOGY DATABASE
# ============================================================

TECHNOLOGIES = {

    # Programming Languages
    "Python": [
        "python",
        "django",
        "flask",
        "fastapi"
    ],

    "Java": [
        "java",
        "spring boot",
        "spring"
    ],

    "JavaScript": [
        "javascript",
        "js"
    ],

    "TypeScript": [
        "typescript"
    ],

    "PHP": [
        "php",
        "laravel"
    ],

    "C#": [
        "c#",
        ".net",
        "asp.net"
    ],

    "C++": [
        "c++"
    ],


    # Frontend
    "React": [
        "react",
        "reactjs"
    ],

    "Angular": [
        "angular"
    ],

    "Vue.js": [
        "vue.js",
        "vuejs"
    ],

    "Next.js": [
        "next.js",
        "nextjs"
    ],


    # Backend
    "Node.js": [
        "node.js",
        "nodejs"
    ],

    "Express.js": [
        "express.js",
        "expressjs"
    ],


    # Cloud
    "AWS": [
        "amazon web services",
        "aws"
    ],

    "Microsoft Azure": [
        "microsoft azure",
        "azure"
    ],

    "Google Cloud": [
        "google cloud",
        "gcp"
    ],


    # Databases
    "PostgreSQL": [
        "postgresql",
        "postgres"
    ],

    "MySQL": [
        "mysql"
    ],

    "MongoDB": [
        "mongodb",
        "mongo db"
    ],

    "Redis": [
        "redis"
    ],


    # Data / AI
    "TensorFlow": [
        "tensorflow"
    ],

    "PyTorch": [
        "pytorch"
    ],

    "OpenAI": [
        "openai"
    ],

    "LangChain": [
        "langchain"
    ],

    "Hugging Face": [
        "hugging face",
        "huggingface"
    ],


    # DevOps
    "Docker": [
        "docker"
    ],

    "Kubernetes": [
        "kubernetes",
        "k8s"
    ],

    "Jenkins": [
        "jenkins"
    ],

    "GitHub": [
        "github"
    ],

    "GitLab": [
        "gitlab"
    ],


    # CMS
    "WordPress": [
        "wordpress"
    ],

    "Shopify": [
        "shopify"
    ]
}


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_text(html):
    """
    Convert HTML into searchable lowercase text.
    """

    if not html:
        return ""

    # Remove script/style content
    html = re.sub(
        r"<script.*?>.*?</script>",
        " ",
        html,
        flags=re.IGNORECASE | re.DOTALL
    )

    html = re.sub(
        r"<style.*?>.*?</style>",
        " ",
        html,
        flags=re.IGNORECASE | re.DOTALL
    )

    # Remove HTML tags
    text = re.sub(
        r"<[^>]+>",
        " ",
        html
    )

    # Normalize spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.lower().strip()


# ============================================================
# EXTRACT TECHNOLOGIES
# ============================================================

def extract_technologies(html):
    """
    Detect technologies mentioned in webpage HTML.
    """

    if not html:
        return []

    text = normalize_text(html)

    detected = []

    for technology, keywords in TECHNOLOGIES.items():

        for keyword in keywords:

            pattern = r"\b" + re.escape(keyword.lower()) + r"\b"

            if re.search(pattern, text):

                detected.append(
                    technology
                )

                break

    return sorted(
        set(detected)
    )