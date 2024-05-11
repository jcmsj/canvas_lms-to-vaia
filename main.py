from typing import Literal
import pandas as pd
from bs4 import BeautifulSoup
from clipboard import paste

def cli():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='File path to read. Attempts to read the clipboard if not provided.')
    parser.add_argument('-o', '--output', help='Output file path')
    # --mode selected|correct
    parser.add_argument('--mode', choices=['selected', 'correct'], default='correct', help='Whether to parse selected answers or correct answers')
    # --print prints the df
    parser.add_argument('--print', action='store_true', help='Print the DataFrame')

    args = parser.parse_args()
    return args
def create_xlsx(df:pd.DataFrame, filename:str):
    '''Create an xlsx file from a DataFrame'''
    df.to_excel(filename, index=False)
    # Vaia's excel template is like:
    # Question	Answer A	answer is correct (TRUE if yes, FALSE if no)	Answer B	answer is correct (TRUE if yes, FALSE if no)	Answer C	answer is correct (TRUE if yes, FALSE if no)	Answer D	answer is correct (TRUE if yes, FALSE if no)	Answer E	answer is correct (TRUE if yes, FALSE if no)	Answer F	answer is correct (TRUE if yes, FALSE if no)

def parseHtml(soup:BeautifulSoup, mode:Literal['selected', 'correct']='correct'):
    # Find the div with class question
    questions = soup.find_all('div', class_='question')
    data = [
        [], # first row: 
        [], # second row: Answer A
        [], # third row: whether answer A is correct
        [], # fourth row: Answer B
        [], # fifth row: whether answer B is correct
        [], # sixth row: Answer C
        [], # seventh row: whether answer C is correct
        [], # eighth row: Answer D
        [], # ninth row: whether answer D is correct
        [], # tenth row: Answer E
        [], # eleventh row: whether answer E is correct
        [], # twelfth row: Answer F
        [], # thirteenth row: whether answer F is correct
    ]
    iToLetter = {
        1: 'A',
        3: 'B',
        5: 'C',
        7: 'D',
        9: 'E',
        11: 'F'
    }
    for question in questions:
        question_text = question.find('div', class_='question_text')
        question_string:str = str(question_text.text).strip().removeprefix('This question has been regraded.')
        data[0].append(question_string)
        answer_containers = question.find_all('div', class_='answer_for_')
        for i, answer_container in enumerate(answer_containers):
            answer_text = answer_container.find('div', class_='answer_text')
            isCorrect = False
            if (mode == 'correct'):
                isCorrect = 'correct_answer' in answer_container['class']
            elif (mode == 'selected'):
                isCorrect = 'selected_answer' in answer_container['class']
            isCorrectText = 'TRUE' if isCorrect else 'FALSE'
            answerIndex = (i + 1)*2-1
            data[answerIndex].append(answer_text.text)
            isCorrectIndex = answerIndex + 1
            data[isCorrectIndex].append(isCorrectText)

        # if there are less than 6 answers, fill the rest with empty strings
        for i in range(1, 12, 2):
            if len(data[i]) < len(data[0]):
                data[i].append('')
                data[i+1].append('')

    # count the number of questions
    question_count = len(data[0])
    # remove rows with zero answers
    data = [col for col in data if len(col) == question_count]
    df = pd.DataFrame(data[0], columns=['Question'])
    for i in range(1, len(data),2):
        answerColumn = f'Answer {iToLetter[i]}'
        df.insert(i, answerColumn, data[i])
        isAnswerIndex = i+1
        df.insert(isAnswerIndex, 'answer is correct (TRUE if yes, FALSE if no)', data[isAnswerIndex], allow_duplicates=True)
    return df

def main():
    '''Run if main module'''
    args = cli()
    if args.file:
        with open(args.file) as f:
            html_content = f.read()
    else:
        html_content = paste()
    soup = BeautifulSoup(html_content, 'html.parser')
    df = parseHtml(soup, args.mode)
    create_xlsx(df, args.output)

    if (args.print):
        print(df)
if __name__ == '__main__':
    main()
