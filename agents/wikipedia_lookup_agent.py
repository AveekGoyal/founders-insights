import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import Tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
from tools import search_wiki_url, verify_wiki_page, get_wiki_content_from_url

load_dotenv()

def lookup(name: str, description: str = "") -> dict:
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
    
    # First search for Wikipedia URL using Tavily
    search_result = search_wiki_url(name)
    if "error" in search_result:
        return {"error": "Could not find Wikipedia URL", "details": search_result["error"]}
    
    wiki_url = search_result["url"]
    
    # Create tools for the agent to verify the page
    tools_for_agent = [
        Tool(
            name="Verify Wikipedia",
            description="Verify if a Wikipedia page matches the person we're looking for",
            func=lambda x: verify_wiki_page(x)
        )
    ]

    # Create the agent with a specific prompt for verification
    verify_template = """
    Given a person's name, description, and Wikipedia URL, verify if this is the correct person.
    
    Person's Name: {name}
    Description: {description}
    Wikipedia URL: {url}
    
    Steps:
    1. Get the Wikipedia page summary
    2. Compare it with the provided description
    3. Verify if key details match (role, company, achievements)
    4. You MUST end your response with one of these two exact phrases:
       - "Final Answer: Yes it definitely matches"
       - "Final Answer: No it does not match"
    
    Your final answer must be exactly one of these two options, with no additional explanation or caveats.
    If you are not 100% certain, answer "No it does not match".
    """

    prompt_template = PromptTemplate(
        template=verify_template,
        input_variables=["name", "description", "url"]
    )

    # Create and run the agent
    prompt = hub.pull("hwchase17/react")
    agent = create_react_agent(llm=llm, tools=tools_for_agent, prompt=prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools_for_agent, verbose=True)
    
    # First verify the Wikipedia page
    verify_result = agent_executor.invoke(
        {
            "input": prompt_template.format(
                name=name,
                description=description,
                url=wiki_url
            )
        }
    )
    
    # If verification failed with error
    if "error" in verify_result.get("output", "").lower():
        return {"error": "Could not verify Wikipedia page", "details": verify_result["output"]}
    
    # Simply check if the exact phrases we want are in the output
    output = verify_result.get("output", "")
    
    if output.strip() == "Yes it definitely matches":
        # Proceed with content fetching and JSON generation
        full_content = get_wiki_content_from_url(wiki_url)
        if "error" in full_content:
            return {"error": "Could not fetch Wikipedia content", "details": full_content["error"]}
        
        # Process the content with GPT-4
        template = """
        Given the following Wikipedia content about {name}, extract and organize their career information.
        
        Wikipedia Content:
        {wiki_content}
        
        Sections available:
        {sections}
        
        Format the response as a JSON object with the following structure:
        {{
            "short_description": "A brief one-line description focusing on current role and main achievement",
            "education": {{
                "degree": "Degree name (if available)",
                "institution": "Institution name",
                "field": "Field of study"
            }},
            "career": {{
                "current_role": {{
                    "title": "Current position (most recent)",
                    "company": "Current company",
                    "description": "Detailed description of current responsibilities",
                    "duration": "Specific time period (e.g., 2020 - Present)",
                    "achievements": [
                        "List current role achievements",
                        "Include ongoing projects"
                    ]
                }},
                "experience": [
                    {{
                        "company": "Company name",
                        "roles": [
                            {{
                                "title": "Specific role title",
                                "duration": "Exact time period",
                                "description": "Detailed role description",
                                "responsibilities": [
                                    "Key responsibility 1",
                                    "Key responsibility 2"
                                ],
                                "achievements": [
                                    "Specific achievement 1",
                                    "Project or initiative led",
                                    "Major milestone reached"
                                ]
                            }}
                        ]
                    }}
                ],
                "total_years_experience": "Calculate total years based on earliest position"
            }}
        }}
        """

        prompt_template = PromptTemplate(
            template=template,
            input_variables=["name", "wiki_content", "sections"]
        )

        result = llm.invoke(
            prompt_template.format(
                name=name,
                wiki_content=full_content["content"],
                sections=json.dumps(full_content["sections"], indent=2)
            )
        )
        
        # Clean and parse the response
        content = result.content
        if content.startswith("```") and content.endswith("```"):
            content = content.split("```")[1]
            if content.startswith("json\n"):
                content = content[5:]
        
        parsed_result = json.loads(content)
        parsed_result["source_url"] = wiki_url
        return parsed_result
    elif output.strip() == "No it does not match":
        return {
            "match": False,
            "reason": "Wikipedia page does not definitively match the person"
        }
    else:
        return {
            "match": False,
            "reason": "No final answer provided in verification"
        }

if __name__ == "__main__":
    name = "Brian Armstrong"
    description = "Coinbase	Founder/CEO"
    result = lookup(name, description)
    print(json.dumps(result, indent=2))
