

class Random:

    @staticmethod
    def find_middle(length_of_list, to_lower):
        """
        Finds the middle index of a list
        :return: middle index if list has unequal size. lower and higher index tuple is equal sitze
        """

        middle = float(length_of_list)/2
        if middle % 2 != 0:
            return int(middle - .5)
        else:
            low_middle = int(middle-1)
            high_middle = int(middle)

            if to_lower:
                return low_middle
            else:
                return (low_middle, high_middle)