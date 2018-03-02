import pandas as pd
import numpy as np
from sklearn import preprocessing
import matplotlib.pyplot as plt


class NormalizationModes:
    MODE_MINMAX = 'minmax-scaler'
    MODE_SCALE = 'standard-scaler'
    MODE_MAX_ABS = 'max-absolute-scaler'
    MODE_ROBUST = 'robust-scaler'
    MODE_NORMALIZER = 'normalizer'


def normalize_one(df_in, mode):

    # Create x, where x the 'scores' column's values as floats
    x = df_in[['A']].values.astype(float)
    result = None

    if mode == NormalizationModes.MODE_MINMAX:
        # Create a minimum and maximum processor object

        feature_range = (-2.5, 2.5)
        min_max_scaler = preprocessing.MinMaxScaler(feature_range=feature_range)

        # Create an object to transform the data to fit minmax processor
        result = min_max_scaler.fit_transform(x)
    elif mode == NormalizationModes.MODE_SCALE:
        standard_scaler = preprocessing.StandardScaler()
        standard_scaler = standard_scaler.fit(x)
        mean = standard_scaler.mean_
        scale = standard_scaler.scale_
        result = standard_scaler.transform(x)
    elif mode == NormalizationModes.MODE_MAX_ABS:
        result = preprocessing.MaxAbsScaler().fit_transform(x)
    elif mode == NormalizationModes.MODE_ROBUST:
        result = preprocessing.RobustScaler().fit_transform(x)
    elif mode == NormalizationModes.MODE_NORMALIZER:
        result = preprocessing.Normalizer().fit_transform(x)


    # Run the normalizer on the dataframe
    df_normalized = pd.DataFrame(result, columns=list('A'))
    return df_normalized


# Create an example dataframe with a column of unnormalized data
#data = {'score': [234,24,14,27,-74,46,73,-18,59,160]}

# data = {'score': np.random.randint(0,100,size=(100, 1))}

NORMALIZATION_MODE = NormalizationModes.MODE_ROBUST
NUMBER_OF_SAMPLES = 10000

# Fixing random state for reproducibility
np.random.seed(19680801)
plot_axis_info = [-10, 10, 0, round(NUMBER_OF_SAMPLES/3)]

data_distribution_1 = np.random.binomial(10, 0.5, NUMBER_OF_SAMPLES)
data_distribution_2 = np.random.vonmises(0.0, 10.0, NUMBER_OF_SAMPLES)
df1 = pd.DataFrame(data_distribution_1, columns=list('A'))
df2 = pd.DataFrame(data_distribution_2, columns=list('A'))



plt.subplot(221)
plt.title('binomial distribution', fontsize=8)
plt.axis(plot_axis_info)
df1['A'].plot(kind='hist')



plt.subplot(222)
plt.title('vonmises distribution', fontsize=8)
plt.axis(plot_axis_info)
df2['A'].plot(kind='hist')


print("data plotted")


df1_normalized = normalize_one(df1, NORMALIZATION_MODE)
df2_normalized = normalize_one(df2, NORMALIZATION_MODE)


plt.subplot(223)
plt.title('binomial distribution-normalized', fontsize=8)
plt.axis(plot_axis_info)
df1_normalized['A'].plot(kind='hist')

plt.subplot(224)
plt.title('vonmises distribution-normalized', fontsize=8)
df2_normalized['A'].plot(kind='hist')
plt.axis(plot_axis_info)

plt.suptitle('Normalization Mode:'+NORMALIZATION_MODE, fontsize=16)
plt.subplots_adjust(left=0.2, wspace=0.8, top=0.8)
plt.show()
print("normalized data plotted")
