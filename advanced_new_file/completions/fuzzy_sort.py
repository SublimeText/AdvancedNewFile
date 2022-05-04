from operator import itemgetter
# import numpy as np

def sort_by_fuzzy(query, choices, limit:int = 0):
    if not query or not choices:
        return choices
    choices_ratio = {}
    for choice in choices:
        choices_ratio[choice] = levenshtein_ratio(query, choice)

    # print(choices_ratio)
    result = [key[0] for key in sorted(choices_ratio.items(), key=itemgetter(1), reverse=True)]
    if limit > 0 and len(result) > limit:
        return result[0:limit]
    else:
        return result

def levenshtein_ratio(s, t):
    """ levenshtein_ratio_and_distance:
        Calculates levenshtein distance between two strings.
        If ratio_calc = True, the function computes the
        levenshtein distance ratio of similarity between two strings
        For all i and j, distance[i,j] will contain the Levenshtein
        distance between the first i characters of s and the
        first j characters of t
    """
    # Initialize matrix of zeros
    rows = len(s)+1
    cols = len(t)+1
    distance = [[0 for i in range(cols)] for j in range(rows)]
    # distance = np.zeros((rows, cols),dtype=int)

    # Populate matrix of zeros with the indeces of each character of both strings
    for i in range(1, rows):
        for k in range(1,cols):
            distance[i][0] = i
            distance[0][k] = k

    # Iterate over the matrix to compute the cost of deletions,insertions and/or substitutions
    for col in range(1, cols):
        for row in range(1, rows):
            if s[row-1].lower() == t[col-1].lower():
                cost = 0 # If the characters are the same in the two strings in a given position [i,j] then the cost is 0
            else:
                # In order to align the results with those of the Python Levenshtein package, if we choose to calculate the ratio
                # the cost of a substitution is 2.
                cost = 1
            distance[row][col] = min(distance[row-1][col] + 1,      # Cost of deletions
                                 distance[row][col-1] + 1,          # Cost of insertions
                                 distance[row-1][col-1] + cost)     # Cost of substitutions

    # Computation of the Levenshtein Distance Ratio
    ratio = ((len(s)+len(t)) - distance[row][col]) / (len(s)+len(t))
    if rows < cols:
        ratio = max(ratio, ((len(s)+len(t)) - distance[row][row]) / (len(s)+len(t)))
    return ratio

# if __name__ == '__main__':
#     print(levenshtein_ratio('test', 'test'))
#     print(levenshtein_ratio('test', 'test tt'))
#     print(levenshtein_ratio('test', 'taebsct'))
#     print(levenshtein_ratio('test', 'tabtest'))
#     print(levenshtein_ratio('test', 'tst tt'))
#     print(sort_by_fuzzy('def', ['advanced_new_file', 'AdvancedNewFile.py', 'AdvancedNewFile.sublime-settings', 'Default (Linux).sublime-keymap', 'Default (OSX).sublime-keymap', 'Default (Windows).sublime-keymap', 'Default.sublime-commands']))