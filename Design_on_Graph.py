from langchain_openai import ChatOpenAI
from langchain_community.graphs import Neo4jGraph
from langchain.chains import GraphCypherQAChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os
from pyvis.network import Network
import uuid
load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_2 = ChatOpenAI(model="gpt-4o", temperature=0)
llm_3 = ChatOpenAI(model="o1-preview", temperature=0)

graph = Neo4jGraph()

memory = ConversationBufferWindowMemory(k=10)

router_prompt = PromptTemplate(
    input_variables=["question"],
    template=""" 
You are an intelligent routing assistant responsible for determining whether a question should be answered using the knowledge graph.

Current question: {question}

Please follow the rules below to decide:
1. If the question **does not contain** "This is a general question" and is clearly related to knowledge graph content (e.g., it contains words like process, operation, resource, predecessor), respond with **"graph"**.
2. If the question is **not related to the knowledge graph** (e.g., it contains words like design, scheme, generate, analyze, check), respond with **"general"**.
3. If the question **contains** the phrase "This is a general question", always respond with **"general"**, regardless of other content.
4. If you are unsure, respond with **"graph"**.

Only respond with **"graph"** or **"general"**. Do not add any other content.
"""
)

router_chain = router_prompt | llm

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
2. Present the answer clearly in **a structured list format**, making it easy to understand the relationships or dependencies.
3. If the question involves sequences (such as operation dependencies), emphasize **precedence relationships** and explain them.
4. Do not include or infer any information that is not directly present in the knowledge graph result.
5. Do not omit any values in graph data.
"""
)

graph_response_chain = graph_response_prompt | llm_2

general_qa_prompt = PromptTemplate(
    input_variables=["question", "history"],
    template=""" 
**Role**: Aircraft Assembly Planning Expert  
**Task**: You are an expert in aircraft fuselage assembly planning. Your task is to generate a complete and feasible assembly scheme based only on the conversation history and current question.

Conversation history: {history}

Current question: {question}

**Process Requirements**:
Phase 1. **Data Extraction**  
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

Phase 2. **Constraint Analysis**  
- Analysis specific constraints
- Analysis automatic and manual quarter aircraft fuselage assembly logic
- List the sequence chains of operations required to complete one automatic 1/4 body assembly
- List the sequence chains of operations required to complete one manual 1/4 body assembly

Phase 3. **Scheme Generation**  
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

Phase 4. **Validation Report**:
- Check if the following conditions are met. Mark ✓ if met, and ✗ if not met.
▪ [✓/✗] Completed 4 assemblies of 1/4 body
▪ [✓/✗] Automatic operations are executed sequentially
▪ [✓/✗] No manual/auto overlap
▪ [✓/✗] Shared steps correctly positioned 
▪ [✓/✗] Resource limits maintained
- If any of the conditions is not met, re-execute phase 3.
"""
)

general_qa_chain = general_qa_prompt | llm_3

def smart_qa_system(question):
    history = memory.load_memory_variables({}).get('history', '')
    graph_html = None
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

    except Exception as e:
        print(f"【Error】Errors in dealing with problems: {str(e)}")
        result = "Sorry, there was an error processing your question. Please try asking the question again or ask a different question."

    memory.save_context({"input": question}, {"output": result})
    return result, graph_html

def generate_graph_html(graph_data):

    net = Network(height="750px", width="100%", directed=True, notebook=False)
    node_records = {}

    data_format = detect_data_format(graph_data)

    format_handlers = {
        "A": process_format_a,
        "B": process_format_b,
        "C": process_format_c,
        "D": process_format_d
    }

    handler = format_handlers.get(data_format)
    if handler:
        handler(net, graph_data, node_records)

    configure_network(net)
    return save_network(net)

def add_node_if_absent(net, node_records, node_id, label=None, color="#97c2fc", shape="box"):
    if node_id not in node_records:
        net.add_node(node_id, label=label or node_id, color=color, shape=shape)
        node_records[node_id] = True

def process_format_a(net, data, node_records):
    for item in data:
        if isinstance(item, dict):
            for value in item.values():
                if isinstance(value, dict):
                    node_id = str(value.get("name", uuid.uuid4()))
                    add_node_if_absent(net, node_records, node_id, label=generate_attribute_label(value))

def process_format_b(net, data, node_records):
    if not data or not isinstance(data[0], dict):
        return

    keys = list(data[0].keys())[:2]
    if len(keys) < 2:
        return

    field1, field2 = keys
    for item in data:
        node1 = str(item.get(field1, ""))
        node2 = str(item.get(field2, ""))
        if node1 and node2:
            add_node_if_absent(net, node_records, node1, color="#97c2fc", shape="box")
            add_node_if_absent(net, node_records, node2, color="#fc9797", shape="box")
            net.add_edge(node1, node2, color="#666666")

def process_format_c(net, data, node_records):
    if not data or not isinstance(data[0], dict):
        return

    sample = data[0]
    dict_field = next((k for k, v in sample.items() if isinstance(v, dict)), None)
    if not dict_field:
        return

    for item in data:
        dict_data = item.get(dict_field, {})
        node1 = str(dict_data.get("name", uuid.uuid4()))
        add_node_if_absent(net, node_records, node1, label=generate_attribute_label(dict_data))

        other_keys = [k for k in item.keys() if k != dict_field]
        if not other_keys:
            continue

        node2_field = other_keys[0]
        node2 = str(item.get(node2_field, ""))
        add_node_if_absent(net, node_records, node2, color="#fc9797", shape="diamond")

        rel_field = next((k for k in other_keys if k != node2_field), None)
        rel = str(item.get(rel_field, "")) if rel_field else ""
        net.add_edge(node1, node2, label=rel, color="#666666")

def process_format_d(net, data, node_records):
    if not data or not isinstance(data[0], dict):
        return

    fields = list(data[0].keys())
    if len(fields) < 3:
        return

    node1_field, node2_field, rel_field = fields[:3]

    for item in data:
        node1 = str(item.get(node1_field, ""))
        node2 = str(item.get(node2_field, ""))
        rel = str(item.get(rel_field, ""))
        if node1 and node2:
            add_node_if_absent(net, node_records, node1)
            add_node_if_absent(net, node_records, node2)
            net.add_edge(node1, node2, label=rel, color="#666666")

def generate_attribute_label(node_data):
    name = node_data.get("name", "Node")
    attrs = "\n".join(f"{k}: {v}" for k, v in node_data.items() if k != "name")
    return f"{name}\n{attrs}" if attrs else name

def detect_data_format(data):
    if not data or not isinstance(data, list) or not isinstance(data[0], dict):
        return "A"

    sample = data[0]
    dict_fields = [k for k, v in sample.items() if isinstance(v, dict)]
    if len(dict_fields) == 1 and len(sample) >= 3:
        return "C"
    elif len(dict_fields) == 0:
        if len(sample) == 2:
            return "B"
        elif len(sample) >= 3:
            return "D"
    return "A"

def configure_network(net):
    net.toggle_physics(True)
    net.set_options("""
    {
        "physics": {
            "forceAtlas2Based": {
                "gravitationalConstant": -50,
                "centralGravity": 0.01,
                "springLength": 100
            },
            "minVelocity": 0.75,
            "solver": "forceAtlas2Based"
        },
        "nodes": {
            "font": {
                "size": 14
            }
        }
    }
    """)

def save_network(net):
    static_dir = os.path.join(os.getcwd(), "static")
    os.makedirs(static_dir, exist_ok=True)
    filename = f"graph_{uuid.uuid4().hex}.html"
    filepath = os.path.join(static_dir, filename)
    net.save_graph(filepath)
    return f"/static/{filename}"

def get_graph_html(data):
    net = Network(height='500px', width='100%', notebook=False, directed=True)
    for item in data:
        r = item.get('r', {})
        name = r.get('name', 'Unknown')
        net.add_node(name, label=name)
    return net.generate_html()