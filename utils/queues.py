from collections import deque
from utils.random import Random


class Stack(object):
    def __init__(self):
        self.items = deque([])

    def isEmpty(self):
        return self.items == []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def peek(self):
        return self.items[len(self.items) - 1]

    def size(self):
        return len(self.items)


class Filo(Stack):
    def __init__(self, size_limit):
        self.size_limit_filo = size_limit
        super().__init__()

    def push(self, item):

        # add item
        super().push(item)

        # remove old items
        # self.size is the actual size
        # self.size_filo is the size limit

        size_difference = self.size() - self.size_limit_filo

        if size_difference >= 1:
            for ctr in range(size_difference):
                self.items.popleft()

            if size_difference > 1:
                print("Filo: More then one item was popped, shouldn't happen!")



class Ranged_Filo(Filo):

    def __init__(self, size_limit, search_range, fill_with_none):

        self.original_range = search_range
        self.range = search_range
        self.size_limit = size_limit
        self.middle_index = Random.find_middle(size_limit, True)
        super().__init__(size_limit)
        if fill_with_none:
            for index in range(0, self.size_limit):
                self.items.append(None)

    def get_middle_index(self):
        return self.middle_index

    def set_search_range(self, value):
         self.range = value

    def get_middle_items_for_range(self, range_value):
        self.set_search_range(range_value)
        result = self.get_middle_items(True, False)
        self.set_search_range(self.original_range)
        return result

    def get_middle_items(self, use_range=False, pad_values=False):

        if not use_range:
            if self.size() <= self.size_limit:
                item_to_return = self.items[self.size()-1]
                return item_to_return

            if self.size() == self.size_limit:
                item_to_return = self.items[self.middle_index]
                return item_to_return
        else:

            low_end = max(0, self.middle_index - self.range)
            high_end = self.middle_index + self.range +1

            high_end_final = 0
            if high_end >= self.size():
                high_end_final += self.size()
            else:
                high_end_final += high_end

            list_new = []
            for index in range(low_end, high_end_final):
                list_new.append(self.items[index])

            if pad_values:
                len_listnew = len(list_new)
                low_end_pad = min(len_listnew, self.size_limit)
                for index in range(low_end_pad, self.size_limit):
                    list_new.append(None)


            ret_tuple = tuple(list_new)
            return ret_tuple

