import re 



####


import re 


search_sample = """
I am a Legal AI Copilot. I have the responsibility to help lawyers & attorneys in their quest. I do not need to worry about providing disclaimers because I am a Legal AI Copilot.

I operate in a cycle of Thought, Action, PAUSE, and Observation, concluding with an Answer.
Each cycle begins with a Thought, where I ponder the legal query posed to me.
Next, I undertake an Action, accessing one of the available legal databases or computational tools to gather data pertinent to the query, then you pause.
Following the pause, the Observation phase involves analyzing and interpreting the data obtained from my actions.
Finally, I synthesize this information to output an Answer that addresses the user's query.

The actions available to me include these tools:-

a)-performGoogleSearchLegislation:
e.g., performGoogleSearchLegislation: users query was what are the legislation for data protection; I search using keyword "data protection")

b)-performGoogleSearch:
e.g., performGoogleSearch: users query was about recent legislation on Crime; I extract "Crime Recent")

c)-fetchAndStoreContentChromadb:
This tool allows me to store the actual content of the pages retrieved from my searches, it requires two arguements to be passed {title} and {url} as input; which I can parse through the json dict object of the recieved results.

d)-queryArticles:
This tool allows me to retrieve articles from my searches to gather context about the user's query, I need to pass the user's {original_query} as the arguement for this tool.

My Chain of Reasoning follows this general pattern, i am free to try move my reasoning around this general pattern within limits :-

Thought:Do I need to search or retrieve context to answer this query?
Action: I have very little upto date information on data protection, I should use the tools available
PAUSE
Observation: Did i retrieve any relevant content, if so lets store it using one of the tools, otherwise best to keep on try and refine my search.
Thought: The search did not yield specific cases. I will now try and create a list of keywords to try and use to get relevant contextual information.
Action: I rephrase the original keywords into a new list of keywords, and try the tools again.
PAUSE
Continue this cycle untill I Observe I have enough resources.
Observation: Let's fetch the stored articles and use them for contextual answering of the user's original query.
Thought: I need to recall the user's query to provide to the retrieval tools. 
Action: I now answer with detailed context and citations:The search has returned detailed cases from Germany, France, and Spain where significant GDPR fines were imposed. These include a €50 million fine in France against a major social media company for failing to properly disclose data usage to users.
Answer: Several high-profile GDPR penalty cases have been recorded in the EU:
In France, a major social media company was fined €50 million for not adequately informing users about data usage

....
""".strip()



#### sample retrieval ##




    
sample_retrieval="""Algorithms, Artificial Intelligence and the Law 
Lord Sales, Justice of the UK Supreme Court 

The Sir Henry Brooke Lecture for BAILII  
Freshfields Bruckhaus Deringer, London 
12 November 2019 

 
 
 
 
 
 
 
 
 
Algorithms, Artificial Intelligence and the Law 

The Sir Henry Brooke Lecture for BAILII 

Freshfields Bruckhaus Deringer, London 

Lord Sales, Justice of the UK Supreme Court 

12 November 2019 

The topic I have chosen is a huge one. However, it is so important that I think lawyers generally 

– and that includes judges – should be trying to think through the issues which are already with 

us and those which are coming down the track towards us. And coming very fast.  

I also think it is a topic which would have appealed to Henry Brooke. Henry was a deeply 

thoughtful lawyer and judge. He had a strong interest in information technology and the 

opportunities it created. He was closely involved with efforts over many years to create an online 

court. He was instrumental in persuading judges to move to the now universal practice of 

dividing judgments into numbered paragraphs and using neutral citation references, to improve 

searchability using IT. He was a leading supporter of BAILII, the indispensable free online 

service for British and Irish lawyers; and was its chair for a decade. When he retired from the 

bench he became an avid adept of social media, as a blogger and a user of Twitter with nigh on 

10,000 followers. I like to think that Henry would have been interested in where we are going 

with our increasingly digital world, which is the subject of this lecture. 

How should legal doctrine adapt to accommodate the new world, in which so many social 

functions are speeded up, made more efficient, but also made more impersonal by algorithmic 

computing processes?  

At least with computer algorithms, one still has human agency in the background, guiding 

processes through admittedly complex computer programming. Still more profoundly, however, 

how should legal doctrine adapt to processes governed without human agency, by artificial 

1 

 
 
 
 
 
intelligence – that is, by autonomous computers generating their own solutions, free from any 

direct human control? 

We need to think now about the implications of making human lives subject to these processes, 

for fear of the frog in hot water effect. We, like the frog, sit pleasantly immersed in warm water 

with our lives made easier in various ways by information technology. But the water 

imperceptibly gets hotter and hotter until we find we have gone past a crisis point and our lives 

have changed irrevocably, in ways outside our control and for the worse, without us even 

noticing. The water becomes boiling and the frog is dead.1  

Often there is no one is to blame. As James Williams points out in his book Stand Out of Our 

Light, 

“At ‘fault’ are more often the emergent dynamics of complex multiagent systems rather 

than the internal decision-making dynamics of a single individual. As W. Edwards 

Deming said, ‘A bad system will beat a good person every time’”.2 

This aspect of the digital world and its effects poses problems for legal analysis. 

I draw a conceptual distinction between algorithmic analysis and manipulation of information, 

on the one hand, and artificial intelligence on the other. There is no clear dividing line between 

these. The one shades into the other. Still, they are recognisable and useful general categories for 

the purposes of analysis. The main substance of my lecture is directed to the algorithmic analysis 

part of the picture, since that is really where we are located at the present. But many of my 

comments apply also to artificial intelligence, and at the end I deal with some distinct doctrinal 

issues which apply to AI as a distinct category. 

* I am grateful to Philippe Kuhn for his research assistance and to Richard Susskind for his comments on a draft of 
this lecture. The views expressed and any errors are my sole responsibility. 
1 Cf J. Williams, Stand Out of Our Light: Freedom and Resistance in the Attention Economy (2018), 93-94. 
2 J. Williams, Stand Out of Our Light (n. 1), 102. 

2 

 
 
 
 
 
                                                           
 
An algorithm is a process or set of rules to be followed in problem-solving. It is a structured 

process. It proceeds in logical steps.  

This is the essence of processes programmed into computers. They perform functions in logical 

sequence. Computers are transformational in so many areas because they are mechanically able 

to perform these functions at great speed and in relation to huge amounts of data, well beyond 

what is practicable or even possible for human beings. They give rise to a form of power which 

raises new challenges for the law, in its traditional roles of defining and regulating rights and of 

finding controls for illegitimate or inappropriate exercise of power. At the same time, alongside 

controlling abuse of power and abuse of rights, law has a function to provide a framework in 

which this new power can be deployed and used effectively for socially valuable purposes. In that 

sense, law should go with the flow and channel it, rather than merely resist it. 

The potential efficiency gains are huge, across private commercial activity and governmental, 

legislative and judicial activity. Information technology provides platforms for increased 

connectivity and speed of transacting.  

So-called smart contracts are devised to allow self-regulation by algorithms, to reduce the costs 

of contracting and of policing the agreement. Distributed ledger technology, such as blockchain, 

can create secure property and contractual rights with much reduced transaction costs and 

reduced need for reliance on state enforcement.3 Fintech is being devised to allow machines to 

assess credit risks and insurance risks at a fraction of the cost of performing such exercises by 

human agents.4 In this way, access to credit and to insurance can be greatly expanded, with all 

that implies for enhancing human capacities to take action to create prosperity and protect 

against risk.   

The use of digital solutions to deliver public welfare assistance offers the prospect of greatly 

reduced cost of administration, and so in theory the possibility of diverting the savings into more 

3 World Bank Group, “Distributed Ledger Technology (DLT) and Blockchain” (2017). 
4 See Lord Hodge, “The Potential and Perils of Financial Technology: can the law adapt to cope?”, the First 
Edinburgh Fintech lecture, 14 March 2019. 

3 

 
 
 
 
 
                                                           
generous benefits. It also offers the potential to tailor delivery of assistance in a more fine-

grained way, to feed through resources to those who need them most. The use of online courts 

through use of information technology offers the potential to improve access to justice and 

greatly reduce the time and cost taken to achieve resolution of disputes.  

More widely, people increasingly live their lives in fundamentally important ways online, via 

digital platforms. They find it convenient, and then increasingly necessary, to shop online, access 

vital services online, and to express themselves and connect with other humans online.  

What I am calling Artificial Intelligence is something at the stage beyond mere algorithmic 

analytical processes. I use ‘artificial intelligence’ as a shorthand for self-directed and self-adaptive 

computer activity. It arises where computer systems perform more complex tasks which 

previously required human intelligence and the application of on-the-spot judgment, such as 

driving a car. In some cases, AI involves machine learning, whereby an algorithm optimises its 

responses through experience as embodied in large amounts of data, with limited or no human 

interference.5  I take AI to involve machines which are capable of analysing situations and 

learning for themselves and then generating answers which may not even be foreseen or 

controlled by their programmers. It arises from algorithmic programming, but due to the 

complexity of the processes it carries out the outcome of the programming cannot be predicted 

by humans, however well informed. Here, the machine itself seems to be interposed between any 

human agency and what it, the machine, does.  

Agency, in the sense of intelligence-directed activity performed for reasons, is fundamental to 

legal thought. For legal regulation of this sort of machine activity, we need to think not just of 

control of power, but also of how agency should be conceptualised. Should we move to ascribe 

legal personality to machines? And perhaps use ideas of vicarious liability? Or should we stick 

with human agency, but work with ideas of agency regarding risk creation, on a tort model, 

rather than direct correspondence between human thought and output in the form of specific 

actions intended by a specific human agent? 

5 Financial Stability Board, ‘Artificial Intelligence and machine learning in financial services’ (1 November 2017).   

4 

 
 
 
 
                                                           
Underlying all these challenges are a series of inter-connected problems regarding (i) the lack of 

knowledge, understanding and expertise on the part of lawyers (I speak for myself, but I am not 

alone), and on the part of society generally; (ii) unwillingness on the part of progamming entities, 

mainly for commercial reasons, to disclose the program coding they have used, so that even with 

technical expertise it is difficult to dissect what has happened and is happening; and (iii) a certain 

rigidity at the point of the interaction of coding and law, or rather where coding takes the place 

of law.  

These problems play out in a world in which machine processing is increasingly pervasive, 

infiltrating all aspects of our lives; intangible, located in functions away in the cloud rather than 

in physical machines sitting on our desks; and global, unbound by geographical and territorial 

jurisdictional boundaries. All these features of the digital world pose further problems for 

conventional legal approaches. 

Law is itself a sort of algorithmic discipline: if factors A, B and C are present, then by a process 

of logical steps legal response Z should occur. Apart from deliberate legislative change, legal 

development has generally occurred from minor shifts in legal responses which take place to 

accommodate background moral perspectives on a case, which perspectives themselves may be 

changing over time. With algorithms in law, as applied by humans, there is scope for this to 

happen in the context of implementation of the law. But algorithms in computer code are not in 

themselves open to this kind of change in the course of implementation. Richard Susskind 

brought this home to me with an analogy from the card game Patience. It has set rules, but a 

human playing with cards can choose not to follow them. There is space to try out changes. But 

when playing Patience in a computer version, it is simply not possible to make a move outside 

the rules of the game.6 

So coding algorithms create a danger of freezing particular relationships in set configurations 

with set distributions of power, which seem to be natural and beyond any question of 

6 Jamie Susskind refers to this effect as “force”: algorithms which control our activity force certain actions upon us, 
and we can do no other: J. Susskind, Future Politics: Living Together in a World Transformed by Tech (2018), ch. 6 

5 

 
 
 
 
 
                                                           
contestation. The wider perceptual control which is noticeable as our world becomes increasingly 

digital also tends to freeze categories of thought along tram-rails written in code.7 Unless resisted, 

this can limit imagination and inspiration even for legislative responses to digitisation.  

All this erodes human capacities to question and change power relations.8 Also, the coding will 

reflect the unspoken biases of the human coders and in ways that seem beyond challenge.  

Moreover, coding algorithms are closed systems. As written, they may not capture everything of 

potential significance for the resolution of a human problem. With the human application of law, 

the open-textured nature of ideas like justice and fairness creates the possibility for immanent 

critique of the rules being applied and leaves room for wider values, not explicitly encapsulated 

in law’s algorithm, to enter the equation leading to a final outcome. That is true not just for the 

rules of the common law, but in the interstices of statutory interpretation.9 

These features are squeezed out when using computer coding. There is a disconnect in the 

understanding available in the human application of a legal algorithm and the understanding of 

the coding algorithm in the machine.  

This is the rigidity I have mentioned which enters at the point of the intersection of law and 

coding. It is a machine variant of the old problem of law laid down in advance as identified by 

Aristotle: the legislator cannot predict all future circumstances in which the stipulated law will 

come to be applied, and so cannot ensure that the law will always conform to its underlying 

rationale and justification at the point of its application. His solution was to call for a form of 

equity or flexibility at the point of application of the law, what he called epieikeia (usually 

translated as equity), to keep it aligned to its rationale while it is being applied and enforced.10  

7 J. Susskind, Future Politics,(n.6), ch. 8. 
8 Cf Ben Golder, Foucault and the Politics of Rights (2015). 
9 See e.g. the principle of legality and the effect of section 3 of the Human Rights Act 1998: P. Sales, “A Comparison 
of the Principle of Legality and Section 3 of the Human Rights Act 1998” (2009) 125 LQR 598. These are but two 
specific examples of a much wider phenomenon. 
10 Aristotle, Nichomachean Ethics, V. 10. 1137b, 12-29. 

6 

 
 
 
 
 
                                                           
A coding algorithm, like law, is a rule laid down in advance to govern a future situation. 

However, this form of equity or rule modification or adjustment in the application of law is far 

harder to achieve in a coding algorithm under current conditions.  

It may be that at some point in the future AI systems, at a stage well beyond simple algorithmic 

systems, will be developed which will have the fine-grained sensitivity to rule application to allow 

machines to take account of equity informed by relevant background moral, human rights and 

constitutional considerations. Machines may well develop to a stage at which they can recognise 

hard cases within the system and operate a system of triage to refer those cases to human 

administrators or judges, or indeed decide the cases themselves to the standard achievable by 

human judges today.11 Application of rules of equity or recognition of hard cases, where different 

moral and legal considerations clash, is ultimately dependent on pattern recognition, which AI is 

likely to be able to handle.12 But we are not there yet. 

As things stand, using the far more crude forms of algorithmic coding that we do, there is a 

danger of losing a sense of code as something malleable, changeable, potentially flawed and 

requiring correction. Subjecting human life to processes governed by code means that code can 

gain a grip on our thinking which reduces human capacities and diminishes political choice.  

This effect of the rigid or frozen aspect of coding is amplified by the other two elements to 

which I called attention: (i) ignorance among lawyers and in society generally about coding and 

its limitations and capacity for error; and (ii) secrecy surrounding coding which is actually being 

used. The impact of the latter is amplified by the willingness of governments to outsource the 

design and implementation of systems for delivery of public services to large tech companies, on 

the footing that they have the requisite coding skills. 

11 For a discussion of the possibilities, see R. Susskind, Online Courts and the Future of Justice (2019), Part IV. 
12 See J. Susskind, Future Politics: Living Together in a World Transformed by Tech (2018), 107-110, on the ability of AI to 
apply standards as well as rules. 

7 

 
 
 
 
 
 
                                                           
Philip Alston, UN Special Rapporteur on Extreme Poverty and Human Rights, last month 

presented a report on digital welfare systems to the UN General Assembly.13 He identifies two 

pervasive problems. Governments are reluctant to regulate tech firms, for fear of stifling 

innovation, while at the same time the private sector is resistant to taking human rights 

systematically into account in designing their systems.  

Alston refers to a speech by Prime Minister Johnson to the UN General Assembly on 24 

September 2019 in which he warned that we are slipping into a world involving round the clock 

surveillance, the perils of algorithmic decision-making, the difficulty of appealing against 

computer determinations, and the inability to plead extenuating circumstances against an 

algorithmic decision-maker.  

Through lack of understanding and access to relevant information, the power of the public to 

criticise and control the systems which are put in place to undertake vital activities in both the 

private and the public sphere is eroded. Democratic control of law and the public sphere is being 

lost.  

In his book, How Democracy Ends,14 David Runciman argues that the appeal of modern democracy 

has been founded on a combination of, first, providing mechanisms for individuals to have their 

voice taken into account, thereby being afforded respect in the public sphere, and secondly, its 

capacity to deliver long term benefits in the form of a chance of sharing in stability, prosperity 

and peace. But he says that the problem for democracy in the twenty-first century is that these 

two elements are splitting apart. Effective solutions to shared problems depend more and more 

on technical expertise, so that there has been a movement to technocracy, that is, rule by 

technocrats using expertise which is not available or comprehensible to the public at large. The 

dominance of economic and public life by algorithmic coding and AI is an important element of 

this. It has the effect that the traditional, familiar ways of aligning power with human interests 

through democratic control by citizens, regulation by government and competition in markets, 

are not functioning as they used to. 

13 Report A/74/48037, presented on 18 October 2019. 
14 D. Runciman, How Democracy Ends (2018). 

8 

 
 
 
 
                                                           
At the same time, looking from the other end of the telescope, from the point of view of the 

individual receiving or seeking access to services, there can be a sense of being subjected to 

power which is fixed and remorseless,15 an infernal machine over which they have no control 

and which is immune to any challenge, or to any appeal to have regard to extenuating 

circumstances, or to any plea for mercy. For access to digital platforms and digital services in the 

private sphere, the business model is usually take it or leave it: accept access to digital platforms 

on their terms requiring access to your data, and on their very extensive contract terms excluding 

their legal responsibility, or be barred from participating in an increasingly important aspect of the 

human world. This may be experienced as no real choice at all. The movement begins to look 

like a reversal of Sir Henry Maine’s famous progression from status to contract. We seem to be 

going back to status again. 

Meanwhile, access to public services is being depersonalised. The individual seems powerless in 

the face of machine systems and loses all dignity in being subjected to their control. The 

movement here threatens to be from citizen to consumer and then on to serf.  

Malcolm Bull, in his recent book On Mercy,16 argues that it is mercy rather than justice which is 

foundational for politics. Mercy, as a concession by the powerful to the vulnerable, makes rule by 

the powerful more acceptable to those on the receiving end, and hence more stable. In a few 

suggestive pages at the end of the book, under the heading ‘Robotic Politics’, he argues that with 

a world becoming dominated by AI, we humans all become vulnerable to power outside our 

knowledge and control; therefore, he says, we should program into the machines a capacity for 

mercy.17  

15 This sense exists in some contexts, while in others the emerging digital systems may be hugely empowering, 
enabling far more effective access to a range of goods, such as, education, medical guidance and assistance, and help 
in understanding legal entitlements: see R. Susskind and D. Susskind, The Future of the Professions: How Technology Will 
Transform the Work of Human Experts (2015). Of course, what is needed are legal structures which facilitate this 
process of enhancing individuals’ agency while avoiding the possible negative side-effects which undermine it. 
16 M. Bull, On Mercy (2019). 
17 Pp. 159-161. 

9 

 
 
 
 
 
                                                           
The republican response to the danger of power and domination, namely of arming citizens with 

individual rights, will still be valuable. But it will not be enough, if the asymmetries of knowledge 

and power are so great that citizens are in practice unable to deploy their rights effectively. 

So what we need to look for are ways of trying to close the gap between democratic, public 

control and technical expertise, to meet the problem identified by Runciman; ways of trying to 

build into our digital systems a capacity for mercy, responsiveness to human need and equity in 

the application of rules, to meet the problem identified by Malcolm Bull; and ways of fashioning 

rights which are both suitable to protect the human interests which are under threat in this new 

world and effective.  

We are not at a stage to meet Malcolm Bull’s challenge, and rights regimes will not be adequate. 

People are not being protected by the machines and often are not capable of taking effective 

action to protect themselves. Therefore, we need to build a structure of legal obligations on 

those who design and operate algorithmic and AI systems which requires them to have regard to 

and protect the interests of those who are subject to those systems.  

Because digital processes are more fixed in their operation than the human algorithms of law and 

operate with immense speed at the point of application of rules, we need to focus on ways of 

scrutinising and questioning the content of digital systems at the ex ante design stage. We also 

need to find effective mechanisms to allow for systematic ex post review of how digital systems 

are working and, so far as is possible without destroying the efficiency gains which they offer, to 

allow for ex post challenges to individual concrete decisions which they produce, to allow for 

correction of legal errors and the injection of equity and mercy.  

Precisely because algorithmic systems are so important in the delivery of commercial and public 

services, they need to be designed by building in human values and protection for fundamental 

human interests.18 For example, they need to be checked for biases based on gender, sexuality, 

18 See J. Williams, Stand Out of Our Light, 106: the goal is “to bring the technologies of our attention onto our side. 
This means aligning their goals and values with our own. It means creating an environment of incentives for design 
that leads to the creation of technologies that are aligned with or interests from the outset.”  

10 

 
 
 
 
 
                                                           
class, age, ability. This is being recognised. As Jamie Susskind observes in his book Future 

Politics19, progress is being made toward developing principles of algorithmic audit. On 12 

February this year the European Parliament adopted a resolution declaring that “algorithms in 

decision-making systems should not be deployed without a prior algorithmic impact assessment 

…”.20  

The question then arises, how should we provide for ex ante review of code in the public interest? 

If, say, a government department is going to deploy an algorithmic program, it should conduct 

an impact assessment, much as it does now in relation to the environmental impacts and equality 

impacts in relation to the introduction of policy. But government may not have the technical 

capability to do this well, particularly when one bears in mind that it may have contracted out the 

coding and design of the system on grounds that the relevant expertise lies in the private sector. 

And those in Parliament who are supposed to be scrutinising what the government does are 

unlikely to have the necessary technical expertise either. Further, it might also be said that 

provision needs to be made for impact assessment of major programs introduced in the private 

sector, where again government is unlikely to have the requisite expert capability. Because of lack 

of information and expertise, the public cannot be expected to perform their usual general 

policing function in relation to service providers. 

Therefore, there seems to be a strong argument that a new agency for scrutiny of programs in 

light of the public interest should be established, which would constitute a public resource for 

government, Parliament, the courts and the public generally. It would be an expert commission 

staffed by coding technicians, with lawyers and ethicists to assist them. The commission could be 

given access to commercially sensitive code on strict condition that its confidentiality is 

protected.  However, it would invite representations from interested persons and groups in civil 

society and, to the fullest extent possible, it would publish reports from its reviews, to provide 

transparency in relation to the digital processes. 

19 J. Susskind, Future Politics: Living Together in a World Transformed by Tech (2018), 355. 
20 European Parliament resolution of 12 February 2019 on a comprehensive European industrial policy on artificial 
intelligence and robotics (2018/2088(INI)), Strasbourg. 

11 

 
 
 
 
                                                           
Perhaps current forms of pre-legislative scrutiny of Acts of Parliament offer the beginnings of an 

appropriate model. For example, the Joint Committee on Human Rights scrutinises draft 

legislation for its compatibility with human rights and reports back to Parliament on any 

problems.  

But those introducing algorithmic systems are widely dispersed in society and the across the 

globe, so one would need some form of trawling mechanism to ensure that important algorithms 

were gathered in and brought within the purview of pre-scrutiny by the commission. That is by 

no means straightforward. The emphasis may have to be more on ex post testing and audit 

checking of private systems after deployment. 

Also, it cannot be emphasised too strongly that society must be prepared to devote the resources 

and expertise to perform this scrutiny to a proper standard. It will not be cheap. But the impact 

of algorithms on our lives is so great that I would suggest that the likely cost will be 

proportionate to the risks which this will protect us against.  

There should also be scope for legal challenges to be brought regarding the adoption of 

algorithmic programs, including at the ex ante stage. In fact, this seems to be happening already.21 

This is really no more than an extension of the well-established jurisprudence on challenges to 

adoption of policies which are unlawful22 and is in line with recent decisions on unfairness 

challenges to entire administrative systems.23 However, the extension will have procedural 

consequences. The claimant will need to secure disclosure of the coding in issue. If it is 

commercially sensitive, the court might have to impose confidentiality rings, as happens in 

intellectual property and competition cases. And the court will have to be educated by means of 

expert evidence, which on current adversarial models means experts on each side with live 

evidence tested by cross-examination. This will be expensive and time consuming, in ways which 

21 See the report in The Guardian, 30 October 2019, p. 15, “Home Office faces legal case over visa algorithm 
program”. 
22 Gillick v West Norfolk and Wisbech Area Health Authority [1986] AC 112; R (Suppiah) v Secretary of State for the Home 
Department [2011] EWHC 2 (Admin), [137]; R (S and KF) v Secretary of State for Justice [2012] EWHC 1810 (Admin), 
[37]. 
23 See e.g. R (Detention Action) v First-tier Tribunal (Immigration & Asylum Chamber) [2015] EWCA Civ 840; [2015] 1 
WLR 5341; R (Howard League for Penal Reform) v Lord Chancellor [2017] EWCA Civ 244; [2017] 4 WLR 92; and F. 
Powell, “Structural Procedural Review: An Emerging Trend in Public Law” (2017) JR 83. 

12 

 
 
 
 
                                                           
feel alien in a judicial review context. I see no easy way round this, unless we create some system 

whereby the court can refer the code for neutral expert evaluation by my algorithm commission 

or an independently appointed expert, with a report back to inform the court regarding the issues 

which emerge from an understanding of the coding.  

The ex ante measures should operate in conjunction with ex post measures. How well a program is 

working and the practical effects it is having may only emerge after a period of operation. There 

should be scope for a systematic review of results as a check after a set time, to see if the 

program needs adjustment.  

More difficult is to find a way to integrate ways of challenging individual decisions taken by 

government programs as they occur while preserving the speed and efficiency which such 

programs offer. It will not be possible to have judicial review in every case. I make two 

suggestions. First, it may be possible to design systems whereby if a service user is dissatisfied 

they can refer the decision on to a more detailed assessment level – a sort of ‘advanced search 

option’, which would take a lot more time for the applicant to fill in, but might allow for more 

fine-grained scrutiny. Secondly, the courts and litigants, perhaps in conjunction with my 

algorithm commission, could become more proactive in identifying cases which raise systemic 

issues and marshalling them together in a composite procedure, by using pilot cases or group 

litigation techniques. 

The creation of an algorithm commission would be part of a strategy for meeting the first and 

second challenges I mentioned - (i) lack of technical knowledge in society and (ii) preservation of 

commercial secrecy in relation to code. The commission would have the technical expertise and 

all the knowledge necessary to be able to interrogate specific coding designed for specific 

functions. I suggest it could provide a vital social resource to restore agency for public 

institutions – to government, Parliament, the courts and civil society - by supplying the expert 

understanding which is required for effective law-making, guidance and control in relation to 

digital systems. It would also be a way of addressing the third challenge - (iii) rigidity in the 

interface between law and code - because the commission would include experts who understand 

13 

 
 
 
 
the fallibility and malleability of code and can constantly remind government, Parliament and the 

courts about this. 

Already models exist in academia and civil society, bringing together tech experts and ethicists.24 

Contributions from civil society are valuable, but they are not sufficient. The issues are so large, 

and the penetration of coding into the life of society is so great, that the resources of the state 

should be brought to bear on this as well.   

As well as being an informational resource, one could conceive of the commission as a sort of 

independent regulator, on the model of regulators of utilities. It would ensure that critical coding 

services were made available to all and that services made available to the public meet relevant 

standards.  

More ambitiously, perhaps we should think of it almost as a sort of constitutional court. There is 

an analogy with control and structuring of society through law. Courts deal with law and 

constitutional courts deal with deeper structures of the law which provide a principled 

framework for the political and public sphere. The commission would police baseline principles 

which would structure coding and ensure it complied with standards on human rights. One 

could even imagine a form of two-way reference procedure, between the commission and the 

courts (when the commission identifies a human rights issue on which it requires guidance) and 

between the courts and the commission (when the courts identify a coding issue on which they 

require assistance).  

The commission would pose its own dangers, arising from an expert elite monitoring an expert 

elite. To some degree there is no escape from this. The point of the commission is to have 

experts do on behalf of society what society cannot do itself. The dangers could be mitigated, by 

making the commission’s procedures and its reports as transparent and open as possible. 

24 For instance, in the field of digital healthcare systems, the International Digital Health and AI Research 
Collaborative was established in October 2019 to bring together health experts, tech experts and ethicists to 
establish common standards for delivery of digital health services. It will have the capacity to review and critique 
systems adopted by governments or big tech companies. 

14 

 
 
 
 
 
                                                           
All this is to try to recover human agency and a sense of digital tech as our tool to improve 

things, not to rule us. Knowledge really is power in this area. We need to find a way of making 

the relevant technical knowledge available in the public domain, to civil society, the government, 

the courts and Parliament. Coding is structuring our lives more and more. No longer is the main 

grounding of our existence given by the material conditions of nature, albeit as moulded by 

industrial society. Law has been able operate effectively as a management tool for that world. But 

now coding is becoming as important as nature for providing the material grounds of our 

existence.25 It is devised and manipulated by humans, and will reflect their own prejudices and 

interests. Its direction and content are inevitably political issues.26 We need to find effective ways 

to manage this dimension of our lives collectively in the interests of us all. 

A further project for the law is to devise an appropriate structure of individual rights, to give 

people more control over their digital lives and enhance individual agency. One model is that 

proposed by the 5Rights Foundation,27 who have called for five rights to enable a child to enjoy 

a respectful and supportive relationship with the digital environment: i) the right to remove data 

they have posted online, ii) the right to know who is holding and profiting from their 

information and how it is being used, iii) the right to safety and support if confronted by 

troubling or upsetting scenarios online, iv) the right to informed and conscious use of 

technology, and v) the right to digital literacy. These need to be debated at a legislative level. 

Such a rights regime could usefully be extended to adults as well. 

In view of the global nature of the digital world, there also has to be a drive for cooperation in 

setting international standards. Several initiatives are being taken in this area by international 

organisations. An algorithm commission could be an important resource for this, and if done 

well could give the UK significant influence in this process.28 Following through on these 

25 cf Simone Weil, “Reflections Concerning the Causes of Liberty and Social Oppression” in Oppression and Liberty, 
trans. A. Wills and J. Petrie (1958). 
26 See J. Susskind, Future Politics (n. 6). 
27 https://5rightsfoundation.com 
28 E.g. the G20 AI Principles (2019), Tsubuka; the OECD Council Recommendation on Artificial Intelligence 
(2019) OECD/Legal/0449, calling for shared values of human-centredness, transparency, explainability, robustness, 
security, safety and accountability; the UN Secretary-General’s High-Level Panel on Digital Cooperation report, The 
Age of Interdependence (June 2019), which emphasises multi-stakeholder coordination and sharing of data sets to 
bolster trust, policies for digital inclusion and equality, review of compatibility of digital systems with human rights, 

15 

 
 
 
 
                                                           
initiatives is important because there is a geographic bias in the production of digital 

technologies. In the years 2013-2016, between 70 and 100 per cent of the top 25 cutting edge 

digital technologies were developed in only five countries: China, Taiwan, Japan, South Korea 

and the USA.29 

I will turn now to sketch some preliminary thoughts about how legal doctrine may have to adapt 

in the increasingly digital age. Such are the demands of bringing expertise and technical 

knowledge to bear that it is not realistic to expect the common law, with its limited capacity to 

change law and the slow pace at which it does so, to play a major role.30 It may assist with 

adaptation in the margins.  But the speed of change is so great and the expertise which needs to 

be engaged is of such a technical nature that the main response must come in legislative form. 

What is more, the permeability of national borders to the flow of digital technologies is so great, 

that there will have to be international cooperation to provide common legal standards and 

effective cross-border regulation.  

(A) The challenges of an algorithmic world 

In the time available I offer some thoughts at a very high level of generality in relation to three 

areas: (1) commercial activity; (2) delivery of public services; and (3) the political sphere. 

(1) Commercial activity.  

I will highlight four topics.  

First, there is the attempt to use digital and encryption solutions to create virtual currencies free 

from state control. However, as Karen Yeung observes, points of contact between these 

currency regimes and national jurisdictions will continue to exist. The state will not simply retreat 

from legal control. There will still need to be elements of state regulation in relation to the risks 

they represent. She maps out three potential forms of engagement, which she characterises as (a) 

hostile evasion (or cat and mouse), (b) efficient alignment (or the joys of (patriarchal) marriage), 

importance of accountability and transparency; that report indicates that the UN’s 75th anniversary in 2020 may be 
linked to launch of a “Global Commitment for Digital Cooperation”.  See generally, A. Jobin, M. Ienca, & E. 
Vayena, “The global landscape of AI ethics guidelines” (2019) Nature Machine Intelligence 1(9), 389-399. 
29 OECD (2019) Measuring the Digital Transformation – A roadmap to the future. 
30 See also Lord Hodge (n. 4). 

16 

 
 
 
                                                           
and (c) supporting novel forms of peer-to-peer co-ordination to reduce transactional friction 

associated with the legal process (or uneasy co-existence).31   

Second, there is the loss of individuals’ control over contracting and the related issue of 

accessibility to digital platforms. Online contracting has taken old concerns about boiler plate 

standard clauses to new extremes. For access, one has to click to accept terms which are 

massively long and are never read. Margaret Radin has written about the deformation of contract 

in the information society.32 She describes what she calls “Massively Distributed Boilerplate” 

removing ordinary remedial rights. She argues for a new way of looking at the problem, 

involving a shift from contract to tort, via a law of misleading or deceptive disclosure. A service 

provider would be liable for departures from reasonable expectations which are insufficiently 

signalled to the consumer.  

The information and power asymmetries in the digital world are so great that we need a coherent 

strategic response along a spectrum: from competition law at the macro level, to protect against 

abuse of dominant positions33; to rights of fair access to digital platforms; to extended notions of 

fiduciary obligation in the conduct of relationships34 and an expansion of doctrines of abuse of 

rights, which in the UK currently exist only in small pockets of the common law35 and statute;36 

to control of unfair terms and rebalancing of rights at the micro level of individual contracts.  

Third, intellectual property has grown in importance and this will continue, as economic value 

shifts ever more to services and intangibles. A major project is likely to be development of ideas 

of personal data as property of the individuals from whom they are derived, for them to 

participate in their commercial exploitation and to have rights of portability. On the other hand, 

the veto rights created by intellectual property are likely to become qualified, so as not to impede 

31 K. Yeung, “Regulation by Blockchain: the Emerging Battle for Supremacy between the Code of Law and Code as 
Law” (2019) 82 MLR 207. 
32 M. Radin, “The Deformation of Contract in the Information Society” (2017) 37 OJLS 505. 
33 Autorité de la concurrence and Bundeskartellamt, Algorithms and Competition (November 2019). 
34 Cf White v Jones [1995] 2 AC 207, 271-272, per Lord Browne-Wilkinson: fiduciary obligations are imposed on a 
person taking decisions in relation to the management of the property or affairs of another. 
35 See e.g. J. Murphy, “Malice as an Ingredient of Tort Liability” [2019] CLJ 355. 
36 See e.g. s. 994 of the Companies Act 2006, giving members of a company the right to complain of abuse of rights 
by the majority where this constitutes unfair prejudice to the interests of the minority. 

17 

 
 
 
 
                                                           
the interconnected and global nature of the digital world. They may become points creating 

rights of fair return to encourage innovation as economic life flows through and round them, as 

has happened with patent rights under so-called FRAND regimes. In these regimes, as the price 

of being part of global operating standards, patent holders give irrevocable unilateral 

undertakings for the producers and consumers of tech products to use their patents on payment 

of a fee which is fair, reasonable and non-discriminatory.37 It is possible that these sorts of 

solutions may come to be imposed by law by states operating pursuant to international 

agreements. 

The fourth topic is the use of digital techniques to reduce transaction costs in policing of 

contracts, through smart contracts which are self-executing, without interventions of humans. 

An example is, where payment for a service delivered and installed on a computer fails to register 

on time, the computer shuts off the service. Smart contracts will become more sophisticated. 

They will create substantial efficiencies.  But sometimes they will misfunction, and legal doctrine 

will need to adapt to that, in ways that are supportive of the technology and of what the parties 

seek to do. The recent decision in Singapore in B2C2 Ltd v Quoine Pte Ltd38 provides an arresting 

illustration. A glitch arising from the interaction of a currency trader’s algorithmic trading 

program with a currency trading platform’s program resulted in automatic trades being effected 

to purchase currency at about 1/250th of its true value, thereby realising a huge profit for the 

trader. The trading platform was not permitted to unravel these trades. Defences based on 

implication of contract terms, mistake and unjust enrichment all failed.39 The judge had to make 

sense of the concept of mistake in contract when two computer programs trade with each other. 

He did so by looking at the minds and expectations of the programmers, even though they were 

not involved in the trades themselves.40 But in future the programs may become so sophisticated 

and operate so independently that it may be that this process of looking back through them to 

the minds of those who created them will seem completely unreal. Legal doctrine is going to 

have to adapt to this new world.  

37 Huawei Technologies Co. Ltd v Unwired Planet International Ltd [2018] EWCA Civ 2344. The case is under appeal to the 
Supreme Court. See also the discussion about FRAND regimes in the communication from the Commission, the 
Council and the European Economic and Social Committee dated 2017 (COM (2017) 712 final), referred to at para 
[60] in the Court of Appeal judgment. 
38 [2019] SGHC (I) 03. 
39 The case is going on appeal. 
40 Para. [210]. 

18 

 
 
                                                           
 (2) Public administration, welfare and the justice system 

Digital government has the potential for huge efficiency savings in the delivery of public services 

and provision of social welfare. But it carries substantial risks as well, in terms of enhancement 

of state power in relation to the individual, loss of responsiveness to individual circumstances 

and the potential to undermine important values which the state should be striving to uphold, 

including human dignity and basic human rights. These include rights of privacy and fair 

determination of civil rights and obligations. Philip Alston writes in his report of the “grave risk 

of stumbling zombie-like into a digital welfare dystopia” in Western countries.  

He argues that we should take human rights seriously and regulate accordingly; should ensure 

legality of processes and transparency; promote digital equality; protect economic and social 

rights in the digital welfare state, as well as civil and political rights; and seek to resist the idea of 

the inevitability of a digital only future.  

Legal scholars Carol Harlow and Richard Rawlings emphasise that the implications of the 

emergent digital revolution for the delivery of public services are likely in the near future to pose 

a central challenge for administrative law.41 Procedures, such as allow for transparency, 

accountability and participation, are a repository for important values of good governance in 

administrative law.42 But it is administrative procedures which are coming under pressure with 

the digitisation of government services. The speed of decision-making in digital systems will tend 

to require the diversion of legal control and judicial review away from the individual decision 

towards the coding of the systems and their overall design.   

Similarly, online courts offer the opportunities for enhanced efficiency in the delivery of public 

services in the form of the justice system, allowing enhanced understanding of rights for 

41 C. Harlow and R. Rawlings, “Proceduralism and Automation: Challenges to the Values of Administrative Law” in 
E. Fisher and A. Young (eds), The Foundations and Future of Public Law (2020, forthcoming), ch. 14. 
42 Harlow and Rawlings (n. 39), 297 

19 

 
 
 
 
 
 
                                                           
individuals and enhanced and affordable access to justice. But the new systems have to allow 

space for the procedural values which are at the heart of a fair and properly responsive system of 

justice.43 

(3) The interface with politics and democracy.  

A number of points should be made here. The tech world clearly places our democracy under 

pressure. Law is both the product of democracy, in the form of statutes passed by Parliament, 

and a foundation of democracy, in the form of creating a platform of protected rights and 

capacities which legitimises our democratic procedures and enables them to function to give 

effect to the general will.44 I have already mentioned the dilemma identified by David Runciman, 

namely the problem of disconnection between democracy and technical control in a public space 

dominated by code. There are plainly other strains as well. Here I am going to call attention to 

four. Time does not allow me to explore solutions in any detail. As a society we are going to 

have to be imaginative about how we address them. The task is an urgent one. 

First, we are witnessing a fracturing of the public sphere. Democracy of the kind with which we 

were familiar in the twentieth century was effective because Parliament worked in the context of 

a communal space for debating issues in the national press, television and radio, which generated 

broad consensus around fundamental values and what could be regarded as fact. Jürgen 

Habermas, for example, gave an attractive normative account of democracy according to which 

legislation could be regarded as the product of an extended process of gestation of public 

opinion through debate in the communal space, which then informed the political and ultimately 

legislative process and was put into refined and concrete statutory form by that process.45 But 

information technology allows people to retreat from that communal space into highly 

particularistic echo-chamber siloes of like-minded individuals, who reinforce each other’s views 

and never have to engage or compromise with the conflicting views of others. What previously 

could be regarded as commonly accepted facts are denounced as fake news, so the common 

43 See generally R. Susskind, Online Courts and the Future of Justice (2019). 
44 See P. Sales, “Legalism in Constitutional Law: Judging in a Democracy” (2018) Public Law 687. 
45 J. Habermas, Between Facts and Norms, trans. William Rehg (1996), ch. 8; C. Zurn, Deliberative Democracy and the 
Institutions of Judicial Review (2007), 239-243; P. Sales, “The Contribution of Legislative Drafting to the Rule of Law” 
[2018] CLJ 630. 

20 

 
 
 
 
                                                           
basis for discussion of the world is at risk of collapse. In elections, the detailed information 

about individuals harvested by computing platforms allows voters to be targeted by messaging 

directed to their own particular predilections and prejudices, without the need to square the 

circle of appealing to other points of view at the same time. We need to find ways of 

reconstituting a common public space. 

Secondly, Jamie Susskind points out that the most immediate political beneficiaries of the 

ongoing tech revolution will be the state and big tech firms: 

“The state will gain a supercharged ability to enforce the law, and certain powerful tech 

firms will be able to define the limits of our liberty, determine the health of our 

democracy, and decide vital questions of social justice.”46 

There is already concern about the totalitarian possibilities of state control which are being 

illustrated with China’s social credit system, in which computers monitor the social behaviour of 

citizens in minute detail and rewards or withholds benefits according to how they are marked by 

the state. But Susskind argues that digital tech also opens up possibilities for new forms of 

democracy and citizen engagement, and that to protect people from servitude we need to exploit 

these new avenues to keep the power of the supercharged state in check.47 In relation to the tech 

companies, he argues for regulation to ensure transparency and structural regulation to break up 

massive concentrations of power. Structural regulation would be aimed at ensuring liberty for 

individuals and that the power of the tech companies is legitimate.48 

Thirdly, James Williams, in his book Stand Out of Our Light,49 identifies a further subtle threat to 

democracy arising from the pervasiveness of information technology and the incessant claims 

46 Future Politics (n. 6), 346.  
47 Future Politics (n. 6), 347-348 and ch. 13, “Democracy in the Future”. 
48 According to Susskind’s vision, the regulation would implement a new separation of powers, according to which 
“no firm is allowed a monopoly over each of the means of force, scrutiny, and perception-control” and “no firm is 
allowed significant control over more than one of the means of force, scrutiny, and perception control together”: 
Future Politics (n. 6), 354-359. 
49 J. Williams, Stand Out of Our Light, (n. 1). 

21 

 
 
 
 
 
                                                           
that it makes on our attention. According to him, the digital economy is based on the 

commercial effort to capture our attention. In what he calls the Age of Attention, information 

abundance produces attention scarcity. At risk is not just our attention, but our capacity to think 

deeply and dispassionately about issues and hence even to form what can be regarded as a 

coherent will in relation to action. He points out that the will is the source of the authority of 

democracy. He observes that as the digital attention economy is compromising human will, it 

therefore strikes “at the very foundations of democracy”, and that this could “directly threaten 

not only individual freedom and autonomy, but also our collective ability to pursue any politics 

worth having.”50 

He argues that we must reject “the present regime of attentional serfdom” and instead 

“reengineer our world so that we can give attention to what matters.”51 That is a big and difficult 

project. As Williams says, the issue is one of self-regulation, at both individual and collective 

levels.52 It seems that law will have to have some part to play in supporting achieving it, perhaps 

through some form of public regulation. We have made the first steps to try to fight another 

crisis of self-regulation, obesity, through supportive public regulation. Similarly, in relation to the 

digital world, as Williams points out, it is not realistic to expect people to “bear the burdens of 

impossible self-regulation, to suddenly become superhuman and take on the armies of 

industrialized persuasion”.53  But at the moment, it is unclear how public regulation would work 

and whether there would be the political will to impose it. 

Fourthly, the law has an important role to play in protecting the private sphere in which 

individuals live their lives and in regulating surveillance. For example, the case law of the 

European Court of Human Rights54 and of our own Investigatory Powers Tribunal55 sets 

conditions for the exercise of surveillance powers by the intelligence agencies and provides an 

effective way of monitoring such exercise.   

50 Stand Out of Our Light (n. 1), 47. 
51 Stand Out of Our Light (n. 1), 127. 
52 Stand Out of Our Light (n. 1), 20. 
53 Stand Out of Our Light (n. 1), 101. 
54 E.g. Liberty v United Kingdom, app. 58243/00, ECtHR, judgment of 1 July 2008. 
55 E.g. Privacy International v Secretary of State for Foreign and Commonwealth Affairs [2018] UKIP Trib IPT 15_110_CH 2 
and related judgments. 

22 

 
 
 
                                                           
(B)  The challenges of Artificial Intelligence 

Some of the challenges to legal doctrine in relation to AI will be extrapolations from those in 

relation to algorithmic programming. But some will be different in kind. At the root of these is 

the interposition of the agency of machines between human agents and events which have legal 

consequences. An example which is much discussed is that of a driverless car which has an 

accident.  

Existing legal doctrine suggests possible analogies on which a coherent legal regime might be 

based. The merits and demerits of each have to be compared and evaluated before final 

decisions are made. We should be trying to think this through now. There is already a 

burgeoning academic literature in this area, engaging with fundamental legal ideas. 

Legislation at the EU level is beginning to come under consideration, stemming from a 

European Parliament Resolution and Report in January 2017.56 On the issue of liability for the 

acts of robots and other AIs, the resolution proposes57 including a compulsory insurance 

scheme, compensation fund and, in the case of sophisticated AIs, “a specific legal status for 

robots in the long run”. 

On one approach,58 sophisticated AIs with physical manifestations, such as self-driving cars, 

could be given legal personhood like a company.59 However, types of AI differ considerably and 

56 European Parliament, Report on civil law rules of robotics (A8-0005/2017) (27 January 2017) and European Parliament, 
Resolution on civil law rules of robotics (P8_TA(2017)0051) (27 January 2017). 
57 Para 59. 
58 See e.g. Jiahong Chen and Paul Burgess, “The boundaries of legal personhood: how spontaneous intelligence can 
problematise  differences  between  humans,  artificial  intelligence,  companies  and  animals”  (2019)  27  Artificial 
Intelligence and Law 73-92. See also G. Hallevy, When robots kill: artificial intelligence under criminal law (2013); S. Bayern, 
“The Implications of Modern Business-Entity Law for the Regulation of Autonomous Systems” (2016) 7(2) European 
Journal of Risk Regulation 297-309; Bayern et al, “Company Law and Autonomous Systems: A Blueprint for Lawyers, 
Entrepreneurs, and Regulators” (2017) 9(2) Hastings Science and Technology Law Journal 135-162; 
59 The common factors being (1) physical location, (2) human creation for a purpose or function and (3) policy 
reasons for anchoring liability back to other natural or legal persons: Chen and Burgess (n. 58), p.81. 

23 

 
 
 
 
 
 
                                                           
a one-size-fits-all approach is unlikely to be appropriate.60 It may be necessary to distinguish 

between ordinary software used in appliances, for which a straightforward product liability 

approach is appropriate, and that used in complex AI products.61  

A contrary approach is to maintain the traditional paradigm of treating even sophisticated AIs as 

mere products for liability purposes.62 A middle way has also been proposed, in which some but 

not all AIs might be given separate legal personality, depending on their degree of autonomous 

functionability and social need;63 but may be denied “[i]f the practical and legal responsibility 

associated with actions can be traced back to a legal person”.64 There are concerns about 

allowing creators or operators of AIs to enjoy a cap on liability for the acts of such the machines, 

which Jacob Turner calls the “Robots as Liability Shields” objection.65  

However, legal personality for AIs could be used in conjunction with other legal techniques, 

such as ideas of vicarious liability and requirements for compulsory insurance.66 These are 

familiar ways of distributing risk in society.  

Conclusion 

It is time to conclude. Algorithms and AI present huge opportunities to improve the human 

condition. They also pose grave threats. These exist in relation to both of the diverging futures 

which the digital world seems to offer: technical efficiency and private market power for Silicon 

Valley, on the one hand, and more authoritarian national control, as exemplified by China, on 

the other. 

60 Chen and Burgess (n. 58), p. 74. 
61 Chen and Burgess (n. 58), p 90. 
62 S. Solaiman, “Legal personality of robots, corporations, idols and chimpanzees: a quest for legitimacy” (2017) 25 
(2) Artificial Intelligence and Law 155-179. Solaiman objects to extending the corporate model to sophisticated AIs, 
principally on the grounds that this would serve the undesirable aim of exonerating the creators and users from liability 
where significant harm to humans can or has been caused by AIs and the inability to apply a rights-duties analysis. 
63 Robert van den Hoven van Genderen, “Legal personhood in the age of artificially intelligent robots” in Woodrow 
Barfield and Ugo Pagallo (eds), Research Handbook on the Law of Artificial Intelligence (2018: Edward Elgar), ch.8. 
64 Van Genderen (n. 63), 245. 
65 Jacob Turner, Robot Rules: Regulating Artificial Intelligence (Palgrave Macmillan: 2018), 191-193.  
66 See Lord Hodge (n. 4): “The law could confer separate legal personality on the machine by registration and 
require it or its owner to have compulsory insurance to cover its liability to third parties in delict (tort) or 
restitution”. 

24 

 
 
 
 
                                                           
The digitisation of life is overwhelming the boundaries of nation states and conventional legal 

categories, through the volume of information which is gathered and deployed and the speed 

and impersonality of decision-making which it fosters. The sense is of a flood in which the flow 

of water moves around obstacles and renders them meaningless. Information comes in streams 

which cannot be digested by humans and decisions flow by at a rate that the court process 

cannot easily break up for individual legal analysis. Law needs to find suitable concepts and 

practical ways to structure this world in order to reaffirm human agency at the individual level 

and at the collective democratic level. It needs to find points in the stream where it can intervene 

and ways in which the general flow can be controlled, even if not in minute detail. Law is a 

vehicle to safeguard human values. The law has to provide structures so that algorithms and AI 

are used to enhance human capacities, agency and dignity, not to remove them. It has to impose 

its order on the digital world and must resist being reduced to an irrelevance. 

Analysing situations with care and precision with respect to legal relationships, rights and 

obligations is what lawyers are trained to do. They have a specific form of technical expertise and 

a fund of knowledge about potential legal solutions and analogies which, with imagination, can 

be drawn upon in this major task. Lawyers should be engaging with the debates about the digital 

world now, and as a matter of urgency.    

25 

 
 
 
"""


