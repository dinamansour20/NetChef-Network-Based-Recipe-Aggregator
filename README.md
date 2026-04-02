# NetChef-Network-Based-Recipe-Aggregator
Finding good recipes scattered across different websites can be frustrating and time-consuming. NetChef solves this by consolidating recipe data into a single, efficient platform. Built as a Python-based networked application, it pulls recipes from the Spoonacular API and organizes them based on user preferences such as specific ingredients, meal type, and dietary needs, all while prioritizing network performance and efficiency behind the scenes.

At its core, NetChef uses Flask to serve a lightweight backend that handles recipe search requests. Users can query by ingredient and meal category such as lunch, dinner, or breakfast, and the app returns structured recipe data from Spoonacular's REST API. To minimize redundant network calls and reduce bandwidth usage, the application integrates Redis as a caching layer. When a query has been made before, the cached response is served instantly instead of hitting the external API again. If Redis is unavailable, the app gracefully falls back to direct API requests, ensuring the user experience remains uninterrupted regardless of cache availability.

A major focus of this project is network traffic analysis and optimization. Using Wireshark, we captured and inspected HTTP/HTTPS packets to examine request and response sizes, TCP handshake behavior, and the differences between cached and uncached traffic patterns. This analysis helped identify inefficiencies such as repeated requests and unnecessary data transfers. The insights gained directly informed our caching and compression strategies moving forward.

Performance metrics are logged throughout the application. API response times are recorded to a CSV file and then visualized using Matplotlib and Pandas. The visualizations include API endpoint usage counts, HTTP status code distributions, request volume over time, and response time comparisons between lunch and dinner endpoints. These charts provide a clear, data-driven picture of how the application performs under different conditions and how each optimization impacts real-world usage.

Security is handled through environment variables managed by python-dotenv, keeping API keys out of the codebase. All external API communication uses HTTPS to prevent eavesdropping and data interception.

Tech Stack: Python, Flask, Redis, Spoonacular API, Wireshark, Matplotlib, Pandas, python-dotenv

Built for CSIT 340: Computer Networks at Montclair State University
