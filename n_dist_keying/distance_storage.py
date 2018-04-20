import operator

class DistanceStorage():
    def __init__(self):

        self.key_val_dict = {}
        self.accumulated_dists_dict = {}
        self.shortest_distance_index = -1

    def store_value(self, setindex1, setindex2, value):
        key_tuple = self.order_input_keys(setindex1, setindex2)
        self.key_val_dict[key_tuple] = value

    def fetch_value(self, setindex1, setindex2):

        key_tuple = self.order_input_keys(setindex1, setindex2)

        if key_tuple not in self.key_val_dict:
            return None

        return self.key_val_dict[key_tuple]

    def order_input_keys(self,key1,key2):
        """
        Orders keys in ascending order and returns corrected tuples
        :param key1: number based key
        :param key2: number based key
        :return: tuple corrected
        """

        if key1>key2:
            return (key2, key1)
        elif key1 < key2:
            return (key1, key2)
        else:
            return (key1, key2)

    def clear_storage(self):
        self.key_val_dict = {}

    def calculate_accumulated_distance(self, setindex):
        """
        For a certain set index, calculate a accumulated distance to all other elements,
        then store the distance, distances to items which are not defined (negative distance value)
        are not counted in for accumulated distance.

        :param setindex: number value of index
        :return:
        """
        acc_dist = 0

        for indextuple in self.key_val_dict:
            if setindex in indextuple:
                distance_value = self.key_val_dict[indextuple]
                if distance_value >= 0:
                    acc_dist = acc_dist + distance_value


        self.accumulated_dists_dict[setindex] = acc_dist

        return setindex

    def calculate_shortest_distance_index(self):

        sorted_dict = sorted(self.accumulated_dists_dict.items(), key = operator.itemgetter(1))
        shortest_index = sorted_dict[0][0]
        self.shortest_distance_index = shortest_index

    def get_shortest_distance_index(self):
        return self.shortest_distance_index