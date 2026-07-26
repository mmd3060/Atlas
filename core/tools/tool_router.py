class ToolRouter:


    def select_tool(self, task):


        tools = []


        text = task.get(
            "text",
            ""
        ).lower()



        if task.get("requires_tool"):

            if any(
                x in text
                for x in [
                    "price",
                    "bitcoin",
                    "قیمت",
                    "weather",
                    "هوا"
                ]
            ):

                tools.append(
                    "web_search"
                )



        if task.get("type") == "code":

            tools.append(
                "code_executor"
            )



        return {

            "tools": tools,

            "count": len(tools)

        }
