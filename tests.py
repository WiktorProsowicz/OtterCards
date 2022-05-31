from data.extracting_from_dictionaries import get_entries_from_diki, get_to_english_from_babla


c, e = get_to_english_from_babla("love", "finnish", 5, 10, True)

print("----entries ---- ")
for card in c:
    print(card)

print("----extras-----")
for extra in e:
    print(extra)