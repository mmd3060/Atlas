from core.analyzer.message_analyzer import MessageAnalyzer


analyzer = MessageAnalyzer()


message = "این کد python مشکل دارد"


result = analyzer.analyze(message)


print(result)
