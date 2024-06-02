import re

# # Sample para variable provided by the user
# para = """
# Here are the extracted details from the provided text:


# Entities: 
# - [2024] EWCA Crim 312
# - Vice President of the Court of Appeal Criminal Division (Lord Justice Holroyde)
# - Mr Justice Picken
# - Mrs Justice Farbey DBE
# - R v Kathleen Crane
# - Royal Courts of Justice, London
# - Fraud Act 2006
# - Criminal Appeal Act 1968

# Labels: 
# - DATE
# - JUDGE
# - JUDGE
# - JUDGE
# - CASENAME
# - COURT
# - LEGAL_PROVISION
# - LEGAL_PROVISION
# """



def parse_entities_labels_from_openai(para):

    entity_pattern = r"Entities:\s*(.*)Labels:"
    label_pattern = r"Labels:\s*(.*)"

    # Extract entities and labels using regular expressions
    entities_match = re.search(entity_pattern, para, re.DOTALL)
    labels_match = re.search(label_pattern, para, re.DOTALL)

    # Extract entities and labels as lists
    entities = entities_match.group(1).strip().split('\n')
    labels = labels_match.group(1).strip().split('\n')

    # Remove leading hyphen and space ("- ") and rename "LEGAL_PROVISION" to "PROVISION"
    entities = [entity.strip()[2:] if entity.strip().startswith("- ") else entity.strip() for entity in entities]
    labels = [label.strip()[2:] if label.strip().startswith("- ") else label.strip() for label in labels]
    labels = ['PROVISION' if label == 'LEGAL_PROVISION' else label for label in labels]

    # Filter out labels not included in the desired list
    desired_labels = ['CASENAME', 'JUDGE', 'COURT', 'PROVISION', 'CITATION']
    ents = [(entities[i], labels[i]) for i in range(len(entities)) if labels[i] in desired_labels]

    # print(ents)
    # print(type(ents))
    return ents
# parse_entities_labels_from_openai(para)

# print(entities)
# print(labels)


def parse_legal_insights(text):
    # Define a pattern that matches the numbered items
    # This pattern captures numbers followed by periods and considers potential bold markdown
    pattern = re.compile(r'\n(\d+)\.\s*\*\*(.*?)\*\*:([^:]*?)(?=\n\d|\n\n|openai-recommendations|$)', re.S)
    
    # Use findall to extract all matches
    matches = pattern.findall(text)
    
    # Process matches to format them into a list of insights
    insights = [f"{num}. {title.strip()}: {description.strip()}" for num, title, description in matches]
    
    return insights



filename_to_responses = {
    "Crane-K-25.01.24.pdf": {
        "insights": ["1. The Importance of Reliable Evidence and the Impact of its Unreliability on Convictions The case highlights the pivotal role of reliable evidence in securing convictions. The Post Office's Horizon system's unreliability, which led to wrongful convictions of several sub-postmasters, underscores the necessity of scrutinizing the evidence's integrity. For future appeals, this insight stresses the need to thoroughly investigate and challenge the reliability of the evidence presented at trial. If the evidence is found unreliable, it may form a strong basis for appealing against wrongful convictions.","2. Duty of Disclosure and Its Violation Constituting an Abuse of Process The judgment emphasizes the prosecution's duty to disclose all material evidence, including that which could undermine its case or support the defendant's case. Failure to disclose such evidence, as seen with the non-disclosure of issues related to the Horizon system, constitutes an abuse of process. This insight is crucial for legal professionals preparing for an appeal, as identifying instances where the duty of disclosure was not met could lead to convictions being overturned. This duty extends to ensuring that all evidence that could affect the outcome of the case, including potential flaws in the evidence's reliability, is shared with the defense.","3. The Potential for Appeals Based on New Evidence or Arguments The successful appeal in this case, based on the unreliability of the Horizon system evidence, showcases the appellate courts' openness to reconsidering convictions when new evidence or arguments emerge. This suggests a wider implication for similar cases where technology or specific evidence types were instrumental in securing convictions. Legal professionals should be encouraged to seek out new evidence or reevaluate the evidence used in the original trial that may not have been properly scrutinized or disclosed. Additionally, this insight highlights the importance of remaining vigilant about advances in technology and forensic methodologies that could cast doubt on the reliability of evidence used in past convictions."],
        "caselaw": ["1. R v Post Office Ltd (No 1) [2020] EWCA Crim 577 Summary: This case is pivotal in the context of the Post Office Horizon scandal. It involved the quashing of multiple convictions of sub-postmasters due to the unreliability of the Horizon system. The Court of Appeal held that the prosecutions were an abuse of process because the Post Office, acting as the prosecutor, failed to disclose evidence about the unreliability of the Horizon system, which could have affected the outcome of the trials.","2. R v Turnbull [1977] QB 224 Summary: Although not directly related to abuse of process, Turnbull is critical for cases relying on questionable evidence, especially identification. The guidelines set out in Turnbull, emphasizing the need for caution before convicting based on weak or unreliable evidence, could be analogously applied to cases involving technological or forensic evidence, arguing for rigorous scrutiny of such evidence's reliability.","3. R v Sang [1980] AC 402 Summary: This case discusses the admissibility of evidence and the discretion of the trial judge to exclude evidence that would have an adverse effect on the fairness of the trial. While it primarily deals with entrapment and evidence obtained in breach of the law, the principles regarding the judge's discretion to ensure a fair trial can extend to cases where convictions are based on unreliable or flawed evidence."],
        "clauses": ["Clause 1: Challenge Based on the Unreliability of Evidence :- Whereas the integrity and reliability of evidence used to secure a conviction are paramount to the fairness of the trial, it shall be grounds for appeal if it can be demonstrated that the conviction was significantly based on evidence later found to be unreliable. This is particularly pertinent in cases where the evidence in question was instrumental in the original conviction, analogous to the demonstrated unreliability of the Horizon system in the referenced judgment.","Clause 2: Duty of Disclosure and Abuse of Process :- Given the prosecutorial duty to disclose all material evidence, including that which might undermine the prosecution's case or support the defendant's case, failure to fulfil this duty shall constitute an abuse of process. An appeal may be sought if it can be proven that such a failure has occurred, affecting the fairness of the trial and the integrity of the conviction, as evidenced by the prosecutorial behavior in the referenced judgment.","Clause 3: Appeal Based on New Evidence or Arguments :- An appeal may be lodged on the basis of new evidence or arguments that come to light post-conviction, which could materially affect the outcome of the original trial. This clause is applicable in scenarios where the new evidence or arguments challenge the reliability of the evidence used in the conviction or highlight prosecutorial misconduct, including but not limited to failure in the duty of disclosure."],
        "appeal":[""" [Your Firm's Letterhead]

        [Date]

        Registrar of the Court of Appeal Criminal Division
        Royal Courts of Justice
        The Strand
        London
        WC2A 2LL

        Dear Registrar,

        Re: Appeal against Conviction of Kathleen Crane - Case No: 2024/00172/B3

        I am writing to formally appeal against the conviction of Mrs. Kathleen Crane in the case referenced above. The judgment handed down on Thursday, 25th January 2024, by Lord Justice Holroyde, Mr. Justice Picken, and Mrs. Justice Farbey, outlines compelling reasons why Mrs. Crane's conviction should be deemed unsafe and subsequently quashed.

        The judgment details the crucial aspect that this is indeed a Horizon case, where the reliability of Horizon data was fundamental to the prosecution. It is evident that there was a lack of independent evidence to substantiate the alleged loss associated with Mrs. Crane's actions. Furthermore, it is established that the prosecution failed to fulfill its duty of investigation and disclosure regarding the reliability of the Horizon system, which undermines the integrity of the conviction.

        In light of the circumstances presented in the judgment, it is clear that Mrs. Crane's conviction was an abuse of the process on multiple grounds. Her plea of guilty was made in the absence of essential information that would have significantly impacted the case against her. As such, I respectfully request an extension of time to apply for leave to appeal and urge the Court to grant leave to appeal and subsequently quash Mrs. Crane's conviction.

        Please let me know if there are any additional requirements or procedures to follow in this appeal process. I am committed to pursuing justice on behalf of Mrs. Kathleen Crane and ensuring that her rights are upheld in this matter.

        Thank you for your attention to this important issue.

        Yours sincerely,

        [Your Name]
        [Your Position]
        [Your Contact Information]"""],
    
    },
    "example_file2": {
        "caselaw": ["caselaw_response_1", "caselaw_response_2", "caselaw_response_3"],
        "insights": ["insights_response_1", "insights_response_2", "insights_response_3"],
        "clauses": ["clause_response_1", "clause_response_2", "clause_response_3"]
    },
}

