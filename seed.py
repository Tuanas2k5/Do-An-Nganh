from werkzeug.security import generate_password_hash
from extensions import db
from modules.users.models import User
from modules.exams.models import ReadingExercise, ReadingQuestion, WritingTopic
from utils.utils import Role

def seed_initial_data():
    print("Bắt đầu quá trình nạp dữ liệu mẫu vào cơ sở dữ liệu...")

    admin = User.query.get(1)
    if not admin:
        admin = User(
            id=1,
            first_name="System",
            last_name="Admin",
            email="admin@learneng.com",
            phone="0901234567",
            password=generate_password_hash("Admin@12345"),
            role=Role.ADMIN,
            active=True
        )
        db.session.add(admin)
        db.session.commit()
        print(" -> Đã tạo tài khoản Admin/Teacher mặc định (ID: 1).")


    if ReadingQuestion.query.filter_by(is_placement_test=True).count() == 0:
        placement_questions = [
            ReadingQuestion(
                question_text="My brother is a doctor. He works in a ______.",
                option_a="school", option_b="hospital", option_c="restaurant", option_d="bank",
                correct_answer="B", level="A1", is_placement_test=True, exercise_id=None
            ),
            ReadingQuestion(
                question_text="They ______ breakfast at 7 o'clock every morning.",
                option_a="have", option_b="has", option_c="having", option_d="had",
                correct_answer="A", level="A1", is_placement_test=True, exercise_id=None
            ),
            # A2
            ReadingQuestion(
                question_text="I ______ to the cinema last night because I was too tired.",
                option_a="don't go", option_b="didn't go", option_c="haven't gone", option_d="wasn't go",
                correct_answer="B", level="A2", is_placement_test=True, exercise_id=None
            ),
            ReadingQuestion(
                question_text="You should ______ an umbrella. It looks like it is going to rain.",
                option_a="take", option_b="taking", option_c="took", option_d="taken",
                correct_answer="A", level="A2", is_placement_test=True, exercise_id=None
            ),
            # B1
            ReadingQuestion(
                question_text="I couldn't attend the meeting ______ I was feeling unwell.",
                option_a="although", option_b="because", option_c="despite", option_d="however",
                correct_answer="B", level="B1", is_placement_test=True, exercise_id=None
            ),
            ReadingQuestion(
                question_text="She has worked for the company ______ she graduated from university.",
                option_a="for", option_b="during", option_c="since", option_d="while",
                correct_answer="C", level="B1", is_placement_test=True, exercise_id=None
            ),
            # B2
            ReadingQuestion(
                question_text="The manager asked us to ______ the problem before making a final decision.",
                option_a="look into", option_b="look after", option_c="look up", option_d="look out",
                correct_answer="A", level="B2", is_placement_test=True, exercise_id=None
            ),
            ReadingQuestion(
                question_text="The project was delayed; ______, the team managed to complete it before the final deadline.",
                option_a="therefore", option_b="nevertheless", option_c="because", option_d="otherwise",
                correct_answer="B", level="B2", is_placement_test=True, exercise_id=None
            ),
            # C1
            ReadingQuestion(
                question_text="Rarely ______ such a comprehensive analysis of the issue before the report was published.",
                option_a="we have seen", option_b="have we seen", option_c="we saw", option_d="did we have seen",
                correct_answer="B", level="C1", is_placement_test=True, exercise_id=None
            ),
            # C2
            ReadingQuestion(
                question_text="The researcher's conclusion was considered ______ because it relied on a remarkably small and unrepresentative sample.",
                option_a="empirical", option_b="tenable", option_c="spurious", option_d="conclusive",
                correct_answer="C", level="C2", is_placement_test=True, exercise_id=None
            ),

            # A1
            ReadingQuestion(
                question_text="NOTICE: Library closed on Sunday. Open Monday to Saturday from 8 a.m. to 6 p.m. When can students visit the library?",
                option_a="Every day", option_b="Only on Sunday", option_c="Monday to Saturday", option_d="Only in the evening",
                correct_answer="C", level="A1", is_placement_test=True, exercise_id=None
            ),
            ReadingQuestion(
                question_text="EMAIL: Hi Anna, I am having a birthday party at my house this Saturday at 6 p.m. I hope you can come! What is the event mentioned in the email?",
                option_a="A school meeting", option_b="A birthday party", option_c="A family trip", option_d="A business meeting",
                correct_answer="B", level="A1", is_placement_test=True, exercise_id=None
            ),
            # A2
            ReadingQuestion(
                question_text="NOTICE: Please leave your bags at the reception desk before entering the museum. Food and drinks are not allowed inside. What should visitors do with their bags?",
                option_a="Take them into the museum", option_b="Leave them at reception", option_c="Give them to a tour guide", option_d="Throw them away",
                correct_answer="B", level="A2", is_placement_test=True, exercise_id=None
            ),
            ReadingQuestion(
                question_text="EMAIL: Dear Tom, The weather forecast says it will rain heavily tomorrow, so I think we should postpone our picnic until next weekend. Why does the writer want to postpone the picnic?",
                option_a="The park is closed.", option_b="Tom is busy.", option_c="The weather may be bad.", option_d="The picnic is too expensive.",
                correct_answer="C", level="A2", is_placement_test=True, exercise_id=None
            ),
            # B1
            ReadingQuestion(
                question_text="ARTICLE: Many university students now choose to study online because it allows them to manage their time more flexibly. However, online learning also requires students to be highly self-disciplined. What is one advantage of online learning mentioned in the text?",
                option_a="It requires no studying.", option_b="It provides more flexible time management.", option_c="It is always cheaper than traditional education.", option_d="It eliminates the need for teachers.",
                correct_answer="B", level="B1", is_placement_test=True, exercise_id=None
            ),
            ReadingQuestion(
                question_text="ARTICLE: Last year, the city introduced a bicycle-sharing program to reduce traffic congestion and air pollution. Although the program initially attracted only a small number of users, participation increased significantly after more bicycle stations were installed. What caused participation to increase?",
                option_a="Bicycles became more expensive.", option_b="The city reduced public transportation.", option_c="More bicycle stations were installed.", option_d="Traffic congestion completely disappeared.",
                correct_answer="C", level="B1", is_placement_test=True, exercise_id=None
            ),
            # B2
            ReadingQuestion(
                question_text="ARTICLE: Remote working has become increasingly common since many organizations discovered that employees could remain productive outside traditional offices. Nevertheless, some managers argue that working remotely can weaken team communication and make it more difficult to maintain a strong organizational culture. What concern do some managers have about remote working?",
                option_a="Employees cannot use computers at home.", option_b="It may negatively affect communication and organizational culture.", option_c="It always reduces employee productivity.", option_d="Workers are unable to complete individual tasks.",
                correct_answer="B", level="B2", is_placement_test=True, exercise_id=None
            ),
            ReadingQuestion(
                question_text="ARTICLE: Governments frequently encourage citizens to adopt renewable energy technologies. While solar panels and wind turbines can reduce dependence on fossil fuels, their widespread adoption may require substantial investment in infrastructure. Furthermore, renewable energy production can be affected by weather conditions, making reliable energy storage increasingly important. What is the main challenge discussed in the passage?",
                option_a="Renewable energy produces too much pollution.", option_b="People do not understand how electricity works.", option_c="Renewable energy requires investment and effective storage solutions.", option_d="Fossil fuels are becoming more environmentally friendly.",
                correct_answer="C", level="B2", is_placement_test=True, exercise_id=None
            ),
            # C1
            ReadingQuestion(
                question_text="ARTICLE: The rapid expansion of artificial intelligence has generated considerable debate about its impact on employment. While automation may eliminate certain routine occupations, it may simultaneously create demand for new forms of expertise. Consequently, the relationship between technological advancement and unemployment is considerably more nuanced than the simple assumption that machines inevitably replace human workers. What does the author suggest about AI and employment?",
                option_a="AI will inevitably cause permanent mass unemployment.", option_b="Technological advancement has a complex relationship with employment.", option_c="AI will have no effect on employment.", option_d="Machines can only replace highly skilled workers.",
                correct_answer="B", level="C1", is_placement_test=True, exercise_id=None
            ),
            # C2
            ReadingQuestion(
                question_text="ARTICLE: Although economic growth is conventionally treated as an unequivocal indicator of societal progress, such an interpretation risks obscuring significant disparities in how prosperity is distributed. Aggregate measures may register impressive increases in national income while simultaneously concealing stagnant living standards among particular demographic groups. A more comprehensive assessment of development, therefore, necessitates consideration not merely of aggregate output but also of distributional equity and broader dimensions of human well-being. What is the central argument of the passage?",
                option_a="Economic growth should never be encouraged.", option_b="National income is irrelevant to societal development.", option_c="Economic growth alone is insufficient for evaluating societal progress.", option_d="Demographic differences have no effect on living standards.",
                correct_answer="C", level="C2", is_placement_test=True, exercise_id=None
            ),
        ]
        db.session.add_all(placement_questions)
        db.session.commit()
        print(" -> Đã nạp thành công 20 câu hỏi Đề thi đầu vào (Placement Test).")


    if ReadingExercise.query.count() == 0:
        reading_exercises = [
            # A1
            ReadingExercise(
                id=1, title='My Daily Routine',
                content='My name is Tom. I am a student. Every day, I wake up at 7:00 AM. I brush my teeth and wash my face. At 7:30 AM, I eat breakfast with my family. I usually have bread and milk. I go to school at 8:00 AM by bus. My classes start at 8:30 AM and finish at 3:00 PM. After school, I play football with my friends in the park. I go home at 5:00 PM. In the evening, I do my homework, eat dinner, and watch TV. I go to bed at 10:00 PM.',
                level='A1', time_limit=10, created_by=1, status='published', is_active=True, version=1
            ),
            ReadingExercise(
                id=2, title='My Pet Dog',
                content='I have a pet dog. His name is Max. He is a small, brown dog with long ears. Max loves to play in the garden. Every morning, I give him food and water. We walk to the park together in the afternoon. Max is very friendly and likes to run after balls. He sleeps in a small bed in my room. I love Max very much.',
                level='A1', time_limit=10, created_by=1, status='published', is_active=True, version=1
            ),
            # A2
            ReadingExercise(
                id=3, title='The Story of Ella’s Garden',
                content='When Ella moved to the countryside with her parents, she was not very excited. At 13, she had spent her entire life in the city, surrounded by traffic, tall buildings, and fast food restaurants. She missed her friends, her school, and the excitement of city life. The small village her parents had chosen seemed boring. Their new home was an old house with a big garden in the back. “You can grow vegetables here,” her father said. Ella didn’t care about vegetables. To her, it just meant more dirt and more bugs. However, one sunny afternoon, she wandered into the garden and noticed small green plants pushing through the soil. Her mom had started planting tomatoes and carrots. Slowly, Ella began to help her mother water the plants. By the end of summer, the garden was full of vegetables, flowers, and butterflies. Ella no longer felt bored. She had found joy in the countryside.',
                level='A2', time_limit=15, created_by=1, status='published', is_active=True, version=1
            ),
            ReadingExercise(
                id=4, title='A Weekend Camping Trip',
                content='Last weekend, my friends and I went camping in the forest. We drove for two hours to reach the campsite. First, we set up our tents near a small river. The weather was a bit cold, but it was not raining. In the evening, we built a fire and cooked hot dogs. We sat around the fire, sang songs, and told stories. We slept very well that night. The next morning, we cleaned up the campsite and went home.',
                level='A2', time_limit=15, created_by=1, status='published', is_active=True, version=1
            ),
            # B1
            ReadingExercise(
                id=5, title='The Benefits of Reading',
                content='Reading is a wonderful habit that can change your life. It not only improves your vocabulary but also reduces stress. People who read regularly tend to have better focus and imagination. Furthermore, reading before bedtime can help you sleep better, unlike looking at mobile screens. When you read a good book, you can travel to different worlds and learn about new cultures without leaving your room. It is highly recommended that teenagers read at least one book every month to develop their critical thinking skills.',
                level='B1', time_limit=15, created_by=1, status='published', is_active=True, version=1
            ),
            ReadingExercise(
                id=6, title='The Benefits of Learning a New Language',
                content='Learning a new language is challenging but highly rewarding. It opens up opportunities to connect with people from different cultures and travel more easily. Furthermore, bilingual people often find it easier to get good jobs in international companies. Studies also show that learning a language is a great workout for the brain, improving memory and concentration. Even studying for just fifteen minutes a day can make a big difference over time.',
                level='B1', time_limit=15, created_by=1, status='published', is_active=True, version=1
            ),
            # B2
            ReadingExercise(
                id=7, title='Transitioning to Renewable Energy',
                content='The escalating climate crisis necessitates an urgent transition from fossil fuels to renewable energy sources such as solar, wind, and hydroelectric power. Reducing our carbon footprint is no longer optional but imperative for the survival of future generations. Although the initial infrastructure costs for renewable energy are substantial, the long-term environmental and economic benefits far outweigh these expenses. Furthermore, individual actions, like reducing energy consumption and minimizing waste, play a crucial role in mitigating the effects of global warming.',
                level='B2', time_limit=20, created_by=1, status='published', is_active=True, version=1
            ),
            ReadingExercise(
                id=8, title='The Evolution of Remote Work',
                content='The concept of remote work has shifted from a rare perk to a fundamental aspect of modern employment. Driven by rapid advancements in digital communication tools, many companies now operate with fully distributed teams. While employees enjoy greater flexibility and the elimination of daily commutes, managers face new challenges. Maintaining team cohesion and monitoring productivity without micromanaging require entirely new leadership strategies. Ultimately, successful remote work depends heavily on trust and clear, asynchronous communication.',
                level='B2', time_limit=20, created_by=1, status='published', is_active=True, version=1
            ),
            # C1
            ReadingExercise(
                id=9, title='The Impact of Urban Architecture',
                content='Urban architecture extends far beyond the mere construction of shelters; it profoundly influences the psychological well-being of its inhabitants. Studies have demonstrated that environments characterized by brutalist, concrete structures can exacerbate feelings of isolation and anxiety. Conversely, the integration of biophilic design—incorporating natural elements such as greenery, natural light, and organic shapes—has been correlated with reduced stress levels and enhanced cognitive function. As urbanization accelerates globally, architects and city planners are increasingly urged to prioritize human-centric designs that nurture mental health rather than solely optimizing for spatial efficiency.',
                level='C1', time_limit=25, created_by=1, status='published', is_active=True, version=1
            ),
            ReadingExercise(
                id=10, title='The Psychological Impact of Social Media Algorithms',
                content='Contemporary social media platforms are underpinned by sophisticated algorithms engineered to maximize user engagement. These systems meticulously track user behavior, creating echo chambers that reinforce pre-existing beliefs and limit exposure to diverse perspectives. Psychologists warn that the continuous variable rewards—manifested as likes and notifications—trigger dopamine releases akin to gambling addiction. Consequently, excessive consumption is increasingly correlated with heightened anxiety and diminished attention spans. Mitigating these effects necessitates not only algorithmic transparency from tech giants but also proactive digital literacy among users.',
                level='C1', time_limit=25, created_by=1, status='published', is_active=True, version=1
            ),
            # C2
            ReadingExercise(
                id=11, title='The Epistemological Implications of Quantum Mechanics',
                content='Quantum mechanics, a cornerstone of modern physics, fundamentally challenges our classical understanding of reality. Unlike Newtonian mechanics, which posits a deterministic universe where the state of a system can be known with absolute precision, quantum theory introduces inherent probabilistic elements. The Heisenberg Uncertainty Principle asserts the impossibility of simultaneously measuring conjugate variables, such as position and momentum, with infinite accuracy. This has profound epistemological implications, suggesting that reality is not an objective, mind-independent entity waiting to be observed, but rather a complex interplay between the observer and the observed system.',
                level='C2', time_limit=30, created_by=1, status='published', is_active=True, version=1
            ),
            ReadingExercise(
                id=12, title='Falsifiability in the Philosophy of Science',
                content='Karl Popper’s criterion of falsifiability revolutionized the demarcation between science and non-science in the 20th century. Rejecting the classical inductivist view, Popper argued that empirical theories can never be conclusively verified; rather, their scientific validity rests upon their inherent vulnerability to being proven false. A theory that accommodates every possible observation, such as certain strands of psychoanalysis, is rendered pseudoscientific under this paradigm. However, the application of falsifiability is fraught with practical complexities, as scientists routinely employ auxiliary hypotheses to rescue core paradigms from anomalous data, a phenomenon famously elaborated by Thomas Kuhn.',
                level='C2', time_limit=30, created_by=1, status='published', is_active=True, version=1
            )
        ]
        db.session.add_all(reading_exercises)
        db.session.commit()
        print(" -> Đã nạp thành công 12 bài tập Reading.")


    if ReadingQuestion.query.filter_by(is_placement_test=False).count() == 0:
        exercise_questions = [
            # Bài 1 (A1)
            ReadingQuestion(exercise_id=1, question_text="What time does Tom wake up?", option_a="7:00 AM", option_b="7:30 AM", option_c="8:00 AM", option_d="10:00 PM", correct_answer="A", level="A1", is_placement_test=False),
            ReadingQuestion(exercise_id=1, question_text="What does Tom usually eat for breakfast?", option_a="Rice and fish", option_b="Bread and milk", option_c="Eggs and meat", option_d="Fruit and juice", correct_answer="B", level="A1", is_placement_test=False),
            ReadingQuestion(exercise_id=1, question_text="How does Tom go to school?", option_a="By car", option_b="By train", option_c="By bus", option_d="On foot", correct_answer="C", level="A1", is_placement_test=False),
            ReadingQuestion(exercise_id=1, question_text="What does Tom do after school?", option_a="He does his homework", option_b="He watches TV", option_c="He goes to bed", option_d="He plays football", correct_answer="D", level="A1", is_placement_test=False),
            ReadingQuestion(exercise_id=1, question_text="When does Tom go to bed?", option_a="3:00 PM", option_b="5:00 PM", option_c="8:30 AM", option_d="10:00 PM", correct_answer="D", level="A1", is_placement_test=False),

            # Bài 2 (A1)
            ReadingQuestion(exercise_id=2, question_text="What kind of animal is Max?", option_a="A cat", option_b="A bird", option_c="A dog", option_d="A rabbit", correct_answer="C", level="A1", is_placement_test=False),
            ReadingQuestion(exercise_id=2, question_text="What color is Max?", option_a="Black", option_b="Brown", option_c="White", option_d="Grey", correct_answer="B", level="A1", is_placement_test=False),
            ReadingQuestion(exercise_id=2, question_text="Where does Max love to play?", option_a="In the house", option_b="In the park", option_c="In the garden", option_d="In the river", correct_answer="C", level="A1", is_placement_test=False),
            ReadingQuestion(exercise_id=2, question_text="When do they walk to the park?", option_a="In the morning", option_b="At night", option_c="In the afternoon", option_d="On weekends", correct_answer="C", level="A1", is_placement_test=False),
            ReadingQuestion(exercise_id=2, question_text="Where does Max sleep?", option_a="In the garden", option_b="In a small bed", option_c="Under the table", option_d="On the sofa", correct_answer="B", level="A1", is_placement_test=False),

            # Bài 3 (A2)
            ReadingQuestion(exercise_id=3, question_text="Why was Ella not excited about moving to the countryside?", option_a="She didn't like her parents", option_b="She hated gardens", option_c="She missed her city life", option_d="She wanted to live on a farm", correct_answer="C", level="A2", is_placement_test=False),
            ReadingQuestion(exercise_id=3, question_text="What did Ella think about growing vegetables at first?", option_a="It was fun", option_b="It meant more dirt and bugs", option_c="It was a good way to save money", option_d="It was too difficult", correct_answer="B", level="A2", is_placement_test=False),
            ReadingQuestion(exercise_id=3, question_text="What did Ella's mom plant?", option_a="Apples and bananas", option_b="Tomatoes and carrots", option_c="Roses and sunflowers", option_d="Potatoes and onions", correct_answer="B", level="A2", is_placement_test=False),
            ReadingQuestion(exercise_id=3, question_text="What did Ella do during the sunny afternoon?", option_a="She went back to the city", option_b="She stayed inside to watch TV", option_c="She wandered into the garden", option_d="She called her old friends", correct_answer="C", level="A2", is_placement_test=False),
            ReadingQuestion(exercise_id=3, question_text="How did Ella feel by the end of summer?", option_a="Bored", option_b="Angry", option_c="Joyful", option_d="Tired", correct_answer="C", level="A2", is_placement_test=False),

            # Bài 4 (A2)
            ReadingQuestion(exercise_id=4, question_text="Where did they go camping?", option_a="Near a beach", option_b="In the forest", option_c="On a mountain", option_d="In a park", correct_answer="B", level="A2", is_placement_test=False),
            ReadingQuestion(exercise_id=4, question_text="How long did they drive?", option_a="One hour", option_b="Two hours", option_c="Three hours", option_d="Four hours", correct_answer="B", level="A2", is_placement_test=False),
            ReadingQuestion(exercise_id=4, question_text="What did they set up first?", option_a="A fire", option_b="Their tents", option_c="A table", option_d="Their food", correct_answer="B", level="A2", is_placement_test=False),
            ReadingQuestion(exercise_id=4, question_text="What was the weather like?", option_a="Hot and sunny", option_b="Raining", option_c="A bit cold", option_d="Snowing", correct_answer="C", level="A2", is_placement_test=False),
            ReadingQuestion(exercise_id=4, question_text="What did they do the next morning?", option_a="Cooked hot dogs", option_b="Sang songs", option_c="Cleaned up and went home", option_d="Swam in the river", correct_answer="C", level="A2", is_placement_test=False),

            # Bài 5 (B1)
            ReadingQuestion(exercise_id=5, question_text="What is one benefit of reading mentioned in the text?", option_a="It makes you sleepy all day", option_b="It improves vocabulary", option_c="It increases stress", option_d="It damages your eyes", correct_answer="B", level="B1", is_placement_test=False),
            ReadingQuestion(exercise_id=5, question_text="How does reading affect focus?", option_a="It makes focus worse", option_b="It has no effect", option_c="It improves focus", option_d="It causes distraction", correct_answer="C", level="B1", is_placement_test=False),
            ReadingQuestion(exercise_id=5, question_text="What is compared to reading before bedtime?", option_a="Eating a snack", option_b="Talking to friends", option_c="Looking at mobile screens", option_d="Listening to music", correct_answer="C", level="B1", is_placement_test=False),
            ReadingQuestion(exercise_id=5, question_text="What can you do when you read a good book?", option_a="Travel to different worlds", option_b="Learn how to cook", option_c="Build a house", option_d="Run faster", correct_answer="A", level="B1", is_placement_test=False),
            ReadingQuestion(exercise_id=5, question_text="What is highly recommended for teenagers?", option_a="To sleep more", option_b="To read at least one book a month", option_c="To play mobile games", option_d="To watch more TV", correct_answer="B", level="B1", is_placement_test=False),

            # Bài 6 (B1)
            ReadingQuestion(exercise_id=6, question_text="What is one benefit of learning a new language?", option_a="It makes traveling harder.", option_b="It helps connect with people.", option_c="It makes you sleep more.", option_d="It reduces physical strength.", correct_answer="B", level="B1", is_placement_test=False),
            ReadingQuestion(exercise_id=6, question_text="Who might find it easier to get a good job?", option_a="People who do not travel", option_b="Bilingual people", option_c="People with bad memory", option_d="People who sleep well", correct_answer="B", level="B1", is_placement_test=False),
            ReadingQuestion(exercise_id=6, question_text="How does language learning affect the brain?", option_a="It damages memory.", option_b="It has no effect.", option_c="It improves memory and concentration.", option_d="It makes the brain tired.", correct_answer="C", level="B1", is_placement_test=False),
            ReadingQuestion(exercise_id=6, question_text="How much daily study can make a big difference?", option_a="Five minutes", option_b="Fifteen minutes", option_c="One hour", option_d="Three hours", correct_answer="B", level="B1", is_placement_test=False),
            ReadingQuestion(exercise_id=6, question_text="How is learning a new language described in the text?", option_a="Challenging but rewarding", option_b="Easy and boring", option_c="Expensive and useless", option_d="Fast and simple", correct_answer="A", level="B1", is_placement_test=False),

            # Bài 7 (B2)
            ReadingQuestion(exercise_id=7, question_text="What transition does the climate crisis necessitate?", option_a="From renewable to fossil fuels", option_b="From fossil fuels to renewable energy", option_c="From wind to solar power", option_d="From hydroelectric to coal", correct_answer="B", level="B2", is_placement_test=False),
            ReadingQuestion(exercise_id=7, question_text="Why is reducing the carbon footprint described as imperative?", option_a="For economic growth", option_b="For the survival of future generations", option_c="To increase fossil fuel usage", option_d="To lower immediate costs", correct_answer="B", level="B2", is_placement_test=False),
            ReadingQuestion(exercise_id=7, question_text="What is a drawback of renewable energy mentioned in the text?", option_a="It causes global warming", option_b="It is not sustainable", option_c="Substantial initial infrastructure costs", option_d="It increases carbon footprints", correct_answer="C", level="B2", is_placement_test=False),
            ReadingQuestion(exercise_id=7, question_text="Which of the following is NOT mentioned as a renewable energy source?", option_a="Solar", option_b="Wind", option_c="Hydroelectric", option_d="Natural gas", correct_answer="D", level="B2", is_placement_test=False),
            ReadingQuestion(exercise_id=7, question_text="What individual actions can help mitigate global warming?", option_a="Increasing waste", option_b="Consuming more energy", option_c="Reducing energy consumption", option_d="Ignoring the carbon footprint", correct_answer="C", level="B2", is_placement_test=False),

            # Bài 8 (B2)
            ReadingQuestion(exercise_id=8, question_text="What has driven the shift towards remote work?", option_a="A lack of office space", option_b="Advancements in digital communication tools", option_c="Employees demanding higher salaries", option_d="The high cost of transportation", correct_answer="B", level="B2", is_placement_test=False),
            ReadingQuestion(exercise_id=8, question_text="What is one benefit of remote work for employees?", option_a="Working longer hours", option_b="Free lunches", option_c="Elimination of daily commutes", option_d="More meetings", correct_answer="C", level="B2", is_placement_test=False),
            ReadingQuestion(exercise_id=8, question_text="What do managers face in a remote setting?", option_a="Easier team monitoring", option_b="New challenges in maintaining cohesion", option_c="Less communication", option_d="Lower employee salaries", correct_answer="B", level="B2", is_placement_test=False),
            ReadingQuestion(exercise_id=8, question_text="What is critical for successful remote work?", option_a="Micromanaging every task", option_b="Working synchronously at all times", option_c="Trust and clear asynchronous communication", option_d="Having a traditional office layout", correct_answer="C", level="B2", is_placement_test=False),
            ReadingQuestion(exercise_id=8, question_text="How has the concept of remote work changed?", option_a="From a fundamental aspect to a rare perk", option_b="From a rare perk to a fundamental aspect", option_c="It has become illegal in many places", option_d="It is now only for managers", correct_answer="B", level="B2", is_placement_test=False),

            # Bài 9 (C1)
            ReadingQuestion(exercise_id=9, question_text="What is the main premise of the text?", option_a="Architecture is solely about building functional shelters.", option_b="Urban design significantly affects mental well-being.", option_c="Brutalist architecture is suitable for modern cities.", option_d="Economic viability should be the primary concern.", correct_answer="B", level="C1", is_placement_test=False),
            ReadingQuestion(exercise_id=9, question_text="According to the text, what effect does biophilic design have?", option_a="It increases feelings of isolation.", option_b="It fragments neighborhoods.", option_c="It reduces stress levels and improves cognitive function.", option_d="It primarily optimizes spatial efficiency.", correct_answer="C", level="C1", is_placement_test=False),
            ReadingQuestion(exercise_id=9, question_text="What do brutalist, concrete structures exacerbate?", option_a="Feelings of community cohesion", option_b="Feelings of isolation and anxiety", option_c="Physical health", option_d="Economic growth", correct_answer="B", level="C1", is_placement_test=False),
            ReadingQuestion(exercise_id=9, question_text="What are architects and city planners urged to prioritize?", option_a="Human-centric designs that nurture mental health", option_b="Building more concrete structures", option_c="Optimizing solely for spatial efficiency", option_d="Reducing the use of natural light", correct_answer="A", level="C1", is_placement_test=False),
            ReadingQuestion(exercise_id=9, question_text="The word \"exacerbate\" in the passage is closest in meaning to:", option_a="Alleviate", option_b="Worsen", option_c="Conceal", option_d="Generate", correct_answer="B", level="C1", is_placement_test=False),

            # Bài 10 (C1)
            ReadingQuestion(exercise_id=10, question_text="What is the primary goal of social media algorithms according to the text?", option_a="To spread diverse perspectives", option_b="To maximize user engagement", option_c="To protect user privacy", option_d="To reduce anxiety", correct_answer="B", level="C1", is_placement_test=False),
            ReadingQuestion(exercise_id=10, question_text="What do echo chambers do?", option_a="Expose users to new ideas", option_b="Help users stop gambling", option_c="Reinforce pre-existing beliefs", option_d="Make users read more books", correct_answer="C", level="C1", is_placement_test=False),
            ReadingQuestion(exercise_id=10, question_text="What psychological mechanism is triggered by notifications?", option_a="Endorphin release similar to exercise", option_b="Dopamine release akin to gambling addiction", option_c="Serotonin reduction", option_d="Adrenaline spikes similar to danger", correct_answer="B", level="C1", is_placement_test=False),
            ReadingQuestion(exercise_id=10, question_text="What is a consequence of excessive social media consumption?", option_a="Enhanced attention spans", option_b="Reduced anxiety", option_c="Heightened anxiety and diminished attention spans", option_d="Better digital literacy", correct_answer="C", level="C1", is_placement_test=False),
            ReadingQuestion(exercise_id=10, question_text="What does the author suggest to mitigate these effects?", option_a="Deleting all social media accounts", option_b="Algorithmic transparency and digital literacy", option_c="Using platforms only on weekends", option_d="Creating faster algorithms", correct_answer="B", level="C1", is_placement_test=False),

            # Bài 11 (C2)
            ReadingQuestion(exercise_id=11, question_text="What fundamental contrast is drawn between Newtonian and quantum mechanics?", option_a="Newtonian mechanics is probabilistic, whereas quantum mechanics is deterministic.", option_b="Newtonian mechanics posits determinism, while quantum theory introduces probabilities.", option_c="Both rely on the absolute precision of conjugate variables.", option_d="Quantum mechanics can measure momentum with infinite accuracy.", correct_answer="B", level="C2", is_placement_test=False),
            ReadingQuestion(exercise_id=11, question_text="According to the Heisenberg Uncertainty Principle, what is impossible?", option_a="To observe reality independently of the human mind.", option_b="To accurately predict the collapse of a wavefunction.", option_c="To measure conjugate variables simultaneously with infinite precision.", option_d="To reconcile Newtonian physics with modern physics.", correct_answer="C", level="C2", is_placement_test=False),
            ReadingQuestion(exercise_id=11, question_text="What is the main epistemological implication discussed in the text?", option_a="Knowledge is strictly confined to macroscopic phenomena.", option_b="Reality exists objectively and is independent of the observer.", option_c="Reality is a complex interaction between the observer and the observed system.", option_d="Human knowledge is incapable of understanding physics.", correct_answer="C", level="C2", is_placement_test=False),
            ReadingQuestion(exercise_id=11, question_text="How does the text describe reality according to quantum mechanics?", option_a="As an objective, mind-independent entity.", option_b="As a completely deterministic system.", option_c="As a complex interplay between the observer and the observed.", option_d="As a predictable sequence of events.", correct_answer="C", level="C2", is_placement_test=False),
            ReadingQuestion(exercise_id=11, question_text="The word \"conjugate\" in the passage most likely refers to:", option_a="Opposing forces in a physical system.", option_b="Variables that are completely unrelated.", option_c="Variables that are mathematically linked in quantum theory.", option_d="The union of classical and modern physics.", correct_answer="C", level="C2", is_placement_test=False),

            # Bài 12 (C2)
            ReadingQuestion(exercise_id=12, question_text="What does Popper’s criterion of falsifiability demarcate?", option_a="Physics from chemistry", option_b="Science from non-science", option_c="Truth from falsehood", option_d="Induction from deduction", correct_answer="B", level="C2", is_placement_test=False),
            ReadingQuestion(exercise_id=12, question_text="What did Popper argue about empirical theories?", option_a="They can be conclusively verified.", option_b="They must accommodate every observation.", option_c="Their validity rests on their vulnerability to being proven false.", option_d="They are inherently pseudoscientific.", correct_answer="C", level="C2", is_placement_test=False),
            ReadingQuestion(exercise_id=12, question_text="According to this paradigm, why might a theory be considered pseudoscientific?", option_a="It relies on mathematics.", option_b="It accommodates every possible observation.", option_c="It is too old.", option_d="It challenges classical induction.", correct_answer="B", level="C2", is_placement_test=False),
            ReadingQuestion(exercise_id=12, question_text="Why is the application of falsifiability practically complex?", option_a="Scientists refuse to read Popper’s work.", option_b="Theories are too simple to falsify.", option_c="Scientists often use auxiliary hypotheses to rescue core paradigms.", option_d="Data collection is impossible.", correct_answer="C", level="C2", is_placement_test=False),
            ReadingQuestion(exercise_id=12, question_text="Who famously elaborated on the phenomenon of rescuing paradigms with auxiliary hypotheses?", option_a="Karl Popper", option_b="Thomas Kuhn", option_c="Isaac Newton", option_d="Albert Einstein", correct_answer="B", level="C2", is_placement_test=False)
        ]
        db.session.add_all(exercise_questions)
        db.session.commit()
        print(" -> Đã nạp thành công 60 câu hỏi bài tập Reading.")


    if WritingTopic.query.count() == 0:
        writing_topics = [
            WritingTopic(
                id=1,
                title='Introduce Yourself',
                description='Write a short paragraph to introduce yourself. You should include: your name, your age, where you live, and your favorite hobbies. Use simple sentences.',
                level='A1', min_words=50, max_words=100, created_by=1, status='published', is_active=True, version=1
            ),
            WritingTopic(
                id=2,
                title='A Memorable Holiday',
                description='Write an email to your English-speaking friend about your last holiday. Tell them where you went, who you went with, what activities you did, and how you felt about the trip.',
                level='A2', min_words=80, max_words=150, created_by=1, status='published', is_active=True, version=1
            ),
            WritingTopic(
                id=3,
                title='The Importance of Learning Languages',
                description='Your English teacher has asked you to write an essay on the following topic: "Why is learning a foreign language important?" Give reasons for your answer and include relevant examples from your own experience.',
                level='B1', min_words=150, max_words=250, created_by=1, status='published', is_active=True, version=1
            ),
            WritingTopic(
                id=4,
                title='Online Shopping vs Traditional Shopping',
                description='Some people prefer online shopping, while others prefer going to physical stores. Discuss the advantages and disadvantages of both methods. Give your own opinion and support it with specific examples.',
                level='B2', min_words=200, max_words=300, created_by=1, status='published', is_active=True, version=1
            ),
            WritingTopic(
                id=5,
                title='The Impact of Artificial Intelligence on Jobs',
                description='Artificial Intelligence (AI) is rapidly changing the modern workplace. To what extent do you agree or disagree that AI will ultimately create more opportunities than it destroys? Support your arguments with specific examples and well-structured reasoning.',
                level='C1', min_words=250, max_words=350, created_by=1, status='published', is_active=True, version=1
            ),
            WritingTopic(
                id=6,
                title='Environmental Policies and Economic Growth',
                description='It is frequently argued that stringent environmental regulations inevitably hinder national economic growth. Evaluate this claim by exploring the tension between sustainable ecological development and economic expansion. Provide a well-reasoned conclusion supported by global examples.',
                level='C2', min_words=300, max_words=450, created_by=1, status='published', is_active=True, version=1
            )
        ]
        db.session.add_all(writing_topics)
        db.session.commit()
        print(" -> Đã nạp thành công 6 đề bài Writing.")

    print("Hoàn tất toàn bộ quá trình nạp dữ liệu khởi tạo!")