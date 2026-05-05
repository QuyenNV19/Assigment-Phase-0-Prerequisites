def Word_Frequency_Dictionary(test):
    list_test = test.lower().split()
    word_dict = {}

    for word in list_test:
        word_dict[word] = word_dict.get(word, 0) + 1
    
    sorted_dict = dict(sorted(word_dict.items(), key=lambda item: item[1], reverse=True))
    
    return sorted_dict    



if __name__ == "__main__":
    D1 = "the quick brown fox"
    D2 = "the lazy dog sleeps"
    D3 = "the fox jumps over the lazy dog"
    test = D1 + " " + D2 + " " + D3
    print(Word_Frequency_Dictionary(test))  
    