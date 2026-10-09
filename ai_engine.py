import os
import json
import random
import re
import time
import requests
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

class InterviewAIEngine:
    """
    Unified AI Engine for the AI Interview Preparation Bot.
    Supports:
      1. Google Gemini (via google-genai or direct REST API)
      2. OpenAI (gpt-4o-mini, gpt-3.5-turbo, etc.)
      3. Groq (llama-3.3-70b-versatile, llama-3.1-8b-instant, etc.)
      4. Custom OpenAI-compatible endpoints (Ollama, OpenRouter, etc.)
      5. Offline Smart Heuristic Fallback Engine (no API key required)
    """

    DEFAULT_DOMAINS = [
        {
            "id": "Artificial Intelligence & ML",
            "name": "Artificial Intelligence & Machine Learning",
            "icon": "🤖",
            "description": "Deep learning, neural networks, supervised/unsupervised learning, transformers & computer vision."
        },
        {
            "id": "Python Programming",
            "name": "Python & Data Structures",
            "icon": "🐍",
            "description": "OOP, memory management, generators, decorators, GIL, algorithms and standard libraries."
        },
        {
            "id": "Full Stack Web Development",
            "name": "Full Stack Web Development",
            "icon": "🌐",
            "description": "Frontend (React, JavaScript), Backend (REST APIs, Node/Flask), state management and auth."
        },
        {
            "id": "Database Management Systems",
            "name": "DBMS, SQL & System Storage",
            "icon": "🗄️",
            "description": "ACID, indexing, query optimization, normalization, transactions, SQL vs NoSQL."
        },
        {
            "id": "System Design & Architecture",
            "name": "System Design & Distributed Systems",
            "icon": "🏗️",
            "description": "Microservices, load balancing, caching, CDN, sharding, high availability & CAP theorem."
        },
        {
            "id": "Cloud, DevOps & Networks",
            "name": "Cloud, DevOps & Computer Networks",
            "icon": "☁️",
            "description": "Docker, Kubernetes, CI/CD, AWS/GCP, TCP/IP, OSI model, DNS, SSL/TLS, and security."
        },
        {
            "id": "Data Structures & Algorithms",
            "name": "Data Structures & Algorithms",
            "icon": "⚡",
            "description": "Arrays, Trees, Graphs, Dynamic Programming, Big-O complexity, searching & sorting."
        },
        {
            "id": "HR & Behavioral",
            "name": "HR & Behavioral (STAR Method)",
            "icon": "💼",
            "description": "Leadership, teamwork, conflict resolution, situational scenarios, and career trajectory."
        }
    ]

    # Curated offline question bank for high quality fallback
    OFFLINE_QUESTIONS = {
        "Artificial Intelligence & ML": [
            {
                "q": "What is the difference between supervised, unsupervised, and reinforcement learning?",
                "type": "Conceptual",
                "difficulty": "Easy",
                "keywords": ["supervised", "unsupervised", "reinforcement", "label", "reward", "agent", "clustering", "training"],
                "model_answer": "Supervised learning trains on labeled data where inputs map to known outputs (e.g. classification, regression). Unsupervised learning discovers hidden patterns or clusters in unlabeled data without explicit targets (e.g. K-Means, PCA). Reinforcement learning trains an autonomous agent to make sequential decisions by interacting with an environment to maximize cumulative numerical rewards through trial and error (e.g. Q-learning, policy gradients)."
            },
            {
                "q": "What is overfitting in machine learning and how do you prevent it?",
                "type": "Technical",
                "difficulty": "Medium",
                "keywords": ["overfitting", "regularization", "dropout", "validation", "cross-validation", "generalization", "data augmentation"],
                "model_answer": "Overfitting happens when a model learns the training data and noise too closely, failing to generalize to unseen test data. To prevent overfitting, practitioners use: 1) Regularization (L1 Lasso, L2 Ridge), 2) Cross-validation (K-fold), 3) Dropout layers in neural networks, 4) Early stopping during training, 5) Pruning in decision trees, and 6) Gathering more data or using data augmentation."
            },
            {
                "q": "Explain the attention mechanism and why transformers revolutionized NLP over RNNs.",
                "type": "Deep Dive",
                "difficulty": "Hard",
                "keywords": ["attention", "transformer", "self-attention", "parallel", "recurrent", "rnn", "vanishing gradient", "context"],
                "model_answer": "RNNs process tokens sequentially, creating bottlenecks in training speed and struggling with long-range dependencies due to vanishing gradients. The Self-Attention mechanism allows a model to weigh the relevance of every word in a sequence with respect to all other words simultaneously. Transformers process tokens in parallel, enabling massive scaling on modern GPUs and capturing nuanced bidirectional context across long documents."
            },
            {
                "q": "What is the difference between Precision and Recall? When would you prioritize one over the other?",
                "type": "Scenario",
                "difficulty": "Medium",
                "keywords": ["precision", "recall", "false positive", "false negative", "f1", "tradeoff", "metric"],
                "model_answer": "Precision is True Positives divided by all predicted positives (how many selected items are relevant). Recall is True Positives divided by actual positives (how many relevant items were found). In cancer detection or fraud prevention, Recall is prioritized because a False Negative is catastrophic. In spam filtering or YouTube search recommendations, Precision is prioritized to avoid irritating users with false alarms."
            }
        ],
        "Python Programming": [
            {
                "q": "What is the Global Interpreter Lock (GIL) in Python and how does it affect concurrency?",
                "type": "Conceptual",
                "difficulty": "Medium",
                "keywords": ["gil", "thread", "interpreter", "cpu-bound", "io-bound", "multiprocessing", "concurrency", "lock"],
                "model_answer": "The GIL is a mutex in CPython that prevents multiple native threads from executing Python bytecode simultaneously. This ensures thread-safety for memory management (reference counting). While it allows multi-threading to speed up I/O-bound tasks (like web scraping or database calls), it prevents true CPU-bound parallelism across multiple cores. For CPU-intensive tasks, developers use the 'multiprocessing' module or subinterpreters to bypass the GIL."
            },
            {
                "q": "Explain how Python manages memory. What is the role of reference counting and garbage collection?",
                "type": "Technical",
                "difficulty": "Medium",
                "keywords": ["memory", "reference counting", "garbage collection", "cyclic", "heap", "gc module", "deallocation"],
                "model_answer": "Python uses automatic memory management consisting of two main systems: 1) Reference Counting: Every object maintains a counter of how many references point to it. When the count drops to zero, its memory is immediately deallocated. 2) Cyclic Garbage Collector: To handle cyclic references (where object A points to B and B points to A, keeping reference count > 0), Python runs a generational garbage collector (Generations 0, 1, 2) that periodically identifies and frees unreachable cyclic clusters."
            },
            {
                "q": "What are Python generators and decorators, and in what practical scenarios would you use them?",
                "type": "Practical",
                "difficulty": "Easy",
                "keywords": ["generator", "yield", "decorator", "wrapper", "memory", "iterator", "logging", "function"],
                "model_answer": "A generator is a function that produces a sequence of values lazily using the 'yield' keyword instead of 'return'. It maintains state between iterations and requires minimal memory, ideal for streaming massive files or infinite series. A decorator is a higher-order function that takes another function as input and extends its behavior without modifying its source code, widely used for logging, authentication, caching (@functools.lru_cache), and rate limiting."
            }
        ],
        "Full Stack Web Development": [
            {
                "q": "Explain the difference between Server-Side Rendering (SSR) and Client-Side Rendering (CSR). When should you choose each?",
                "type": "Architecture",
                "difficulty": "Medium",
                "keywords": ["ssr", "csr", "seo", "bundle", "hydration", "performance", "first contentful paint", "react"],
                "model_answer": "In CSR (traditional SPA with React/Vue), the server sends a minimal HTML shell and a large JavaScript bundle; the client browser executes the JS to render UI. In SSR (Next.js/Nuxt), the server renders full HTML on demand per request and streams it to the browser, followed by hydration. Choose SSR when SEO, fast First Contentful Paint, and link previews are critical (e.g. e-commerce, blogs). Choose CSR for interactive dashboards and SaaS portals where SEO is not a priority."
            },
            {
                "q": "How do JWT (JSON Web Tokens) work for user authentication, and where should they be safely stored?",
                "type": "Security",
                "difficulty": "Medium",
                "keywords": ["jwt", "token", "header", "payload", "signature", "http-only", "cookie", "xss", "csrf"],
                "model_answer": "A JWT contains three parts separated by dots: Header, Payload, and Signature. The server signs the token using a secret or private key upon login. The client attaches it to subsequent requests (e.g. Authorization: Bearer <token>). For security, tokens should NOT be stored in localStorage due to vulnerability to XSS (Cross-Site Scripting) attacks. The best practice is storing them in an HTTP-only, Secure, SameSite cookie, combined with short-lived access tokens and refresh token rotation."
            },
            {
                "q": "What is the Virtual DOM in React and how does the reconciliation algorithm optimize rendering?",
                "type": "Technical",
                "difficulty": "Medium",
                "keywords": ["virtual dom", "reconciliation", "diffing", "render", "state", "batching", "performance"],
                "model_answer": "The Virtual DOM is a lightweight in-memory JavaScript representation of the real browser DOM. When a component's state or props change, React creates a new Virtual DOM tree and runs its diffing algorithm (reconciliation) to compare it with the previous snapshot. Instead of updating the entire real DOM (which is expensive and causes browser reflows), React computes the minimal set of real DOM mutations needed and applies them in batches."
            }
        ],
        "Database Management Systems": [
            {
                "q": "What are ACID properties in relational databases and why are they important?",
                "type": "Core",
                "difficulty": "Easy",
                "keywords": ["acid", "atomicity", "consistency", "isolation", "durability", "transaction", "rollback", "commit"],
                "model_answer": "ACID guarantees transactional reliability in relational databases: 1) Atomicity: All operations in a transaction succeed, or the entire transaction is rolled back (all-or-nothing). 2) Consistency: A transaction transitions the database from one valid state to another according to schema constraints. 3) Isolation: Concurrent transactions do not interfere with one another (managed via isolation levels like Read Committed, Serializable). 4) Durability: Once committed, updates are permanently preserved even during system crashes."
            },
            {
                "q": "Explain how database indexing works (e.g. B-Trees) and what the trade-offs are.",
                "type": "Performance",
                "difficulty": "Medium",
                "keywords": ["index", "b-tree", "b+tree", "lookup", "binary", "write", "insert", "storage", "performance"],
                "model_answer": "An index is a data structure (typically a self-balancing B+Tree) that sorts table columns to allow logarithmic O(log N) lookups instead of sequential full table scans O(N). Trade-offs: While indexes dramatically accelerate SELECT queries and WHERE/JOIN filters, they consume extra disk storage and slow down INSERT, UPDATE, and DELETE operations because the index tree must be rebalanced upon every mutation."
            },
            {
                "q": "When would you choose a NoSQL database (like MongoDB or Cassandra) over a Relational SQL database (like PostgreSQL)?",
                "type": "System Design",
                "difficulty": "Medium",
                "keywords": ["nosql", "sql", "relational", "schema", "scale", "horizontal", "vertical", "acid", "document"],
                "model_answer": "Choose SQL when you have structured data requiring strict relational integrity, complex multi-table JOINs, and strict ACID guarantees (e.g. financial transactions, order processing). Choose NoSQL when: 1) You require flexible, polymorphic or evolving schema (Document stores like MongoDB), 2) Massive write throughput with horizontal partitioning across clusters (Columnar like Cassandra), or 3) Ultra-low latency key-value caching (Redis)."
            }
        ],
        "System Design & Architecture": [
            {
                "q": "How would you design a rate limiter for an API handling millions of requests per minute?",
                "type": "System Design",
                "difficulty": "Hard",
                "keywords": ["rate limiter", "token bucket", "leaky bucket", "redis", "sliding window", "distributed", "429", "latency"],
                "model_answer": "To build a scalable rate limiter: 1) Algorithm: Token Bucket or Sliding Window Counter offers great balance between burst handling and memory efficiency. 2) Storage: Use an in-memory datastore like Redis cluster with Redis Lua scripts for atomic increments and TTL expiry to avoid race conditions. 3) Architecture: Place the rate limiter at the API Gateway layer (Kong, Envoy, or Cloudflare) so unauthorized requests are rejected early with HTTP 429 Too Many Requests before hitting internal microservices."
            },
            {
                "q": "Explain the CAP Theorem. Can a distributed system achieve all three guarantees?",
                "type": "Theory",
                "difficulty": "Medium",
                "keywords": ["cap", "consistency", "availability", "partition tolerance", "network", "distributed", "trade-off"],
                "model_answer": "The CAP Theorem states that in a distributed data store, you can only guarantee two out of three properties simultaneously: Consistency (all nodes see identical data at the same moment), Availability (every non-failing node returns a response), and Partition Tolerance (the system continues operating despite dropped network packets between nodes). In reality, network partitions (P) are unavoidable in distributed hardware, so systems must choose between CP (Consistency over Availability, e.g. HBase, CockroachDB) or AP (Availability over Consistency, e.g. Cassandra, DynamoDB with eventual consistency)."
            }
        ],
        "Cloud, DevOps & Networks": [
            {
                "q": "What happens under the hood when a user types a URL (like https://google.com) into their browser and presses Enter?",
                "type": "Core",
                "difficulty": "Medium",
                "keywords": ["dns", "tcp", "handshake", "tls", "ssl", "http", "ip", "arp", "render", "syn", "ack"],
                "model_answer": "1) URL Parsing & DNS Lookup: The browser checks local cache, then queries recursive DNS resolvers to resolve domain name to an IP address. 2) TCP 3-Way Handshake: Client and server establish connection via SYN, SYN-ACK, ACK. 3) TLS Handshake: Cryptographic keys and certificates are exchanged for HTTPS encryption. 4) HTTP Request: Browser transmits HTTP GET request. 5) Server Response: Web server/load balancer processes request and returns HTTP 200 with HTML payload. 6) Browser Rendering: Browser parses HTML to DOM, CSS to CSSOM, executes JS, and renders the webpage."
            },
            {
                "q": "What is the difference between a Container (Docker) and a Virtual Machine (VM)?",
                "type": "DevOps",
                "difficulty": "Easy",
                "keywords": ["docker", "container", "vm", "hypervisor", "kernel", "guest os", "isolation", "lightweight"],
                "model_answer": "Virtual Machines run on a Hypervisor (Type 1 or Type 2) and package an entire Guest Operating System along with kernel and virtualized hardware, making them heavy (gigabytes) and slower to boot. Containers virtualize at the OS level, sharing the host machine's Linux kernel while isolating processes using Linux namespaces and cgroups. Containers are lightweight (megabytes), boot in milliseconds, and consume far less CPU and memory."
            }
        ],
        "Data Structures & Algorithms": [
            {
                "q": "Explain the difference between Breadth-First Search (BFS) and Depth-First Search (DFS). When would you prefer BFS over DFS?",
                "type": "Algorithm",
                "difficulty": "Easy",
                "keywords": ["bfs", "dfs", "queue", "stack", "shortest path", "recursion", "graph", "tree", "level"],
                "model_answer": "BFS traverses a graph or tree level by level using a FIFO Queue, whereas DFS explores as deep as possible along each branch before backtracking using a LIFO Stack or recursion. Prefer BFS when searching for the shortest path in an unweighted graph, finding nearest neighbors, or exploring peer nodes. Prefer DFS when solving mazes, detecting cycles, topological sorting, or when memory is constrained on wide trees."
            },
            {
                "q": "How does a Hash Table achieve O(1) average time complexity, and how are hash collisions handled?",
                "type": "Data Structure",
                "difficulty": "Medium",
                "keywords": ["hash", "hash table", "collision", "chaining", "open addressing", "load factor", "o(1)"],
                "model_answer": "A hash table uses a hash function to map keys to bucket indices in an underlying array, enabling constant-time O(1) access. Collisions happen when two distinct keys produce the same index. They are handled by: 1) Separate Chaining: Each bucket stores a linked list or balanced binary search tree of colliding key-value pairs. 2) Open Addressing: When a collision occurs, the table probes for the next open slot (linear probing, quadratic probing, or double hashing). When load factor exceeds a threshold (typically 0.75), the table doubles its capacity and rehashes."
            }
        ],
        "HR & Behavioral": [
            {
                "q": "Tell me about a time you faced a difficult technical challenge or bug. How did you resolve it?",
                "type": "STAR Behavioral",
                "difficulty": "Medium",
                "keywords": ["situation", "task", "action", "result", "debug", "solution", "team", "learned"],
                "model_answer": "In STAR format: Situation: During final deployment of our web portal, API response times spiked by 400% under modest traffic. Task: As lead developer, I had to identify the root cause and restore normal performance before launch. Action: I instrumented database APM logs and discovered an N+1 query vulnerability in our user profile service. I refactored the ORM queries using eager loading (JOINs) and added Redis caching for frequent reads. Result: Query execution dropped from 1800ms to 45ms, and the application smoothly handled 10,000 concurrent simulated users during launch."
            },
            {
                "q": "How do you handle disagreements with a teammate regarding technical architecture or code design?",
                "type": "Behavioral",
                "difficulty": "Medium",
                "keywords": ["listen", "objective", "data", "compromise", "code review", "respect", "team", "consensus"],
                "model_answer": "I focus on the objective requirements rather than personal pride. First, I actively listen to understand my teammate's perspective and rationale. Second, we evaluate both approaches against objective criteria: performance benchmarks, maintainability, scalability, and delivery timelines. If needed, we build a quick Proof of Concept (POC) to test real metrics, or seek input from a senior architect. Once a decision is made, I commit fully to the agreed direction."
            },
            {
                "q": "Where do you see yourself in 3 to 5 years in your engineering career?",
                "type": "Career",
                "difficulty": "Easy",
                "keywords": ["growth", "leadership", "technical", "skills", "impact", "mentorship", "architecture"],
                "model_answer": "Over the next 3 to 5 years, my goal is to evolve into a well-rounded senior engineer. In the first 1-2 years, I want to master the company's tech stack, deliver high-impact features, and contribute clean, tested code. By years 3-5, I want to take ownership of end-to-end system architectures, mentor junior engineers, and bridge technical execution with business strategy to deliver scalable products."
            }
        ]
    }

    def __init__(self):
        self.provider = os.getenv("AI_PROVIDER", "gemini").lower()
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.groq_api_key = os.getenv("GROQ_API_KEY", "")
        self.custom_api_url = os.getenv("CUSTOM_API_URL", "")
        self.custom_api_key = os.getenv("CUSTOM_API_KEY", "")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.groq_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    def get_config(self):
        """Returns non-sensitive configuration state to frontend."""
        has_gemini = bool(self.gemini_api_key and len(self.gemini_api_key.strip()) > 5)
        has_openai = bool(self.openai_api_key and len(self.openai_api_key.strip()) > 5)
        has_groq = bool(self.groq_api_key and len(self.groq_api_key.strip()) > 5)
        has_custom = bool(self.custom_api_url and len(self.custom_api_url.strip()) > 5)

        active = self.provider
        # If active provider has no key and isn't offline, check if any other has key
        if active == "gemini" and not has_gemini:
            if has_openai: active = "openai"
            elif has_groq: active = "groq"
            else: active = "offline"
        elif active == "openai" and not has_openai:
            if has_gemini: active = "gemini"
            elif has_groq: active = "groq"
            else: active = "offline"

        return {
            "active_provider": active,
            "configured": {
                "gemini": has_gemini,
                "openai": has_openai,
                "groq": has_groq,
                "custom": has_custom,
                "offline": True
            },
            "models": {
                "gemini": self.gemini_model,
                "openai": self.openai_model,
                "groq": self.groq_model
            },
            "domains": self.DEFAULT_DOMAINS
        }

    def update_config(self, data):
        """Update API keys and providers dynamically and update .env."""
        if "provider" in data:
            self.provider = str(data["provider"]).lower()
        if "gemini_api_key" in data and data["gemini_api_key"]:
            self.gemini_api_key = str(data["gemini_api_key"]).strip()
        if "openai_api_key" in data and data["openai_api_key"]:
            self.openai_api_key = str(data["openai_api_key"]).strip()
        if "groq_api_key" in data and data["groq_api_key"]:
            self.groq_api_key = str(data["groq_api_key"]).strip()
        if "gemini_model" in data and data["gemini_model"]:
            self.gemini_model = str(data["gemini_model"]).strip()
        if "openai_model" in data and data["openai_model"]:
            self.openai_model = str(data["openai_model"]).strip()
        if "groq_model" in data and data["groq_model"]:
            self.groq_model = str(data["groq_model"]).strip()

        # Persist to .env
        self._save_to_env()
        return self.get_config()

    def _save_to_env(self):
        try:
            env_content = f"""# AI Interview Preparation Assistant Environment Variables
AI_PROVIDER={self.provider}
GEMINI_API_KEY={self.gemini_api_key}
GEMINI_MODEL={self.gemini_model}
OPENAI_API_KEY={self.openai_api_key}
OPENAI_MODEL={self.openai_model}
GROQ_API_KEY={self.groq_api_key}
GROQ_MODEL={self.groq_model}
CUSTOM_API_URL={self.custom_api_url}
CUSTOM_API_KEY={self.custom_api_key}
"""
            with open(".env", "w", encoding="utf-8") as f:
                f.write(env_content)
        except Exception as e:
            print("Failed to save .env file:", e)

    def test_connection(self, provider=None, key=None, model=None):
        """Quickly tests an AI provider connection and returns latency & status."""
        test_prov = (provider or self.provider).lower()
        start_time = time.time()

        if test_prov == "offline":
            return {"success": True, "message": "Offline Smart Heuristic Mode is ready and active.", "latency_ms": 2}

        if test_prov == "gemini":
            api_key = key or self.gemini_api_key
            model_name = model or self.gemini_model
            if not api_key:
                return {"success": False, "message": "No Google Gemini API key provided."}
            try:
                # Try google-genai SDK first
                from google import genai
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model=model_name,
                    contents="Respond with only the single word: OK"
                )
                latency = round((time.time() - start_time) * 1000)
                if response and response.text:
                    return {"success": True, "message": f"Successfully connected to Gemini ({model_name})!", "latency_ms": latency}
                else:
                    return {"success": False, "message": "Gemini returned an empty response."}
            except Exception as e:
                # Fallback to direct REST API ping
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
                    headers = {"Content-Type": "application/json"}
                    payload = {"contents": [{"parts": [{"text": "Say OK"}]}]}
                    res = requests.post(url, headers=headers, json=payload, timeout=10)
                    latency = round((time.time() - start_time) * 1000)
                    if res.status_code == 200:
                        return {"success": True, "message": f"Successfully connected to Gemini REST API ({model_name})!", "latency_ms": latency}
                    return {"success": False, "message": f"Gemini API Error ({res.status_code}): {res.text}"}
                except Exception as rest_err:
                    return {"success": False, "message": f"Connection failed: {str(e)}"}

        elif test_prov == "openai":
            api_key = key or self.openai_api_key
            model_name = model or self.openai_model
            if not api_key:
                return {"success": False, "message": "No OpenAI API key provided."}
            try:
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                payload = {
                    "model": model_name,
                    "messages": [{"role": "user", "content": "Respond with OK"}],
                    "max_tokens": 10
                }
                res = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=10)
                latency = round((time.time() - start_time) * 1000)
                if res.status_code == 200:
                    return {"success": True, "message": f"Successfully connected to OpenAI ({model_name})!", "latency_ms": latency}
                return {"success": False, "message": f"OpenAI Error ({res.status_code}): {res.text}"}
            except Exception as e:
                return {"success": False, "message": f"OpenAI connection error: {str(e)}"}

        elif test_prov == "groq":
            api_key = key or self.groq_api_key
            model_name = model or self.groq_model
            if not api_key:
                return {"success": False, "message": "No Groq API key provided."}
            try:
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                payload = {
                    "model": model_name,
                    "messages": [{"role": "user", "content": "Respond with OK"}],
                    "max_tokens": 10
                }
                res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=10)
                latency = round((time.time() - start_time) * 1000)
                if res.status_code == 200:
                    return {"success": True, "message": f"Successfully connected to Groq ({model_name})!", "latency_ms": latency}
                return {"success": False, "message": f"Groq Error ({res.status_code}): {res.text}"}
            except Exception as e:
                return {"success": False, "message": f"Groq connection error: {str(e)}"}

        return {"success": False, "message": f"Unknown provider: {test_prov}"}

    def _call_llm(self, prompt, system_instruction=None, json_mode=True):
        """Unified LLM call supporting Gemini, OpenAI, Groq, or fallback to None."""
        config = self.get_config()
        active = config["active_provider"]

        if active == "gemini" and self.gemini_api_key:
            try:
                from google import genai
                client = genai.Client(api_key=self.gemini_api_key)
                full_prompt = prompt
                if system_instruction:
                    full_prompt = f"System Instruction: {system_instruction}\n\nUser Request:\n{prompt}"
                if json_mode:
                    full_prompt += "\n\nCRITICAL: Return strictly valid raw JSON only without markdown formatting or code blocks."

                response = client.models.generate_content(
                    model=self.gemini_model,
                    contents=full_prompt
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                print("Gemini SDK error, falling back to REST or alternative:", e)
                # Try REST API for Gemini
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.gemini_model}:generateContent?key={self.gemini_api_key}"
                    headers = {"Content-Type": "application/json"}
                    payload = {"contents": [{"parts": [{"text": full_prompt}]}]}
                    res = requests.post(url, headers=headers, json=payload, timeout=20)
                    if res.status_code == 200:
                        data = res.json()
                        text = data['candidates'][0]['content']['parts'][0]['text']
                        return text
                except Exception as rest_e:
                    print("Gemini REST error:", rest_e)

        elif active == "openai" and self.openai_api_key:
            try:
                headers = {"Authorization": f"Bearer {self.openai_api_key}", "Content-Type": "application/json"}
                messages = []
                if system_instruction:
                    messages.append({"role": "system", "content": system_instruction})
                messages.append({"role": "user", "content": prompt + ("\n\nReturn strictly valid JSON only." if json_mode else "")})
                payload = {
                    "model": self.openai_model,
                    "messages": messages,
                    "temperature": 0.7
                }
                if json_mode and "gpt-4" in self.openai_model:
                    payload["response_format"] = {"type": "json_object"}

                res = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=20)
                if res.status_code == 200:
                    data = res.json()
                    return data["choices"][0]["message"]["content"]
            except Exception as e:
                print("OpenAI API error:", e)

        elif active == "groq" and self.groq_api_key:
            try:
                headers = {"Authorization": f"Bearer {self.groq_api_key}", "Content-Type": "application/json"}
                messages = []
                if system_instruction:
                    messages.append({"role": "system", "content": system_instruction})
                messages.append({"role": "user", "content": prompt + ("\n\nReturn strictly valid JSON only." if json_mode else "")})
                payload = {
                    "model": self.groq_model,
                    "messages": messages,
                    "temperature": 0.7
                }
                res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=20)
                if res.status_code == 200:
                    data = res.json()
                    return data["choices"][0]["message"]["content"]
            except Exception as e:
                print("Groq API error:", e)

        return None

    def _clean_json_response(self, raw_text):
        """Clean markdown markers and parse JSON safely."""
        if not raw_text:
            return None
        text = raw_text.strip()
        # Remove markdown triple backtick fences if present
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.MULTILINE)
        text = re.sub(r"\s*```$", "", text, flags=re.MULTILINE)
        text = text.strip()

        # Find first { and last }
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(text[start:end+1])
            except Exception as e:
                print("JSON parse error:", e, "Raw text:", text)
        return None

    def generate_question(self, domain, experience_level="Fresher / Junior", difficulty="Medium", job_role="Software Engineer", previous_questions=None):
        """
        Dynamically generates an interview question using the configured AI model.
        Falls back seamlessly to curated question bank if offline or API is unavailable.
        """
        previous_questions = previous_questions or []
        system_prompt = (
            "You are an expert technical interviewer and hiring manager at a top technology company. "
            "Your job is to generate a realistic, thought-provoking, and practical interview question "
            "tailored to the candidate's chosen domain, experience level, and role."
        )

        prompt = f"""
Generate an interview question for:
- Domain: {domain}
- Target Role: {job_role}
- Experience Level: {experience_level}
- Difficulty Level: {difficulty}
- Previously asked questions to avoid: {json.dumps(previous_questions[-6:])}

Please return a single JSON object with these exact keys:
{{
  "question": "The interview question text",
  "type": "Conceptual | Problem-Solving | Architecture | Scenario | Behavioral",
  "difficulty": "{difficulty}",
  "domain": "{domain}",
  "hints": ["A helpful nudge or key aspect the candidate should address in their answer"],
  "expected_key_points": ["Key point 1", "Key point 2", "Key point 3"],
  "context": "Brief 1-sentence context on why this question matters in real-world engineering."
}}
"""
        raw_res = self._call_llm(prompt, system_instruction=system_prompt, json_mode=True)
        parsed = self._clean_json_response(raw_res)

        if parsed and "question" in parsed:
            return {
                "q": parsed["question"],
                "type": parsed.get("type", "Technical"),
                "difficulty": parsed.get("difficulty", difficulty),
                "domain": domain,
                "hints": parsed.get("hints", ["Structure your answer logically and explain with an example."]),
                "expected_key_points": parsed.get("expected_key_points", []),
                "context": parsed.get("context", "Common interview question testing fundamentals and clarity."),
                "source": "AI Model"
            }

        # Seamless Offline Fallback
        return self._offline_get_question(domain, difficulty, previous_questions)

    def _offline_get_question(self, domain, difficulty, previous_questions):
        """Picks a question from the curated offline question bank."""
        pool = self.OFFLINE_QUESTIONS.get(domain)
        if not pool:
            # Try to match substring
            for k in self.OFFLINE_QUESTIONS:
                if domain.lower() in k.lower() or k.lower() in domain.lower():
                    pool = self.OFFLINE_QUESTIONS[k]
                    break
        if not pool:
            pool = self.OFFLINE_QUESTIONS["Artificial Intelligence & ML"]

        # Filter out questions already asked if possible
        unasked = [item for item in pool if item["q"] not in previous_questions]
        chosen = random.choice(unasked) if unasked else random.choice(pool)

        return {
            "q": chosen["q"],
            "type": chosen.get("type", "Technical"),
            "difficulty": chosen.get("difficulty", difficulty),
            "domain": domain,
            "hints": ["Define the core concept clearly, compare with alternatives, and give a short real-world example."],
            "expected_key_points": chosen.get("keywords", [])[:5],
            "context": "Standard industry interview topic.",
            "source": "Curated Offline Engine"
        }

    def evaluate_answer(self, question, answer, domain="General", experience_level="Junior", is_follow_up=False, parent_question=""):
        """
        Deeply evaluates a candidate's answer using the AI Model.
        Returns:
          - accuracy (0-10)
          - relevance (0-10)
          - communication (0-10)
          - technical_depth (0-10)
          - overall (0-10)
          - strengths (list)
          - improvements (list)
          - missing_points (list)
          - feedback (paragraph)
          - ideal_answer (model response)
          - follow_up_question (dynamic interviewer follow-up)
        """
        clean_answer = (answer or "").strip()
        if not clean_answer or len(clean_answer.split()) < 3:
            return {
                "accuracy": 0.0,
                "relevance": 0.0,
                "communication": 0.0,
                "technical_depth": 0.0,
                "overall": 0.0,
                "strengths": ["None noted — the response was empty or too brief."],
                "improvements": ["Provide a complete response answering all parts of the question.", "Use at least 2-4 structured sentences with technical terms."],
                "missing_points": ["Core definitions", "Mechanisms / How it works", "Practical examples"],
                "feedback": "No substantial answer was submitted. Please attempt to explain the concept or structure your thoughts.",
                "ideal_answer": self._get_offline_model_answer(question),
                "follow_up_question": "Would you like to try explaining this concept in your own words first?",
                "source": "AI Evaluator"
            }

        system_prompt = (
            "You are a Senior Principal Interviewer at a premier technology company. "
            "You are conducting a live interview evaluation. Evaluate the candidate's answer constructively, "
            "rigorously, and fairly against industry hiring standards. "
            "Provide quantitative scoring and actionable qualitative guidance."
        )

        prompt = f"""
Domain: {domain}
Experience Level: {experience_level}
Interview Question: {question}
Candidate's Answer: {clean_answer}

Perform a comprehensive evaluation and return a single valid JSON object with the following schema:
{{
  "accuracy": <float 0.0 to 10.0 representing factual/technical correctness>,
  "relevance": <float 0.0 to 10.0 representing how directly and fully it answers the specific question asked>,
  "communication": <float 0.0 to 10.0 representing clarity, structure, tone, grammar, and articulation>,
  "technical_depth": <float 0.0 to 10.0 representing depth of knowledge, trade-offs, and nuances>,
  "overall": <float 0.0 to 10.0, weighted: 0.35*accuracy + 0.25*relevance + 0.20*technical_depth + 0.20*communication>,
  "strengths": [<list of 2-3 specific things the candidate explained well or got right>],
  "improvements": [<list of 2-3 specific actionable things to improve or clarify>],
  "missing_points": [<list of 1-3 key concepts, terms, or trade-offs the candidate missed>],
  "feedback": "<2-4 sentences of personalized, constructive feedback as an interviewer>",
  "ideal_answer": "<A comprehensive, stellar 3-5 sentence model answer demonstrating how a top candidate would answer this>",
  "follow_up_question": "<A natural, insightful follow-up question that challenges the candidate further on their answer>"
}}
"""
        raw_res = self._call_llm(prompt, system_instruction=system_prompt, json_mode=True)
        parsed = self._clean_json_response(raw_res)

        if parsed and "overall" in parsed:
            # Normalize and clamp scores
            accuracy = round(max(0.0, min(10.0, float(parsed.get("accuracy", 6.0)))), 1)
            relevance = round(max(0.0, min(10.0, float(parsed.get("relevance", 6.0)))), 1)
            communication = round(max(0.0, min(10.0, float(parsed.get("communication", 6.0)))), 1)
            technical_depth = round(max(0.0, min(10.0, float(parsed.get("technical_depth", 6.0)))), 1)
            overall = round(max(0.0, min(10.0, float(parsed.get("overall", (accuracy*0.35 + relevance*0.25 + technical_depth*0.20 + communication*0.20))))), 1)

            return {
                "accuracy": accuracy,
                "relevance": relevance,
                "communication": communication,
                "technical_depth": technical_depth,
                "overall": overall,
                "strengths": parsed.get("strengths", ["Addressed the core question"]),
                "improvements": parsed.get("improvements", ["Provide a concrete real-world example"]),
                "missing_points": parsed.get("missing_points", []),
                "feedback": parsed.get("feedback", "Good effort. Incorporate more technical nuances and examples."),
                "ideal_answer": parsed.get("ideal_answer", ""),
                "follow_up_question": parsed.get("follow_up_question", ""),
                "source": "AI Model"
            }

        # Offline Intelligent Fallback Evaluation
        return self._offline_evaluate_answer(question, clean_answer, domain)

    def _get_offline_model_answer(self, question):
        for domain_list in self.OFFLINE_QUESTIONS.values():
            for item in domain_list:
                if item["q"].lower() in question.lower() or question.lower() in item["q"].lower():
                    return item.get("model_answer", "")
        return "An ideal answer should state the clear definition, explain the underlying mechanism or principles, contrast with alternatives, and illustrate with a practical engineering example."

    def _offline_evaluate_answer(self, question, answer, domain):
        """Intelligent heuristic evaluator when offline or no API key is provided."""
        words = set(re.findall(r"\w+", answer.lower()))
        word_count = len(answer.split())

        # Find matching question in database
        matched_item = None
        for domain_list in self.OFFLINE_QUESTIONS.values():
            for item in domain_list:
                if item["q"].lower() in question.lower() or question.lower() in item["q"].lower():
                    matched_item = item
                    break
            if matched_item:
                break

        keywords = matched_item.get("keywords", ["structure", "system", "performance", "method", "data"]) if matched_item else ["system", "concept", "example", "process"]
        matched_kw = [k for k in keywords if k.lower() in words]

        kw_ratio = len(matched_kw) / max(1, len(keywords))
        kw_score = min(10.0, round(kw_ratio * 10, 1))

        # Length / completeness scoring
        # ~60-120 words is typical good interview response length
        if word_count < 20:
            length_factor = word_count / 20.0 * 5.0
        elif word_count <= 100:
            length_factor = 5.0 + ((word_count - 20) / 80.0) * 5.0
        else:
            length_factor = 9.5

        # Communication scoring (capitalization, punctuation, sentence structure)
        has_sentences = len(re.split(r"[.!?]+", answer)) >= 2
        starts_capital = answer[0].isupper() if answer else False
        comm_score = 9.0 if (has_sentences and starts_capital and word_count >= 30) else (7.0 if starts_capital else 5.0)

        accuracy = min(10.0, round(kw_score * 0.6 + length_factor * 0.4, 1))
        relevance = min(10.0, round(kw_score * 0.7 + length_factor * 0.3, 1))
        tech_depth = min(10.0, round(kw_score * 0.8 + length_factor * 0.2, 1))
        overall = round(accuracy * 0.35 + relevance * 0.25 + tech_depth * 0.20 + comm_score * 0.20, 1)

        missing = [k for k in keywords if k.lower() not in words][:3]
        strengths = []
        if matched_kw:
            strengths.append(f"Correctly referenced key terminology: {', '.join(matched_kw[:3])}.")
        if word_count >= 40:
            strengths.append("Provided a reasonably detailed explanation.")
        else:
            strengths.append("Addressed the question promptly.")

        improvements = []
        if missing:
            improvements.append(f"Incorporate related concepts such as: {', '.join(missing)}.")
        if word_count < 45:
            improvements.append("Elaborate on the mechanism with a real-world scenario or architecture example.")
        improvements.append("Structure answers using clear stages: Definition, Mechanism, Trade-offs.")

        if overall >= 8.0:
            feedback = "Excellent response! Clear technical precision with relevant vocabulary and structure."
        elif overall >= 6.0:
            feedback = "Solid foundation. Deepen your explanation by addressing underlying trade-offs and adding a practical example."
        else:
            feedback = "Good start, but your answer lacks sufficient technical depth and key terms. Review the model answer below."

        ideal = matched_item.get("model_answer", self._get_offline_model_answer(question)) if matched_item else self._get_offline_model_answer(question)
        follow_up = f"Could you provide a concrete production example where you applied this, and discuss any trade-offs you encountered?"

        return {
            "accuracy": accuracy,
            "relevance": relevance,
            "communication": round(comm_score, 1),
            "technical_depth": tech_depth,
            "overall": overall,
            "strengths": strengths,
            "improvements": improvements,
            "missing_points": missing,
            "feedback": feedback,
            "ideal_answer": ideal,
            "follow_up_question": follow_up,
            "source": "Smart Heuristic Engine"
        }

    def generate_session_summary(self, candidate_name="Candidate", domain="General", experience_level="Junior", results=None):
        """
        Produces a comprehensive final interview debrief, hiring verdict,
        radar metrics, and customized study roadmap using AI.
        """
        results = results or []
        if not results:
            return {
                "candidate_name": candidate_name,
                "overall_score": 0.0,
                "verdict": "Incomplete Session",
                "summary": "No questions were evaluated in this session.",
                "roadmap": ["Start a new practice interview session."],
                "category_scores": {"accuracy": 0, "relevance": 0, "communication": 0, "technical_depth": 0}
            }

        scores = [r.get("score", 0.0) for r in results]
        avg_score = round(sum(scores) / len(scores), 1)

        # Average criteria
        acc_list = [r.get("accuracy", r.get("score", 0)) for r in results]
        rel_list = [r.get("relevance", r.get("score", 0)) for r in results]
        comm_list = [r.get("communication", r.get("score", 0)) for r in results]
        tech_list = [r.get("technical_depth", r.get("score", 0)) for r in results]

        avg_acc = round(sum(acc_list) / len(acc_list), 1)
        avg_rel = round(sum(rel_list) / len(rel_list), 1)
        avg_comm = round(sum(comm_list) / len(comm_list), 1)
        avg_tech = round(sum(tech_list) / len(tech_list), 1)

        # Hiring Verdict
        if avg_score >= 8.5:
            verdict = "Strong Hire 🌟"
            status_desc = "Outstanding performance! Demonstrates deep domain expertise, articulate communication, and strong problem-solving acumen."
        elif avg_score >= 7.0:
            verdict = "Hire 👍"
            status_desc = "Good candidate foundation. Meets expectations for the role with solid understanding of core principles."
        elif avg_score >= 5.5:
            verdict = "Leaning Hire / Needs Practice ⚠️"
            status_desc = "Acceptable conceptual familiarity, but needs more depth, precision, and structured real-world examples."
        else:
            verdict = "Needs Significant Preparation ❌"
            status_desc = "Critical foundational gaps identified. Recommend structured study on core domain concepts before interviewing."

        prompt = f"""
Candidate: {candidate_name}
Domain: {domain}
Experience Level: {experience_level}
Questions Answered: {len(results)}
Overall Average Score: {avg_score}/10
Criteria Scores: Accuracy: {avg_acc}, Relevance: {avg_rel}, Communication: {avg_comm}, Technical Depth: {avg_tech}
Results Details:
{json.dumps([{"q": r.get("question"), "score": r.get("score"), "strengths": r.get("strengths", []), "improvements": r.get("improvements", [])} for r in results], indent=2)}

Generate a personalized interview debrief and structured 3-step preparation roadmap.
Return a valid JSON object:
{{
  "verdict": "{verdict}",
  "hiring_status": "{status_desc}",
  "executive_summary": "<A 2-3 sentence executive evaluation summarizing the candidate's strongest points and main blindspots>",
  "key_strengths": ["Strength 1", "Strength 2"],
  "critical_gaps": ["Gap 1", "Gap 2"],
  "preparation_roadmap": [
    "Step 1: Focus area and targeted study",
    "Step 2: Recommended practice methodology",
    "Step 3: Mock interview strategy"
  ]
}}
"""
        raw_res = self._call_llm(prompt, json_mode=True)
        parsed = self._clean_json_response(raw_res)

        if parsed:
            return {
                "candidate_name": candidate_name,
                "overall_score": avg_score,
                "verdict": parsed.get("verdict", verdict),
                "hiring_status": parsed.get("hiring_status", status_desc),
                "executive_summary": parsed.get("executive_summary", status_desc),
                "key_strengths": parsed.get("key_strengths", ["Solid effort across technical questions."]),
                "critical_gaps": parsed.get("critical_gaps", ["Explain trade-offs and underlying mechanics."]),
                "preparation_roadmap": parsed.get("preparation_roadmap", [
                    "Review domain fundamentals and practice defining concepts in 2 clear sentences.",
                    "Adopt the STAR method for behavioral and scenario questions.",
                    "Practice explaining code architectures and performance trade-offs out loud."
                ]),
                "category_scores": {
                    "accuracy": avg_acc,
                    "relevance": avg_rel,
                    "communication": avg_comm,
                    "technical_depth": avg_tech
                }
            }

        # Offline fallback summary
        return {
            "candidate_name": candidate_name,
            "overall_score": avg_score,
            "verdict": verdict,
            "hiring_status": status_desc,
            "executive_summary": status_desc,
            "key_strengths": [
                f"Demonstrated good baseline knowledge across {domain}.",
                "Clear effort in structuring responses."
            ],
            "critical_gaps": [
                "Include more domain-specific terminology and architecture examples.",
                "Discuss engineering trade-offs and edge cases."
            ],
            "preparation_roadmap": [
                f"1. Deepen your study of core {domain} patterns and internal mechanics.",
                "2. Practice the STAR framework (Situation, Task, Action, Result) for clarity.",
                "3. Perform 3-5 mock interview drills weekly with timed answer delivery."
            ],
            "category_scores": {
                "accuracy": avg_acc,
                "relevance": avg_rel,
                "communication": avg_comm,
                "technical_depth": avg_tech
            }
        }

# Global singleton engine instance
engine = InterviewAIEngine()
