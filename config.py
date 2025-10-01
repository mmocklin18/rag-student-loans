from langchain.prompts import PromptTemplate

BASE_URL = "https://www.consumerfinance.gov"

LISTING_PAGES = [
    "https://www.consumerfinance.gov/consumer-tools/student-loans/answers/basics/?page=1",
    "https://www.consumerfinance.gov/consumer-tools/student-loans/answers/basics/?page=2",
]

CFPB_BOILERPLATE = [
    # Standard disclaimer
    "Learn how the CFPB can help you",
    "The content on this page provides general consumer information.",
    "It is not legal advice or regulatory guidance.",
    "The CFPB updates this information periodically.",
    "We do not endorse the third-party or guarantee the accuracy of this third-party information.",
    "There may be other resources that also serve your needs.",

    # Site-specific extras
    "Searches are limited to",
    "Searches are limited to 75 characters.",
    "We're the Consumer Financial Protection Bureau",
    "View older versions of this page",
    "Page last modified",

    # Marketing / filler lines
    "Sign up for the latest financial tips and information right to your inbox.",
    "Read more about closing the deal",
    "Learn more about",
    "Learn more strategies",
    "Learn more options",
    "Learn more at the Department of Education’s",
]

CUSTOM_PROMPT_TEMPLATE = """
You are a financial aid assistant.

You will be given a set of retrieved documents from two sources:
- UGA FAQs (short Q&A entries, considered authoritative for UGA-specific policies)
- CFPB or DOE docs (longer explainers, considered general policy context)

Instructions:
1. If the user’s question is UGA-specific, always quote a UGA FAQ first.
2. If the question is general (repayment, default, forgiveness, etc.), prioritize general sources. 
3. If both are relevant, answer with the UGA FAQ first, then add supporting info from general sources.
4. If nothing is relevant, say you don’t have enough info.

{context}

Question: {question}
Answer:
"""