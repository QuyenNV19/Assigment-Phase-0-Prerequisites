

def Text_Chunking(tokens, chunk_size, overlap):
    chunk = []
    step = chunk_size - overlap
    for i in range(0, len(tokens) - chunk_size + 1, step):
        chunk.append(tokens[i : i + chunk_size])
    return chunk

        
if __name__ == "__main__":
    tokens = ["a", "b", "c", "d", "e", "f", "g"]
    chunk_size = 3
    overlap = 1
    chunked = Text_Chunking(tokens, chunk_size, overlap)
    print(chunked)
    