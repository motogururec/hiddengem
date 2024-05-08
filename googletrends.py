from pytrends.request import TrendReq
from crewai_tools import BaseTool
import pandas as pd
from typing import List,Dict

class GoogleTrends(BaseTool):
    name: str = "Google Trends"
    description: str = "Look for trends using Google Trends"

    def _run(self, topics: Dict[str, List[Dict[str, str]]]) -> Dict[str, List[Dict[str, str]]]:
        """
        Enhances the input topics with Google Trends data.

        Parameters:
            topics (Dict[str, List[Dict[str, str]]]): A structured dataset where keys are categories (e.g., "Startup_Ideas")
                                                      and values are lists of posts, each post being a dictionary containing at least a 'title'.

        Returns:
            Dict[str, List[Dict[str, str]]]: The input dataset enriched with Google Trends data for each post title.
        """
        pytrend = TrendReq()
        for category, posts in topics.items():
            for post in posts:
                # Extract keyword from the post title
                keyword = post['title']
                pytrend.build_payload(kw_list=[keyword], timeframe="today 3-m", geo="")
                trends_data = pytrend.interest_over_time()

                if not trends_data.empty:
                    # Assuming we use the mean interest value as an example
                    post['google_trend_interest'] = trends_data[keyword].mean()
                else:
                    post['google_trend_interest'] = "No data found"
        print("topics:",topics)
        return topics