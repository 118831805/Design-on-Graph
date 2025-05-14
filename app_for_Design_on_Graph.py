import gradio as gr
from Design_on_Graph import smart_qa_system
import os
import time
from pathlib import Path
import urllib.parse

def clean_old_graphs(static_folder="static", max_age=3600):
    current_time = time.time()
    static_path = Path(static_folder)

    if not static_path.exists():
        return

    for html_file in static_path.glob("graph_*.html"):
        file_age = current_time - html_file.stat().st_mtime
        if file_age > max_age:  # 删除超过1小时的旧文件
            try:
                html_file.unlink()
            except Exception as e:
                print(f"Error deleting {html_file}: {e}")

def get_graph_file_url(graph_html_path):
    if not graph_html_path:
        return None

    full_path = Path(os.getcwd()) / graph_html_path.lstrip("/")

    if not full_path.exists():
        return None

    return f"file/{urllib.parse.quote(str(full_path))}"

def get_graph_html_content(graph_html_path):
    if not graph_html_path:
        return "..."

    full_path = Path(os.getcwd()) / graph_html_path.lstrip("/")

    if not full_path.exists():
        return "..."

    with open(full_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    return f"""
    <div style='width: 100%; height: 650px; border: 1px solid #ccc; overflow: hidden;'>
        <iframe 
            srcdoc="{html_content.replace('"', '&quot;')}"
            style="width: 100%; height: 100%; border: none;"
        ></iframe>
    </div>
    """


with gr.Blocks() as demo:

    with gr.Row():
        with gr.Column(scale=1, min_width=120):
            gr.Image(value="logo.png", show_label=False, container=False, show_download_button=False,
                     show_share_button=False, interactive=False, show_fullscreen_button=False)
        with gr.Column(scale=2):
            gr.Markdown(
                """
                <h1 style="margin-bottom: 2px; font-size: 28px;">Design-on-Graph: A graph retrieval-augmented generation-based method to support manufacturing system design</h2>
                <p style="font-size: 18px; margin-top: 0;">Supported by the AI4DESE Laboratory, SUSTech, Shenzhen, China.</p>
                """,
                elem_id="custom_title",
                container=False
            )

    with gr.Row():

        with gr.Column(scale=4):
            graph_html = gr.HTML(
                """
                <div style='border: 1px solid #ccc; padding: 10px; height: 650px;
                           display: flex; align-items: center; justify-content: center;'>
                    <p style='color: #666;'>Graph will be shown here after querying...</p>
                </div>
                """
            )

        with gr.Column(scale=5):
            chatbot = gr.Chatbot(label="Chat", elem_id="chatbot", type="messages", height=497)
            user_input = gr.Textbox(placeholder="Ask something...", label=None, lines=1)

            with gr.Row():
                send_btn = gr.Button("Send")
                clear_btn = gr.Button("Clear")

    with gr.Row():
        gr.Markdown("**Examples:**")
        gr.Button("Process").click(
            lambda: "List the subprocess of each process.", None, user_input)
        gr.Button("Operation").click(
            lambda: "List all information of operations. Merge information according to manual and automatic.", None, user_input)
        gr.Button("Resource").click(
            lambda: "List all information of resources.", None, user_input)
        gr.Button("Required resource").click(
            lambda: "Search all relationships between operations and resources. List all names of operations, names of resources, and number of need resources. Merge information according to the operation.",None, user_input)
        gr.Button("Predecessor").click(
            lambda: "List all predecessors of each operation.", None, user_input)
        gr.Button("Plan").click(
            lambda: """This is a general question. Please help me design a complete aircraft fuselage assembly scheme that includes the assembly of four 1/4 bodies, using both automatic and manual methods. Your plan should follow these specific constraints:

1. The first two operations must be "S40_00001_Jig in" and "S40_01001_Set up working environment", and the last operation must be "S40_00002_Jig out". They only need to be executed once during the whole assembly scheme.
2. "S40_04012_Deburring int, positioning, attach them automatic" (automatic) or "S40_04013_Deburring int, positioning, attach them manual" (manual) marks the completion of one 1/4 aircraft fuselage assembly. You must include a total of four such operations to complete the assembly of the entire aircraft fuselage.
3. Automatic assembly operations can only be performed in series, and only one 1/4 body can be automatically assembled at a time. However, manual assembly can be done in series or parallel. At most two sets of manual operations can be carried out in parallel.
4. Manual and automatic operations cannot be carried out in parallel.
5. Only the same manual operations can be carried out in parallel. Different manual operations cannot be carried out in parallel due to their explicit front-back dependencies.
6. Following "S40_04014_Deinstall LFT and rails", must execute: "S40_02002_Cleanup and add sealant" and "S40_02003_Inspection".
7. If multiple 1/4 bodies are manually assembled in series or parallel, it only needs to execute "S40_02002_Cleanup and add sealant" and "S40_02003_Inspection" at the final completion.
8. If multiple 1/4 bodies are automatically assembled in series, only one execution of "S40_02001_Set in position Rails and LFT" is required. When multiple 1/4 bodies are assembled, the final execution of "S40_04014-Deinstall LFT and rails" is needed.
9. Each operation depends on preceding operations, which must be completed first. These dependencies are detailed in the conversation history. Your operation sequence must strictly obey all these dependencies.

Use the conversation history to determine the full list of operations, their types, durations, resources, and dependencies. Present your scheme in a table format, include parallel labels (a, b, c) where appropriate, and calculate the total time and cost. Finally, verify that all constraints have been fully met.""", None, user_input)
        gr.Button("Check").click(
            lambda: "This is a general question: check whether the generated automatic and manual schemes meet the predecessor requirements between operations. If not, please regenerate.", None, user_input)

    def handle_chat(user_message, history):
        clean_old_graphs()

        response, graph_html_path = smart_qa_system(user_message)

        graph_html_content = get_graph_html_content(graph_html_path)

        updated_messages = history + [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": response}
        ]

        return updated_messages, graph_html_content


    send_btn.click(
        fn=handle_chat,
        inputs=[user_input, chatbot],
        outputs=[chatbot, graph_html]
    )

    clear_btn.click(
        fn=lambda: ([], """
            <div style='border: 1px solid #ccc; padding: 10px; height: 650px;
                      display: flex; align-items: center; justify-content: center;'>
                <p style='color: #666;'>Graph will be shown here after querying...</p>
            </div>
        """),
        inputs=[],
        outputs=[chatbot, graph_html]
    )

if __name__ == "__main__":
    static_dir = os.path.join(os.getcwd(), "static")
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

    demo.launch(
        server_name="localhost",
        server_port=7860,
        share=False
    )