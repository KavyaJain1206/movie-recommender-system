import pickle
import pandas as pd

# Load DataFrame directly
movies = pickle.load(open('movies.pkl', 'rb'))

# Optional check
movies = pd.DataFrame(movies) if isinstance(movies, dict) else movies
movies.head()  # Display the first few rows of the DataFrame

movie_list = movies['title'].values
print(movies.head())  # Display the first few rows of the DataFrame