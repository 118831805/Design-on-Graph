# Design-on-Graph
Design-on-Graph: A graph retrieval-augmented generation-based method to support manufacturing system design

🔗 ​**Knowledge-Aware Manufacturing System Design | 🏗️ LLM+KG Powered Automation**​

---

## 1. Overall project description

-This project proposes the **Design-on-Graph** method, which is an intelligent design framework for manufacturing systems based on **GraphRAG​**. It utilizes a Large Language Model (LLM) to efficiently manage domain knowledge and automatically generate design solutions.


-The ontology and knowledge graph constructed for this project can be found in the GitHub repository, with the following links: https://github.com/zhengxiaochen/ontology_aircraft_system

### 1.1 Core Innovation：
- 🧠 ​**Knowledge dynamic retrieval**​：Using a multi round dialogue mechanism to intelligently retrieve structured constraint conditions from the knowledge graph in the manufacturing field

- 🏭 ​**Context aware design**​：Utilizing dialogue history archiving to achieve continuous accumulation of design knowledge and contextual inference
  
- ✈️ ​**Industrial grade verification**​：Constructing a complete AI agent workflow using the aircraft fuselage connection system as a testing scenario
  

### 1.2 Technical highlights：
✅ ​**Cross modal knowledge fusion**​  
Unify the encoding of structured knowledge (graph data) such as topological constraints and physical parameters of manufacturing systems with natural language descriptions (text data)

✅ ​**Multi objective optimization support**​  
Balancing multidimensional optimization objectives such as production efficiency, cost control, and performance indicators through LLM's chain reasoning capability

✅ ​**Interpretable design**​  
All generated design schemes come with a knowledge traceability path, supporting the retrieval of original domain knowledge nodes through backtracking 

### 1.3 Core Content：
The design of large-scale equipment manufacturing systems plays a crucial role in ensuring product performance, optimizing production efficiency, and reducing lifecycle costs. Effective reuse of domain knowledge is essential for maintaining both the quality and efficiency of manufacturing system design. Although existing knowledge graph technologies standardize the representation and storage of such domain knowledge, the complex design constraints and multiple optimization objectives of manufacturing systems still pose significant challenges to the efficient reuse of domain knowledge. Recent advancements in the large language model (LLM) and retrieval-augmented generation (RAG) have led to the emergence of graph retrieval-augmented generation (GraphRAG), which presents a promising approach to overcoming these challenges. This paper proposes a novel GraphRAG-based method, Design-on-Graph, to support knowledge management and automated generation of design plans for manufacturing systems. This method employs the LLM to intelligently retrieve and verbalize structured domain knowledge through multi-turn conversations, achieving high-efficiency knowledge management for manufacturing systems. Additionally, the retrieved domain knowledge is systematically archived within conversation history, providing contextual support for LLM-driven reasoning tasks to streamline automated design processes. Finally, a case study on an aircraft fuselage joint system serves as the test scenario, and an AI agent incorporating all the above functionalities is developed to demonstrate and evaluate the performance of the proposed Design-on-Graph method.

![0db01adc3553f46fbae9a7d4a7a72b4](https://github.com/user-attachments/assets/24f7a978-e4ff-4ab1-a3f6-61daf7e4eb4c)


### 1.4 Related papers：
If you think our code is helpful to you, please cite the following paper：

[1] Design-on-Graph: A graph retrieval-augmented generation-based method to support manufacturing system design

[2] An Ontology-based Engineering system to supporort aircraft manufacturing system design

[3] A semantic-driven tradespace framework to accelerate aircraft manufacturing system design

[4] An aircraft assembly process formalism and verification method based on semantic modeling and MBSE

---

## 2. Introduction to Core Documents

This project includes two core modules for collaborative work, forming a complete closed loop from knowledge reasoning to visual application.


They are **Design_on_Graph.py**and **app_for_Design_on_Graph.py**, which will be introduced one by one.

### 2.1 `Design_on_Graph.py` - Core reasoning engine
​**Positioning**​：The interaction center between knowledge graph and LLM in the manufacturing field

▸ Core functions：  

-**Knowledge Retrieval**: Extracting structured data such as topological constraints and material properties from manufacturing knowledge graphs through SPARQL queries

-**Multi round conversation management**: Maintain conversation history context (` ConversationBufferWindowMemory `)

-**Design Verification**: Check the compliance of generated solutions with manufacturing standards

▸ The core architecture is shown in the following figure：  

![c660ad2d7de037d9d87d9e53de00c41](https://github.com/user-attachments/assets/a4cbd701-cc9a-4694-a460-047b50fb9dec)



#### ​**Design-on-Graph Core Data Structure Manual**​：

```python

 1. Main Components

🔗  1.1 Language Models
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_2 = ChatOpenAI(model="gpt-4o", temperature=0)
llm_3 = ChatOpenAI(model="o1-preview", temperature=0)

🔗  1.2 Graph Database Connection
graph = Neo4jGraph()

🔗  1.3 Memory Component
memory = ConversationBufferWindowMemory(k=10)


 2. Chain Components

🧠 ​ 2.1 Router Chain
Prompt Template:

router_prompt = PromptTemplate(
    input_variables=["question"],
    template=""" 
You are an intelligent routing assistant responsible for determining whether a question should be answered using the knowledge graph.

Current question: {question}

Please follow the rules below to decide:
1. If the question ​**does not contain**​ "This is a general question" and is clearly related to knowledge graph content (e.g., it contains words like process, operation, resource, predecessor), respond with ​**​"graph"​**.
2. If the question is ​**not related to the knowledge graph**​ (e.g., it contains words like design, scheme, generate, analyze, check), respond with ​**​"general"​**.
3. If the question ​**contains**​ the phrase "This is a general question", always respond with ​**​"general"​**, regardless of other content.
4. If you are unsure, respond with ​**​"graph"​**.

Only respond with ​**​"graph"​**​ or ​**​"general"​**. Do not add any other content.
"""
)

Chain Construction:

router_chain = router_prompt | llm



🧠 ​ 2.2 Cypher Chain

cypher_chain = GraphCypherQAChain.from_llm(
    llm=llm,
    graph=graph,
    allow_dangerous_requests=True,
    verbose=True,
    exclude_types=[
        "Class", "Relationship", "_GraphConfig", "SCO_RESTRICTION",
        "DOMAIN", "RANGE", "isSubClassOf", "isSubPropertyOf", "hasOptionalAutoOperation",
        "hasOptionalManualOperation"
    ],
    top_k=300,
    return_direct=True,
    return_intermediate_steps=True
)



🧠 ​ 2.3 Graph Response Chain

Prompt Template:

graph_response_prompt = PromptTemplate(
    input_variables=["question", "graph_data", "cypher"],
    template=""" 
You are a professional assistant for answering questions about aircraft fuselage assembly using knowledge graph results. All query results are directly retrieved from the knowledge graph and are accurate and structured.

Your goal is to help users understand the dependencies and semantics of aircraft assembly operations, based solely on the given data.

Current question: {question}

Cypher query executed: {cypher}

Query results from the knowledge graph: {graph_data}

Instructions:
1. Carefully analyze the query result and extract only the relevant information needed to answer the current question.
2. Present the answer clearly in ​**a structured list format**, making it easy to understand the relationships or dependencies.
3. If the question involves sequences (such as operation dependencies), emphasize ​**precedence relationships**​ and explain them.
4. Do not include or infer any information that is not directly present in the knowledge graph result.
5. Do not omit any values in graph data.
"""
)

Chain Construction:

graph_response_chain = graph_response_prompt | llm_2



🧠 ​ 2.4 General QA Chain

Prompt Template:

general_qa_prompt = PromptTemplate(
    input_variables=["question", "history"],
    template=""" 
​**Role**: Aircraft Assembly Planning Expert  
​**Task**: You are an expert in aircraft fuselage assembly planning. Your task is to generate a complete and feasible assembly scheme based only on the conversation history and current question.

Conversation history: {history}

Current question: {question}

​**Process Requirements**:
Phase 1. ​**Data Extraction**​  
- Extract ALL operations and resources from conversation history, show them as a table
1. For each operation, document:  
▪ Type (Manual/Automatic)  
▪ Duration (min)  
▪ Required Resources (name (number))  
▪ Immediate Predecessors  
2. For each resource, document:
▪ Cost (€/h)  
▪ Calendar  
▪ Quantity 

Phase 2. ​**Constraint Analysis**​  
- Analysis specific constraints
- Analysis automatic and manual quarter aircraft fuselage assembly logic
- List the sequence chains of operations required to complete one automatic 1/4 body assembly
- List the sequence chains of operations required to complete one manual 1/4 body assembly

Phase 3. ​**Scheme Generation**​  
- Generate a complete aircraft fuselage assembly scheme following the output format, including the assembly of four quarter-fuselages.
- The generated scheme must meet the following requirements：
▪ Only the same manual operations can be carried out in parallel
▪ Automatic operations cannot be carried out in parallel with any other operations
- Output Format:
| Order | Operation | Type | Required Resources | Duration | Start Time | End Time | Parallel Group |
|-------|-----------|------|---------- ---------|----------|------------|----------|----------------|
Note:
▪ Order: Use a single number (1, 2, 3, ...) if it is executed sequentially
▪ Order: Use number + letter suffix (4a, 4b) if it is executed in parallel
▪ Parallel Group: Use letter suffix (a, b)
▪ This plan must include the assembly of four quarter-fuselages.
▪ You must generate a complete list of scheme without any form of omission

Phase 4. ​**Validation Report**:
- Check if the following conditions are met. Mark ✓ if met, and ✗ if not met.
▪ [✓/✗] Completed 4 assemblies of 1/4 body
▪ [✓/✗] Automatic operations are executed sequentially
▪ [✓/✗] No manual/auto overlap
▪ [✓/✗] Shared steps correctly positioned 
▪ [✓/✗] Resource limits maintained
- If any of the conditions is not met, re-execute phase 3.
"""
)

Chain Construction:

general_qa_chain = general_qa_prompt | llm_3



3. Smart QA System Function

✈️ 3.1 Function Definition

def smart_qa_system(question):
    history = memory.load_memory_variables({}).get('history', '')
    graph_html = None

✈️ 3.2 Main Processing Logic

    try:
        response = router_chain.invoke({"question": question})
        response_type = response.content.strip().lower()

        if response_type == "graph":
            print("【System】Judged as a Graph problem, queried using the query assistant")

            cypher_output = cypher_chain.invoke({"query": question})
            graph_data = cypher_output.get("result", cypher_output)

            intermediate_steps = cypher_output.get("intermediate_steps", [])
            if intermediate_steps and isinstance(intermediate_steps[0], dict):
                cypher = intermediate_steps[0].get("query", "").replace("cypher", "").strip()
            else:
                cypher = ""

            print(f"【Debug】Generated Cypher: {cypher}")
            print(f"【Debug】Raw data for knowledge graphs: {graph_data}")

            graph_html = generate_graph_html(graph_data)
            print(f"【Debug】Path to the HTML file of the generated Knowledge Graph: {graph_html}")

            answer = graph_response_chain.invoke({
                "question": question,
                "graph_data": graph_data,
                "cypher": cypher
            })
        else:
            print("【System】Judged as a Design question, answered using the reasoning assistant.")
            answer = general_qa_chain.invoke({
                "question": question,
                "history": history
            })

        result = answer.content
✈️ 3.3 Error Handling

    except Exception as e:
        print(f"【Error】Errors in dealing with problems: {str(e)}")
        result = "Sorry, there was an error processing your question. Please try asking the question again or ask a different question."

✈️ 3.4 Memory Management and Return

    memory.save_context({"input": question}, {"output": result})
    return result, graph_html

 ``` 

### 2.2 app_for_Design_on_Graph.py - Visual application interface


#### ​**app_for_Design_on_Graph Core Data Structure Manual**​：

```python

🖼️ 1.1 Overall layout

with gr.Blocks() as demo:
  
    with gr.Row():
        with gr.Column(scale=1, min_width=120):
            gr.Image(...) 
        with gr.Column(scale=2):
            gr.Markdown(...)  
    
    
    with gr.Row():
        with gr.Column(scale=4):
            graph_html = gr.HTML(...)  
        with gr.Column(scale=5):
            chatbot = gr.Chatbot(...)  
            user_input = gr.Textbox(...)  
          
            with gr.Row():
                send_btn = gr.Button("Send")
                clear_btn = gr.Button("Clear")
    
    
    with gr.Row():
        gr.Markdown("​**Examples:​**​")
        gr.Button("Process").click(...)
        gr.Button("Operation").click(...)
      



🗃️ 2. Core Interaction Logic

🗃️ 2.1 Message handler

def handle_chat(user_message, history):
    clean_old_graphs()
    response, graph_html_path = smart_qa_system(user_message)
    graph_html_content = get_graph_html_content(graph_html_path)
    
    return [
        history + [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": response}
        ],
        graph_html_content
    ]


    
🗃️ 2.2 Button binding

send_btn.click(
    fn=handle_chat,
    inputs=[user_input, chatbot],
    outputs=[chatbot, graph_html]
)

clear_btn.click(
    fn=lambda: ([], default_graph_html),
    outputs=[chatbot, graph_html]
)


🤖  3. Preset query template

🤖  3.1 Process inquiry

"List the subprocess of each process."

🤖 3.2 Resource Query

"List all information of resources."

🤖 3.3 Scheme design query

"""This is a general question. Please help me design a complete aircraft fuselage assembly scheme...
(Contains 9 specific constraints)"""


🌐 4. System Configuration

🌐 4.1 Static resource directory

static_dir = os.path.join(os.getcwd(), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

🌐 4.2 Startup parameter 

demo.launch(
    server_name="localhost",
    server_port=7860,
    share=False
)


```


## 3. Environment configuration .env

```ini
# ========================
# ️️️️️✈️ Core AI service configuration
# ========================
OPENAI_API_KEY=  
OPENAI_BASE_URL=  

# ========================
# ️️️️️🏭 Manufacturing Knowledge Graph Connection
# ========================
NEO4J_URI=bolt://localhost:7687       
NEO4J_USERNAME=aerospace_engineer    
NEO4J_PASSWORD=
```
