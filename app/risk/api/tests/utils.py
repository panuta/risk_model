

def matching_dict_in_list(matching_dict, the_list):
    """
    If `matching_dict` is found in `the_list`, return index of the_list. Otherwise, return -1
    """
    for i, list_item in enumerate(the_list):
        found = 0
        for dict_item in matching_dict:
            for list_dict_item in list_item:
                if dict_item == list_dict_item:
                    found += 1

        if found == len(matching_dict):
            return i

    return -1