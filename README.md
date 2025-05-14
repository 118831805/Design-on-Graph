# Design-on-Graph
Design-on-Graph: A graph retrieval-augmented generation-based method to support manufacturing system design

🔗 ​**Knowledge-Aware Manufacturing System Design | 🏗️ LLM+KG Powered Automation**​

---

## 1. 项目整体描述

-本项目提出**Design-on-Graph**方法，这是一个基于**GraphRAG（图检索增强生成）​**的制造系统智能化设计框架，通过大语言模型（LLM）实现领域知识的高效管理与设计方案的自动生成。

-本项目构建的本体和知识图谱可以在github仓库中找到，链接如下：https://github.com/zhengxiaochen/ontology_aircraft_system

### 1.1 核心创新：
- 🧠 ​**知识动态检索**​：采用多轮对话机制智能检索制造领域知识图谱中的结构化约束条件
- 🏭 ​**上下文感知设计**​：利用对话历史归档实现设计知识的持续积累与上下文关联推理
- ✈️ ​**工业级验证**​：以飞机机身连接系统为测试场景构建完整AI代理工作流

### 1.2 技术亮点：
✅ ​**跨模态知识融合**​  
将制造系统的拓扑约束、物理参数等结构化知识（图数据）与自然语言描述（文本数据）统一编码  

✅ ​**多目标优化支持**​  
通过LLM的链式推理能力平衡生产效率、成本控制、性能指标等多维度优化目标  

✅ ​**可解释性设计**​  
所有生成的设计方案均附带知识溯源路径，支持回溯检索到的原始领域知识节点  

### 1.3 核心内容：
The design of large-scale equipment manufacturing systems plays a crucial role in ensuring product performance, optimizing production efficiency, and reducing lifecycle costs. Effective reuse of domain knowledge is essential for maintaining both the quality and efficiency of manufacturing system design. Although existing knowledge graph technologies standardize the representation and storage of such domain knowledge, the complex design constraints and multiple optimization objectives of manufacturing systems still pose significant challenges to the efficient reuse of domain knowledge. Recent advancements in the large language model (LLM) and retrieval-augmented generation (RAG) have led to the emergence of graph retrieval-augmented generation (GraphRAG), which presents a promising approach to overcoming these challenges. This paper proposes a novel GraphRAG-based method, Design-on-Graph, to support knowledge management and automated generation of design plans for manufacturing systems. This method employs the LLM to intelligently retrieve and verbalize structured domain knowledge through multi-turn conversations, achieving high-efficiency knowledge management for manufacturing systems. Additionally, the retrieved domain knowledge is systematically archived within conversation history, providing contextual support for LLM-driven reasoning tasks to streamline automated design processes. Finally, a case study on an aircraft fuselage joint system serves as the test scenario, and an AI agent incorporating all the above functionalities is developed to demonstrate and evaluate the performance of the proposed Design-on-Graph method.

![0db01adc3553f46fbae9a7d4a7a72b4](https://github.com/user-attachments/assets/24f7a978-e4ff-4ab1-a3f6-61daf7e4eb4c)


### 1.4 相关论文：
如果您认为我们的代码对您有帮助，请引用以下论文：

[1] Design-on-Graph: A graph retrieval-augmented generation-based method to support manufacturing system design

[2] An Ontology-based Engineering system to supporort aircraft manufacturing system design

[3] A semantic-driven tradespace framework to accelerate aircraft manufacturing system design

[4] Development of an application ontology for knowledge management to support aircraft assembly system design

---

## 2. 核心文件介绍

本项目包含两个协同工作的核心模块，形成从知识推理到可视化应用的完整闭环。

分别是**Design_on_Graph.py**与**app_for_Design_on_Graph.py**，接下来将逐一介绍。


### 2.1 `Design_on_Graph.py` - 核心推理引擎
​**定位**​：制造领域知识图谱与LLM的交互中枢  
▸ 核心功能：  
- ​**知识检索**​：通过SPARQL查询从制造知识图谱中提取拓扑约束、材料属性等结构化数据  
- ​**多轮对话管理**​：维护对话历史上下文（`ConversationBufferWindowMemory`）  
- ​**设计验证**​：检查生成方案与制造标准的合规性  


▸ 核心架构如下图所展示：  

![c660ad2d7de037d9d87d9e53de00c41](https://github.com/user-attachments/assets/a4cbd701-cc9a-4694-a460-047b50fb9dec)



#### ​**Design-on-Graph核心数据结构手册**​：

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






 ``` 

### 2.2 app_for_Design_on_Graph.py - 可视化应用接口



#### ​**app_for_Design_on_Graph核心数据结构手册**​：

```python


```python

1.1 整体布局
with gr.Blocks() as demo:
    # 标题区
    with gr.Row():
        with gr.Column(scale=1, min_width=120):
            gr.Image(...)  # 徽标
        with gr.Column(scale=2):
            gr.Markdown(...)  # 标题文本
    
    # 主内容区
    with gr.Row():
        with gr.Column(scale=4):
            graph_html = gr.HTML(...)  # 图形区
        with gr.Column(scale=5):
            chatbot = gr.Chatbot(...)  # 聊天区
            user_input = gr.Textbox(...)  # 输入框
            # 操作按钮
            with gr.Row():
                send_btn = gr.Button("Send")
                clear_btn = gr.Button("Clear")
    
    # 示例区
    with gr.Row():
        gr.Markdown("​**Examples:​**​")
        gr.Button("Process").click(...)
        gr.Button("Operation").click(...)
        # ...其他示例按钮



2. 核心交互逻辑
2.1 消息处理函数
python
复制
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
2.2 按钮绑定
python
复制
# 发送按钮
send_btn.click(
    fn=handle_chat,
    inputs=[user_input, chatbot],
    outputs=[chatbot, graph_html]
)

# 清除按钮
clear_btn.click(
    fn=lambda: ([], default_graph_html),
    outputs=[chatbot, graph_html]
)
3. 预设查询模板
3.1 流程查询
python
复制
"List the subprocess of each process."
3.2 资源查询
python
复制
"List all information of resources."
3.3 方案设计查询
python
复制
"""This is a general question. Please help me design a complete aircraft fuselage assembly scheme...
(包含9条具体约束条件)"""
4. 系统配置
4.1 静态资源目录
python
复制
static_dir = os.path.join(os.getcwd(), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
4.2 启动参数
python
复制
demo.launch(
    server_name="localhost",
    server_port=7860,
    share=False
)
🖼️ 

🗃️ ​​
🤖 
    

🌐

```


## 3. 环境配置.env

```ini
# ========================
# ️️️️️✈️ 核心AI服务配置
# ========================
OPENAI_API_KEY=  
OPENAI_BASE_URL=  

# ========================
# ️️️️️🏭 制造知识图谱连接
# ========================
NEO4J_URI=bolt://localhost:7687       
NEO4J_USERNAME=aerospace_engineer    
NEO4J_PASSWORD=
```
