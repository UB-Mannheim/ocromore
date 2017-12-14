class Marker:

    @staticmethod
    def is_not_marked(element):
        """
        This changes element property marked

        If a given element hasn't got marked property - add marked=False and return false
        If a given element has marked property, but marked=False return False
        If a given element has marked property and marked=True return True

        :param element: element to check upon
        :return: see description
        """

        if not hasattr(element, 'marked'):
            element.marked = False

        if element.marked is True or element.marked is False:
            return not element.marked
        else:
            raise Exception("THIS SHOULDN'T HAPPEN!")
            return False

    @staticmethod
    def mark_element(element):
        """
        Set property marked in element to True
        :param element: element to mark
        :return:
        """
        element.marked = True

    @staticmethod
    def mark_element_custom_tag(element,tag):
        element[tag] = True

    @staticmethod
    def is_element_marked_with_custom_tag(element,tag):
        if not hasattr(element, tag):
            return False

        if element[tag] is True or element[tag] is False:
            return element[tag]
        else:
            raise Exception("THIS SHOULDN'T HAPPEN!")
            return False