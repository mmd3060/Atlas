from core.cost.token_analyzer import TokenAnalyzer


analyzer = TokenAnalyzer()



messages = [

    "سلام",

    "این کد python مشکل دارد و باید debug شود",

    "یک مقاله کامل درباره هوش مصنوعی با جزئیات زیاد بنویس",

    "یک توضیح جامع درباره شبکه های عصبی بده"

]



for msg in messages:

    print("\nMessage:")
    print(msg)

    print(
        analyzer.analyze(msg)
    )
