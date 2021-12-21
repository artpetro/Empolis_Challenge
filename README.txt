Solution files:
Task 1: nelson_rules_time_series_results.csv
Task 2: log_data_time_series.txt

Code:
Task 1: nelson_rules.py
Task 2: data_flow.py

Description of code:
The code is well documented. 
See comments for description how it works.

Run instructions:
Task 1:
Requirements:
python 3.7
matplotlib
numpy >= 1.20.0
Run: python nelson_rules.py -i INPUT_FILE -o OUTPUT_FILE [-p SOME_VALUE]
Task 2:
Requirements:
python 3.7
Run: python data_flow.py -i INPUT_FILE -o OUTPUT_FILE

My methodology:
- understanding the problem, searching the Internet. E.g. for task 1 I need to know what Nelson's rules are.
- understanding the data.
- Selection of programming language and libraries. I choose Python because there is a numpy library. So, i can handle
arrays, which is needed to solve Task 1.
I think there are already powerful libraries that can be selected for that Task 2, but I am not familiar with 
kafka or other event processing libraries. So, I implement my own solution.
- Internet search for existing solutions.
- Coding, coding, coding...

Challenges:
- Task 1: I'm not familiar with pure functional programming, but I hope my solution is sufficient.
- Task 2: The task itself is relatively simple (compared to Task 1), but I think I should be using an event processing library here.

Limitation:
- Task 1: my solution can be used for post processing of data, not for real time processing. But the implemented methods
can serve as a basis for further solutions.
- Task 2: the solution is not flexible, that is, if the data format changes or the output format or the requirements are changed,
then my solution also has to be adapted. Task 2 was solved by hard coding the requirements.

Possible improvements: 
- unit tests
- Use of suitable libraries or frameworks for Task 2. However, the decision can only be made if the specific environment of
use is known
