from sklearn import preprocessing
import pandas as pd

class NormalizationModes:
    MODE_MINMAX = 'minmax-scaler'
    MODE_STANDARD_SCALE = 'standard-scaler'
    MODE_MAX_ABS = 'max-absolute-scaler'
    MODE_ROBUST_SCALE = 'robust-scaler'
    MODE_NORMALIZER = 'normalizer'
    MODE_SCALE = 'scale'


class DataframeNormalizer(object):

    @staticmethod
    def normalize_one(df_in, mode, from_series=False):

        if from_series is False:
            # Create x, where x the 'scores' column's values as floats
            x = df_in[['A']].values.astype(float)
        else:
            x = df_in.values.astype(float)

        result = None

        if mode == NormalizationModes.MODE_MINMAX:
            # Create a minimum and maximum processor object
            # X_std = (X - X.min(axis=0)) / (X.max(axis=0) - X.min(axis=0))
            # X_scaled = X_std * (max - min) + min

            feature_range = (0, 100)  # strange for lognormal, for others ok
            min_max_scaler = preprocessing.MinMaxScaler(feature_range=feature_range)

            # Create an object to transform the data to fit minmax processor
            result = min_max_scaler.fit_transform(x)
        elif mode == NormalizationModes.MODE_STANDARD_SCALE:
            standard_scaler = preprocessing.StandardScaler(with_mean=True, with_std=True)
            standard_scaler = standard_scaler.fit(x)
            mean = standard_scaler.mean_
            scale = standard_scaler.scale_
            result = standard_scaler.transform(x)  # fairly well, but maxmin has to be adapter
        elif mode == NormalizationModes.MODE_MAX_ABS:
            result = preprocessing.MaxAbsScaler().fit_transform(x)  # strange results
        elif mode == NormalizationModes.MODE_ROBUST_SCALE:

            result = preprocessing.RobustScaler(with_centering=True,
                                                with_scaling=True,
                                                quantile_range=(25.0,75.0),
                                                copy=True).fit_transform(x)

        elif mode == NormalizationModes.MODE_NORMALIZER:
            normalization_modes = ["l1", "l2", "max"]
            mode_index = 2
            result = preprocessing.Normalizer(norm=normalization_modes[mode_index]) \
                .fit_transform(x)  # strange results

        elif mode == NormalizationModes.MODE_SCALE:
            result =  preprocessing.scale(x, axis=0, with_mean=True, with_std=True, copy=True)


        # Run the normalizer on the dataframe
        df_normalized = pd.DataFrame(result, columns=list('A'))
        return df_normalized