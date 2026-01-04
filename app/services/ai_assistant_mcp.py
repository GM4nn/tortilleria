"""
AI Assistant with MCP-like Tool System
The AI can execute SQL queries directly on the database using tools
Uses Claude Sonnet 4.5 with function calling (tool use)
"""

import json
from typing import Dict, Any


from anthropic import Anthropic
from app.constants import AI_ASSISTANT_MAX_TOKENS, AI_ASSISTANT_SYSTEM_PROMPT, AI_ASSISTANT_TEMPERATURE
from app.constants import AI_ASSISTANT_MODEL
from app.services.db_tool import DatabaseTool


class AIAssistantMCP:
    """
    AI Assistant using Claude's native tool calling
    The AI can execute SQL directly on the database
    """

    def __init__(self):
        self.model = AI_ASSISTANT_MODEL
        self.db_tool = DatabaseTool()

    def _get_client(self):
        """Get Anthropic client with current API key"""
        from app import api_key
        if not api_key.API_KEY:
            raise Exception("Por favor, configura primero el asistente usando el botón ⚙️")
        return Anthropic(api_key=api_key.API_KEY)

    def ask(self, question: str, max_iterations: int = 5) -> dict:
        """
        Ask a question to the AI assistant using Claude's tool calling

        Returns:
            dict with keys:
            - response: str (respuesta en lenguaje natural)
            - sql_queries: list (queries SQL ejecutadas)
            - success: bool
        """

        executed_queries = []
        messages = [{"role": "user", "content": question}]

        try:
            # Define the SQL execution tool for Claude
            tools = [{
                "name": "execute_sql",
                "description": (
                    "Ejecuta una consulta SQL SELECT en la base de datos de la tortillería. "
                    "SOLO se permiten consultas SELECT (lectura). "
                    "Úsala para obtener datos sobre ventas, productos, insumos, proveedores, etc."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "La consulta SQL SELECT a ejecutar. Debe seguir la sintaxis de SQLite."
                        }
                    },
                    "required": ["query"]
                }
            }]

            # System prompt with schema

            for iteration in range(max_iterations):
                
                print(f"[DEBUG] Iteración {iteration + 1}/{max_iterations}")

                # Call Claude with tools
                client = self._get_client()
                response = client.messages.create(
                    model=self.model,
                    max_tokens=AI_ASSISTANT_MAX_TOKENS,
                    temperature=AI_ASSISTANT_TEMPERATURE,
                    system=AI_ASSISTANT_SYSTEM_PROMPT,
                    tools=tools,
                    messages=messages
                )

                print(f"[DEBUG] Stop reason: {response.stop_reason}")

                # Process response
                if response.stop_reason == "tool_use":
                    
                    # Claude wants to use a tool
                    assistant_message = {"role": "assistant", "content": response.content}
                    messages.append(assistant_message)

                    # Process tool calls
                    tool_results = []
                    for block in response.content:
                        
                        if block.type == "tool_use":
                            tool_name = block.name
                            tool_input = block.input

                            print(f"[DEBUG] Tool call: {tool_name} - {tool_input}")

                            if tool_name == "execute_sql":
                                sql_query = tool_input.get("query", "")
                                executed_queries.append(sql_query)

                                # Execute SQL
                                result = self.db_tool.execute_sql(sql_query)

                                if result["success"]:
                                    data = result["data"]

                                    # Check if data is empty or null
                                    is_empty = (
                                        not data or
                                        len(data) == 0 or
                                        (len(data) == 1 and all(v is None or v == 0 for v in data[0].values()))
                                    )

                                    if is_empty:
                                        # Return clear message that data is empty
                                        content = json.dumps([], ensure_ascii=False) + "\n\n⚠️ DATOS VACÍOS: La consulta no retornó resultados. Responde al usuario que no hay datos disponibles para su pregunta (ejemplo: 'No hay ventas de tortillas de maíz este mes' o 'No se encontraron datos para este período')."
                                    else:
                                        content = json.dumps(data, ensure_ascii=False)

                                    tool_results.append({
                                        "type": "tool_result",
                                        "tool_use_id": block.id,
                                        "content": content
                                    })
                                else:
                                    tool_results.append({
                                        "type": "tool_result",
                                        "tool_use_id": block.id,
                                        "content": f"Error: {result['error']}",
                                        "is_error": True
                                    })

                    # Add tool results to conversation
                    messages.append({"role": "user", "content": tool_results})

                elif response.stop_reason == "end_turn":
                    # Claude finished - extract final answer
                    
                    final_text = ""
                    for block in response.content:
                        if hasattr(block, "text"):
                            final_text += block.text

                    print(f"[DEBUG] Respuesta final: {final_text[:200]}")

                    return {
                        "success": True,
                        "response": final_text.strip(),
                        "sql_queries": executed_queries
                    }

                else:
                    
                    # Unexpected stop reason
                    print(f"[DEBUG] Stop reason inesperado: {response.stop_reason}")
                    break

            return {
                "success": False,
                "response": "No pude generar una respuesta después de varios intentos.",
                "sql_queries": executed_queries
            }

        except Exception as e:
            error_msg = str(e)
            return {
                "success": False,
                "response": f"Error: {error_msg}",
                "sql_queries": executed_queries
            }

    def check_status(self) -> Dict[str, Any]:
        """Check if Claude API is properly configured"""

        try:

            # Try a simple API call to verify the key works
            try:
                client = self._get_client()
                client.messages.create(
                    model=self.model,
                    max_tokens=10,
                    messages=[{"role": "user", "content": "test"}]
                )

                return {
                    "status": "ready",
                    "message": f"Claude Sonnet 4.5 está listo",
                    "model": self.model
                }
            except Exception as api_error:
                error_str = str(api_error)

                return {
                    "status": "error",
                    "message": f"Error conectando con Claude: {error_str}"
                }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Error verificando Claude: {str(e)}"
            }


# Singleton instance
ai_assistant_mcp = AIAssistantMCP()
