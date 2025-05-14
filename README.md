# Design-on-Graph
Design-on-Graph: A graph retrieval-augmented generation-based method to support manufacturing system design

🔗 ​**Knowledge-Aware Manufacturing System Design | 🏗️ LLM+KG Powered Automation**​

---

## 1. 项目整体描述

-本项目提出**Design-on-Graph**方法，这是一个基于**GraphRAG（图检索增强生成）​**的制造系统智能化设计框架，通过大语言模型（LLM）实现领域知识的高效管理与设计方案的自动生成。

-本项目构建的本体和知识图谱可以在github仓库中找到，链接如下：https://github.com/zhengxiaochen/ontology_aircraft_system

### 1.1核心创新：
- 🧠 ​**知识动态检索**​：采用多轮对话机制智能检索制造领域知识图谱中的结构化约束条件
- 🏭 ​**上下文感知设计**​：利用对话历史归档实现设计知识的持续积累与上下文关联推理
- ✈️ ​**工业级验证**​：以飞机机身连接系统为测试场景构建完整AI代理工作流

### 1.2技术亮点：
✅ ​**跨模态知识融合**​  
将制造系统的拓扑约束、物理参数等结构化知识（图数据）与自然语言描述（文本数据）统一编码  

✅ ​**多目标优化支持**​  
通过LLM的链式推理能力平衡生产效率、成本控制、性能指标等多维度优化目标  

✅ ​**可解释性设计**​  
所有生成的设计方案均附带知识溯源路径，支持回溯检索到的原始领域知识节点  

### 1.3核心内容：
The design of large-scale equipment manufacturing systems plays a crucial role in ensuring product performance, optimizing production efficiency, and reducing lifecycle costs. Effective reuse of domain knowledge is essential for maintaining both the quality and efficiency of manufacturing system design. Although existing knowledge graph technologies standardize the representation and storage of such domain knowledge, the complex design constraints and multiple optimization objectives of manufacturing systems still pose significant challenges to the efficient reuse of domain knowledge. Recent advancements in the large language model (LLM) and retrieval-augmented generation (RAG) have led to the emergence of graph retrieval-augmented generation (GraphRAG), which presents a promising approach to overcoming these challenges. This paper proposes a novel GraphRAG-based method, Design-on-Graph, to support knowledge management and automated generation of design plans for manufacturing systems. This method employs the LLM to intelligently retrieve and verbalize structured domain knowledge through multi-turn conversations, achieving high-efficiency knowledge management for manufacturing systems. Additionally, the retrieved domain knowledge is systematically archived within conversation history, providing contextual support for LLM-driven reasoning tasks to streamline automated design processes. Finally, a case study on an aircraft fuselage joint system serves as the test scenario, and an AI agent incorporating all the above functionalities is developed to demonstrate and evaluate the performance of the proposed Design-on-Graph method.

### 1.4相关论文：
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

​**关键数据结构**​：
```python
class ManufacturingDesign:
    def __init__(self):
        self.design_parameters = {}  # 存储材料/尺寸等参数
        self.constraint_graph = nx.Graph()  # 网络X构建的约束关系图
        self.optimization_metrics = []  # 成本/强度等优化目标





### 2.1核心创新：


### 2.2核心创新：

- ✅ 特性1（例如：基于XX技术的高性能处理）
- ✅ 特性2（例如：支持XX格式的灵活输入）
- ✅ 特性3（例如：提供可视化监控界面）

适用场景：  
• 场景1（例如：需要快速处理XX数据的开发者）  
• 场景2（例如：希望自动化XX流程的团队）

### 2.1 `main.py`（或核心入口文件）
- 📌 功能：系统主入口，负责初始化配置和启动流程
- 🔧 关键参数：
  ```python
  --config 指定配置文件路径
  --debug  启用调试模式
