from langchain_core.prompts.few_shot import FewShotPromptTemplate
from langchain_core.prompts.prompt import PromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_chroma import Chroma

# Revised examples for legal contexts
examples = [
    {
        "sample_question": "Can the verdict of a breach of contract be appealed?",
        "answer": """
Are follow up questions needed here: Yes.
Follow up: On what grounds was the original verdict based?
Intermediate answer: The verdict was based on the defendant's failure to deliver services as per the terms agreed upon.
Follow up: What are acceptable grounds for an appeal in breach of contract cases?
Intermediate answer: Acceptable grounds include procedural errors, misapplication of law, new evidence, or fundamental injustice in the trial's outcome.
So the final answer is: Yes, if errors in procedure or legal interpretation can be demonstrated.
""",
    },
    {
        "sample_question": "What are possible defenses in a defamation lawsuit?",
        "answer": """
Are follow up questions needed here: Yes.
Follow up: Was the statement claimed as defamation factual or opinion?
Intermediate answer: The statement was categorized as an opinion.
Follow up: Does the context of the statement imply actual harm or malice?
Intermediate answer: The context does not support actual harm or express malice.
Follow up: Does the plaintiff's public figure status affect the defense?
Intermediate answer: Yes, public figures must prove actual malice to establish defamation.
So the final answer is: Defenses include truth, opinion, and lack of malice, particularly significant in cases involving public figures.
""",
    },
    {
        "sample_question": "How can a judgment in a patent infringement case be challenged?",
        "answer": """
Are follow up questions needed here: Yes.
Follow up: Was the patent's validity assessed considering prior art?
Intermediate answer: The trial did not fully assess the scope of prior art.
Follow up: Is there new evidence that could invalidate the patent?
Intermediate answer: Recent findings suggest prior art that directly relates to the patented invention.
Follow up: Were there errors in how the patent law was applied in the original judgment?
Intermediate answer: There was a significant misinterpretation of patent law regarding the non-obviousness criteria.
So the final answer is: The judgment can be challenged based on new evidence of prior art and misapplication of patent law standards.
""",
    },
{
    "sample_question": "Under what circumstances can a criminal conviction be overturned on appeal?",
    "answer": """
    Are follow up questions needed here: Yes.
    Follow up: Was there any prosecutorial misconduct during the trial?
    Intermediate answer: Yes, evidence of misconduct was documented.
    Follow up: Were the defendant's rights violated during the investigation?
    Intermediate answer: There was a violation of the right to a fair trial.
    So the final answer is: A conviction can be overturned if there was prosecutorial misconduct or a violation of constitutional rights.
    """
},
{
    "sample_question": "What are the grounds for appealing a civil litigation ruling regarding a property dispute?",
    "answer": """
    Are follow up questions needed here: Yes.
    Follow up: Were all factual disputes properly resolved by the jury?
    Intermediate answer: Key factual disputes were overlooked in the jury's decision.
    Follow up: Was there an error in applying property laws?
    Intermediate answer: The application of property laws was flawed, impacting the ruling.
    So the final answer is: Grounds for appeal include unresolved factual disputes and legal errors in the application of property laws.
    """
},
{
    "sample_question": "What legal remedies are available if a contract is breached by one party?",
    "answer": """
    Are follow up questions needed here: Yes.
    Follow up: What was the nature of the breach?
    Intermediate answer: The breach involved non-delivery of promised goods.
    Follow up: What are the potential compensations for this type of breach?
    Intermediate answer: Remedies include damages, specific performance, or cancellation and restitution.
    So the final answer is: Remedies for breach of contract can include compensatory damages, specific performance, or contract rescission.
    """
},


]


##### the code below will be utilised for calling the appropriate prompt samples to be similarity matched


question = "What are the legal requirements for filing a personal injury claim?"

def call_prompt_example_generator(user_question):

    # Create prompt templates
    example_prompt = PromptTemplate(
        input_variables=["sample_question", "answer"], 
        template="Sample question: {sample_question}\n{answer}"
    )

    # Example selector setup
    example_selector = SemanticSimilarityExampleSelector.from_examples(
        examples,
        OpenAIEmbeddings(),
        Chroma,
        k=1
    )

    # Select the most similar example to the input
    selected_examples = example_selector.select_examples({"question": user_question})
    # Display selected examples
    final_prompt = FewShotPromptTemplate(
    example_selector=example_selector,
    example_prompt=example_prompt,
    suffix="User's Question is: {input}",
    input_variables=["input"],
)
    print(final_prompt.format(input=user_question))


    return final_prompt


example_prompt=call_prompt_example_generator(question)
