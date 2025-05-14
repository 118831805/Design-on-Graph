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

### ​**Design-on-Graph 核心数据结构手册**​：

```python
🔗 知识图谱交互层
class EnhancedNeo4jGraph(Neo4jGraph):
    """
    航空制造知识图谱连接器（扩展自langchain_community.graphs.Neo4jGraph）
    
    关键数据表：
    │ 节点类型       │ 属性示例                      │ 标签          │
    │---------------│------------------------------│---------------│
    │ Operation     │ name, duration, auto/manual  │ HAS_PRECEDENCE│
    │ Resource      │ type, cost, quantity         │ REQUIRES      │
    │ Constraint    │ standard, tolerance          │ APPLIES_TO    │
    """
    QUERY_TEMPLATES = {
        "precedence": "MATCH (a:Operation)-[r:HAS_PRECEDENCE]->(b) RETURN a.name, type(r), b.name",
        "resource": "MATCH (o:Operation)-[r:REQUIRES]->(res) RETURN o.name, res.type, r.quantity"
    }

🧠 多轮对话记忆体
python
复制
class AssemblyMemory(ConversationBufferWindowMemory):
    """
    飞机装配对话上下文存储器（继承自ConversationBufferWindowMemory）
    
    数据结构：
    {
        "history": [
            {
                "input": "如何优化第3象限铆接顺序？",
                "output": "建议方案：1. 先完成自动铆接（操作A12）...",
                "metadata": {
                    "constraints": ["ASME_Y14.5", "ISO_9001"],
                    "resources": ["RivetBot-3"]
                }
            }
        ],
        "buffer_size": 10  # 保留最近10轮关键对话
    }
    """
🛠️ 制造设计核心类
python
复制
class AircraftAssemblyDesign:
    def __init__(self):
        # 设计参数（航空专用字段）
        self.design_parameters = {
            "material": ("AL-7075", "NASM-1256"),  # 材料标准
            "joint_type": ["lap", "butt"],         # 连接形式
            "load_requirements": {                 # 载荷要求
                "static": "≥3.5kN", 
                "fatigue": "10^6 cycles"
            }
        }
        
        # 约束关系图（使用networkX扩展）
        self.constraint_graph = nx.MultiDiGraph(
            incoming_graph_data=None,
            ​**​{
                "node_type": {
                    "operation": {"color": "#FF6B6B", "shape": "box"},
                    "resource": {"color": "#4ECDC4", "shape": "diamond"}
                },
                "edge_attrs": {
                    "HAS_PRECEDENCE": {"style": "dashed"},
                    "REQUIRES": {"arrowsize": 1.5}
                }
            }
        )
        
        # 优化指标（航空特定指标）
        self.optimization_metrics = [
            ("weight_reduction", "Δkg", "目标减重"),
            ("cost", "€", "总成本"),
            ("assembly_time", "min", "工位周期")
        ]
📊 图数据解析规范
python
复制
GRAPH_DATA_SCHEMA = {
    # 格式A：单节点详情（用于资源/操作详情展示）
    "Format_A": {
        "sample": [{"operation": {"name": "A12", "type": "auto"}}],
        "mapping": {
            "name": "节点名称",
            "type": ("manual", "auto")
        }
    },
    
    # 格式B：二元关系对（用于工序依赖）
    "Format_B": {
        "sample": [{"pre_op": "A11", "post_op": "A12"}],
        "required_fields": ["pre_op", "post_op"]
    },
    
    # 格式C：嵌套属性（用于带约束的操作）
    "Format_C": {
        "sample": [{
            "operation": {"name": "A12", "duration": 120},
            "constraint": {"type": "parallel_limit", "value": 2}
        }],
        "nested_fields": ["operation", "constraint"]
    }
}
⚙️ 可视化配置
python
复制
VISUALIZATION_PROFILES = {
    "default": {
        "physics": {
            "solver": "forceAtlas2Based",
            "gravitationalConstant": -50  # 负值实现节点分散
        },
        "nodes": {
            "operation": {
                "color": {
                    "auto": "#5F6FFF",
                    "manual": "#FF7E5F"
                },
                "size": {
                    "critical": 25,
                    "normal": 15
                }
            },
            "resource": {
                "shape": "diamond",
                "color": "#6BDD9D"
            }
        }
    },
    "simplified": {
        "physics": {"enabled": False},
        "nodes": {"fixed": True}
    }
}
#### 🧠多轮对话记忆体


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
