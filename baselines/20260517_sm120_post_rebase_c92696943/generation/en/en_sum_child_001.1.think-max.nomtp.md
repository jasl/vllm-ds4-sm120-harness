# Generation Transcript

- Case: `en_sum_child_001`
- Language group: `en`
- Workload: `reading_summary`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 69.762859
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 1644, "total_tokens": 8469, "completion_tokens": 6825, "prompt_tokens_details": null}`
- Prompt tokens: 1644
- Completion tokens: 6825
- Total tokens: 8469

## Prompt

```markdown
Read the public-domain passage below and produce a structured English summary.

Output requirements:
1. A 120-word maximum plot summary.
2. A bullet list of Mary’s character traits shown in the passage, each supported by a concrete detail.
3. A short paragraph explaining how the setting creates emotional distance or isolation.
4. Three discussion questions suitable for ages 10–12.
5. Do not add plot information from outside the passage.

素材来源：Frances Hodgson Burnett, The Secret Garden, opening excerpt
来源链接：https://www.gutenberg.org/ebooks/113
版权/授权说明：Project Gutenberg lists this eBook as public domain in the USA.

【待处理素材】
When Mary Lennox was sent to Misselthwaite Manor to live with her uncle everybody said she was the most disagreeable-looking child ever seen. It was true, too. She had a little thin face and a little thin body, thin light hair and a sour expression. Her hair was yellow, and her face was yellow because she had been born in India and had always been ill in one way or another. Her father had held a position under the English Government and had always been busy and ill himself, and her mother had been a great beauty who cared only to go to parties and amuse herself with gay people. She had not wanted a little girl at all, and when Mary was born she handed her over to the care of an Ayah, who was made to understand that if she wished to please the Mem Sahib she must keep the child out of sight as much as possible. So when she was a sickly, fretful, ugly little baby she was kept out of the way, and when she became a sickly, fretful, toddling thing she was kept out of the way also. She never remembered seeing familiarly anything but the dark faces of her Ayah and the other native servants, and as they always obeyed her and gave her her own way in everything, because the Mem Sahib would be angry if she was disturbed by her crying, by the time she was six years old she was as tyrannical and selfish a little pig as ever lived. The young English governess who came to teach her to read and write disliked her so much that she gave up her place in three months, and when other governesses came to try to fill it they always went away in a shorter time than the first one. So if Mary had not chosen to really want to know how to read books she would never have learned her letters at all.

One frightfully hot morning, when she was about nine years old, she awakened feeling very cross, and she became crosser still when she saw that the servant who stood by her bedside was not her Ayah.

“Why did you come?” she said to the strange woman. “I will not let you stay. Send my Ayah to me.”

The woman looked frightened, but she only stammered that the Ayah could not come and when Mary threw herself into a passion and beat and kicked her, she looked only more frightened and repeated that it was not possible for the Ayah to come to Missie Sahib.

There was something mysterious in the air that morning. Nothing was done in its regular order and several of the native servants seemed missing, while those whom Mary saw slunk or hurried about with ashy and scared faces. But no one would tell her anything and her Ayah did not come. She was actually left alone as the morning went on, and at last she wandered out into the garden and began to play by herself under a tree near the veranda. She pretended that she was making a flower-bed, and she stuck big scarlet hibiscus blossoms into little heaps of earth, all the time growing more and more angry and muttering to herself the things she would say and the names she would call Saidie when she returned.

“Pig! Pig! Daughter of Pigs!” she said, because to call a native a pig is the worst insult of all.

She was grinding her teeth and saying this over and over again when she heard her mother come out on the veranda with someone. She was with a fair young man and they stood talking together in low strange voices. Mary knew the fair young man who looked like a boy. She had heard that he was a very young officer who had just come from England. The child stared at him, but she stared most at her mother. She always did this when she had a chance to see her, because the Mem Sahib—Mary used to call her that oftener than anything else—was such a tall, slim, pretty person and wore such lovely clothes. Her hair was like curly silk and she had a delicate little nose which seemed to be disdaining things, and she had large laughing eyes. All her clothes were thin and floating, and Mary said they were “full of lace.” They looked fuller of lace than ever this morning, but her eyes were not laughing at all. They were large and scared and lifted imploringly to the fair boy officer’s face.

“Is it so very bad? Oh, is it?” Mary heard her say.

“Awfully,” the young man answered in a trembling voice. “Awfully, Mrs. Lennox. You ought to have gone to the hills two weeks ago.”

The Mem Sahib wrung her hands.

“Oh, I know I ought!” she cried. “I only stayed to go to that silly dinner party. What a fool I was!”

At that very moment such a loud sound of wailing broke out from the servants’ quarters that she clutched the young man’s arm, and Mary stood shivering from head to foot. The wailing grew wilder and wilder. “What is it? What is it?” Mrs. Lennox gasped.

“Someone has died,” answered the boy officer. “You did not say it had broken out among your servants.”

“I did not know!” the Mem Sahib cried. “Come with me! Come with me!” and she turned and ran into the house.

After that appalling things happened, and the mysteriousness of the morning was explained to Mary. The cholera had broken out in its most fatal form and people were dying like flies. The Ayah had been taken ill in the night, and it was because she had just died that the servants had wailed in the huts. Before the next day three other servants were dead and others had run away in terror. There was panic on every side, and dying people in all the bungalows.

During the confusion and bewilderment of the second day Mary hid herself in the nursery and was forgotten by everyone. Nobody thought of her, nobody wanted her, and strange things happened of which she knew nothing. Mary alternately cried and slept through the hours. She only knew that people were ill and that she heard mysterious and frightening sounds. Once she crept into the dining-room and found it empty, though a partly finished meal was on the table and chairs and plates looked as if they had been hastily pushed back when the diners rose suddenly for some reason. The child ate some fruit and biscuits, and being thirsty she drank a glass of wine which stood nearly filled. It was sweet, and she did not know how strong it was. Very soon it made her intensely drowsy, and she went back to her nursery and shut herself in again, frightened by cries she heard in the huts and by the hurrying sound of feet. The wine made her so sleepy that she could scarcely keep her eyes open and she lay down on her bed and knew nothing more for a long time.
```

## Reasoning Content

```text
Thinking. 1.  **Analyze the Request:**
    *   Input Text: Public domain excerpt from *The Secret Garden* by Frances Hodgson Burnett (first few chapters/opening section, specifically focusing on Mary's backstory and the cholera outbreak).
    *   Task: Produce a structured English summary.
    *   Requirements:
        1.  Plot summary (max 120 words).
        2.  Bullet list of Mary’s character traits with concrete details from the passage.
        3.  Paragraph explaining how the setting creates emotional distance or isolation.
        4.  Three discussion questions (ages 10–12).
        5.  No outside plot info.

2.  **Analyze the Input Text (The Secret Garden excerpt):**
    *   **Protagonist:** Mary Lennox.
    *   **Setting (Initial):** India, bungalow of a British government official.
    *   **Backstory:** Mary is born in India to a busy, ill father and a beautiful, socialite mother who didn't want her. She is raised by native servants (Ayah) who obey her every whim to keep her quiet. This makes her tyrannical, selfish, sickly, and sour.
    *   **Inciting Incident:** Cholera outbreak. The morning after the outbreak starts, Mary wakes up to an unfamiliar servant, throws a tantrum. She wanders outside, overhears her mother panicking to a young officer. The servants wail (Ayah has died). Cholera spreads.
    *   **Mary's Actions:** Hides in the nursery, is forgotten by everyone. Cries and sleeps. Sneaks into the dining room, eats fruit and biscuits, drinks wine, gets drowsy, falls asleep.

    *Let's strictly adhere to the prompt and avoid bringing in later information about Misselthwaite Manor, Colin, etc. Wait, the prompt says "Do not add plot information from outside the passage."*
    "When Mary Lennox was sent to Misselthwaite Manor to live with her uncle..."
    Okay, the passage *does* start with that sentence. So it's not outside information, it's the very first line. I can use the Misselthwaite Manor part, but everything else must stick to *this specific passage*.

    *Requirement Check 1 (Plot Summary):* Max 120 words.
    *Opening sentence included.*
    Orphaned (implied by being sent away? The passage ends with her asleep, the parents' death is not explicitly stated in this specific passage excerpt, wait. Let me check the exact passage boundaries in the prompt).
    "【待处理素材】" starts with "When Mary Lennox was sent to Misselthwaite Manor..."
    "When Mary Lennox was sent to Misselthwaite Manor to live with her uncle everybody said she was the most disagreeable-looking child ever seen."
    ...then it goes into the India backstory.
    ..."So if Mary had not chosen to really want to know how to read books she would never have learned her letters at all."
    ...Cholera outbreak.
    ..."The wine made her so sleepy that she could scarcely keep her eyes open and she lay down on her bed and knew nothing more for a long time."

    Okay, this is the exact text block provided. The summary must cover this exact block.

    *Plot Summary Draft:*
    Orphaned and sent to England, Mary Lennox is a disagreeable, sickly child born in India to a neglectful mother and an ill father.
    Raised by an Ayah who always gave her her way to keep her quiet, she became a tyrannical and selfish child. A cholera outbreak strikes the household. Mary’s mother learns the situation is “awfully” bad. The Ayah dies, and servants wail and flee. Panic ensues. In the confusion, Mary is forgotten and hides alone in the nursery. She scrounges food from an abandoned dining table, drinks a glass of wine, and falls into a deep, oblivious sleep, separated from the death and terror around her.

    Word count check: ~120 words.

    *Requirement Check 2 (Character Traits):*
    Mary’s character traits with concrete details.
    - **Disagreeable/Sour:** Described as having a "sour expression".
    - **Tyrannical and Selfish:** "as tyrannical and selfish a little pig as ever lived"; governesses quit because they disliked her so much.
    - **Ill-tempered/Cross:** Wakes up "feeling very cross"; gets into a "passion" and beats/kicks the new servant.
    - **Racially prejudiced (reflecting the times/upbringing):** Calls a native a "Pig! Daughter of Pigs!" knowing it is the "worst insult of all".
    - **Neglected/Lonely:** Her mother didn't want her and kept her out of sight; during the cholera outbreak she "was forgotten by everyone. Nobody thought of her, nobody wanted her".
    - **Determined (in one specific thing):** "if Mary had not chosen to really want to know how to read books she would never have learned her letters at all."
    - **Resourceful (out of necessity):** When left alone, she ate fruit and biscuits and drank wine to satisfy her hunger and thirst.

    *Requirement Check 3 (Setting/Emotional Distance):*
    "How the setting creates emotional distance or isolation"
    The passage explicitly shows how the setting physically and emotionally isolates Mary. She is born in India but kept entirely separate from her parents by an Ayah who must keep her "out of sight." The bungalow itself becomes a house of panic and death during the cholera outbreak, yet Mary is completely forgotten, hiding alone in the nursery. The distance between her and her mother is stark; Mary observes her mother from afar, referring to her as "the Mem Sahib." The final, powerful image of the setting is Mary drinking wine in an empty dining-room with scattered chairs, symbolizing her complete isolation from the dying world around her. She is a forgotten child in a house of death, emotionally adrift and physically abandoned.

    *Requirement Check 4 (Discussion Questions for ages 10-12):*
    Questions should be text-based, inferential, and engaging for the target age.
    1. Why does Mary feel such anger and frustration at the beginning of the cholera outbreak? What does the way she acts towards the servants tell us about how she was raised?
    2. Do you think Mary’s parents treated her fairly? Why or why not? Use details from the text to support your answer.
    3. The author describes Mary as being "forgotten by everyone" during the chaos of the illness. Why do you think this happens, and how do you think it made Mary feel, given the little we know about her life so far?
    4. The text says she was a “tyrannical and selfish little pig.” Is this Mary’s fault, or is it the way she was raised? What evidence can you find?

3.  **Refine and Format the Output:**
    *Ensure no outside plot info.*

    **1. Plot Summary (Max 120 words):**
    Orphaned and sent to Misselthwaite Manor, Mary Lennox is the disagreeable, sickly child of neglectful parents in India. Raised by a servant who always gave her way to keep her quiet, Mary grew tyrannical and selfish. A fatal cholera outbreak strikes the household. Mary overhears her mother panic with an officer, then the servants wail, signaling her Ayah's death. Panic and death spread. In the confusion of the second day, Mary hides, forgotten by everyone. She scavenges food and wine from an abandoned dining table. Too strong for her, the wine makes her deeply drowsy, and she falls asleep alone in her nursery, completely isolated from the terror and loss around her.

    *Word count check: ~110 words.*

    **2. Bullet List of Character Traits:**
    - **Disagreeable and Sour:** The text describes her having a "sour expression," a "thin light hair," and a general appearance that makes people call her the "most disagreeable-looking child."
    - **Tyrannical and Selfish:** She is described as "as tyrannical and selfish a little pig as ever lived" because her servants always gave in to her.
    - **Ill-Tempered and Violent:** When a strange servant comes to her, she throws herself into a "passion" and "beat and kicked her."
    - **Neglected and Unloved:** Her mother did not want her and handed her over to an Ayah, ordering her to keep Mary "out of sight." During the outbreak, "nobody thought of her, nobody wanted her."
    - **Resourceful in a Childish Way:** When hungry and alone, she finds fruit, biscuits, and wine to sustain herself.

    **3. Short Paragraph on Setting Creating Emotional Distance/Isolation:**
    The Indian setting of the bungalow creates profound isolation for Mary by physically and emotionally separating her from her family. She is raised "out of sight" by servants, while her mother is a distant figure she can only stare at. The chaotic setting of the cholera outbreak deepens this isolation; Mary is “forgotten by everyone” in the confusion. The final image of the setting—Mary alone in the abandoned dining room with hastily pushed-back chairs—powerfully symbolizes her status as a forgotten child, completely detached from the life-and-death drama unfolding around her.

    **4. Three Discussion Questions (ages 10–12):**
    1. The author says Mary was "as tyrannical and selfish a little pig as ever lived." Do you think Mary is entirely to blame for this, or did the way she was raised by her parents and the servants cause this? Use evidence from the text.
    2. When the cholera breaks out, Mary hides and is forgotten by everyone. How do you think it would feel to be completely unnoticed and left alone in a house where so many people are sick and dying?
    3. Mary calls a native servant a "Pig! Daughter of Pigs!" because she knows it is the worst insult. What does this behavior, along with the way she speaks to all the servants, show you about her understanding of the world and her place in it?

    *Wait, I need to review the exact parameters. "Output requirements: ...Three discussion questions suitable for ages 10–12."*

    Let's refine the questions to be more pointed and using simpler wording, while staying strictly to the text.
    Q1: Do you think Mary is a bad child, or is she a product of the way she was raised? Use examples from the text.
    Q2: Mary’s mother tells the young officer she stayed for a “silly dinner party” instead of leaving. How does this detail help you understand Mary’s relationship with her mother?
    Q3: The text says Mary was “kept out of the way” since she was a baby. How does this treatment explain her behavior, like the tantrum she throws when a new servant wakes her up?

    Let's make sure the summary doesn't say "orphaned" if the passage doesn't explicitly state the parents die.
    Passage: "After that appalling things happened... The cholera had broken out... During the confusion and bewilderment of the second day Mary hid herself in the nursery and was forgotten by everyone... The wine made her so sleepy that she could scarcely keep her eyes open and she lay down on her bed and knew nothing more for a long time."

    The passage says "When Mary Lennox was sent to Misselthwaite Manor to live with her uncle". This implies sending her to England. The rest of the passage is backstory. It does not explicitly state that her parents die in this specific *passage*, but the knowledge of her being sent to her uncle is what frames it.
    *Correction*: The very first sentence *is* part of the passage. I can say "Sent to live with her uncle..." but I shouldn't assume anything about the *reasons* for the sending that aren't stated, although the outbreak heavily implies it. The text says "sent to Misselthwaite Manor to live with her uncle". The final sentence has her falling asleep in the bungalow during the outbreak. The transition to England is not in this *specific* selected text. The summary should cover the arc of the *given passage*.
    Actually, the passage starts with the sentence about being sent to her uncle, but then immediately jumps into a flashback: "When Mary Lennox was sent to Misselthwaite Manor to live with her uncle everybody said she was the most disagreeable-looking child ever seen. It was true, too. She had a little thin face... Her father had held a position... and her mother had been a great beauty... So when she was a sickly, fretful, ugly little baby..."

    Okay, the entire passage is the flashback explaining *why* she was disagreeable. The plot arc of the passage is:
    1. Mary is sent to her uncle (implied frame).
    2. Flashback to her backstory in India: neglect, selfishness.
    3. The cholera outbreak: mother panics, Ayah dies, chaos.
    4. Mary hides, is forgotten, eats, drinks wine, falls asleep.
    Don't claim the parents die in the summary if the passage only confirms the Ayah's death. The passage says the mother clutched the officer and ran inside, and wailing started. Then "Three other servants were dead". The text itself cuts off with Mary sleeping.

    Let's check "After that appalling things happened... and dying people in all the bungalows."
    "She only knew that people were ill... The child ate some fruit... and went back to her nursery... and she lay down on her bed and knew nothing more for a long time."

    Yes, her parents' fate is not explicitly stated in this specific excerpt. I will avoid saying "orphaned" strictly. The framing is she *was* sent to her uncle. The excerpt details *why*. The summary can just say she was "sent to Misselthwaite Manor" and then summarize the flashback.

    *Revised Plot Summary:*
    As a child in India, Mary Lennox is described as sickly, sour, and the most disagreeable-looking child. Neglected by her socialite mother and raised by an obedient servant, she grows tyrannical and selfish, causing governesses to quit. A devastating cholera outbreak strikes. Mary’s mother, having ignored the danger, panics. Mary overhears their fears and the wailing announcing her Ayah’s death. In the ensuing chaos, Mary is completely forgotten. She hides in the nursery, eats leftovers from an abandoned dining table, and drinks wine. The alcohol makes her drowsy, and she falls asleep, isolated from the terror and death happening around her.

    *Wait, does the passage say "orphaned"?* "When Mary Lennox was sent to Misselthwaite Manor to live with her uncle..."
    I can just state this fact from the text. "A sickly, sour girl is sent to live with her uncle in England. The passage explains why: born in India to a neglectful mother..."

    **Headings/Structure:**
    - **Plot Summary:**
    - **Mary’s Character Traits:**
    - **Setting and Isolation:**
    - **Discussion Questions:**

    Let's ensure the traits list matches the prompt's request perfectly: "A bullet list of Mary’s character traits shown in the passage, each supported by a concrete detail."

    Trait 1: Disagreeable and sour-faced. *Detail*: She had a "sour expression" and looked "sickly".
    Trait 2: Tyrannical and selfish. *Detail*: She got her own way in everything from her Ayah, making her "as tyrannical and selfish a little pig as ever lived".
    Trait 3: Temperamental and violent. *Detail*: When a strange servant came, Mary "threw herself into a passion and beat and kicked her".
    Trait 4: Neglected and unloved. *Detail*: Her mother wanted her kept "out of sight", and during the cholera outbreak, "nobody thought of her, nobody wanted her".
    Trait 5: Resourceful (or self-reliant in a pinch). *Detail*: When left alone, she got fruit and biscuits to eat and drank wine to quench her thirst.

    Paragraph on setting creating emotional distance:
    "The setting of the British colonial bungalow in India creates profound emotional distance by physically separating Mary from her parents. She is raised out of sight by servants. During the cholera outbreak, the house becomes a place of panic, yet Mary is a forgotten observer, left alone in the nursery while the adults rush around. The final scene of her eating alone in the abandoned dining-room, surrounded by the messy evidence of a hastily abandoned meal, powerfully illustrates her complete isolation from the adults and the life-or-death crisis around her."

    Discussion questions for 10-12 years old:
    1. Mary is described as a "tyrannical and selfish little pig." Why do you think she acts this way? Do you feel sorry for her? Why or why not? (Based on: neglect, being given own way).
    2. Mary’s mother is mentioned several times, but Mary mostly watches her from a distance. What does this tell you about their relationship? (Based on: "the Mem Sahib", being kept out of sight, her mother not wanting her).
    3. During the cholera outbreak, Mary is “forgotten by everyone.” How do you think she feels being completely alone while terrible things are happening around her? What does she do to take care of herself? (Based on: hiding, crying, eating/drinking).

    Let's review word count for the plot summary.
    "A sickly, sour girl is sent to live with her uncle in England. As a child in India, Mary Lennox was neglected by her socialite mother and raised by a servant who always obeyed her, making her tyrannical. A cholera outbreak strikes, and Mary overhears her mother’s panic. After her Ayah dies, chaos erupts. Forgotten in the confusion, Mary hides alone in the nursery. She scavenges food and wine from an abandoned table, becomes drowsy, and falls asleep, completely isolated from the death surrounding her."

    Word count: 79 words. Very safe.

    Let's refine the "Character Traits" section to ensure it distinguishes the trait from the detail.
    - **Sickly and Sour:** The text describes her "little thin face," "thin light hair," and "sour expression," noting she was always ill in one way or another.
    - **Tyrannical and Selfish:** She was "as tyrannical and selfish a little pig as ever lived" because her servants never said no to her.
    - **Ill-Tempered and Violent:** When woken by a strange servant, she "threw herself into a passion and beat and kicked her."
    - **Neglected and Unwanted:** Her mother did not want a daughter and gave orders for her to be kept "out of sight."
    - **Selfishness / Cruelty (Verbal):** She called a native a "Pig! Daughter of Pigs!" using the worst insult she knew against someone weaker than her.
    - **Forgotten and Lonely:** During the cholera outbreak, "nobody thought of her, nobody wanted her."
    - **Self-Reliant (within her limits):** When left alone and hungry, she found "fruit and biscuits" and "drank a glass of wine" to take care of herself.

    Let's check the "Three discussion questions suitable for ages 10–12" request. The questions should be open-ended, encouraging text-based discussion.
    1. The text describes Mary as a "tyrannical and selfish little pig." Do you think this is entirely her fault, or is it a result of how she was raised? Use evidence from the passage.
    2. Mary’s mother is a distant figure who doesn't want a child and keeps her "out of sight." How do you think this treatment affects Mary's behavior and how she sees the world?
    3. At the end of the passage, Mary is completely forgotten and falls asleep alone while a deadly disease spreads around her. How does the author make you feel about Mary in this moment—do you pity her, or are you angry at her bad behavior? Why?

    Looks solid. Let's make sure the formatting is clean.

    **1. Plot Summary:**
    A sickly, sour girl is sent to live with her uncle in England. The passage explains why: born in India to a neglectful mother and a busy father, Mary was raised by a servant who always gave her her way, turning her tyrannical. A cholera outbreak strikes. Mary overhears her mother panic and hears the wailing that announces her Ayah’s death. In the confusion of the next day, Mary is completely forgotten. She scavenges food and wine from an abandoned dining table. The wine makes her drowsy, and she falls asleep in her nursery, isolated from the terror and death happening around her.
    *Word Count: ~110*

    **2. Mary’s Character Traits:**
    - **Disagreeable and Sour-looking:** The text states she had a "sour expression" and a "thin face" and "thin body," making everyone say she looked disagreeable.
    - **Tyrannical and Selfish:** Growing up, she was "as tyrannical and selfish a little pig as ever lived" because everyone always obeyed her.
    - **Ill-Tempered and Violent:** When a new servant woke her, Mary "threw herself into a passion and beat and kicked her."
    - **Neglected and Unloved:** Her mother did not want her and had her kept "out of sight," and during the outbreak "nobody thought of her, nobody wanted her."
    - **Verbally Cruel:** She calls a native servant a "Pig! Daughter of Pigs!" knowing it is the worst insult.
    - **Self-Reliant (when necessary):** When alone, she found and ate "fruit and biscuits" and drank wine to sustain herself.

    **3. How the setting creates emotional distance or isolation:**
    The setting of the British colonial bungalow in India creates a profound emotional distance between Mary and her family. She is physically separated from her parents, raised "out of sight" by an Ayah. Mary herself observes her mother from afar, calling her "the Mem Sahib" rather than Mother. This distance grows into total isolation during the cholera outbreak. While the adults panic and die, Mary is “forgotten by everyone” and left to wander the empty rooms. The final image of her eating alone in the abandoned dining-room, surrounded by the evidence of a hastily abandoned family meal, powerfully represents her status as an isolated, forgotten child.

    **4. Three discussion questions suitable for ages 10–12:**
    1. The author says Mary was “as tyrannical and selfish a little pig as ever lived.” Do you think Mary is mostly to blame for this, or are the adults around her responsible? Use details from the text.
    2. Mary calls a native servant a “Pig! Daughter of Pigs!” because she knows it is a terrible insult. What does this action, along with the way she treats other servants, suggest about how she was raised and what she has learned from her parents?
    3. How do you think Mary felt when she was “forgotten by everyone” and hiding alone while the cholera outbreak terrified the adults? Does your sympathy for her outweigh your dislike of her bad behavior? Why or why not?

    Let's double check that everything is tied strictly to the passage provided.
    - "When Mary Lennox was sent to Misselthwaite Manor to live with her uncle..."
    - "The secret garden" is not the focus of this passage.
    - "Detail: She had a little thin face and a little thin body, thin light hair and a sour expression." -> Disagreeable.
    - "Detail: She was as tyrannical and selfish a little pig as ever lived." -> Tyrannical and selfish.
    - "Detail: Mary threw herself into a passion and beat and kicked her." -> Violent temper.
    - "Detail: She never remembered seeing familiarly anything but the dark faces of her Ayah... The young English governess who came to teach her... disliked her so much..." and "her mother... had not wanted a little girl at all... keep the child out of sight." -> Unloved, neglected.
    - "Detail: So if Mary had not chosen to really want to know how to read books she would never have learned her letters at all." -> Determined (maybe a bit of a stretch, but it's a detail from the text showing a sliver of will).

    "Detail: She called a native a 'Pig! Daughter of Pigs!'" -> Prejudiced/Cruel.

    Summary:
    "A sickly, sour girl is sent to live with her uncle in England. Born in India to a neglectful mother and a busy father, Mary was raised by a servant who always gave her her way, turning her tyrannical and selfish. A cholera outbreak strikes, killing her Ayah and spreading chaos. Mary overhears her mother’s panic. During the confusion, Mary is forgotten by everyone. She hides, scavenging food and wine from an abandoned dining table. The wine makes her drowsy, and she falls asleep in her nursery, completely isolated from the terror and death around her."
    This seems completely accurate to the passage and doesn't add outside plot info (e.g., the specific events at Misselthwaite Manor, Colin, Archibald Craven).

    Wait, the prompt says "Do not add plot information from outside the passage."
    The passage is the specific text block provided. The summary must only reflect events within that block. I must not imply that her parents died in the outbreak if the passage doesn't say it, even though it happens later in the book. The passage says "The cholera had broken out... people were dying like flies. The Ayah had been taken ill in the night, and it was because she had just died." ... "Three other servants were dead." ... "She only knew that people were ill." The text cuts off with her falling asleep in the nursery in India after the outbreak.

    The first sentence of the passage is: "When Mary Lennox was sent to Misselthwaite Manor to live with her uncle everybody said she was the most disagreeable-looking child ever seen."
    The rest of the passage is the backstory explaining why she was sent/disagreeable.
    My summary should reflect that the passage itself frames the plot.
    "The passage introduces Mary Lennox, who is sent to live with her uncle in England, looking deeply disagreeable. It then explains her unhappy early childhood in India. Born to a neglectful mother, she is raised by servants who spoil her, making her selfish. A cholera outbreak causes panic, the death of her nurse, and chaos. Forgotten by everyone, Mary hides alone, eats leftover food, drinks wine, and falls asleep, completely isolated."

    Let's check the Emotional Distance paragraph again.
    "explaining how the setting creates emotional distance or isolation."
    The setting is India + the bungalow.
    Points:
    1. Raised by an Ayah who must keep her out of sight.
    2. Mother is a distant beauty she watches from afar.
    3. During the cholera, the house is chaotic, she is forgotten.
    4. Abandoned dining room scene shows her isolation emotionally even in the midst of a shared family space.
    "The colonial bungalow creates emotional distance by physically separating Mary from her parents. She is raised out of sight by servants. The distance is reinforced when she observes her mother from a far, addressing her formally as 'the Mem Sahib'. This isolation becomes physical during the cholera outbreak. The house fills with panic, but Mary is 'forgotten by everyone'. The image of her eating alone in the abandoned dining-room, surrounded by the mess of a family interrupted, perfectly captures her status as a detached, lonely child."

    *Final check of the questions:*
    1. Do you think Mary is a bad child, or did her upbringing make her this way? Use details from the text.
    (Opens analysis of nature vs nurture, text has "tyrannical and selfish", "always gave her her own way", "kept out of sight").
    2. The text says Mary’s mother “cared only to go to parties” and didn’t want a little girl. How do the parents’ choices affect Mary’s personality and behavior?
    (Focus on neglect, text evidence).
    3. What do you think Mary is feeling when she is “forgotten by everyone” during the crisis? Is it loneliness, fear, relief, or something else? Use her actions (eating, drinking wine, sleeping) to support your answer.
    (Inference, character motivation, text evidence).

    Everything perfectly aligns with the prompt constraints. Ready.
```

## Assistant

```markdown
**Plot Summary**

The passage introduces Mary Lennox, a sickly, sour child sent to live with her uncle. A flashback reveals her early childhood in India: born to a neglectful mother and a busy father, she was raised by servants who always obeyed her, making her tyrannical and selfish. A devastating cholera outbreak strikes the household. Mary overhears her mother’s terrified conversation with an officer and hears the wailing that announces her Ayah’s death. In the chaos, Mary is completely forgotten. She hides alone in the nursery, scavenges food and wine from an abandoned dining table, and falls into a deep, drowsy sleep, isolated from the terror and death around her.

**Mary’s Character Traits**

- **Sickly and sour-looking:** She has a “little thin face,” “thin light hair,” and a “sour expression.”
- **Tyrannical and selfish:** She was “as tyrannical and selfish a little pig as ever lived” because her servants always gave her her own way.
- **Violent and ill-tempered:** When a strange servant wakes her, she “threw herself into a passion and beat and kicked her.”
- **Neglected and unloved:** Her mother kept her “out of sight,” and during the outbreak “nobody thought of her, nobody wanted her.”
- **Verbally cruel:** She calls a native a “Pig! Daughter of Pigs!” knowing it is the worst insult.
- **Self-reliant (when forced):** When left alone, she finds “fruit and biscuits” and drinks wine to sustain herself.

**The Setting’s Role in Creating Emotional Distance**

The colonial bungalow in India creates emotional distance by physically separating Mary from her parents. She is raised “out of sight” by servants, and her mother is a distant figure she watches from afar, calling her “the Mem Sahib” instead of Mother. This distance becomes total isolation during the cholera outbreak. The house fills with panic and death, yet Mary is “forgotten by everyone” and left entirely alone. The stark image of her eating in the abandoned dining-room, surrounded by hastily pushed-back chairs from a disrupted family meal, powerfully symbolizes her complete detachment from the life-and-death crisis around her.

**Discussion Questions for Ages 10–12**

1. Mary is described as a “tyrannical and selfish little pig.” Do you think she is mostly to blame for her behavior, or did the way she was raised cause it? Use evidence from the passage.
2. Why do you think Mary’s mother kept her “out of sight”? How does this treatment help explain why Mary acts the way she does toward the servants?
3. During the cholera outbreak, Mary is “forgotten by everyone.” What do you think she feels in that moment—loneliness, fear, or something else? What clues does her behavior (eating, drinking wine, falling asleep) give you?
```
