from core.tools.tool_router import ToolRouter


router = ToolRouter()


task = {

"type":"code",

"text":"write python telegram bot",

"requires_tool":False

}


print(
    router.select_tool(task)
)
