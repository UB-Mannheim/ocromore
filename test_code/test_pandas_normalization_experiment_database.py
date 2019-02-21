"""
This is a experiment which checks if the confidence outputs of
the different engines if they are scaled around different
median (therefore histogram plotting and stuff) therefore
the pandas dataframes are used with a Normalization module
implemented, that provides different methods.

This could be used in future implementations to improve
results, at the moment the confidence scaling is
done with fixed factors (20.02.2019)
"""



import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from akf_corelib.df_objectifier import DFObjectifier
from n_dist_keying.database_handler import DatabaseHandler
from test_code.test_pandas_dataframe_normalization import NormalizationModes, DataframeNormalizer as dn


# Create an example dataframe with a column of unnormalized data
#data = {'score': [234,24,14,27,-74,46,73,-18,59,160]}
# data = {'score': np.random.randint(0,100,size=(100, 1))}

NORMALIZATION_MODE = NormalizationModes.MODE_SCALE
MAX_HIST_Y = 5000
NUMBER_OF_INPUTS = 3
NUMBER_OF_HISTOGRAM_BINS = 50
DB_DIR = './Testfiles/sql/'

plot_axis_info = [0, 100, 0, MAX_HIST_Y]
dbdir_abs = 'sqlite:///' + str(Path(DB_DIR).absolute())

dataframe_wrapper = DFObjectifier(dbdir_abs + '/1957.db', '0237_1957_hoppa-405844417-0050_0290')

database_handler = DatabaseHandler(dataframe_wrapper, NUMBER_OF_INPUTS)
xconfs_abbyy = dataframe_wrapper.df.reset_index().set_index("ocr").loc["Abbyy","x_confs"]
xconfs_ocro = dataframe_wrapper.df.reset_index().set_index("ocr").loc["Ocro","x_confs"]
xconfs_tess = dataframe_wrapper.df.reset_index().set_index("ocr").loc["Tess","x_confs"]


df1 = pd.DataFrame(xconfs_abbyy.values.astype('float'), columns=list('A'))
df2 = pd.DataFrame(xconfs_ocro.values.astype('float'), columns=list('A'))
df3 = pd.DataFrame(xconfs_tess.values.astype('float'), columns=list('A'))


plt.subplot(231)
plt.title('abbyy distribution', fontsize=8)
plt.axis(plot_axis_info)
df1['A'].plot(kind='hist', bins=NUMBER_OF_HISTOGRAM_BINS)



plt.subplot(232)
plt.title('ocro distribution', fontsize=8)
plt.axis(plot_axis_info)
df2['A'].plot(kind='hist', bins=NUMBER_OF_HISTOGRAM_BINS)


plt.subplot(233)
plt.title('tess distribution', fontsize=8)
plt.axis(plot_axis_info)
df3['A'].plot(kind='hist', bins=NUMBER_OF_HISTOGRAM_BINS)

print("data plotted")


df1_normalized = dn.normalize_one(df1, NORMALIZATION_MODE)
df2_normalized = dn.normalize_one(df2, NORMALIZATION_MODE)
df3_normalized = dn.normalize_one(df3, NORMALIZATION_MODE)

if NORMALIZATION_MODE == NormalizationModes.MODE_ROBUST_SCALE or \
    NORMALIZATION_MODE == NormalizationModes.MODE_SCALE:

    # do a post standardization value scaling again
    df1_normalized = dn.normalize_one(df1, NormalizationModes.MODE_MINMAX)
    df2_normalized = dn.normalize_one(df2, NormalizationModes.MODE_MINMAX)
    df3_normalized = dn.normalize_one(df3, NormalizationModes.MODE_MINMAX)


plt.subplot(234)
plt.title('abbyy distribution-normalized', fontsize=8)
plt.axis(plot_axis_info)
df1_normalized['A'].plot(kind='hist', bins=NUMBER_OF_HISTOGRAM_BINS)

plt.subplot(235)
plt.title('ocro distribution-normalized', fontsize=8)
df2_normalized['A'].plot(kind='hist', bins=NUMBER_OF_HISTOGRAM_BINS)
plt.axis(plot_axis_info)

plt.subplot(236)
plt.title('tess distribution-normalized', fontsize=8)
df3_normalized['A'].plot(kind='hist', bins=NUMBER_OF_HISTOGRAM_BINS)
plt.axis(plot_axis_info)


plt.suptitle('Normalization Mode:'+NORMALIZATION_MODE, fontsize=16)
plt.subplots_adjust(left=0.2, wspace=0.8, top=0.8)
plt.show()
print("normalized data plotted")
