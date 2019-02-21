"""
This part of experiment which checks and normalizes
confidences of outputs in different engines.
This shows how histograms can look like to determine
scalings. (main is test_pandas_normalization_experiment_database.py)


This could be used in future implementations to improve
results, at the moment the confidence scaling is
done with fixed factors (20.02.2019)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from test_pandas_dataframe_normalization import NormalizationModes, DataframeNormalizer as dn


# Create an example dataframe with a column of unnormalized data
#data = {'score': [234,24,14,27,-74,46,73,-18,59,160]}
# data = {'score': np.random.randint(0,100,size=(100, 1))}

NORMALIZATION_MODE = NormalizationModes.MODE_STANDARD_SCALE
NUMBER_OF_SAMPLES = 10000

# Fixing random state for reproducibility
np.random.seed(19680801)
plot_axis_info = [-10, 10, 0, round(NUMBER_OF_SAMPLES/3)]

data_distribution_1 = np.random.binomial(10, 0.5, NUMBER_OF_SAMPLES)
data_distribution_2 = np.random.vonmises(0.0, 10.0, NUMBER_OF_SAMPLES)
data_distribution_3 = np.random.lognormal(mean=0.0, sigma=1.0, size=NUMBER_OF_SAMPLES)

df1 = pd.DataFrame(data_distribution_1, columns=list('A'))
df2 = pd.DataFrame(data_distribution_2, columns=list('A'))
df3 = pd.DataFrame(data_distribution_3, columns=list('A'))


plt.subplot(231)
plt.title('binomial distribution', fontsize=8)
plt.axis(plot_axis_info)
df1['A'].plot(kind='hist')



plt.subplot(232)
plt.title('vonmises distribution', fontsize=8)
plt.axis(plot_axis_info)
df2['A'].plot(kind='hist')


plt.subplot(233)
plt.title('lognormal distribution', fontsize=8)
plt.axis(plot_axis_info)
df3['A'].plot(kind='hist')

print("data plotted")


df1_normalized = dn.normalize_one(df1, NORMALIZATION_MODE)
df2_normalized = dn.normalize_one(df2, NORMALIZATION_MODE)
df3_normalized = dn.normalize_one(df3, NORMALIZATION_MODE)


plt.subplot(234)
plt.title('binomial distribution-normalized', fontsize=8)
plt.axis(plot_axis_info)
df1_normalized['A'].plot(kind='hist')

plt.subplot(235)
plt.title('vonmises distribution-normalized', fontsize=8)
df2_normalized['A'].plot(kind='hist')
plt.axis(plot_axis_info)

plt.subplot(236)
plt.title('lognormal distribution-normalized', fontsize=8)
df3_normalized['A'].plot(kind='hist')
plt.axis(plot_axis_info)


plt.suptitle('Normalization Mode:'+NORMALIZATION_MODE, fontsize=16)
plt.subplots_adjust(left=0.2, wspace=0.8, top=0.8)
plt.show()
print("normalized data plotted")
