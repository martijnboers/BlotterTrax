class ArrayUtil:
    @staticmethod
    def safe_list_get(using_list, default, *index):
        try:
            value = using_list
            for i in index:
                value = value[i]

            return value
        except (IndexError, KeyError):
            return default
