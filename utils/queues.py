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

    def get_current_length(self):
        return len(self.items)

    def is_full(self):
        if self.get_current_length() == self.size_limit_filo:
            return True
        else:
            return False

    def get_content_as_string(self):
        content = ''.join(self.items)
        return content

    def push(self, item, filterchar=None):

        if filterchar is not None and item == filterchar:
            return # don't push the filtered char

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

    def pop_multi(self, number):
        accumulated_pop = []
        for i in range(0,number):
            popped =  self.items.popleft()
            accumulated_pop.append(popped)


        return accumulated_pop


class Ranged_Filo(Filo):

    def __init__(self, size_limit, search_range, fill_with_none, fill_range_only=False):

        self.original_range = search_range
        self.range = search_range
        self.size_limit = size_limit
        self.middle_index = Random.find_middle(size_limit, True)
        self.low_end_for_setting = self.middle_index - self.range

        super().__init__(size_limit)
        if fill_with_none:
            if fill_range_only is False:
                for index in range(0, self.size_limit):
                    self.items.append(None)
            else:
                for index in range(0, search_range):
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

    def set_item_in_midrange(self, x_index, new_value):
        index = self.low_end_for_setting + x_index
        self.items[index] = new_value

    def get_item_around_middle(self,position_relative_to_mid):
        index_to_check = self.middle_index+position_relative_to_mid
        if index_to_check < 0 or index_to_check > self.size()-1:
            return None

        item_to_return = self.items[index_to_check]
        return item_to_return

    def get_middle_items(self, use_range=False, pad_values=False, return_as_list=False):

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

            if return_as_list is True:
                return list_new

            ret_tuple = tuple(list_new)
            return ret_tuple

class SearchSpace(object):

    def __init__(self,y_size, x_size, x_search_range, fill_with_none, fill_range_only=False):
        self._y_size = y_size
        self._queues = self.init_queues(y_size, x_size, x_search_range, fill_with_none, fill_range_only)

    def get_y_size(self):
        return self._y_size

    def push_queue_value(self, y_index, value):
        self._queues[y_index].push(value)

    def get_middle_queue_values(self, y_index):
        retval = self._queues[y_index].get_middle_items(use_range=True, return_as_list=True)
        return retval

    def get_middle_queue_value(self, y_index):
        retval = self._queues[y_index].get_middle_items(use_range=False, return_as_list=False)
        return retval

    def get_value_around_middle(self,y_index, middle_offset):
        retval = self._queues[y_index].get_item_around_middle(middle_offset)
        return retval

    def init_queues(self, y_size, x_size, x_search_range, fill_with_none, fill_range_only):
        queues = []
        for index in range(0, y_size):
            rf = Ranged_Filo(x_size, x_search_range, fill_with_none, fill_range_only)
            queues.append(rf)
        return queues

    def push_column(self, values):

        for y_index in range(0, self.get_y_size()):
            self.push_queue_value(y_index, values[y_index])

    def get_middle_matrix(self, print_line_wise=False):
        """
        Get the whole range around the middle item
        :return:
        """
        middle_matrix = []

        for y_index in range(0, self.get_y_size()):
            mid_queue_vals = self.get_middle_queue_values(y_index)
            middle_matrix.append(mid_queue_vals)

            if print_line_wise is True:
                print(mid_queue_vals)

        return middle_matrix

    def update_value_midrange(self, y_index, x_index, new_value):
        self._queues[y_index].set_item_in_midrange(x_index, new_value)


    def update_middle_matrix(self, middle_matrix):

        for y_index in range(0, self.get_y_size()):
            row = middle_matrix[y_index]
            for x_index, value in enumerate(row):
                self.update_value_midrange(y_index,x_index,value)


        return middle_matrix

