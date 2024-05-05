import re
from sklearn.metrics.pairwise import cosine_similarity
from langchain_openai import OpenAIEmbeddings

def split_into_sentences(text):
    return re.split(r'(?<=[.?!])\s+', text.strip())

def combine_sentences(sentences, buffer_size=1):
    combined = []
    for i in range(len(sentences)):
        combined_text = ' '.join(sentences[max(0, i-buffer_size):i+buffer_size+1])
        combined.append({'sentence': combined_text, 'index': i})
    return combined

def get_embeddings(combined_sentences):
    embeddings_model = OpenAIEmbeddings()  # Ensure API key is configured
    texts = [item['sentence'] for item in combined_sentences]
    return embeddings_model.embed_documents(texts)

def find_breakpoints(sentences, threshold=0.05):  # Lowered threshold for testing
    embeddings = get_embeddings(sentences)
    breakpoints = []
    for i in range(len(embeddings) - 1):
        sim = cosine_similarity([embeddings[i]], [embeddings[i+1]])[0][0]
        print(f'Similarity between sentence {i} and {i+1}: {sim}')  # Debug similarity
        if 1 - sim > threshold:
            breakpoints.append(i)
    return breakpoints

def main_chunker(text, sentence_buffer_size=1, breakpoint_threshold=0.05):  # Adjusted parameters
    sentences = split_into_sentences(text)
    combined_sentences = combine_sentences(sentences, buffer_size=sentence_buffer_size)
    breakpoints = find_breakpoints(combined_sentences, threshold=breakpoint_threshold)
    
    chunks = []
    start_index = 0
    for bp in breakpoints:
        chunk = ' '.join([sentences[i] for i in range(start_index, bp + 1)])
        chunks.append(chunk)
        start_index = bp + 1
    if start_index < len(sentences):
        chunk = ' '.join(sentences[start_index:])
        chunks.append(chunk)
    
    return chunks

example_text = "The Solicitors’ terms and conditions made it clear that they would not give commercial or investment or tax advice. Thereafter, the Solicitors provided the Claimants with a Two of those essential terms were set out expressly in writing. They were that the Solicitors would: (i) explain the effect of any important document, and (ii) advise of any risk of which the Solicitors were aware, or which was reasonably foreseeable.At [76], Andrew Baker J said that the MoD was not \u201cself-evidently wrong\u201d to suggest \nthat it was in some way important or likely that the findings made upon the trial of lead \nclaims would be treated by the parties as persuasive. At [77]-[78], he said that, if the \n\u201ccommonality  across  the  claims  cohort  were  very  limited\u201d,  there  would  not  be  the \nnecessary convenience. In Abbott, Garnham J had approved 8 lead cases in which the \nMoD had accepted that there was enough commonality for the decisions made \u201cto be \nof real significance for all the rest\u201d, which was a concession that acknowledged the \nconvenience  of  common  disposal.  It  is  for  consideration  whether  this  passage  put \nforward what might be described as a \u201creal significance test\u201d either in addition to or \ninstead  of  the  real  progress  test  already  mentioned.  In  the  light  of  this  and  the \npromulgation of the real progress test, I am not sure that Andrew Baker J actually meant \neither in [71] (as to which, see [31] above) or in the concluding words of [77] to say \nthat common issues had to bind other parties rather than just having a persuasive impact. \nHe actually said in [77]: \u201cwhereby it will be beyond argument that the significance in \nquestion has the character of findings that bind and not merely findings that may have \na persuasive impact\u201d. I will deal, in any event, at [51]-[52] with the correctness of that \nproposition. I should note, however, at this point that the first point in the Claimants\u2019 \nRespondents\u2019 Notice argues that Abbott ought to have decided (if it did not) that the \ntrial of common issues in proceedings brought by multiple claimants would \u201cproduce a \nbinding determination\u201d on all parties."

chunks = main_chunker(example_text)

for chunk in chunks:
    print(f"Chunk: {chunk}\n")
print(len(chunks))