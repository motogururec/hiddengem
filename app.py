import streamlit as st
import pandas as pd
import os
from langchain_groq import ChatGroq
import operator
import os
from typing import Annotated, Sequence, TypedDict , List
from crewai import Agent, Crew, Process, Task
import sys
from langchain.tools import tool
import praw
import time 
from crewai_tools import BaseTool
import re
from datetime import datetime
from stream import StreamToStreamlit
from reddidtrends import RedditTrends
from googletrends import GoogleTrends
from langchain.agents import Tool
from langchain_community.tools import DuckDuckGoSearchRun
import streamlit_shadcn_ui as ui


def main():
    with open( "style.css" ) as css:
        st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)
        

    
  
    # Set up the customization options
    st.sidebar.title('Customization')
    model = st.sidebar.selectbox(
        'Choose a model',
        ['llama3-8b-8192', 'mixtral-8x7b-32768', 'gemma-7b-it','llama3-70b-8192']
    )
    llm = ChatGroq(
            temperature=0, 
            groq_api_key = st.secrets["GROQ_API_KEY"], 
            model_name=model
        )
    
    with st.sidebar:
        st.markdown("---")
        st.markdown(
            '<h5>Made with ❤ in &nbsp<img src="https://streamlit.io/images/brand/streamlit-mark-color.png" alt="Streamlit logo" height="16">&nbsp by <a href="https://twitter.com/tuantruong">@tuantruong</a></h5>',
            unsafe_allow_html=True,
        )


    

    # Streamlit UI
    st.title(' SASS Niche Idea  - LLM CrewAI ')
    multiline_text = """
    The CrewAI Machine Learning Assistant is designed to guide you through the process of finding a niche in the tech industry.
    """
    

    st.markdown(multiline_text, unsafe_allow_html=True)
    subreddit = st.text_input("Enter the sub reddits that you want to search here:")
    #subreddit_name = st.text_input("Enter the subreddit name:")
    # google_trends = GoogleTrends()
    reddit_trends = RedditTrends()
    
    search = DuckDuckGoSearchRun()
    search_tool = Tool(
    name="duckduckgo_search", #match the name from crewai's Action: duckduckgo_search
    description="A search tool used to query DuckDuckGoSearchRun for search results when trying to find information from the internet.",
    func=search.run
)

  
    trigger_btn = ui.button(text="Get the ideas", key="trigger_btn")
  # Run the workflow
    if trigger_btn:
        niche_analyst = Agent(
            role="Niche Analyst",
            goal="Find inspiring SASS ideas from specified subreddits ",
            backstory="""You are an AI tasked with continuously monitoring specified subreddits to identify trending discussions around SaaS ideas. 
            Your discoveries will lay the groundwork for further market analysis and MVP feature recommendations.""",
            tools=[reddit_trends],  # Assuming reddit_trends is an object of RedditTrends
            verbose=True,
            allow_delegation=False,
            max_iter = 3,
            llm=llm,
        )
        
        
        # Competitor Analysis Agent for identifying similar SaaS products
        competitor_analyst = Agent(
            role="Competitor Analyst",
            goal="Identify existing competitors for the trending SaaS ideas, and analyze their strengths and weaknesses",
            backstory="""You dive deep into the web to find existing SaaS solutions that match the ideas found. Your research helps in understanding the competitive landscape, highlighting the potentials.""",
            tools=[search_tool],  # Assuming competitor_analysis is an object of CompetitorAnalysis
            llm=llm,
            
        )

        # Feature Analyst Agent for MVP feature suggestions
        feature_analyst = Agent(
            role="Feature Analyst",
            goal="Suggest potential features for MVP based on the compiled analysis",
            backstory="""With the insights provided by the Market and Competitor Analysts, you suggest a possible feature set for the MVP. Your goal is to craft a compelling value proposition for future development.""",
            llm=llm,
            verbose=True,
            allow_delegation=True,
        )
        
        # Task for Trend Analyst to scrape trending SaaS ideas from specified subreddits
        niche_analysis_task = Task(
            description=f""" Based on these subreddit : {subreddit}.
            Scrape specified subreddits for trending discussions around SaaS ideas. Focus on identifying emerging trends, popular discussions, and the most engaging content related to SaaS products.
            """,
            expected_output=f"""
            Maxium of 10 SASS ideas containing the specific idea, including the problem, solution and a brief overview of the discussion around idea. 
            This list will serve as the foundation for further analysis, list are concise and easy to follow. List should be concise and easy to follow.
            """,
            agent=niche_analyst,
            async_execution=False,
        )

        # Task for Competitor Analyst to conduct an in-depth analysis of existing solutions
        competitor_analysis_task = Task(
            description="""
            Conduct a detailed analysis of existing competitors for the sass ideas.
            """,
            expected_output="""
            A concise competitor analysis for each idea,  listing major competitors, their key features, pricing. Highlight any gaps or opportunities for innovation, or problems to solve.
            """,
            agent=competitor_analyst,
            async_execution=False,
            context=[niche_analysis_task],
        )

        # Task for Feature Analyst to outline potential MVP features
        mvp_feature_suggestion_task = Task(
            description="""
            Based on the comprehensive analysis provided by the  trend  and competitor analysis, suggest potential features for each idea. Focus on unique selling points and core functionalities written in concise format.
            """,
            expected_output="""
            A report  on top SASS ideas with brief description and market potential, and suggested MVP features for each idea. Report should be in formatted markdown.
            """,
            agent=feature_analyst,
            async_execution=False,
            context=[competitor_analysis_task],
        )
        
           
        with st.spinner("Running Workflow..."):
            # Niche Analyst Agent for Subreddit Scraping
            # Forming the tech-focused crew
            crew = Crew(
            agents=[niche_analyst, competitor_analyst,feature_analyst],
            tasks=[niche_analysis_task, competitor_analysis_task, mvp_feature_suggestion_task],
            verbose=2,
            process=Process.sequential,
            full_output=True,
            )
            original_stdout = sys.stdout
            sys.stdout = StreamToStreamlit(st)
            
            result = ""
            result_container = st.empty()
            for delta in crew.kickoff():
                result += delta  # Assuming delta is a string, if not, convert it appropriately
                result_container.markdown(result)
        
                    

if __name__ == "__main__":
    main()

