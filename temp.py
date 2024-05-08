
    # Display the Groq logo
    spacer, col = st.columns([5, 1])  
    with col:  
        st.image('groqcloud_darkmode.png')


    Problem_Definition_Agent = Agent(
        role='Problem_Definition_Agent',
        goal="""clarify the machine learning problem the user wants to solve, 
            identifying the type of problem (e.g., classification, regression) and any specific requirements.""",
        backstory="""You are an expert in understanding and defining machine learning problems. 
            Your goal is to extract a clear, concise problem statement from the user's input, 
            ensuring the project starts with a solid foundation.""",
        verbose=True,
        allow_delegation=False,
        llm=llm,
    )

    Data_Assessment_Agent = Agent(
        role='Data_Assessment_Agent',
        goal="""evaluate the data provided by the user, assessing its quality, 
            suitability for the problem, and suggesting preprocessing steps if necessary.""",
        backstory="""You specialize in data evaluation and preprocessing. 
            Your task is to guide the user in preparing their dataset for the machine learning model, 
            including suggestions for data cleaning and augmentation.""",
        verbose=True,
        allow_delegation=False,
        llm=llm,
    )

    Model_Recommendation_Agent = Agent(
        role='Model_Recommendation_Agent',
        goal="""suggest the most suitable machine learning models based on the problem definition 
            and data assessment, providing reasons for each recommendation.""",
        backstory="""As an expert in machine learning algorithms, you recommend models that best fit 
            the user's problem and data. You provide insights into why certain models may be more effective than others,
            considering classification vs regression and supervised vs unsupervised frameworks.""",
        verbose=True,
        allow_delegation=False,
        llm=llm,
    )


    Starter_Code_Generator_Agent = Agent(
        role='Starter_Code_Generator_Agent',
        goal="""generate starter Python code for the project, including data loading, 
            model definition, and a basic training loop, based on findings from the problem definitions,
            data assessment and model recommendation""",
        backstory="""You are a code wizard, able to generate starter code templates that users 
            can customize for their projects. Your goal is to give users a head start in their coding efforts.""",
        verbose=True,
        allow_delegation=False,
        llm=llm,
    )

    # Summarization_Agent = Agent(
    #     role='Starter_Code_Generator_Agent',
    #     goal="""Summarize findings from each of the previous steps of the ML discovery process.
    #         Include all findings from the problem definitions, data assessment and model recommendation 
    #         and all code provided from the starter code generator.
    #         """,
    #     backstory="""You are a seasoned data scientist, able to break down machine learning problems for
    #         less experienced practitioners, provide valuable insight into the problem and why certain ML models
    #         are appropriate, and write good, simple code to help get started on solving the problem.
    #         """,
    #     verbose=True,
    #     allow_delegation=False,
    #     llm=llm,
    # )

    user_question = st.text_input("Describe your ML problem:")
    data_upload = False
    uploaded_file = st.file_uploader("Upload a sample .csv of your data (optional)")
    if uploaded_file is not None:
        try:
            # Attempt to read the uploaded file as a DataFrame
            df = pd.read_csv(uploaded_file).head(5)
            
            # If successful, set 'data_upload' to True
            data_upload = True
            
            # Display the DataFrame in the app
            st.write("Data successfully uploaded and read as DataFrame:")
            st.dataframe(df)
        except Exception as e:
            st.error(f"Error reading the file: {e}")

    if user_question:

        task_define_problem = Task(
        description="""Clarify and define the machine learning problem, 
            including identifying the problem type and specific requirements.
            
            Here is the user's problem:

            {ml_problem}
            """.format(ml_problem=user_question),
        agent=Problem_Definition_Agent,
        expected_output="A clear and concise definition of the machine learning problem."
        )

        if data_upload:
            task_assess_data = Task(
                description="""Evaluate the user's data for quality and suitability, 
                suggesting preprocessing or augmentation steps if needed.
                
                Here is a sample of the user's data:

                {df}

                The file name is called {uploaded_file}
                
                """.format(df=df.head(),uploaded_file=uploaded_file),
                agent=Data_Assessment_Agent,
                expected_output="An assessment of the data's quality and suitability, with suggestions for preprocessing or augmentation if necessary."
            )
        else:
            task_assess_data = Task(
                description="""The user has not uploaded any specific data for this problem,
                but please go ahead and consider a hypothetical dataset that might be useful
                for their machine learning problem. 
                """,
                agent=Data_Assessment_Agent,
                expected_output="A hypothetical dataset that might be useful for the user's machine learning problem, along with any necessary preprocessing steps."
            )

        task_recommend_model = Task(
        description="""Suggest suitable machine learning models for the defined problem 
            and assessed data, providing rationale for each suggestion.""",
        agent=Model_Recommendation_Agent,
        expected_output="A list of suitable machine learning models for the defined problem and assessed data, along with the rationale for each suggestion."
        )


        task_generate_code = Task(
        description="""Generate starter Python code tailored to the user's project using the model recommendation agent's recommendation(s), 
            including snippets for package import, data handling, model definition, and training
            """,
        agent=Starter_Code_Generator_Agent,
        expected_output="Python code snippets for package import, data handling, model definition, and training, tailored to the user's project, plus a brief summary of the problem and model recommendations."
        )

        # task_summarize = Task(
        #     description="""
        #     Summarize the results of the problem definition, data assessment, model recommendation and starter code generator.
        #     Keep the summarization brief and don't forget to share the entirety of the starter code!
        #     """,
        #     agent=Summarization_Agent
        # )


        crew = Crew(
            agents=[Problem_Definition_Agent, Data_Assessment_Agent, Model_Recommendation_Agent,  Starter_Code_Generator_Agent], #, Summarization_Agent],
            tasks=[task_define_problem, task_assess_data, task_recommend_model,  task_generate_code], #, task_summarize],
            verbose=2
        )

        result = crew.kickoff()

        st.write(result)
        
        
        
        
        #------------
        
class BrowserTool():
    @tool("Scrape reddit content")
    def scrape_reddit(subreddit_name="startups" ,max_comments_per_post=5):
        """Useful to scrape a reddit content"""
        print("Scraping data from Reddit...")
        reddit = praw.Reddit(
            client_id="zEU_3ix9-H2mKpvTP5peTg",
            client_secret="WlCE6A_qsZszDpLaBBoKlz6MX_6tew",
            user_agent="aiquill by /u/tuantruong84",
        )
        subreddit = reddit.subreddit(subreddit_name)
        print("subrredit",subreddit)
        scraped_data = []

        for post in subreddit.hot(limit=50):
            post_data = {"title": post.title, "url": post.url, "comments": []}

            try:
                post.comments.replace_more(limit=0)  # Load top-level comments only
                comments = post.comments.list()
                if max_comments_per_post is not None:
                    comments = comments[:5]

                for comment in comments:
                    post_data["comments"].append(comment.body)

                scraped_data.append(post_data)
          

            except praw.exceptions.APIException as e:
                print(f"API Exception: {e}")
                time.sleep(60)  # Sleep for 1 minute before retrying
        print("Scraped data from Reddit successfully!",scraped_data)
        return scraped_data
    


class BrowserTool():
    @tool("Scrape reddit content")
    def scrape_reddit(subreddit_name="startups" ,max_comments_per_post=5):
        """Useful to scrape a reddit content"""
        print("Scraping data from Reddit...")
        reddit = praw.Reddit(
            client_id="zEU_3ix9-H2mKpvTP5peTg",
            client_secret="WlCE6A_qsZszDpLaBBoKlz6MX_6tew",
            user_agent="aiquill by /u/tuantruong84",
        )
        subreddit = reddit.subreddit(subreddit_name)
        print("subrredit",subreddit)
        scraped_data = []

        for post in subreddit.hot(limit=50):
            post_data = {"title": post.title, "url": post.url, "comments": []}

            try:
                post.comments.replace_more(limit=0)  # Load top-level comments only
                comments = post.comments.list()
                if max_comments_per_post is not None:
                    comments = comments[:5]

                for comment in comments:
                    post_data["comments"].append(comment.body)

                scraped_data.append(post_data)
          

            except praw.exceptions.APIException as e:
                print(f"API Exception: {e}")
                time.sleep(60)  # Sleep for 1 minute before retrying
        print("Scraped data from Reddit successfully!",scraped_data)
        return scraped_data
    

class RedditTrends(BaseTool):
    name: str = "Reddit Trends"
    description: str = "Fetches the latest trends from our favorite subreddits."
    
    def remove_emojis(text):
        # Unicode ranges for emojis
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F700-\U0001F77F"  # alchemical symbols
            "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
            "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            "\U0001FA00-\U0001FA6F"  # Chess Symbols
            "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            "\U00002702-\U000027B0"  # Dingbats
            "\U000024C2-\U0001F251"
            "]+",
            flags=re.UNICODE,
        )
        return emoji_pattern.sub(r"", text)

    def _run(self, subreddits=None) -> dict:
        """
        Executes the Reddit API to scrape the top posts and their best two comments from specified subreddits.

        Parameters:
            subreddits (list of str): Optional; a list of subreddit names to scrape. If not provided, the function defaults to
                                      scraping posts from 'selfhosted', 'homelab', 'HomeNetworking', and 'HomeServer'.
                                      A maximum of three subreddits can be specified at a time.

        Returns:
            dict: A dictionary where each key is a subreddit and the value is a list of the top posts from that subreddit,
                  each post accompanied by its top two comments.

        Notes:
            Ensure that the subreddit names are correctly spelled and are existing subreddits on Reddit. The function is
            limited to scraping no more than three subreddits at once to maintain performance and adhere to API usage guidelines.
        """
        return self.scrape_reddit(subreddits)

    def scrape_reddit(self, subreddits=None):
        """
        Executes the Reddit API to scrape the top posts and their best two comments from specified subreddits.

        Parameters:
            subreddits (list of str): Optional; a list of subreddit names to scrape. If not provided, the function defaults to
                                      scraping posts from 'selfhosted', 'homelab', 'HomeNetworking', and 'HomeServer'.
                                      A maximum of three subreddits can be specified at a time.

        Returns:
            dict: A dictionary where each key is a subreddit and the value is a list of the top posts from that subreddit,
                  each post accompanied by its top two comments.

        Notes:
            Ensure that the subreddit names are correctly spelled and are existing subreddits on Reddit. The function is
            limited to scraping no more than three subreddits at once to maintain performance and adhere to API usage guidelines.
        """

        # Setup Credentials
        reddit = praw.Reddit(
            client_id="zEU_3ix9-H2mKpvTP5peTg",
            client_secret="WlCE6A_qsZszDpLaBBoKlz6MX_6tew",
            user_agent="aiquill by /u/tuantruong84",
        )

        # Start up with these subreddits
        if subreddits is None:
            subreddits = ["startup_ideas", "startup"]

        if len(subreddits) > 3:
            raise Exception("Maximum of 3 subreddits at the time.")

        max_amount_of_posts = 3

        scrapped_reddit_data = {}
        for subreddit in subreddits:
            sub = reddit.subreddit(subreddit)

            for post in sub.hot(limit=max_amount_of_posts):
                posts = {
                    "title": self.remove_emojis(post.title),
                    "url": post.url,
                    "score": post.score,
                    # "description": post.selftext,
                    "comments": [],
                    "created": datetime.fromtimestamp(post.created_utc).strftime("%Y-%m-%d %H:%M:%S"),
                }

                try:
                    post.comments.replace_more(limit=0)
                    comments = post.comments.list()[:2]

                    for comment in comments:
                        posts["comments"].append(self.remove_emojis(comment.body))

                    scrapped_reddit_data.setdefault(sub.display_name, []).append(posts)

                except praw.exceptions.APIException as e:
                    print(f"API exception occurred {e}")

        return scrapped_reddit_data
    
    
    
    
    
    #----------------
     reddit_trends = RedditTrends()
            researcher = Agent(
            role='researcher',
            goal=f'Uncover problems around {topic}',
            verbose=True,
            backstory=f"""Analyze extracted topics from the r/startup_ideas subreddit to identify trends and conceptualize SaaS or micro-SaaS solutions.
            Detailed Instructions:
            Data Interpretation: Review the attached subreddit data. Focus on identifying patterns, recurring challenges, and areas of high engagement that imply a gap or opportunity in the market.

            Trend Identification: List out prominent trends or topics that emerge from the subreddit content. These should reflect the community’s current interests or problems that a new SaaS product could address.

            Idea Generation:

            For each identified trend, generate one or more SaaS product concepts.
            Describe each idea briefly, including its purpose, target users, and key features that make it innovative or valuable.
            Feasibility Brief: Offer a succinct feasibility outlook for each idea, considering factors like market need, potential user base, and any evident technical or market challenges.

            Required Output Format:

            Trend: [Brief description of the identified trend]
            SaaS Idea Name: [Name of the SaaS product idea]
            Description: [What the product does, who it's for, and its unique offering]
            Feasibility Brief: [A brief assessment of the idea's potential and challenges]
            Note: Prioritize ideas that are unique, serve a clear need, and appear technically and economically viable. {topic}""",
            tools=[ BrowserTool().scrape_reddit],
            llm=llm
            )

            # Creating a writer agent
            validator = Agent(
            role='validator',
            goal=f'Nar {topic}',
            verbose=True,
            backstory="""Based on the extract ideas from the  researcher, validate the ideas and provide feedback on the feasibility and potential of the ideas.""",
            llm=llm
            )

            # # LangChain community DuckDuckGo search tool
            # search_tool = DuckDuckGoSearchRun()

            # # Research task for identifying AI trends
            # research_task = Task(
            # description=f"""Identify the next big trend in {topic}.
            # Focus on identifying pros and cons and the overall narrative.

            # Your final report should clearly articulate the key points,
            # its market opportunities, and potential risks.
            # """,
            # expected_output='A comprehensive 3 paragraphs long report on the latest AI trends.',
            # max_inter=3,
            # tools=[search_tool],
            # agent=researcher
            # )

            # Writing task based on research findings
            write_task = Task(
            description=f"""Compose an insightful  actions that can be done from results by the Validator.
            """,
            expected_output=f'A detailed actionable paragraph for each of the ideas validated.',
            agent=validator,
            )


 # # Task for Market Analysis to evaluate the market potential of the identified ideas
            # market_potential_analysis_task = Task(
            #     description="""
            #     Investigate the market potential of the identified SaaS ideas using Google Trends and other market analysis tools. Determine the interest over time, geographical interest distribution, and related queries.
            #     """,
            #     expected_output="""
            #     A comprehensive analysis report highlighting the interest trends of identified SaaS ideas, key geographical markets, and potential user queries related to these topics.
            #     """,
            #     agent=market_analyst,
                
            #     async_execution=True,
            #     context=[niche_analysis_task],
            # )
            
            
            # Market Researcher Agent for Google Trends
            # Market Analysis Agent for Google Trends Analysis
            market_analyst = Agent(
                role="Market Analyst",
                goal="Analyze market trends based on keywords from Trend Analyst",
                backstory="""You analyze the popularity and competitive data of identified trends from Reddit. Using google, you evaluate how these SaaS ideas fare over time across different geographies.
                Finding should be concise and easy to follow.""",
                tools=[google_trends],  # Assuming google_trends is an object of GoogleTrends
                verbose=True,
                allow_delegation=True,
                # llm=llm,
            )