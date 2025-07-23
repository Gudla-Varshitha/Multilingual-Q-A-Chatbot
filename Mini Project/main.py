from app.qa_pipeline import answer_question
from app.translate import translate_text
from app.detect_language import detect_language

def main():
    user_input = input('Ask your question: ')
    output_lang = input('Enter preferred output language (e.g., hi, te, fr): ')
    src_lang = detect_language(user_input)
    print(f'Detected input language: {src_lang}')
    answer = answer_question(user_input, src_lang)
    translated = translate_text(answer, 'en', output_lang)
    print(f'Answer: {translated}')

if __name__ == '__main__':
    main()