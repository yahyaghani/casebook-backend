import Levenshtein

def levenshtein_distance(str1, str2):
    return Levenshtein.distance(str1, str2)


str1 = "(2003) 37 EHRR CD66"
str2 = "(2016) 62 EHRR 2"
distance = levenshtein_distance(str1, str2)
print(f"Levenshtein distance between '{str1}' and '{str2}' is {distance}")

def jaccard_similarity(str1, str2):
    set1 = set(str1)
    set2 = set(str2)
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    return len(intersection) / len(union)

similarity = jaccard_similarity(str1, str2)
print(f"Jaccard similarity between '{str1}' and '{str2}' is {similarity}")
