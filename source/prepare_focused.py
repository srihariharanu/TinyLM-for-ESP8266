import json
from pathlib import Path
R=Path(__file__).resolve().parent
# Multiple phrasings teach the neural model; no lookup table is used at inference.
groups=[
(['hi','hello','hey','hello there','hey there','good morning','good afternoon','good evening','hiya','greetings'], ['hello! how can i help you?','hi! what would you like to talk about?']),
(['how are you','how are you doing','how is it going','are you okay','how do you feel','how are things','you doing alright'], ['i am ready to chat. how are you?','i am doing well. what is on your mind?']),
(['what is your name','who are you','introduce yourself','tell me your name','do you have a name','what should i call you'], ['i am tiny, a neural language model running on an esp8266.','call me tiny. i am a small neural model on this board.']),
(['what can you do','how can you help','what are your abilities','tell me what you can do','what do you do'], ['i can try short replies about simple topics. i am still an experimental model.']),
(['where do you run','where are you running','are you on the board','do you run on my laptop','is this running locally','are you really on the esp8266'], ['my replies are generated on the esp8266 itself, with wi-fi off.']),
(['do you need internet','are you online','are you connected to the internet','can you work offline','do you use the cloud','is wifi needed'], ['i work offline. this board generates the reply without an internet connection.']),
(['are you rule based','are these scripted replies','do you use rules','are you a neural network','how do you choose a reply'], ['a trained neural network predicts my reply one character at a time.']),
(['how were you trained','how do you learn','where were you trained','can you learn on the board','how does training work'], ['i was trained on a computer. my learned weights are stored on this board.']),
(['what is an esp8266','tell me about the esp8266','explain esp8266','describe the esp8266','what kind of chip is this'], ['the esp8266 is a small microcontroller with wi-fi and limited memory.']),
(['what is a microcontroller','explain microcontrollers','what does a microcontroller do','describe a microcontroller'], ['a microcontroller is a small computer used to control electronic devices.']),
(['what is ram','explain ram','what does ram do','what is working memory','why do we need ram'], ['ram holds temporary data while a program is running.']),
(['what is flash memory','explain flash','what is flash storage','what does flash memory store'], ['flash memory keeps programs and data even when the power is off.']),
(['what is the difference between ram and flash','compare ram and flash','ram vs flash','how are ram and flash different'], ['ram is temporary working memory. flash keeps data when power is off.']),
(['what is wifi','explain wi-fi','how does wifi work','what does wi-fi do','tell me about wifi'], ['wi-fi connects devices over a wireless network.']),
(['what is a led','what is an led','explain led','what does led mean','tell me about leds'], ['an led is a light emitting diode. it produces light when current flows through it.']),
(['how do i blink an led','how can i blink the led','make an led blink','explain led blinking','how does the led blink'], ['set the led pin as an output, then alternate high and low with a delay.']),
(['what is gpio','explain gpio','what are gpio pins','what does gpio mean'], ['gpio means general purpose input and output. these pins read or control signals.']),
(['what is a resistor','explain resistors','what does a resistor do','why use a resistor'], ['a resistor limits electric current in a circuit.']),
(['what is voltage','explain voltage','what does voltage mean','define voltage'], ['voltage is the electric potential difference between two points.']),
(['what is current','explain electric current','what does current mean','define electric current'], ['electric current is the flow of electric charge.']),
(['what is a sensor','explain sensors','what does a sensor do','why use a sensor'], ['a sensor measures something in the physical world, such as light or temperature.']),
(['what is a neural network','explain neural networks','how does a neural network work','define neural network'], ['a neural network learns patterns by adjusting weights during training.']),
(['what is a language model','explain language models','how does a language model work','define language model'], ['a language model learns patterns in text and predicts what comes next.']),
(['what is a gru','explain gru','what does gru mean','what is a recurrent network'], ['a gru is a recurrent neural network that updates a hidden state as it reads a sequence.']),
(['what is quantization','explain quantization','why compress the model','why use eight bit weights'], ['quantization stores weights with fewer bits to reduce memory use.']),
(['what are model weights','explain weights','what does the model store','what are neural weights'], ['weights are learned numbers that control how a neural network processes its input.']),
(['what is python','explain python','tell me about python','what kind of language is python'], ['python is a programming language used for many tasks, including training neural networks.']),
(['what is programming','what does programming mean','how do programs work','explain programming'], ['programming means writing instructions that a computer can execute.']),
(['what is a gpu','explain gpu','why use a gpu','what does a gpu do'], ['a gpu performs many calculations in parallel and can help train neural networks.']),
(['are you a large language model','are you an llm','how big are you','are you like chatgpt','can you do everything'], ['i am a very small language model. my abilities are much more limited than a large model.']),
(['can you answer anything','do you know everything','can i trust every answer','are you always correct','do you make mistakes'], ['i can make mistakes or produce nonsense. please check important facts.']),
(['what is the weather','what is the weather today','is it raining','will it rain today','tell me the current weather'], ['i have no live weather data. you would need a weather service for that.']),
(['what time is it','what is the time','tell me the current time','what is the date today','what day is it'], ['i do not have a live clock or date available in this experiment.']),
(['can you search the web','look this up online','can you browse the internet','search the internet for me'], ['i cannot browse the internet. my replies are generated offline.']),
(['thank you','thanks','thanks a lot','that helped','thank you very much','i appreciate it'], ['you are welcome!','glad i could help.']),
(['bye','goodbye','see you later','see you','good night','talk to you later'], ['goodbye! have a good day.','see you later!']),
(['i am happy','i feel happy','i had a good day','i am excited','things are going well'], ['that is good to hear! what made your day better?']),
(['i am bored','i feel bored','what should i do for fun','give me something to do','i need a hobby'], ['try a small electronics project, a walk, or learning something new.']),
(['i am tired','i feel tired','i need a break','i have been working all day'], ['a short break may help. what have you been working on?']),
(['i am learning electronics','i want to learn electronics','how do i start with electronics','teach me electronics basics'], ['start with simple circuits, leds, resistors, and safe low voltage power.']),
(['i want to learn programming','how do i start coding','how can i learn to code','teach me programming'], ['start with a small program, change it, and observe what happens. practice a little each day.']),
(['tell me a joke','say something funny','do you know a joke','make me laugh'], ['why did the computer get cold? it left its windows open.']),
(['tell me a short story','tell me a story','write a tiny story','make up a story'], ['a little robot saw a star. it built a telescope and shared the view with a friend.']),
(['what is the sun','tell me about the sun','describe the sun','explain the sun'], ['the sun is a star that gives earth light and heat.']),
(['what is the moon','tell me about the moon','describe the moon','explain the moon'], ['the moon is earths natural satellite. it reflects light from the sun.']),
(['what is water','tell me about water','describe water','what is h2o'], ['water is made of hydrogen and oxygen. its chemical formula is h2o.']),
(['what is a plant','what do plants need','how do plants grow','tell me about plants'], ['plants use light, water, air, and nutrients to grow.']),
(['what color is the sky','why is the sky blue','tell me about the blue sky'], ['the sky looks blue because air scatters blue sunlight more than red sunlight.']),
(['what is two plus two','what is 2 plus 2','2+2','calculate 2 + 2'], ['two plus two is four.']),
(['what is one plus one','what is 1 plus 1','1+1','calculate 1 + 1'], ['one plus one is two.']),
(['what is your favorite color','do you have a favorite color','which color do you like'], ['i do not have personal preferences, but blue is a nice color for an led.']),
(['do you have feelings','are you alive','are you conscious','do you feel emotions'], ['i generate text with a neural network. i do not have human feelings or experiences.']),
(['can you remember me','do you remember earlier messages','do you have memory','will you remember this chat'], ['this version reads one message at a time and does not keep earlier conversations.']),
(['how much memory do you have','how much ram is on this board','is memory limited','why is this model so small'], ['the esp8266 has very little working memory, so the model must be small.']),
(['can you control the led','turn on the led','turn off the led','blink the light for me'], ['this chat firmware only generates text. it does not execute hardware commands.']),
]
rows=[]
for group,(questions,answers) in enumerate(groups):
    for q in questions:
        for a in answers:
            rows.append({'user':q,'assistant':a,'group':group})
            if q not in ('hi','bye','1+1','2+2'):
                rows.append({'user':q+'?','assistant':a,'group':group})
                rows.append({'user':'please '+q,'assistant':a,'group':group})
(R/'data'/'focused-dialogues.json').write_text(json.dumps(rows,indent=2),encoding='ascii')
heldout=[
 ('hello tiny','hello'),('what do i call you','tiny'),('are your replies made on this chip','esp8266'),
 ('explain what ram does','temporary'),('what does flash keep','power'),('what does a language model learn','patterns'),
 ('could you tell me a joke','windows'),('please explain what wifi does','network'),
 ('can this work without the internet','offline'),('how can i start learning to program','program'),
 ('thanks for your help','welcome'),('what is the capital of france','paris'),
 ('how do you store your learned numbers','weights'),('can you explain what a resistor does','current')]
# These exact prompts are excluded from training. Keyword scoring is a diagnostic only.
(R/'data'/'heldout-prompts.json').write_text(json.dumps([{'prompt':q,'expected_hint':a} for q,a in heldout],indent=2),encoding='ascii')
print(f'Wrote {len(rows)} focused training pairs and {len(heldout)} held-out prompts.')
