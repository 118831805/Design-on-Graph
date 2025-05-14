# Design-on-Graph
Design-on-Graph: A graph retrieval-augmented generation-based method to support manufacturing system design


## 1. 项目整体描述
The design of large-scale equipment manufacturing systems plays a crucial role in ensuring product performance, optimizing production efficiency, and reducing lifecycle costs. Effective reuse of domain knowledge is essential for maintaining both the quality and efficiency of manufacturing system design. Although existing knowledge graph technologies standardize the representation and storage of such domain knowledge, the complex design constraints and multiple optimization objectives of manufacturing systems still pose significant challenges to the efficient reuse of domain knowledge. Recent advancements in the large language model (LLM) and retrieval-augmented generation (RAG) have led to the emergence of graph retrieval-augmented generation (GraphRAG), which presents a promising approach to overcoming these challenges. This paper proposes a novel GraphRAG-based method, Design-on-Graph, to support knowledge management and automated generation of design plans for manufacturing systems. This method employs the LLM to intelligently retrieve and verbalize structured domain knowledge through multi-turn conversations, achieving high-efficiency knowledge management for manufacturing systems. Additionally, the retrieved domain knowledge is systematically archived within conversation history, providing contextual support for LLM-driven reasoning tasks to streamline automated design processes. Finally, a case study on an aircraft fuselage joint system serves as the test scenario, and an AI agent incorporating all the above functionalities is developed to demonstrate and evaluate the performance of the proposed Design-on-Graph method.
本项目是一个**XXXX工具/系统/库**，主要解决**XXXX问题**。核心特性包括：

- ✅ 特性1（例如：基于XX技术的高性能处理）
- ✅ 特性2（例如：支持XX格式的灵活输入）
- ✅ 特性3（例如：提供可视化监控界面）

适用场景：  
• 场景1（例如：需要快速处理XX数据的开发者）  
• 场景2（例如：希望自动化XX流程的团队）

[![GitHub stars](https://img.shields.io/github/stars/用户名/仓库名?style=social)](https://github.com/用户名/仓库名)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 2. 核心文件介绍

### 2.1 `main.py`（或核心入口文件）
- 📌 功能：系统主入口，负责初始化配置和启动流程
- 🔧 关键参数：
  ```python
  --config 指定配置文件路径
  --debug  启用调试模式
