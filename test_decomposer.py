from core.brain.task_decomposer import TaskDecomposer

decomposer = TaskDecomposer()

message = "طراحی معماری یک AI Agent حرفه ای با حافظه و ابزار و سیستم تصمیم گیری"

steps = decomposer.decompose(message)

print(steps)
