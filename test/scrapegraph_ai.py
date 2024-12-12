from scrapegraph_py import Client

"""
This is a sample script to demonstrate how to use the scrapegraph_py library.
"""
api_key = None

client = Client(api_key=api_key)

# Basic usage
response = client.smartscraper(
    website_url="https://www.philips.com.cn/",
    user_prompt="Bring up key information"
)

print(response)