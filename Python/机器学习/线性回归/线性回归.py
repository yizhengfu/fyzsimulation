import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# Read the data from the CSV file
data = pd.read_csv('income.csv')

# Extract the education and income columns
education = data['Education']
income = data['Income']

plt.scatter( )
#-----------↑↑↑-fill your answer-↑↑↑-------------#
plt.xlabel('Education')
plt.ylabel('Income')
plt.title('Income vs Education')
plt.show()