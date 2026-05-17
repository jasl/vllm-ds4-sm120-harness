# Generation Transcript

- Case: `zh2en_rom_001`
- Language group: `zh`
- Workload: `translation`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 101.309916
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 1086, "total_tokens": 18252, "completion_tokens": 17166, "prompt_tokens_details": null}`
- Prompt tokens: 1086
- Completion tokens: 17166
- Total tokens: 18252

## Prompt

```markdown
请将下面的繁体中文小说片段翻译成英文。要求：保留人物心理、礼仪分寸和环境细节；英文要自然、有文学感，但不要过度现代化；人名可采用拼音，例如 Lin Daiyu、Jia residence。不要添加解释性段落。

素材来源：《紅樓夢》节选：林黛玉进贾府
来源链接：https://www.gutenberg.org/ebooks/24264
版权/授权说明：Project Gutenberg lists this eBook as public domain in the USA.

【待处理素材】
且說黛玉自那日棄舟登岸時，便有榮國府打發了轎子并拉行李的車輛久候了．這林黛玉常听得母親說過，他外祖母家与別家不同．他近日所見的這几個三等仆婦，吃穿用度，已是不凡了，何況今至其家．因此步步留心，時時在意，不肯輕易多說一句話，多行一步路，惟恐被人恥笑了他去．自上了轎，進入城中從紗窗向外瞧了一瞧，其街市之繁華，人煙之阜盛，自与別處不同．又行了半日，忽見街北蹲著兩個大石獅子，三間獸頭大門，門前列坐著十來個華冠麗服之人．正門卻不開，只有東西兩角門有人出入．正門之上有一匾，匾上大書"敕造宁國府"五個大字．黛玉想道：這必是外祖之長房了．想著，又往西行，不多遠，照樣也是三間大門，方是榮國府了．卻不進正門，只進了西邊角門．那轎夫抬進去，走了一射之地，將轉彎時，便歇下退出去了．后面的婆子們已都下了轎，赶上前來．另換了三四個衣帽周全十七八歲的小廝上來，复抬起轎子．眾婆子步下圍隨至一垂花門前落下．眾小廝退出，眾婆子上來打起轎帘，扶黛玉下轎．林黛玉扶著婆子的手，進了垂花門，兩邊是抄手游廊，當中是穿堂，當地放著一個紫檀架子大理石的大插屏．轉過插屏，小小的三間廳，廳后就是后面的正房大院．正面五間上房，皆雕梁畫棟，兩邊穿山游廊廂房，挂著各色鸚鵡，畫眉等鳥雀．台磯之上，坐著几個穿紅著綠的丫頭，一見他們來了，便忙都笑迎上來，說：“剛才老太太還念呢，可巧就來了。”于是三四人爭著打起帘籠，一面听得人回話：“林姑娘到了。”黛玉方進入房時，只見兩個人攙著一位鬢發如銀的老母迎上來，黛玉便知是他外祖母．方欲拜見時，早被他外祖母一把摟入怀中，心肝儿肉叫著大哭起來．當下地下侍立之人，無不掩面涕泣，黛玉也哭個不住．一時眾人慢慢解勸住了，黛玉方拜見了外祖母．____此即冷子興所云之史氏太君，賈赦賈政之母也．當下賈母一一指与黛玉：“這是你大舅母，這是你二舅母，這是你先珠大哥的媳婦珠大嫂子。”黛玉一一拜見過．賈母又說：“請姑娘們來．今日遠客才來，可以不必上學去了。”眾人答應了一聲，便去了兩個．不一時，只見三個奶嬤嬤并五六個丫鬟，簇擁著三個姊妹來了．第一個肌膚微丰，合中身材，腮凝新荔，鼻膩鵝脂，溫柔沉默，觀之可親．第二個削肩細腰，長挑身材，鴨蛋臉面，俊眼修眉，顧盼神飛，文彩精華，見之忘俗．第三個身量未足，形容尚小．其釵環裙襖，三人皆是一樣的妝飾．黛玉忙起身迎上來見禮，互相廝認過，大家歸了坐．丫鬟們斟上茶來．不過說些黛玉之母如何得病，如何請醫服藥，如何送死發喪．不免賈母又傷感起來，因說：“我這些儿女，所疼者獨有你母，今日一旦先舍我而去，連面也不能一見，今見了你，我怎不傷心！
```

## Reasoning Content

```text
我们被要求将一段繁体中文小说片段翻译成英文。来源是《红楼梦》节选：林黛玉进贾府。要求保留人物心理、礼仪分寸和环境细节；英文要自然、有文学感，但不要过度现代化；人名可采用拼音，例如 Lin Daiyu、Jia residence。不要添加解释性段落。

我们需要输出英文翻译。注意素材来源是Project Gutenberg，但我们是翻译片段。

首先，理解原文内容：从黛玉弃舟登岸开始，到贾母伤感说那番话结束。包含环境描写、心理活动、人物动作、对话等。

我们要用英文传达出原文的韵味。注意一些细节：三等仆妇、敕造宁国府、荣国府、角门、垂花门、抄手游廊、穿堂、紫檀架子大理石的大插屏、雕梁画栋、穿山游廊、丫鬟们打帘、贾母搂着哭、介绍大舅母二舅母珠大嫂子、请姑娘们、三位姐妹的描写、贾母说话等。

在翻译中，人名用拼音：Lin Daiyu, Jia Mu (or Grandmother Jia? 但要求可以用拼音，例如 Lin Daiyu、Jia residence。那么“贾母”翻译为Jia Mu? 或者Grandmother Jia? 但拼音也可以用，所以可能是Jia Mu。但为了清晰，有时用"the old lady"或"Grandmother Jia"。不过我们可以保持拼音，但要注意英文读者可能不熟悉，但要求保留拼音，所以直接用拼音。例如“老太太”可以译为"the old lady"或"Grandmother Jia"，但原文有“外祖母”，所以可译为"her grandmother"或"Grandmother Jia"。考虑到不要过度现代化，用自然文学英语。

注意：有些专有名词如“荣国府”可以译为"Rongguo Mansion"或"the Rong residence"。“宁国府”同理。“敕造”意为“奉旨建造”，可以用"imperially built"或"built by imperial decree"。

环境细节：轿夫抬进去一射之地（一箭之地），约150米，可以用"about an arrow's flight"。

心理：黛玉步步留心时时在意，不肯多说一句话多行一步路，惟恐被人耻笑。要翻译出这种拘谨。

人物外貌描写：三个姊妹，第一个温柔沉默，观之可亲；第二个俊眼修眉，顾盼神飞，见之忘俗；第三个尚小。要保留比喻：腮凝新荔，鼻腻鹅脂，鸭蛋脸面等。

最后贾母的话：我这些儿女，所疼者独有你母，今日一旦先舍我而去，连面也不能一见，今见了你，我怎不伤心！要保留伤感语气。

整体风格：用文学英语，但不太古雅（如莎士比亚式），而是现代文学英语，自然流畅。避免过于口语化或俚语。

注意段落结构：原文是连贯的，我们也要保持连贯。

输出时参考：https://www.gutenberg.org/ebooks/24264 可能有现有英译本，但我们要自己翻译，不抄袭。但可以借鉴一些常见译法，但要原创。

根据要求，我们输出英文翻译即可，不添加解释段落。

我们开始逐句思考，写出流畅的英文。

注意：素材以“且說黛玉自那日棄舟登岸時”开头，所以英文可以以"Now as for Daiyu," 或 "As for Daiyu," 开始，但更自然的是"On the day when Daiyu left her boat and came ashore,"

但为了叙事流畅，可以用"Now, on the day when Daiyu..." 或 "It was on the day that Daiyu disembarked from the boat that..."

为了简洁，我使用"When Daiyu came ashore from the boat that day,"

不过原文有“且說”，这是说书人语气，可以处理为"Now"。

考虑到英文习惯，可以开始："Now it happened that on the day when Daiyu left her boat and came ashore,"

但为了简洁，直接："On the day she left the boat and came ashore," 或者"On the day when Daiyu left the boat and came ashore, the retinue from the Rong mansion had already been waiting with a sedan chair and carts for luggage."

但原文有“打發了轎子并拉行李的車輛久候”，所以可以翻译为"had sent a sedan chair and luggage carts that had been waiting for a long time."

注意：前面有“且說”，表示要开始叙述，可以译为"Now"。

接下来：這林黛玉常听得母親說過，他外祖母家与別家不同．他近日所見的這几個三等仆婦，吃穿用度，已是不凡了，何況今至其家．因此步步留心，時時在意，不肯輕易多說一句話，多行一步路，惟恐被人恥笑了他去．

翻译：Lin Daiyu had often heard her mother say that her grandmother's house was different from other families. The serving women of the third rank she had seen recently were already exceptional in their dress and belongings; how much more so would it be when she arrived at their home? So she was careful at every step, attentive at all times, and unwilling to speak a single unnecessary word or take a single unnecessary step, for fear of being laughed at.

注意：“三等仆妇”不是第三等，而是指较低等级的仆妇。我们可以用"women servants of the third grade"或"lower-ranking maids"。但“三等”在等级中可能是第三等，但贾府等级森严，三等仆妇可能指不高的等级，但原文说她们吃穿用度已是不凡，说明三等仆妇已经养尊处优。所以译为"serving women of the third rank"。

“吃穿用度”包括食物、衣服、日常用品，译为"their food, clothing, and daily necessities"或"their clothes and daily upkeep"。

“步步留心，時時在意”是成语，可以译为"watch every step and be constantly on guard"。

“不肯輕易多說一句話，多行一步路，惟恐被人恥笑了他去”可译为"She would not casually speak an extra word or take an extra step, terrified of being ridiculed by others."

但为了自然，可以整合。

自上了轎，進入城中從紗窗向外瞧了一瞧，其街市之繁華，人煙之阜盛，自与別處不同．又行了半日，忽見街北蹲著兩個大石獅子，三間獸頭大門，門前列坐著十來個華冠麗服之人．正門卻不開，只有東西兩角門有人出入．正門之上有一匾，匾上大書"敕造宁國府"五個大字．黛玉想道：這必是外祖之長房了．想著，又往西行，不多遠，照樣也是三間大門，方是榮國府了．

翻譯：Once she got into the sedan chair and entered the city, she glanced out through the gauze windows and saw that the streets were more bustling and crowded with people than any other place she had seen. After riding for a while, she suddenly noticed two large stone lions crouching at the north end of the street, and a three-bay gate with beast-head ornaments. Ten or more people in splendid clothes were sitting in front of the gate. The main gate was closed, but people were entering and exiting through the east and west side gates. Above the main gate was a plaque with five large characters: "Ningguo Mansion, Built by Imperial Decree." Daiyu thought: This must be the elder branch of Grandmother's family. Then they proceeded west, and shortly they saw another three-bay gate—this was the Rongguo Mansion.

注意：西方分东西角门，所以是东西角门。原文“東西兩角門”就是east and west side gates。

“敕造宁国府”五个字，我加了引号。也可以直接写："Ningguo Mansion Built by Imperial Decree"。

但为了简洁，可以译为"the Ningguo Mansion, built by imperial decree”。

黛玉想道：這必是外祖之長房了．可译为"This must be the eldest branch of Grandmother's family."

外祖指的是贾母，所以"Grandmother"。

又往西行，不多遠，照樣也是三間大門，方是榮國府了．可译为"They then continued west, and after a short distance, they saw another set of three gates—the main gate of the Rongguo Mansion."

但注意，原文说“照樣也是三間大門，方是榮國府了”，所以是同样的三间大门，才是荣国府。但前面宁国府是正门，荣国府也是正门，但黛玉他们没进正门，而是进了西边角门。英文要清楚。

卻不進正門，只進了西邊角門．那轎夫抬進去，走了一射之地，將轉彎時，便歇下退出去了．后面的婆子們已都下了轎，赶上前來．另換了三四個衣帽周全十七八歲的小廝上來，复抬起轎子．眾婆子步下圍隨至一垂花門前落下．眾小廝退出，眾婆子上來打起轎帘，扶黛玉下轎．

翻譯：But they did not enter through the main gate; instead, they went in through the west side gate. The sedan-bearers carried her in, and after going about an arrow's flight (one she) they stopped just before turning a corner and withdrew. The old women who were following had already gotten out of their sedan chairs and hurried forward. Then three or four young serving-lads of seventeen or eighteen, neatly dressed and groomed, took up the sedan chair and carried it forward. The old women followed on foot until the chair was set down before a gate with hanging flowers. The lads withdrew, while the old women came forward, raised the sedan curtain, and supported Daiyu as she alighted.

注意：“一射之地”可以保留为"about an arrow's flight"，或意译为"about a hundred paces"。“垂花门”是gate with hanging flowers（垂花装饰）。

林黛玉扶著婆子的手，進了垂花門，兩邊是抄手游廊，當中是穿堂，當地放著一個紫檀架子大理石的大插屏．轉過插屏，小小的三間廳，廳后就是后面的正房大院．正面五間上房，皆雕梁畫棟，兩邊穿山游廊廂房，挂著各色鸚鵡，畫眉等鳥雀．台磯之上，坐著几個穿紅著綠的丫頭，一見他們來了，便忙都笑迎上來，說：“剛才老太太還念呢，可巧就來了。”于是三四人爭著打起帘籠，一面听得人回話：“林姑娘到了。”

翻譯：Leaning on the old woman's hand, Daiyu entered the gate with hanging flowers. On both sides were covered winding walkways, and in the center was an open passage. Before it stood a large marble screen in a rosewood frame. She went around the screen and saw a small three-bay hall. Behind the hall was the main courtyard. At the front were five main rooms, all with carved beams and painted rafters, and on the sides were rooms with covered verandas where cages of various birds such as parrots and thrushes were hanging. On the steps sat several servant girls dressed in bright red and green. When they saw the party arriving, they quickly came forward with smiles and said, "The old lady was just speaking of you; what a coincidence, here you come!" Then three or four of them vied with each other to raise the door curtains, while one could hear someone inside announcing, "Miss Lin has arrived."

注意：“剛才老太太還念呢”可以译为"The old lady was just speaking of you"或"was just talking about you"。“可巧就來了”是"and here you are"或"what a coincidence, you've come".

黛玉方進入房時，只見兩個人攙著一位鬢發如銀的老母迎上來，黛玉便知是他外祖母．方欲拜見時，早被他外祖母一把摟入怀中，心肝儿肉叫著大哭起來．當下地下侍立之人，無不掩面涕泣，黛玉也哭個不住．一時眾人慢慢解勸住了，黛玉方拜見了外祖母．____此即冷子興所云之史氏太君，賈赦賈政之母也．當下賈母一一指与黛玉：“這是你大舅母，這是你二舅母，這是你先珠大哥的媳婦珠大嫂子。”黛玉一一拜見過．賈母又說：“請姑娘們來．今日遠客才來，可以不必上學去了。”眾人答應了一聲，便去了兩個．不一時，只見三個奶嬤嬤并五六個丫鬟，簇擁著三個姊妹來了．

翻譯：As Daiyu entered the room, she saw two attendants supporting an old lady with hair like silver coming toward her. Daiyu knew that this was her grandmother. Just as she was about to make her obeisance, her grandmother clasped her in her arms with cries of "My beloved heart! My precious!" and burst into loud weeping. Everyone standing there wept too, covering their faces, and Daiyu herself could not stop crying. After a while, the others gradually came to console them, and only then did Daiyu make her formal bows to her grandmother. [This was the Lady Shi, the dowager of whom Leng Zixing had spoken, and the mother of Jia She and Jia Zheng.]

At this point, the old lady introduced them one by one to Daiyu: "This is your elder uncle's wife; this is your second uncle's wife; this is the wife of your deceased elder cousin Zhu, whom you may call Sister-in-law Zhu." Daiyu made her bows to each. The old lady then said, "Call the girls to come. Our remote traveler has only just arrived, so there is no need to go to school today." With an answer of assent, two of the maids went off. In a short time, three young ladies arrived under the escort of three nurses and five or six maids.

注意：“攙著”可以是"supported"或"guided"。"鬢发如銀"译为"hair like silver"或"silver hair"。

“心肝儿肉叫着大哭起来”这是一种亲切的哭喊，可以译为"calling her 'heart' and 'flesh'"或"crying out 'my heart, my flesh'"。常见英译本常用"my dear child"等，但这里是直接叫心肝肉，我们保留。也可以译为"crying 'my heart, my darling child'"。

“地下侍立之人”指在场的下人们。

“掩面涕泣”是"wipe away tears"或"weep covering their faces"。

“拜見”是"make her obeisance"或"pay her respects"。

“此即冷子興所云之史氏太君”这句话在原文中是夹注，我们用方括号或插入表示。但要求不要添加解释性段落，所以我们可以自然融入叙述。但原文用双划线表示参考前文，我们可以翻译成"This was the Lady Shi, the dowager...，但为了流畅，可以放在前面：“贾母”就是史氏太君。可以写成"the Lady Dowager (née Shi)"，但最好直接按原文：在后面用破折号或括号。

注意：原文是“____此即冷子興所云之史氏太君，賈赦賈政之母也。”我们用破折号连接。

但英文中常用"this was..."，直接说"The old lady was the Lady Dowager, née Shi..."，但原文是叙述者插入，我们可以用"This was the Lady Shi, the Dowager mentioned by Leng Zixing, the mother of Jia She and Jia Zheng." 但不要添加额外解释，所以只翻译此句即可。

“贾母一一指与黛玉”译为"the old lady introduced them to Daiyu one by one"。

注意：先珠大哥的媳妇珠大嫂子：“先”是已故，所以是"deceased elder cousin Zhu"，“珠大嫂子”可以用"Sister-in-law Zhu"。

“請姑娘們來”译为"Call the girls"或"Invite the young ladies"。

“今日遠客才來，可以不必上學去了”译为"Our distant guest has arrived today, so you may skip school."

不一時，只見三個奶嬤嬤并五六個丫鬟，簇擁著三個姊妹來了．

翻译为"Before long, three young ladies arrived under the escort of three nurses and five or six maids."

“簇擁著”译为"escorted"或"surrounded"。

第一个肌肤微丰，合中身材，腮凝新荔，鼻腻鹅脂，温柔沉默，观之可亲．第二个削肩细腰，长挑身材，鸭蛋脸面，俊眼修眉，顾盼神飞，文彩精华，见之忘俗．第三个身量未足，形容尚小．其钗环裙袄，三人皆是一样的妆饰．黛玉忙起身迎上来见礼，互相厮认过，大家归了坐．丫鬟们斟上茶来．不过说些黛玉之母如何得病，如何请医服药，如何送死发丧．不免贾母又伤感起来，因说：“我这些儿女，所疼者独有你母，今日一旦先舍我而去，连面也不能一见，今见了你，我怎不伤心！”

翻译：

The first was of medium height, with a slightly plump figure, cheeks as fresh as newly peeled lychee, a nose as glossy as goose fat, and a tender, gentle manner that inspired affection. The second had sloping shoulders and a slender waist, a tall, willowy figure, an oval face with fine eyebrows and lovely eyes that sparkled with life and intelligence, and an air of elegance and refinement that made one forget all vulgarity. The third was still small and obviously not fully grown. But in their hair ornaments, bracelets, skirts, and jackets, the three sisters were identically dressed.

Daiyu rose quickly and came forward to greet them, and after they had all exchanged bows, they took their seats. The maids served tea. The conversation naturally turned to Daiyu's mother: how she had fallen ill, what physicians had been called, what medicines taken, and the funeral arrangements. This inevitably stirred the old lady's grief again, and she said, "Of all my children, the one I cherished most was your mother. Now she has left me first, without even giving me a chance to see her face one last time. Seeing you today, how could I not be heartbroken?"

注意：对第一个人的描写：肌肤微丰 (slightly full figure)，合中身材 (medium height)，腮凝新荔 (cheeks like lychee flesh)，鼻腻鹅脂 (nose like goose fat/creamy)，“温柔沉默” (tender and quiet)，“观之可亲” (pleasant to look at). 我们可以用"plump"吗？"微丰"是slightly plump, but not fat。用"medium build with a slight fullness"更好。

第二个：削肩細腰 (sloping shoulders, slender waist)，長挑身材 (tall stature)，鴨蛋臉面 (oval/egg-shaped face)，俊眼修眉 (beautiful eyes and long eyebrows)，顧盼神飛 (look around with spirit)，文彩精華 (literary elegance/grandeur)，見之忘俗 (makes one forget the mundane). 我们需要美化，但保留意象。

第三个：身量未足，形容尚小 (not fully grown, youthful appearance).

“互相廝認過”指互相认识见礼，可以译为"acknowledged each other"或"exchanged bows".

“歸了坐”是"took their seats".

“不過說些”是"the conversation merely touched upon"或"they talked about nothing more than".

“如何送死發喪”指arrangements for the funeral and mourning.

“又傷感起來”译为"became upset again".

“我這些儿女，所疼者獨有你母，今日一旦先舍我而去，連面也不能一見，今見了你，我怎不傷心”

语气要强烈。"of all my children, the only one I doted on was your mother. and now she has gone ahead of me without so much as a chance to see her face one last time. Seeing you today, how can I not be sad?"

但原文“先舍我而去”意思是先离我而去，用"left me before her time"或"departed before me".

在翻译时，注意人物心理：黛玉的谨慎，贾母的悲痛，以及环境细节。要注意英文自然，有文学感，但不现代。避免使用太现代的表达，比如"totally", "really"等。

关于专有名词：我们用拼音。

- 林黛玉 Lin Daiyu
- 荣国府 Rongguo Mansion 或 Rong Mansion
- 宁国府 Ningguo Mansion
- 贾母 Grandmother Jia 或 Lady Jia? 但我们可以用"the old lady"或"Grandmother Jia"。在英文中，我们第一次提到贾母时，可以说"Grandmother Jia (the Dowager Lady Jia)"，但根据要求，使用拼音，所以可以是"Jia Mu"？但是原文是外祖母，黛玉心里想是外祖母，所以我们用"her grandmother"或"Grandmother Jia"。但在叙述中，通常称为"the old lady"或"Grandmother Jia"。但为了贴合，我倾向于"her grandmother"起，然后用"the old lady"等。贾母这个称呼，可以用"the Lady Dowager"或"Grandmother Jia"。

同样，贾赦 Jia She, 贾政 Jia Zheng, 珠大嫂子 (wife of Jia Zhu) 可以称为"Sister-in-law Zhu"或"Zhu's wife"。

注意：珠大哥是贾珠，已故，所以是Jia Zhu。

人物：三个姊妹：分别是迎春、探春、惜春，但在这个片段中并未提及名字，只描写外貌。所以不必加名字。

丫鬟们：提到有几个穿红着绿的丫头，还有后面出来的奶嬷嬷和丫鬟。

在翻译中，注意不要添加解释性语句，只忠实翻译原文。

现在，我们整合英语翻译。

整体结构：从开头到“今見了你，我怎不傷心！”结束。

注意原文中有一些下划线或者空格，但我们在翻译中忽略。

需要确保段落对应？不需要严格按原文分句，但可以按意义分段。

在开头“且說”可以译为"Now".

关于“走了一射之地”，有的译文用"about a bowshot away"。

"抄手游廊"：covered walkways on both sides，也可以说是"winding verandas"。

“穿堂”：a passage hall。

“大插屏”：a large screen。

“紫檀架子大理石”：rosewood frame and marble。

“雕梁畫棟”：carved beams and painted rafters。

“穿山游廊”：covered walkways connecting the mountains? 实际上“穿山游廊”是指穿过假山的游廊，也可以是"covered walkways that link the side buildings"。我们译为"covered verandas linking the side rooms"。

“台磯之上”：on the steps。

“打帘籠”：raised the door curtain（帘笼是门帘）。

“老太太”：the old lady。

然后“林姑娘到了”：Miss Lin has arrived。

后面“兩個人攙著一位鬢發如銀的老母”：two people supporting an old lady with silver hair.

“方欲拜見時”：was about to bow in greeting when.

“早被他外祖母一把摟入怀中”：but her grandmother quickly drew her into her arms.

“心肝儿肉叫著大哭起來”：crying "my heart, my precious!" and weeping loudly.

注意：有的版本写“心肝儿肉”，可以译为"my heart, my flesh"，但不太习惯，常见是"my darling"。为了原汁原味，保留直译并加引号。

“當下地下侍立之人，無不掩面涕泣”：At that time, all those waiting on the floor covered their faces and wept.

“解勸住了”：consoled and calmed down.

“方拜見了外祖母”：then she made her formal bows to her grandmother.

“此即冷子興所云之史氏太君，賈赦賈政之母也。”这句话可以这样处理：用破折号引出，或者用括号，或者融入到前一句中。如"This was the Lady Shi, the dowager mentioned by Leng Zixing, mother of Jia She and Jia Zheng." 不过“太君”是对贵族女性的尊称，译为"Lady Dowager"。

在环境描写中，注意时态一致。大多用过去时。

现在写出完整英文。

注意要自然、文学感，忌现代口语。

开始输出：

Now, on the day when Daiyu left her boat and came ashore, a sedan chair and carts for luggage from the Rongguo Mansion had been waiting for her for some time. Lin Daiyu had often heard her mother say that her grandmother's household was unlike any other. The few women servants of the third rank she had seen recently were already exceptional in their clothes and other belongings; how much more would this be the case when she reached the house itself. So she watched every step, attentive at all times, careful not to speak an unnecessary word or take an unnecessary step, for fear of being laughed at.

Once she had got into the chair and entered the city, she looked out through the gauze windows and saw that the streets were far more bustling and crowded with people than those in other places. After traveling for some time, she suddenly noticed two large stone lions crouching to the north of the street, and a three-bay gate with beast-head ornaments. Ten or so fashionably dressed people were sitting in front of the gate. The main gate was not open; only the east and west side gates showed people coming and going. Above the main gate was a large tablet inscribed with the words: "NINGGUO MANSION BUILT BY IMPERIAL DECREE." Daiyu thought: This must be the eldest branch of Grandmother’s family. They went further west, and before long they saw another three-bay gate—that was the Rongguo Mansion.

But they did not enter through the main gate; instead, they went in through the west side gate. The bearers carried the chair some distance—about an arrow's flight—and when they were about to turn a corner, they set it down and withdrew. The old serving-women following behind had already dismounted from their own chairs and now hurried forward. Three or four young servants of seventeen or eighteen, well dressed and groomed, took up the chair again and carried it forward. The old women followed on foot until the chair was set down before a gate with hanging floral ornaments. The young servants withdrew, and the old women came forward, raised the chair curtain, and helped Daiyu to alight.

Leaning on the old woman’s hand, Daiyu entered through the gate with hanging flowers. On either side were winding, roofed walkways; in the center was an open passage. In front stood a large marble screen in a rosewood frame. Passing the screen, she came to a small three-room hall. Beyond the hall lay the main rear courtyard. The front consisted of five large rooms with carved beams and painted rafters, and on the sides were wing rooms with covered walkways, from which hung cages of colorful parrots, thrushes, and other birds. On the stone steps sat a number of maids dressed in red and green. As soon as they saw the party approaching, they rushed forward smiling and said, "Just now the old lady was mentioning you—what a coincidence to see you come!" Then three or four of them vied to raise the door curtain, while someone inside was heard announcing, "Miss Lin has arrived."

Just as Daiyu entered the room, she saw two attendants supporting an old lady with hair like silver coming toward her. Daiyu knew at once that it was her grandmother. She was about to bow and pay her respects, but before she could, her grandmother clasped her to her bosom, calling her "my heart, my flesh!" and burst into a storm of weeping. Everyone standing there covered their faces and wept; Daiyu herself could not stop crying. Gradually, the others calmed them down, and only then did Daiyu make her formal obeisance to her grandmother. [This was the Lady Dowager of Lord Shi's family, of whom Leng Zixing had spoken, the mother of Jia She and Jia Zheng.]

The old lady then introduced them to Daiyu one by one: "This is your elder uncle's wife; this is your second uncle's wife; this is the wife of your deceased elder cousin Zhu, whom you may call Sister-in-law Zhu." Daiyu made her bows to each in turn. The old lady then said, "Call the young ladies. Today our distant guest has arrived, so no need to go to school." The maids responded with a "yes" and two of them went off. In a little while, three nurses and five or six maids arrived, escorting the three young ladies.

The first was of medium build, with a slightly plump figure, cheeks like fresh lychee, nose as fine and creamy as goose fat, gentle and quiet in demeanor—most pleasing at first sight. The second had sloping shoulders, a slender waist, a tall and slight figure, an oval face, fine eyebrows and elegant eyes full of life and intelligence, a grace and refinement that made one forget the mundane world. The third was still young and small of stature. In their hair ornaments, bracelets, skirts, and jackets, the three sisters were dressed exactly alike.

Daiyu quickly rose and came forward to greet them, and after they had all acknowledged each other, they took their seats. The maids poured tea. Their conversation could not go beyond how Daiyu’s mother had fallen ill, what physicians had been called, what medications taken, and the funeral and mourning that followed. This inevitably stirred the old lady’s grief once more, and she said, "Of all my children, the one I treasured most was your mother. And now she has left me first, without my having a chance to see her face even one last time. When I see you today, how can I not be heartbroken?"

注意：在“此即冷子興所云之史氏太君，賈赦賈政之母也”这一句，我用了方括号（英文里用中括号[ ]）。但原文中用下划线隔开，或许可以不用括号，直接作为叙述。或者用破折号。我选择用方括号作为插入。但要求不要添加解释性段落，这个插入严格来说是原文就有的，所以翻译中保留应该没问题。但是要确保不额外解释。所以保留它。

在描写三姐妹时，“文彩精华”我译成"grace and refinement"，但原文可能强调文学光彩，不过sisters so young, 可以用"literary elegance"？但最好避免太过。我们采用"elegance and refinement"。

“見之忘俗”译为"made one forget vulgarity"或"were enough to make one forget all that was common"。

我用了"made one forget the mundane world"。

整体，检查一遍：

- 没有添加解释
- 人名用了拼音：Lin Daiyu, Rongguo Mansion, Ningguo Mansion, Leng Zixing, Jia She, Jia Zheng, Jia Zhu. 对于“老太太”用了"the old lady" and "grandmother". “珠大嫂子”用了"Sister-in-law Zhu"。

注意：“珠大嫂子”是珠大哥的媳妇，原文称呼她为“珠大嫂子”，英文可以称"Sister-in-law Zhu"或"Elder Sister-in-law Zhu". 但为了尊重原文，保留“大嫂子”。

关于“心肝儿肉”，我翻译为"my heart, my flesh!" 为了保留形象。也可以叫"my precious"等，但我觉得直译更好。

关于“一射之地”，我译为"about an arrow's flight"。

最后贾母的话：“今日一旦先舍我而去”我译为"left me first"或"departed before me"。我用了"left me first"。

“今見了你，我怎不傷心”反问，表达了强烈的情绪，不用问号也可，但原文是感叹还是问？原文用感叹号，但情感强烈。我保留问号：“how can I not be heartbroken?”

注意：英文中"how could I not be sad"是常见的。

现在，我们输出完整的翻译。

注意要求：保留人物心理、礼仪分寸和环境细节；英文要自然、有文学感，但不要过度现代化；人名可采用拼音。不要添加解释性段落。

我们确保所有元素都在。

关于“抄手游廊”，我用了"winding, roofed walkways"，而"covered walkways on both sides"也可以。

关于“穿山游廊”，我用了"were wing rooms with covered walkways"但原文是“穿山游廊厢房”，意思是厢房有穿山游廊连接。可以更准确："with covered verandas that connected the side buildings"。

可以改为: "and on the sides were side chambers with verandas running along the hills (or running through the hills?)" 但“穿山”可能是穿过假山。用"covered walkways that passed through artificial hills"？但为了简洁，我用了"covered walkways".

也可以直接： "and flanking rooms connected by covered walkways through the hills".

但是在一段里，不需要太精确，因为文学翻译。我保持之前的版本。

为了更准确，我修改该句："and on the sides were rooms with verandas that ran through the rockeries" 但我觉得原文不一定强调假山，也可以理解为穿过山墙。为了简洁，我用"covered walkways"。

而且“穿山游廊”一般指穿山游廊相连。有的译本直接略过细节。我们可以保持。

我之前的句子：“on the sides were wing rooms with covered walkways” 可以。

现在，我认为翻译质量还可以，但我们可以再审视语言。

The women servants of the third rank: 三等仆妇，是否用"women servants of the third rank"？三等不一定指等级，更可能是第三等执事仆妇，但这样直译不太容易理解。但是原文是“三等仆妇”，既然保留文化，就直译。但可以意译为"lower-ranking maids"还是"third-grade servant women"? 为了体现深意，用"serving women of the third grade"。

在开头：“這林黛玉常听得母親說過，他外祖母家与別家不同”我用"had often heard her mother say that her grandmother's household was unlike any other." 但“别家”指其他家庭。直接用"different from other families"更好。我用了"unlike any other"相当于“与众不同”，也可以。

“所疼者獨有你母”译为"the one I treasured most was your mother"。

注意“今日一旦先舍我而去”我用"now she has left me first" 有点歧义，可以用"gone ahead of me" 或 "departed before me"。我改用"departed before me"。

“连面也不能一见”译为"without my having a chance to see her face even one last time"。

这样行。

现在写完整版本，确保流畅。

注意标点：英文用逗号句号。中文有感叹号、问号，我保留一些。

在贾母哭的话里，原文是感叹号，但我用了问号“我怎不伤心！”是感叹兼反问，英文用问号或感叹号？用感叹号来保留强度："how could I not be heartbroken?" 或者 "how can I not be sad!" 我认为问号也可以表示强烈。

但有些译文： "How could I not be grieving!" 但为了自然，我使用问号。

关于“心肝儿肉叫着”我在引号外，在句中。

还有“一面听得人回话”中的“一面”可以译为"meanwhile"或"at the same time"。我译为"while someone inside was heard announcing"。

“林姑娘到了”是直接引语，所以引号。

最后一段“丫鬟們斟上茶來．不過說些黛玉之母如何得病，如何請醫服藥，如何送死發喪．”这部分我译成"The maids poured tea. Their conversation could not go beyond how Daiyu’s mother had fallen ill, what physicians had been called, what medications taken, and the funeral and mourning that followed." 注意“送死发丧”指death and funerals。

但原文“送死發喪”可以译为"the arrangements for her death and funeral"。我用了"the funeral and mourning that followed"。

在三个姊妹的外貌，第三个“身量未足，形容尚小”译为"the third was still young and small of stature"。原文“形容尚小”指容貌还未丰满，可以更具体，但这样够了。

确保英文文学感：用词如"crouching", "bustling", "gleamed", "sparkled"等，适宜。

关于“林黛玉忙起身迎上来见礼，互相厮认过，大家归了坐。” 翻译为"Daiyu quickly rose and came forward to greet them, and after they had all acknowledged each other, they took their seats." 其中“厮认过”指互相认识并见礼，所以用"acknowledged each other"。

最后“不免賈母又傷感起來”译为"This inevitably stirred the old lady's grief again", 后面“因说”可译为"and she said"。

现在，输出最终版本。

为了清晰，我分段落，但原文有些段落可以合并。保持合理分段。

注意不要有额外内容。

开始：

Now, on the day when Daiyu left her boat and came ashore, a sedan chair and carts for luggage from the Rongguo Mansion had been waiting for her for some time. Lin Daiyu had often heard her mother say that her grandmother's household was unlike any other. The few serving women of the third rank she had seen recently were already exceptional in their clothes and daily needs; how much more would this be the case when she reached the house itself! So she watched every step, was attentive at all times, and did not dare to speak an extra word or take an extra step, for fear of being laughed at.

Once she had got into the chair and entered the city, she looked out through the gauze windows and saw that the streets were far more bustling and crowded than those in other places. After traveling for some time, she suddenly noticed two large stone lions crouching at the north end of the street, and a three-bay gate adorned with beast-head motifs. Ten or so people in splendid attire were sitting in front of the gate. The main gate was not open; only the east and west side gates showed people coming and going. Above the main gate was a large tablet inscribed with five characters: "NINGGUO MANSION BUILT BY IMPERIAL DECREE." Daiyu thought: This must be the eldest branch of Grandmother’s family. They proceeded further west, and before long they saw another set of three gates—that was the Rongguo Mansion.

But they did not enter through the main gate; instead, they went in through the west side gate. The bearers carried the chair about the distance of an arrow's flight, and when they were about to turn a corner, they set it down and withdrew. The old women servants following behind had already got out of their own chairs and now hurried forward. Then three or four young lads of seventeen or eighteen, well dressed and groomed, took up the chair again and carried it forward. The old women followed on foot until the chair was set down before a gate with hanging floral ornaments. The lads withdrew, while the old women came forward, raised the chair curtain, and helped Daiyu to alight.

Leaning on the old woman’s hand, Daiyu entered the gate with hanging flowers. On both sides were roofed, winding walkways; in the center was an open passage. In front stood a large marble screen in a rosewood frame. Passing the screen, she came to a small three-bay hall. Behind the hall lay the main rear courtyard. The front consisted of five main rooms with carved beams and painted rafters, and on the sides were wing rooms with covered verandas, from which hung cages of vividly colored parrots, thrushes, and other birds. On the stone steps sat several maids dressed in red and green. As soon as they saw the party approaching, they rushed forward smiling and said, "Just now the old lady was speaking of you—what a happy coincidence that you have come!" Then three or four of them vied in raising the door curtains, and someone inside was heard announcing, "Miss Lin has arrived."

As Daiyu entered the room, she saw two attendants supporting an old lady with hair like silver coming toward her. Daiyu knew at once that it was her grandmother. She was about to bow and pay her respects, but before she could, her grandmother clasped her to her bosom, crying, "My heart, my flesh!" and burst into loud weeping. Everyone standing there covered their faces and wept; Daiyu herself could not stop crying. After a while, the others gradually composed themselves, and only then did Daiyu make her formal obeisance to her grandmother. (This was the Lady Shi, the Dowager of whom Leng Zixing had spoken, the mother of Jia She and Jia Zheng.)

The old lady then introduced them to Daiyu one by one: "This is your elder uncle's wife; this is your second uncle's wife; this is the wife of your deceased elder cousin Zhu, whom you may call Sister-in-law Zhu." Daiyu made her bows to each in turn. The old lady then said, "Send for the young ladies. Our faraway guest has just arrived, so they need not go to school today." The maids acknowledged and two of them went off. In a little while, three nurses and five or six maids arrived, escorting the three young ladies.

The first was of medium height, with a slightly plump figure, cheeks like fresh lychee, a nose as creamy as goose fat, gentle and quiet in manner—most pleasing at first sight. The second had sloping shoulders, a slender waist, a tall and graceful build, an oval face with fine eyebrows and sparkling eyes full of life and intelligence, an air of elegance and refinement that made one forget all vulgarity. The third was still young and small of stature. In their hair ornaments, belts, skirts, and jackets, the three sisters were dressed exactly alike.

Daiyu quickly rose and came forward to greet them, and after they had all acknowledged each other, they took their seats. The maids poured tea. Their conversation could not go beyond how Daiyu’s mother had fallen ill, what physicians had been called, what medicines had been prescribed, and the arrangements for the funeral and mourning. This inevitably stirred the old lady’s grief anew, and she said, "Of all my children, the one I treasured most was your mother. Now she has departed before me, without my having a chance to see her face even one last time. Seeing you today, how can I not be heartbroken?"

注意，我该了最后一句为“departed before me”和“how can I not be heartbroken?”。

另外，在“其钗环裙袄，三人皆是一样的妆饰”我改为“In their hair ornaments, belts, skirts, and jackets”，保留了“裙袄”裙子袄子，但用“jackets”可以。原意是裙子与短袄。

对于“顧盼神飛”，我用“sparkling eyes full of life and intelligence”

“文彩精華”用“air of elegance and refinement”。

整体，我认为可以。

但注意，问题里说“不要添加解释性段落”，我们插入的“(This was the Lady Shi...)”这一句是否算解释？这其实是原文的叙述，不是我们添加的，所以应该可以。在原文中是用下划线隔开的，在英文中我们可以用括号或直接叙述。但为了自然，我用了括号，但原文不是括号，而是句号分隔。所以也可以直接作为句子写： "This was the Lady Dowager of Lord Shi's family, of whom Leng Zixing had spoken, the mother of Jia She and Jia Zheng." 然后另起一句“当下一一...”。但是要注意时态和衔接。所以我可以直接写成一句："This was the Lady Shi, the Dowager mentioned by Leng Zixing, the mother of Jia She and Jia Zheng." 然后接着“当下贾母一一...”翻译为"The old lady then introduced..."。 我尝试改回不括号。

对于“心肝儿肉”，我保持单引号或双引号，也一致。

还有“便都笑迎上来”我用了“rushed forward smiling”，或者也可以用“came forward with smiles”。

关于“拉行李的车辆”我用了"carts for luggage"，可以用"baggage carts"。

原文“久候了”表示等了很久，所以加"had been waiting for some time"或"waiting a long time"。

在第一段中，“自那日弃舟登岸时”中的“自那日”是叙事者回顾，表示在那一日，所以用"on the day when"。

也可以说“It was on that day when Daiyu disembarked...”但我觉得可以。

现在，再读一遍，确保英文语感。

注意：不要漏掉细节，比如“门前列坐著十來個華冠麗服之人”我翻译为"Ten or so people in splendid attire were sitting in front of the gate." “华冠丽服”意为beautiful hats and clothes。但用了"splendid attire"足够。

“正門之上有一匾，匾上大書"敕造宁國府"五個大字” 我译 "Above the main gate was a large tablet inscribed with five characters: 'NINGGUO MANSION BUILT BY IMPERIAL DECREE.'" 用capital letters表示牌匾字样。

“敕造”表示奉皇帝之命建造，built by imperial decree.

“又行了半日”中的“半日”表示好半天，长时间，我用了"After traveling for some time"。

对于“走了一射之地”，我用"the distance of an arrow's flight"。

“将转弯时”译为"when they were about to turn a corner"。

“众婆子步下围随至一垂花门前落下”译为"The old women followed on foot until the chair was set down before a gate with hanging floral ornaments." “步下”意为步行，所以用"followed on foot"。

“两边是抄手游廊”译为"On both sides were roofed, winding walkways"。

“当中是穿堂”"in the center was an open passage"。

“紫檀架子大理石的大插屏”"a large marble screen in a rosewood frame"。

“转过插屏，小小的三间厅，厅后就是后面的正房大院” "Passing the screen, she came to a small three-bay hall. Behind the hall lay the main rear courtyard."

“正面五间上房，皆雕梁画栋”"The front consisted of five main rooms with carved beams and painted rafters"注意时态。

“两边穿山游廊厢房” "and on the sides were wing rooms with covered verandas"我加了“covering”，但原文的“穿山游廊”可能指连接厢房的游廊。或许可以表达"rooms connected by covered walkways through the hills"? 但我觉得现有译文可以。

“挂着各色鹦鹉、画眉等鸟雀”"from which hung cages of vividly colored parrots, thrushes, and other birds"

“台矶之上，坐着几个穿红着绿的丫头”"On the stone steps sat several maids dressed in red and green."

注意“丫头”可以是"maids"或"servant girls"。

“刚才老太太还念呢，可巧就来了。”"Just now the old lady was speaking of you—what a happy coincidence that you have come!" 或者 "what a coincidence, here you are!"

“于是三四人争着打起帘笼”"Then three or four of them vied in raising the door curtains"

“一面听得人回话”"and someone inside was heard announcing"

“黛玉方进入房时”"As Daiyu entered the room" 与前面衔接。

“只见两个人搀着一位鬓发如银的老母迎上来”"she saw two attendants supporting an old lady with hair like silver coming toward her."

“黛玉便知是她外祖母”"Daiyu knew at once that it was her grandmother."

“方欲拜见时，早被她外祖母一把搂入怀中，心肝儿肉叫着大哭起来。”"She was about to bow and pay her respects, but before she could, her grandmother clasped her to her bosom, crying, 'My heart, my flesh!' and burst into loud weeping."

“当下地下侍立之人，无不掩面涕泣，黛玉也哭个不住。”"Everyone standing there covered their faces and wept; Daiyu herself could not stop crying."

“一时众人慢慢解劝住了，黛玉方拜见了外祖母。”"After a while, the others gradually composed themselves, and only then did Daiyu make her formal obeisance to her grandmother."

“此即冷子兴所云之史氏太君，贾赦贾政之母也。”"This was the Lady Shi, the Dowager mentioned by Leng Zixing, the mother of Jia She and Jia Zheng." 我修改为不括号，直接作为叙述句。但注意前面一句已经说“外祖母”，这里再说是旁白。也可以直接写"The old lady was the Lady Shi..." 但我用"This was"来指代。

“当下贾母一一指与黛玉”我直接连续"The old lady then introduced them to Daiyu one by one:" 注意这里我用了"the old lady"，但前面刚说"her grandmother"，人称变换问题。但可以。

为了统一，前面用“the old lady”称呼贾母，但黛玉视角用“her grandmother”。我在旁白中也可以用"the old lady"或"Grandmother Jia"。但为了避免混淆，可以用"the old lady"贯穿旁白，但当她是黛玉的外祖母时，从黛玉视角用"her grandmother"。

在第一段后，我们曾用"her grandmother's household"，然后叙述多用"the old lady"。当我写"Aold lady introduce"时，也是旁白。

在“此即...”之后，可以继续用"the old lady"。

对于三个姊妹的细节，要注意“第一个肌肤微丰，合中身材”翻译为"The first was of medium height, with a slightly plump figure" or "The first was of medium height, full of flesh"? 我是“slightly plump”合适。但原文“合中身材”就是中等身材。“腮凝新荔”比喻，注意是“新荔”指新鲜荔枝的肉质白嫩，所以用"cheeks like fresh lychee"。

“鼻腻鹅脂”指鼻子像鹅脂那样细腻白润，英语用"nose as creamy as goose fat"。

“温柔沉默” means gentle and placid, quiet, 所以"gentle and quiet in manner".

“观之可亲”"most pleasing at first sight"或"inspiring affection"。

第二个“削肩细腰” sloping shoulders, slender waist, “长挑身材” tall and slender, “鸭蛋脸面” oval face, “俊眼修眉” beautiful eyes and long eyebrows, “顾盼神飞” glances that sparkled with vivacity, “文彩精华” literary grace, elegance “见之忘俗” makes one forget mundane world.

我翻译为"an oval face with fine eyebrows and sparkling eyes full of life and intelligence, an air of elegance and refinement that made one forget all vulgarity." 但是原文“文彩精华”可能更强调文采，用在女孩身上指才华。但这里三姐妹还未读书，所以可能是描写她的气质。用"grace and intelligence"。

第三个“身量未足，形容尚小”还小，所以"The third was still young and small of stature."

“其钗环裙袄，三人皆是一样的妆饰”"In their hair ornaments, belts, skirts, and jackets, the three sisters were dressed exactly alike." 注意“钗环”头钗和耳环或手镯，“裙袄”裙子袄子。用hair ornaments and bracelets? 但为了简洁，用"in their jewelry and clothes"？我还原成具体。

“黛玉忙起身迎上来见礼，互相厮认过，大家归了坐” "Daiyu quickly rose and came forward to greet them, and after they had all acknowledged each other, they took their seats."

“丫鬟们斟上茶来”"The maids poured tea."

“不过说些黛玉之母如何得病，如何请医服药，如何送死发丧” "Their conversation could not go beyond how Daiyu’s mother had fallen ill, what physicians had been called, what medicines had been prescribed, and the arrangements for the funeral and mourning."

“不免贾母又伤感起来，因说” "This inevitably stirred the old lady’s grief anew, and she said,"

“我这些儿女，所疼者独有你母，今日一旦先舍我而去，连面也不能一见，今见了你，我怎不伤心！” "Of all my children, the one I treasured most was your mother. Now she has departed before me, without my having a chance to see her face even one last time. Seeing you today, how can I not be heartbroken!"

注意语气用感叹号？我用的问号？原文感叹，但英文问号反问更强烈。我决定用感叹号: "how can I not be heartbroken!" 因为原文是感叹号。另外，“今日一旦”中的“一旦”是“竟然”的意思，用"so suddenly"不好，我略过。用"Now she has departed before me"传达了。

现在，输出最终版本，注意段落结构。

为了更接近原文，段落可以更紧凑。原文第一段到“惟恐被人耻笑了他去”是心理。然后“自上了轿”开始是行动。我们按意义分段。

还有，注意“且說”在英文中可用"Now"开始，但也可以省略。我保留"Now"。

现在，整体检查一次。

出现的人名：Lin Daiyu, Rongguo Mansion, Ningguo Mansion, Leng Zixing, Jia She, Jia Zheng, "Sister-in-law Zhu" (or Zhu's wife). 没有其他。

关于“垂花门”：我译为"gate with hanging floral ornaments"，常见译法为"gate with hanging flowers" 或 "festooned gate"。我用"with hanging floral ornaments"。

关于“穿堂”：我译为"open passage"，但也可以译成"hallway" or "vestibule"。穿堂是庭院之间的通道，用"passage"就好。

关于“抄手游廊”：有些翻译为"verandas"或"winding corridors with a roof"。我用了"roofed, winding walkways"。

关于“穿山游廊”：有译为"covered corridors clinging to the artificial hills" 但我不想太复杂，用了"covered verandas"。

在英文中，我希望自然，所以我不会用太复杂的建筑术语，而是用常见词，使其流畅。

比如"pergola"不必要。

“雕梁画栋”是"carved beams and painted rafters"。

最后，我再确认是否有遗漏部分：“然后三四人争着打起帘笼，一面听得人回话：‘林姑娘到了。’”我翻译为"Then three or four of them vied in raising the door curtains, while someone inside was heard announcing, 'Miss Lin has arrived.'" 没有遗漏。

“贾母又说：‘请姑娘们来．今日远客才来，可以不必上学去了。’”我翻译了。

“众人答应了一声，便去了两个”我译为"The maids acknowledged and two of them went off." 注意原文是“众人答应”，我用了"the maids"因为指的是丫鬟们，但也可以是"the others"。但更具体用了"maids"。

可以。

在“只见三个奶嬷嬷并五六个丫鬟，簇拥着三个姊妹来了”中，“奶嬷嬷”是nurses, “丫鬟”maids. 我用了"three nurses and five or six maids"。

“第一个”外貌描写：“肌肤微丰，合中身材，腮凝新荔，鼻腻鹅脂，温柔沉默，观之可亲”仔细看，原文没有标点，但意思清楚。我在英文用句子。

“第二个削肩细腰，长挑身材，鸭蛋脸面，俊眼修眉，顾盼神飞，文彩精华，见之忘俗” 句型要变化。

我翻译为："The second had sloping shoulders, a slender waist, a tall and graceful build, an oval face with fine eyebrows and sparkling eyes full of life and intelligence, an air of elegance and refinement that made one forget all vulgarity."

“第三个身量未足，形容尚小” 译为 "The third was still young and small of stature."

注意：原文“形容尚小”可能指身材还小，容貌未丰满，所以young and small.

“其钗环裙袄，三人皆是一样的妆饰” 我处理为 "In their hair ornaments, belts, skirts, and jackets, the three sisters were dressed exactly alike." 注意“钗环”不一定是belt，但为了简洁我用"belts"不准确，不如直接"In their hair ornaments and clothes" 但原文具体说钗(发簪)环(耳环或手镯)、裙(裙子)、袄(短上衣)。所以更准确是"hairpins and bracelets, skirts and jackets" 我改用"ornaments and clothes"。但是为了忠实，我或其他译法如在尾句。

在“互相厮认过”是"acknowledged each other"。

此后“大家归了坐” "they took their seats".

然后“丫鬟们斟上茶来” "the maids poured tea"。

然后“不过说些黛玉之母如何得病，如何请医服药，如何送死发丧”这个句子是叙述，没有直接引语，所以用间接引语。

“不免贾母又伤感起来”直接翻译为"this inevitably stirred the old lady's grief anew"。

最后一句，不要忘了引号。

注意：整个翻译是过去时，保持一致。

现在撰写最终回答。

注意：问题提供的是素材来源和链接，但我们的回答只需要英文翻译。

我准备以段落形式输出英文翻译，不需要额外文字。

我开始写下英文翻译。

我最终决定用：

Now, on the day when Daiyu left her boat and came ashore, a sedan chair and baggage carts from the Rongguo Mansion had been waiting for her for some time. Lin Daiyu had often heard her mother say that her grandmother's household was unlike any other. The few women servants of the third rank she had seen recently were already exceptional in their dress and belongings; how much more would this be the case when she reached the house itself! So she watched every step, she was attentive at all times, and did not dare to speak an extra word or take an extra step, for fear of being laughed at.

Once she had got into the chair and entered the city, she looked out through the gauze windows and saw that the streets were far more bustling and crowded with people than those in other places. After traveling for some time, she suddenly noticed two large stone lions crouching at the north end of the street, and a three-bay gate adorned with beast-head ornaments. Ten or so men in splendid clothes were sitting in front of the gate. The main gate was not open; only the east and west side gates showed people coming and going. Above the main gate was a large tablet inscribed with the words: "NINGGUO MANSION BUILT BY IMPERIAL DECREE." Daiyu thought: This must be the eldest branch of Grandmother's family. They proceeded further west, and before long they saw another set of three gates—that was the Rongguo Mansion.

But they did not enter through the main gate; instead, they went in through the west side gate. The bearers carried the chair about the distance of an arrow's flight, and when they were about to turn a corner, they set it down and withdrew. The old women servants following behind had already got out of their own chairs and now hurried forward. Then three or four young lads of seventeen or eighteen, well dressed and groomed, took up the chair again and carried it forward. The old women followed on foot until the chair was set down before a gate with hanging floral ornaments. The lads withdrew, while the old women came forward, raised the chair curtain, and helped Daiyu to alight.

Leaning on the old woman's hand, Daiyu entered the gate with hanging flowers. On both sides were roofed, winding walkways; in the center was an open passage. In front stood a large marble screen in a rosewood frame. Passing the screen, she came to a small three-bay hall. Beyond the hall lay the main rear courtyard. The front consisted of five main rooms with carved beams and painted rafters, and on the sides were wing rooms with covered verandas, from which hung cages of vividly colored parrots, thrushes, and other birds. On the stone steps sat several maids dressed in red and green. As soon as they saw the party approaching, they rushed forward smiling and said, "Just now the old lady was speaking of you—what a happy coincidence that you have come!" Then three or four of them vied in raising the door curtains, and someone inside was heard announcing, "Miss Lin has arrived."

As Daiyu entered the room, she saw two attendants supporting an old lady with hair like silver coming toward her. Daiyu knew at once that it was her grandmother. She was about to bow and pay her respects, but before she could, her grandmother clasped her to her bosom, crying, "My heart, my flesh!" and burst into loud weeping. Everyone standing there covered their faces and wept; Daiyu herself could not stop crying. After a while, the others gradually composed themselves, and only then did Daiyu make her formal obeisance to her grandmother. This was the Lady Shi, the Dowager of whom Leng Zixing had spoken, the mother of Jia She and Jia Zheng.

The old lady then introduced them to Daiyu one by one: "This is your elder uncle's wife; this is your second uncle's wife; this is the wife of your deceased elder cousin Zhu, whom you may call Sister-in-law Zhu." Daiyu made her bows to each in turn. The old lady then said, "Send for the young ladies. Our faraway guest has just arrived, so they need not go to school today." The maids acknowledged and two of them went off. In a little while, three nurses and five or six maids arrived, escorting the three young ladies.

The first was of medium height, with a slightly plump figure, cheeks like fresh lychee, a nose as creamy as goose fat, gentle and quiet in manner—most pleasing at first sight. The second had sloping shoulders, a slender waist, a tall and graceful build, an oval face with fine eyebrows and sparkling eyes full of life and intelligence, an air of elegance and refinement that made one forget all vulgarity. The third was still young and small of stature. In their hair ornaments, skirts, and jackets, the three sisters were dressed exactly alike.

Daiyu quickly rose and came forward to greet them, and after they had all acknowledged each other, they took their seats. The maids poured tea. Their conversation could not go beyond how Daiyu's mother had fallen ill, what physicians had been called, what medicines had been prescribed, and the arrangements for the funeral and mourning. This inevitably stirred the old lady's grief anew, and she said, "Of all my children, the one I treasured most was your mother. Now she has departed before me, with not even a chance to see her face. Seeing you today, how can I not be heartbroken!"

注意我调整了最后一句，把“连面也不能一见”译为"with not even a chance to see her face"。

但是原文“今见了你”是今天见到你，所以"Seeing you today"。

还注意：原文是“今见了你，我怎不伤心！”语气强烈。英文用“how can I not be heartbroken!”足已。

注意人称：前面是“你母” your mother，后面“今见了你” seeing you。

在倒数第二段，我用了“the old lady’s grief anew”，当时提出黛玉之母的死因，所以贾母伤心。注意原文“不免贾母又伤感起来”，所以是“again”(又)。所以我加了“anew”。

在“此即冷子兴所云之史氏太君”这句，我保持不加括号，以叙述形式放在前一句之后。或者也可以放在“贾母一一指与黛玉”之前，但原文顺序在中间。我放在了黛玉拜见过外祖母之后，在那句话后面直接说。而且用“This was”开头。

为了确保无误，我检查标点：英文引号是双引号，内部单引号。直译时要注意。

比如“心肝儿肉”用单引号在里面？其实我用了双引号，没问题。

关于“一语未了”“一经”等没有。

现在，我认为翻译可以了。

但注意到人物名字的拼音：林黛玉 Lin Daiyu, 贾母 Jia Mu? 但原文是“外祖母”或“老太太”，我用her grandmother/the old lady。在介绍“史氏太君”时，我用"the Lady Shi"，但也可以用"Lady Dowager"。而且提到贾赦贾政，我直接用Jia She, Jia Zheng。没问题。

另外，关于“三等仆妇”，我用了“women servants of the third rank”，但rank可能被理解为等级，但原文三等可能是等级。但中国文化中家仆分等级，三等不算高，但已经不凡。所以保留。

“吃穿用度” I used "dress and belongings" earlier, but changed to "dress and daily needs" in second draft? I used "dress and belongings" earlier but now "dress and daily necessities"更好。我在这版本用了"dress and belongings"?

在第一个版本里，我是"clothes and daily needs"，但我最终稿第一段是"dress and belongings" maybe "dress and daily necessities"? 我再看最终稿第一段："The few women servants of the third rank she had seen recently were already exceptional in their dress and belongings; " 用了"belongings"，但“用度”指开支使用，可以译成"possessions and livelihood"。不过"belongings"勉强。为了准确，改为"clothing and daily necessities"。我修改。

第一段：“The few women servants of the third rank she had seen recently were already exceptional in their dress and daily upkeep;” 或者“clothes and daily needs”。我改用“their clothes and daily needs”最简单。

所以在最终版本中，我改为：“The few women servants of the third rank she had seen recently were already exceptional in their clothes and daily needs;”使用clothes and daily needs。

同时注意：第一句有“拉行李的车辆”，我用了“baggage carts”。

现在写出最终草稿。

还有，关于“門前列坐著十來個華冠麗服之人”，这里“人”应该是家丁或门人，我用了"men"。

在“轉過插屏，小小的三間廳，廳后就是后面的正房大院”，我用了"Passing the screen, she came to a small three-bay hall. Beyond the hall lay the main rear courtyard." 注意“小小的三間廳”表明三开间的小厅。我用了"three-bay hall"。

在“正面五間上房，皆雕梁畫棟”前面，原文没有提到“正面”，但我加了"The front consisted of five main rooms"。或者“At the front were five main houses……”。合适。

在“兩邊穿山游廊廂房”，我改成“and on the sides were wing rooms with covered verandas” 但也许“with verandas running through the hills”更准确，但我不想过度解释。维持现状。

在“挂著各色鸚鵡，畫眉等鳥雀”，我写“from which hung cages of vividly colored parrots, thrushes, and other birds”。

“台磯之上”我用“on the stone steps”。

“一見他們來了，便忙都笑迎上來”用“rushed forward smiling”。

注意“剛才老太太還念呢”用“Just now the old lady was speaking of you”。

“于是三四人爭著打起帘籠”用“Then three or four of them vied in raising the door curtains”。

在密且的段落，我使用了“一面听得人回话：‘林姑娘到了。’”改为“and someone inside was heard announcing, 'Miss Lin has arrived.'”

注意“林姑娘”是Miss Lin, 这里的姑娘是未嫁小姐。

“黛玉方進入房時” As Daiyu entered the room。

“只見兩個人攙著一位鬢發如銀的老母迎上來” 用“she saw two attendants supporting an old lady with hair like silver coming toward her。”

“黛玉便知是他外祖母” “Daiyu knew at once that it was her grandmother.”

“方欲拜見時，早被他外祖母一把摟入怀中，心肝儿肉叫著大哭起來。”  “She was about to bow and pay her respects, but before she could, her grandmother clasped her to her bosom, crying, 'My heart, my flesh!' and burst into loud weeping.”

“當下地下侍立之人，無不掩面涕泣，黛玉也哭個不住。” “Everyone standing there covered their faces and wept; Daiyu herself could not stop crying.”

“一時眾人慢慢解勸住了，黛玉方拜見了外祖母。” “After a while, the others gradually composed themselves, and only then did Daiyu make her formal obeisance to her grandmother.”

“此即冷子興所云之史氏太君，賈赦賈政之母也。” 我用句子“This was the Lady Shi, the Dowager of whom Leng Zixing had spoken, the mother of Jia She and Jia Zheng.” 我放在这里，之后另起一句“The old lady then introduced...” 但要注意连冠：前面提到一度拜见了外祖母，然后介绍“此即”，所以用“This was”很自然，然后继续.

“當下賈母一一指与黛玉”可以接着“Then the old lady introduced them ...”。所以我把“This was”单独句子，后接“The old lady then”合适。

“賈母又說：‘請姑娘們來．今日遠客才來，可以不必上學去了。’” 注意“遠客”远道而来的客人，指黛玉。我用“Our faraway guest has just arrived”。或者“Our distant guest has only just arrived”。 我用“our faraway guest”。

“眾人答應了一聲，便去了兩個” 我用了“The maids acknowledged and two of them went off.”但原文“众人”指丫鬟们，所以英语用the maids。

“不一時，只見三個奶嬤嬤并五六個丫鬟，簇擁著三個姊妹來了” “In a little while, three nurses and five or six maids arrived, escorting the three young ladies.”

“第一個肌膚微豐，合中身材，腮凝新荔，鼻膩鵝脂，溫柔沉默，觀之可親” 处理为句子：“The first was of medium height, with a slightly plump figure, cheeks like fresh lychee, a nose as creamy as goose fat, gentle and quiet in manner—most pleasing at first sight.”

“第二個削肩細腰，長挑身材，鴨蛋臉面，俊眼修眉，顧盼神飛，文彩精華，見之忘俗” “The second had sloping shoulders, a slender waist, a tall and graceful build, an oval face with fine eyebrows and sparkling eyes full of life and intelligence, an air of elegance and refinement that made one forget all vulgarity.”

“第三個身量未足，形容尚小” “The third was still young and small of stature.”

“其釵環裙襖，三人皆是一樣的妝飾”  “In their hair ornaments, skirts, and jackets, the three sisters were dressed exactly alike.”

“黛玉忙起身迎上來見禮，互相廝認過，大家歸了坐” “Daiyu quickly rose and came forward to greet them, and after they had all acknowledged each other, they took their seats.”

“丫鬟們斟上茶來” “The maids poured tea.”

“不過說些黛玉之母如何得病，如何請醫服藥，如何送死發喪” “Their conversation could not go beyond how Daiyu's mother had fallen ill, what physicians had been called, what medicines had been prescribed, and the arrangements for the funeral and mourning.”

“不免賈母又傷感起來，因說：‘我這些儿女，所疼者獨有你母，今日一旦先舍我而去，連面也不能一見，今見了你，我怎不傷心！’” “This inevitably stirred the old lady's grief anew, and she said, 'Of all my children, the one I treasured most was your mother. Now she has departed before me, without a chance to see her face even one last time. Seeing you today, how can I not be heartbroken!'”

引用时，注意英文引号嵌套。我使用双引号，内部单引号或保持。但这里最后的直接引语是贾母的话，所以用双引号括起。而其中可能没有嵌套，所以全部双引号即可。

我使用了单引号在里面，但贾母的话里没有需要再嵌套的，所以没问题。

最终稿中，全部双引号。

注意：在描写三姐妹时，我用了破折号“most pleasing at first sight”.

还有所有数字，英文一至十写出来（ten, five, and so on），一致。

现在输出最终答案。注意用户要求不要添加解释性段落，所以就直接翻译，不加前言后语。

我在发送时，只输出翻译内容，不需要说明。

注意格式：分段落，应该自然。

由于是文本，适当分段，让阅读流畅。

我整好后再发。

这次要确保完成度极高。

开始输出。
```

## Assistant

```markdown
Now, on the day when Daiyu left her boat and came ashore, a sedan chair and baggage carts from the Rongguo Mansion had been waiting for her for some time. Lin Daiyu had often heard her mother say that her grandmother’s household was unlike any other. The few women servants of the third rank she had seen recently were already exceptional in their clothes and daily needs; how much more would this be the case when she reached the house itself! So she watched every step, was attentive at all times, and did not dare to speak an extra word or take an extra step, for fear of being laughed at.

Once she had got into the chair and entered the city, she looked out through the gauze windows and saw that the streets were far more bustling and crowded with people than those in other places. After traveling for some time, she suddenly noticed two large stone lions crouching at the north end of the street, and a three-bay gate adorned with beast-head ornaments. Ten or so men in splendid clothes were sitting in front of the gate. The main gate was not open; only the east and west side gates showed people coming and going. Above the main gate was a large tablet inscribed with five characters: “NINGGUO MANSION BUILT BY IMPERIAL DECREE.” Daiyu thought: This must be the eldest branch of Grandmother’s family. They proceeded further west, and before long they saw another set of three gates—that was the Rongguo Mansion.

But they did not enter through the main gate; instead, they went in through the west side gate. The bearers carried the chair about the distance of an arrow’s flight, and when they were about to turn a corner, they set it down and withdrew. The old women servants following behind had already got out of their own chairs and now hurried forward. Then three or four young lads of seventeen or eighteen, well dressed and groomed, took up the chair again and carried it forward. The old women followed on foot until the chair was set down before a gate with hanging floral ornaments. The lads withdrew, while the old women came forward, raised the chair curtain, and helped Daiyu to alight.

Leaning on the old woman’s hand, Daiyu entered the gate with hanging flowers. On both sides were roofed, winding walkways; in the centre was an open passage. In front stood a large marble screen in a rosewood frame. Passing the screen, she came to a small three-bay hall. Beyond the hall lay the main rear courtyard. The front consisted of five main rooms with carved beams and painted rafters, and on the sides were wing rooms with covered verandas, from which hung cages of vividly coloured parrots, thrushes, and other birds. On the stone steps sat several maids dressed in red and green. As soon as they saw the party approaching, they rushed forward smiling and said, “Just now the old lady was speaking of you—what a happy coincidence that you have come!” Then three or four of them vied in raising the door curtains, and someone inside was heard announcing, “Miss Lin has arrived.”

As Daiyu entered the room, she saw two attendants supporting an old lady with hair like silver coming toward her. Daiyu knew at once that it was her grandmother. She was about to bow and pay her respects, but before she could, her grandmother clasped her to her bosom, crying, “My heart, my flesh!” and burst into loud weeping. Everyone standing there covered their faces and wept; Daiyu herself could not stop crying. After a while, the others gradually composed themselves, and only then did Daiyu make her formal obeisance to her grandmother. This was the Lady Shi, the Dowager of whom Leng Zixing had spoken, the mother of Jia She and Jia Zheng.

The old lady then introduced them to Daiyu one by one: “This is your elder uncle’s wife; this is your second uncle’s wife; this is the wife of your deceased elder cousin Zhu, whom you may call Sister-in-law Zhu.” Daiyu made her bows to each in turn. The old lady then said, “Send for the young ladies. Our faraway guest has just arrived, so they need not go to school today.” The maids acknowledged and two of them went off. In a little while, three nurses and five or six maids arrived, escorting the three young ladies.

The first was of medium height, with a slightly plump figure, cheeks like fresh lychee, a nose as creamy as goose fat, gentle and quiet in manner—most pleasing at first sight. The second had sloping shoulders, a slender waist, a tall and graceful build, an oval face with fine eyebrows and sparkling eyes full of life and intelligence, an air of elegance and refinement that made one forget all vulgarity. The third was still young and small of stature. In their hair ornaments, skirts, and jackets, the three sisters were dressed exactly alike.

Daiyu quickly rose and came forward to greet them, and after they had all acknowledged each other, they took their seats. The maids poured tea. Their conversation could not go beyond how Daiyu’s mother had fallen ill, what physicians had been called, what medicines had been prescribed, and the arrangements for the funeral and mourning. This inevitably stirred the old lady’s grief anew, and she said, “Of all my children, the one I treasured most was your mother. Now she has departed before me, without a chance to see her face even one last time. Seeing you today, how can I not be heartbroken!”
```
