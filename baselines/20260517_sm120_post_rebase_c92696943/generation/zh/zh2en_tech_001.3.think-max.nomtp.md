# Generation Transcript

- Case: `zh2en_tech_001`
- Language group: `zh`
- Workload: `translation`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 148.6657
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 1112, "total_tokens": 15723, "completion_tokens": 14611, "prompt_tokens_details": null}`
- Prompt tokens: 1112
- Completion tokens: 14611
- Total tokens: 15723

## Prompt

```markdown
请将下面的繁体中文古代技术文本翻译成英文。目标不是逐字古雅，而是让现代英语读者理解造纸流程。要求：忠实保留工序、材料、时间和因果关系；必要时可用括号给出极短解释；不要扩写为百科文章。

素材来源：《天工開物》节选：造竹紙
来源链接：https://www.gutenberg.org/ebooks/25273
版权/授权说明：Project Gutenberg lists this eBook as public domain in the USA.

【待处理素材】
凡造竹紙，事出南方，而閩省獨專其盛。當筍生之後，看視山窩深淺，其竹以將生枝葉者為上料。節界芒種，則登山砍伐，截斷五、七尺長，就於本山開塘一口，註水其中漂浸。恐塘水有涸時，則用竹梘通引，不斷瀑流註入。浸至百日之外，加功槌洗，洗去粗殼與青皮（是名殺青），其中竹穰形同苎麻樣。用上好石灰化汁塗漿，入楻桶下煮，火以八日八夜為率。

凡煮竹，下鍋用徑四尺者，鍋上泥與石灰捏弦，高闊如廣中煮鹽牢盆樣，中可裁水十餘石。上蓋楻桶，其圍丈五尺，其徑四尺餘。蓋定受煮，八日已足。歇火一日，揭楻取出竹麻，入清水漂塘之內洗淨。其塘底面、四維皆用木板合縫砌完，以妨泥汙（造粗紙者不須為此）。洗淨，用柴灰漿過，再入釜中，其上按平，平鋪稻草灰寸許。桶內水滾沸，即取出別桶之中，仍以灰汁淋下。倘水冷，燒滾再淋。如是十餘日，自然臭爛。取出入臼受舂（山國皆有水碓），舂至形同泥面，傾入槽內。

凡抄紙槽，上合方半，尺寸闊狹，槽視簾，簾視紙。竹麻已成，槽內清水浸浮其面三寸許，入紙藥水汁於其中（形同桃竹葉，方語無定名），則水幹自成潔白。凡抄紙簾，用刮磨絕細竹絲編成。展捲張開時，下有縱橫架匡。兩手持簾入水，蕩起竹麻，入於簾內。厚薄由人手法，輕蕩則薄，重蕩則厚。竹料浮簾之頃，水從四際淋下槽內，然後覆簾，落紙於板上，疊積千萬張。數滿，則上以板壓，俏繩入棍，如榨酒法，使水氣淨盡流幹。然後，以輕細銅鑷逐張揭起、焙乾。凡焙紙，先以土磚砌成夾巷，下以磚蓋巷地面，數塊以往，即空一磚。火薪從頭穴燒發，火氣從磚隙透巷，外磚盡熱。濕紙逐張貼上焙乾，揭起成帙。

近世闊幅者，名大四連，一時書文貴重。其廢紙，洗去朱墨污穢，浸爛，入槽再造，全省從前煮浸之力，依然成紙，耗亦不多。南方竹賤之國，不以為然。北方即寸條片角在地，隨手拾取再造，名曰還魂紙。竹與皮，精與粗，皆同之也。若火紙、糙紙，斬竹煮麻，灰漿水淋，皆同前法，唯脫簾之後，不用烘焙，壓水去濕，日曬成幹而已。

盛唐時，鬼神事繁，以紙錢代焚帛（北方用切條，名曰板錢），故造此者，名曰火紙。荊楚近俗，有一焚侈至千斤者。此紙十七供冥燒，十三供日用。其最粗而厚者，名曰包裹紙，則竹麻和宿田晚稻稿所為也。若鉛山諸邑所造柬紙，則全用細竹料厚質蕩成，以射重價。最上者曰官柬。富貴之家，通刺用之，其紙敦厚而無筋膜；染紅為吉柬，則先以白礬水染過，後上紅花汁雲。

造皮紙
```

## Reasoning Content

```text
Thinking. 1.  **Analyze the Request:**
    *   **Task:** Translate a specific traditional Chinese technical text (on bamboo papermaking from *Tiangong Kaiwu*) into English.
    *   **Target Audience:** Modern English readers who want to understand the papermaking process.
    *   **Style/Constraint 1:** Not literally archaic word-for-word ("不是逐字古雅"). Focus on clarity.
    *   **Style/Constraint 2:** Faithfully preserve order, materials, time, and cause/effect ("忠實保留工序、材料、時間和因果關係").
    *   **Style/Constraint 3:** Use very short parenthetical explanations if necessary.
    *   **Style/Constraint 4:** Do NOT expand into an encyclopedia article (不要擴寫為百科文章).
    *   **Source:** *Tiangong Kaiwu* excerpt, Project Gutenberg (public domain).
    *   **Pre-fed text:** "造皮紙" (Making Bark Paper). Wait, the prompt text is about "造竹紙". The user gave me the text. Wait, the text ends in the middle of the "造皮紙" section? No, the provided text is specifically titled "造竹紙" (Bamboo Papermaking) in the prompt, but the text *itself* ends with "造皮紙". Let me check the actual excerpt provided.

    Let me carefully re-read the provided text.
    "凡造竹紙..." -> This is the main text.
    "造皮紙" -> This is a heading/section mentioned at the very end of the provided text. Should I translate this final heading as well? Yes, "造皮紙" is technically part of the provided material, but the main body of the text is "造竹紙". The prompt says "素材來源：《天工開物》節選：造竹紙". I will translate the entire provided block of text faithfully, including "造皮紙" as the final part, but treat it as a title/subheading. Actually, the text clearly describes bamboo papermaking for the vast majority. The last line says "造皮紙" which is just the title of the next section in the source text. The user might not want me to expand on it. The prompt says "请将下面的繁体中文古代技术文本翻译成英文". The text provided *is* the text. I will translate the text as given.

    Let's analyze the given text fragment by fragment.

    **Core Translation Strategy:**
    *   Modern English, clear technical steps.
    *   Keep the specific tools (1 尺 = ~0.33 meters? I'll just Romanize or describe. But I need to be careful with measures. I can use approximations or keep the Chinese units and let the reader infer. "Five to seven chi long" -> a chi is a foot. 1尺 = 33.3cm. We can use "five to seven feet".
    *   Special terms: "殺青" (killing the green / removing the green skin). "形同苎麻樣" (like ramie fibers).
    *   "抄紙簾" (paper mold / screen).
    *   "焙乾" (drying over a heated wall / baking dry).
    *   "還魂紙" (recycled paper / "returned soul paper").
    *   "火紙" (funeral paper / touch paper / spirit paper).
    *   "吉柬" (festive / lucky greeting cards).

    **Detailed translation prompts:**
    1. "凡造竹紙，事出南方，而閩省獨專其盛。" -> Bamboo papermaking originated in the south, and Fujian province is particularly renowned for it.
    2. "當筍生之後，看視山窩深淺，其竹以將生枝葉者為上料。" -> After the bamboo shoots grow, inspect the bamboo groves. The best material is bamboo that is about to grow branches and leaves.
    3. "節界芒種，則登山砍伐，截斷五、七尺長，就於本山開塘一口，註水其中漂浸。" -> Around the Grain in Ear (Mangzhong) solar term, bamboo is cut down on the mountain. It is cut into lengths of five to seven chi. A pond is dug right on the mountain and filled with water to soak the bamboo.
    4. "恐塘水有涸時，則用竹梘通引，不斷瀑流註入。" -> Lest the pond water dry up, bamboo pipes are used to continuously channel a waterfall into it.
    5. "浸至百日之外，加功槌洗，洗去粗殼與青皮（是名殺青），其中竹穰形同苎麻樣。" -> After soaking for over a hundred days, the bamboo is taken out and pounded and washed to remove the outer rind and green skin (this process is called "Shiqing" / killing the green). The inner pulp looks like ramie fibers.
    6. "用上好石灰化汁塗漿，入楻桶下煮，火以八日八夜為率。" -> A high-quality lime solution is made into a slurry and used to coat and mix with the fibers. This is placed in a wooden vat (Huangtong) and boiled over a fire for eight days and eight nights.
    7. "凡煮竹，下鍋用徑四尺者，鍋上泥與石灰捏弦，高闊如廣中煮鹽牢盆樣，中可裁水十餘石。" -> The cauldron used for boiling has a diameter of four chi. A ridge of mud and lime is plastered around its rim, making it similar in height and breadth to the salt pans of Guangdong, capable of holding over ten dan of water.
    8. "上蓋楻桶，其圍丈五尺，其徑四尺餘。蓋定受煮，八日已足。" -> A large wooden vat (Huangtong) covers the cauldron, with a circumference of one zhang and five chi, and a diameter of over four chi. The lid is sealed, and the bamboo is cooked. Eight days is sufficient.
    9. "歇火一日，揭楻取出竹麻，入清水漂塘之內洗淨。" -> After resting the fire for a day, the vat is opened and the bamboo pulp (Zhuma) is taken out and washed clean in a pond of fresh water.
    10. "其塘底面、四維皆用木板合縫砌完，以妨泥汙（造粗紙者不須為此）。" -> The bottom and sides of this washing pond must be completely lined with tightly joined wooden planks to prevent mud contamination (this is not necessary when making coarse paper).
    11. "洗淨，用柴灰漿過，再入釜中，其上按平，平鋪稻草灰寸許。" -> Once clean, the pulp is mixed with wood ash slurry and put back into another cauldron. It is flattened, and a layer of rice straw ash about an inch thick is spread on top.
    12. "桶內水滾沸，即取出別桶之中，仍以灰汁淋下。倘水冷，燒滾再淋。如是十餘日，自然臭爛。" -> When the water in the vat boils, the pulp is taken out and placed in another vat, and the ash lye is poured over it again. If the lye cools down, it is boiled again before being poured. After repeating this process for over ten days, the bamboo fibers naturally become thoroughly decomposed and rotten.
    13. "取出入臼受舂（山國皆有水碓），舂至形同泥面，傾入槽內。" -> The decomposed material is then put into a mortar and pestle and beaten (mountainous regions generally have water-powered trip-hammers for this). It is beaten until it has the consistency of mud, then poured into a vat (the pulp mixing vat).
    14. "凡抄紙槽，上合方半，尺寸闊狹，槽視簾，簾視紙。" -> The pulp vat is rectangular. Its dimensions depend on the size of the paper mold (the screen), and the mold depends on the size of the paper desired.
    15. "竹麻已成，槽內清水浸浮其面三寸許，入紙藥水汁於其中（形同桃竹葉，方語無定名），則水幹自成潔白。" -> When the bamboo pulp is ready, it is suspended in clear water about three inches deep in the vat. A "paper medicine" liquid is added to the vat (this is an infusion made from a plant like kiwi vine or similar mucilaginous plant; local names vary). This allows the paper to become white and formed as the water drains.
    16. "凡抄紙簾，用刮磨絕細竹絲編成。展捲張開時，下有縱橫架匡。兩手持簾入水，蕩起竹麻，入於簾內。" -> The paper mold (the screen) is woven from extremely thin, polished bamboo strips. When opened and stretched, it is supported by a wooden frame. The vatman holds the mold with both hands, dips it into the vat, and lifts it so that the bamboo fibers are distributed evenly over the screen.
    17. "厚薄由人手法，輕蕩則薄，重蕩則厚。" -> The thickness of the sheet depends on the vatman's skill: a gentle lift forms a thin sheet, a vigorous lift forms a thick sheet.
    18. "竹料浮簾之頃，水從四際淋下槽內，然後覆簾，落紙於板上，疊積千萬張。" -> As the fibers settle on the screen, the water drains out from the sides back into the vat. The mold is then turned over, and the sheet of paper is couched onto a pile of paper on a board. Thousands of sheets are accumulated in this way.
    19. "數滿，則上以板壓，俏繩入棍，如榨酒法，使水氣淨盡流幹。" -> When the pile reaches the desired height, a board is placed on top and pressure is applied by tightening ropes around the pile with sticks (like a wine press), forcing the water out entirely.
    20. "然後，以輕細銅鑷逐張揭起、焙乾。" -> After pressing, the sheets are carefully peeled off one by one with fine copper tweezers and taken to be dried.
    21. "凡焙紙，先以土磚砌成夾巷，下以磚蓋巷地面，數塊以往，即空一磚。" -> The drying chamber is built as a narrow alleyway with brick walls. The floor of the alley is made of bricks, with every few bricks left open (as a fire gap).
    22. "火薪從頭穴燒發，火氣從磚隙透巷，外磚盡熱。濕紙逐張貼上焙乾，揭起成帙。" -> A fire is lit in the firebox at the head of the alley. The heat passes through the gaps and heats the bricks. The damp sheets are pasted onto the hot brick walls. Once dry, they are peeled off and gathered into quires.
    23. "近世闊幅者，名大四連，一時書文貴重。" -> Recently, wide-format paper called "Da Si Lian" (Big Four Link) became highly valued for calligraphy and writing.
    24. "其廢紙，洗去朱墨污穢，浸爛，入槽再造，全省從前煮浸之力，依然成紙，耗亦不多。" -> Waste paper is washed to remove ink stains, soaked until it falls apart, and put back into the vat to be remanufactured. This completely saves the earlier boiling and soaking steps, yet still produces good paper with little fiber loss.
    25. "南方竹賤之國，不以為然。北方即寸條片角在地，隨手拾取再造，名曰還魂紙。" -> In the South where bamboo is cheap, this is not considered worthwhile. In the North, even small scraps and pieces of paper found on the ground are collected and recycled, a product called "Returned Soul Paper" (Huanhun Zhi).
    26. "竹與皮，精與粗，皆同之也。" -> Whether it is bamboo or bark paper, fine or coarse, the principle is the same.
    27. "若火紙、糙紙，斬竹煮麻，灰漿水淋，皆同前法，唯脫簾之後，不用烘焙，壓水去濕，日曬成幹而已。" -> As for the making of Fire Paper and Rough Paper, the steps of cutting bamboo, boiling the fibers, treating with ash and water are the same. The only difference is that after couching, instead of being baked dry, the paper is simply pressed and then dried in the sun.
    28. "盛唐時，鬼神事繁，以紙錢代焚帛（北方用切條，名曰板錢），故造此者，名曰火紙。" -> During the High Tang dynasty, activities related to spirits and ghosts increased, and paper money replaced burnt silk as an offering. (In the North, it is cut into strips called Board Cash). Thus, this paper is called Fire Paper.
    29. "荊楚近俗，有一焚侈至千斤者。此紙十七供冥燒，十三供日用。" -> The customs of the Chu region are lavish, with some people burning up to a thousand catties in a single ceremony. Of this paper, 70% is used for spirit burning, and 30% for daily use.
    30. "其最粗而厚者，名曰包裹紙，則竹麻和宿田晚稻稿所為也。" -> The coarsest and thickest type is called Wrapping Paper. It is made by mixing bamboo pulp with old field late-season rice straw.
    31. "若鉛山諸邑所造柬紙，則全用細竹料厚質蕩成，以射重價。" -> The "Card Paper" (Jian Zhi) made in places like Yanshan County is entirely made from fine bamboo material, formed thickly on the mold, and commands a high price.
    32. "最上者曰官柬。富貴之家，通刺用之，其紙敦厚而無筋膜；染紅為吉柬，則先以白礬水染過，後上紅花汁雲。" -> The finest is "Official Card" (Guan Jian). Rich and noble families use it for calling cards. This paper is thick and strong with no fiber clumps. For festive "Red Cards" (Ji Jian), the paper is first treated with alum water and then dyed with safflower juice.
    33. "造皮紙" -> "Making Bark Paper (Zaopi Zhi)". (This is the heading for the next section, I will just translate it directly).

    Wait, the text in the prompt ends with "造皮紙". Let me look closely. The entire text is an excerpt. The text "造皮紙" is the title of the *next* chapter or a major heading in the text. I will treat it as a section header.

    Let's review the instructions carefully.
    "目标不是逐字古雅，而是让现代英语读者理解造纸流程。要求：忠实保留工序、材料、时间和因果关系；必要时可用括号给出极短解释；不要扩写为百科文章。"

    So, no long explanations like a Wikipedia article. Keep it concise and accurate. Short parentheticals are allowed.

    Let's build the translation step by step, paying close attention to the technical terms and processes.

    "凡造竹紙，事出南方，而閩省獨專其盛。"
    "Bamboo papermaking originated in the south, but it is in Fujian province that this craft is most flourishing and specialized."

    "當筍生之後，看視山窩深淺，其竹以將生枝葉者為上料。"
    "After the bamboo shoots appear, one observes the condition of the groves. The best material comes from bamboo that is about to grow branches and leaves."

    "節界芒種，則登山砍伐，截斷五、七尺長，就於本山開塘一口，註水其中漂浸。"
    "Around the Mangzhong (Grain in Ear) solar term, the bamboo is cut down on the mountain, trimmed to lengths of 5 to 7 chi (approx. 1.7 to 2.3 meters). A pond is dug right there on the mountain, and water is let in to soak the bamboo."

    "恐塘水有涸時，則用竹梘通引，不斷瀑流註入。"
    "To prevent the pond from drying up, bamboo aqueducts are used to channel a continuous flow from a waterfall into it."

    "浸至百日之外，加功槌洗，洗去粗殼與青皮（是名殺青），其中竹穰形同苎麻樣。"
    "After soaking for over a hundred days, the bamboo is pounded and washed with great effort to remove the rough outer skin and green rind (this process is called 'Shāqīng' / killing the green). The inner fibrous pulp now resembles ramie fiber."

    "用上好石灰化汁塗漿，入楻桶下煮，火以八日八夜為率。"
    "A solution made from high-quality slaked lime is mixed with the fibers. This mixture is placed in a large wooden vat (the Huangtong) and boiled, with a standard duration of eight days and eight nights."

    "凡煮竹，下鍋用徑四尺者，鍋上泥與石灰捏弦，高闊如廣中煮鹽牢盆樣，中可裁水十餘石。"
    "For boiling the bamboo, an iron cauldron with a diameter of 4 chi (approx. 1.3m) is used. A rim of mud and lime is built up around the cauldron, making it deep and wide like the salt-boiling pans of Guangdong, capable of holding over 10 bushels of water."

    "上蓋楻桶，其圍丈五尺，其徑四尺餘。蓋定受煮，八日已足。"
    "The large Huangtong vat is placed as a lid over this setup. Its circumference is 1 zhang and 5 chi (approx. 5m), and its diameter is over 4 chi (approx. 1.3m). Once sealed and heated, the eight-day cooking commences."

    "歇火一日，揭楻取出竹麻，入清水漂塘之內洗淨。"
    "The fire is then extinguished for a day. The vat is opened and the bamboo pulp (Zhuma) is taken out and washed clean in a pond of fresh water."

    "其塘底面、四維皆用木板合縫砌完，以妨泥汙（造粗紙者不須為此）。"
    "The bottom and sides of this washing pond are lined with tightly joined wooden planks to prevent contamination from mud. (This step is unnecessary for making coarse paper)."

    "洗淨，用柴灰漿過，再入釜中，其上按平，平鋪稻草灰寸許。"
    "Once washed, the pulp is mixed with wood-ash slurry and placed back into a cauldron. It is leveled flat, and a uniform layer of rice-straw ash, about an inch thick, is spread over it."

    "桶內水滾沸，即取出別桶之中，仍以灰汁淋下。倘水冷，燒滾再淋。如是十餘日，自然臭爛。"
    "When the water in the cauldron boils, the pulp is taken out and placed in another container. The hot alkaline filtrate (ash lye) is poured over it again. If the lye becomes cold, it is reboiled before being poured. Repeating this process for over ten days causes the fibers to naturally decompose and disintegrate."

    "取出入臼受舂（山國皆有水碓），舂至形同泥面，傾入槽內。"
    "The decomposed material is then taken out and beaten in a mortar (mountain regions generally have water-powered trip-hammers for this). It is beaten until it has the consistency of mud, then poured into the pulp vat."

    "凡抄紙槽，上合方半，尺寸闊狹，槽視簾，簾視紙。"
    "The pulp vat is rectangular. Its dimensions are determined by the size of the paper mold, and the mold's size is determined by the desired paper size."

    "竹麻已成，槽內清水浸浮其面三寸許，入紙藥水汁於其中（形同桃竹葉，方語無定名），則水幹自成潔白。"
    "When the bamboo pulp is ready, it is suspended in clear water about three inches deep in the vat. A 'paper-making drug' (a mucilaginous plant extract, looking somewhat like Actinidia leaves, whose local names vary) is added to the suspension. This allows the water to drain away, leaving a clean, white sheet of paper."

    "凡抄紙簾，用刮磨絕細竹絲編成。展捲張開時，下有縱橫架匡。兩手持簾入水，蕩起竹麻，入於簾內。"
    "The paper mold (the screen) is woven from extremely thin, polished bamboo strips. When stretched out for use, it rests on a supporting wooden frame. [The vatman] holds the mold with both hands and dips it into the vat, lifting and rocking it so that the bamboo fibers are suspended and settle evenly onto the screen."

    "厚薄由人手法，輕蕩則薄，重蕩則厚。"
    "The thickness of the sheet depends on the vatman's technique: a gentle dipping motion produces thin sheets, while a vigorous dipping motion produces thick sheets."

    "竹料浮簾之頃，水從四際淋下槽內，然後覆簾，落紙於板上，疊積千萬張。"
    "As the bamboo fibers float on the screen, the water drains from the four sides back into the vat. The mold is then turned over, depositing the wet sheet of paper onto a board. Sheets are stacked up, thousands upon thousands."

    "數滿，則上以板壓，俏繩入棍，如榨酒法，使水氣淨盡流幹。"
    "Once the stack has reached the desired height, a board is placed on top, and pressure is applied by tightening ropes threaded through sticks (like a wine press), squeezing all the water out of the stack."

    "然後，以輕細銅鑷逐張揭起、焙乾。"
    "After pressing, the sheets are carefully peeled apart one by one using fine and slender copper tweezers, and they are taken to be dried."

    "凡焙紙，先以土磚砌成夾巷，下以磚蓋巷地面，數塊以往，即空一磚。"
    "The paper drying room is built as a narrow alleyway of brick walls. The floor of the alley is paved with bricks; every few bricks are left out to create gaps."

    "火薪從頭穴燒發，火氣從磚隙透巷，外磚盡熱。濕紙逐張貼上焙乾，揭起成帙。"
    "A fire is lit in the firebox at the head of the alley. The hot air and smoke pass through the gaps and heat the main wall of the alley. The damp paper sheets are pasted onto this heated wall one by one to dry. Once dry, they are peeled off and gathered into quires."

    "近世闊幅者，名大四連，一時書文貴重。"
    "In recent times, wide-format paper called 'Da Si Lian' (Big Four Sheet Connection) has become highly valued for calligraphy and important documents."

    "其廢紙，洗去朱墨污穢，浸爛，入槽再造，全省從前煮浸之力，依然成紙，耗亦不多。"
    "Waste paper is washed to remove red ink and stains, soaked until disintegrated, and put back into the vat to be made anew. This completely saves the earlier processes of boiling and soaking, yet still produces paper with little loss of material."

    "南方竹賤之國，不以為然。北方即寸條片角在地，隨手拾取再造，名曰還魂紙。"
    "In the southern regions where bamboo is cheap, this recycling method is not practiced. In the North, however, even small scraps of paper dropped on the ground are picked up and recycled. This recycled paper is called 'Huanhun Zhi' (Returned-Soul Paper)."

    "竹與皮，精與粗，皆同之也。"
    "Whether it is bamboo or bark paper (leather paper), fine or coarse, the general principles of this recycling are the same."

    "若火紙、糙紙，斬竹煮麻，灰漿水淋，皆同前法，唯脫簾之後，不用烘焙，壓水去濕，日曬成幹而已。"
    "As for Fire Paper and Rough Paper, the steps of cutting the bamboo, boiling the fibers, and treating them with ash lye and water washing are identical to the methods described above. The only difference is that after couching, instead of being baked dry, the paper is merely pressed to remove water and then dried in the sun."

    "盛唐時，鬼神事繁，以紙錢代焚帛（北方用切條，名曰板錢），故造此者，名曰火紙。"
    "During the height of the Tang dynasty, due to the increased prevalence of spiritual and funerary rites, paper money replaced burnt silk offerings. (In the North, it is cut into strips called 'Board Cash'). Therefore, the paper made for this purpose is called 'Fire Paper'."

    "荊楚近俗，有一焚侈至千斤者。此紙十七供冥燒，十三供日用。"
    "In the modern customs of the Jing-Chu region, some particularly lavish burnings consume up to a thousand catties of paper. 70% of this paper is used for spirit burning, and 30% is used for everyday practical purposes."

    "其最粗而厚者，名曰包裹紙，則竹麻和宿田晚稻稿所為也。"
    "The coarsest and thickest type of this is called Wrapping Paper. It is made by mixing bamboo pulp with the stalks of late-season rice from old fields."

    "若鉛山諸邑所造柬紙，則全用細竹料厚質蕩成，以射重價。"
    "As for the Fine Letter Paper (Jianzhi) made in places like Yanshan county, it is formed thickly on the mold using entirely fine bamboo material, with the aim of fetching a high price."

    "最上者曰官柬。富貴之家，通刺用之，其紙敦厚而無筋膜；染紅為吉柬，則先以白礬水染過，後上紅花汁雲。"
    "The top-grade kind is called Official Card Paper. Wealthy and noble families use it for name cards. This paper is thick and sturdy, with no fiber clumps or coarse strands in it. To dye it for festive Red Cards, it is first treated with an alum solution, and then colored with a solution of safflower."

    "造皮紙"
    "Making Bark Paper (Zaopi Zhi)"

    Let's refine the style.
    The user wants "忠实保留工序、材料、时间和因果关系". This is very strict.
    I need to avoid making it sound like a Wikipedia article summarizing the process. For instance, I shouldn't say "The *Tiangong Kaiwu* describes...". Just describe the process itself.

    Let's check the specific terms:
    "楻桶" -> Vat. Huangtong.
    "抄紙簾" -> Paper mold / screen.
    "紙藥水汁" -> Paper-making drug / mucilaginous plant extract.
    "殺青" -> Killing the green.
    "竹麻" -> Bamboo pulp / bamboo fibers.
    "還魂紙" -> Recycled paper / returned-soul paper.
    "火紙" -> Fire paper / spirit paper.

    Let's review the first line.
    "凡造竹紙，事出南方，而閩省獨專其盛。"
    "Making Bamboo Paper: The industry originated in southern China, but Fujian province is particularly famous for its thriving and specialized production."

    "當筍生之後，看視山窩深淺，其竹以將生枝葉者為上料。"
    "After the bamboo shoots sprout, the bamboo groves in the mountain valleys are inspected. The best material is bamboo which is about to branch out and grow leaves."

    "節界芒種，則登山砍伐，截斷五、七尺長，就於本山開塘一口，註水其中漂浸。"
    "Around the Mangzhong (Grain in Ear) solar term (early June), the bamboo is cut down, trimmed into lengths of five to seven chi (roughly 1.7 to 2.3 meters). A pond is dug right there on the mountain, filled with water, and the bamboo is steeped in it."

    "恐塘水有涸時，則用竹梘通引，不斷瀑流註入。"
    "To prevent the pond from drying up, a bamboo aqueduct is used to pipe a continuous stream of falling water into it."

    "浸至百日之外，加功槌洗，洗去粗殼與青皮（是名殺青），其中竹穰形同苎麻樣。"
    "After soaking for over a hundred days, the bamboo is vigorously pounded and washed to remove the outer green skin and rind (this step is called 'Shiqing', or 'killing the green'). The inner fibrous pulp that remains looks like ramie fibers."

    "用上好石灰化汁塗漿，入楻桶下煮，火以八日八夜為率。"
    "A good quality lime is slaked into a milky liquid and used to coat the pulp. The mixture is put into a large wooden vat (Huangtong) and boiled for eight days and eight nights as the standard practice."

    "凡煮竹，下鍋用徑四尺者，鍋上泥與石灰捏弦，高闊如廣中煮鹽牢盆樣，中可裁水十餘石。"
    "For boiling the bamboo, the cauldron used has a diameter of four chi (approx. 1.3m). A rim of mud mixed with lime is built around the cauldron's edge, making it tall and wide, similar to the salt-boiling basins of Guangdong. It can hold over ten dan (approx. 1000 liters) of water."

    "上蓋楻桶，其圍丈五尺，其徑四尺餘。蓋定受煮，八日已足。"
    "The Huangtong vat is placed like a cover over this. It has a circumference of one zhang and five chi (approx. 5m), and a diameter of over four chi (approx. 1.3m). The lid is sealed tight, and the cooking proceeds. Eight days is sufficient."

    "歇火一日，揭楻取出竹麻，入清水漂塘之內洗淨。"
    "After the fire is let to rest for a day, the vat is opened, and the bamboo pulp (Zhuma) is taken out and cleaned in a reservoir of fresh water."

    "其塘底面、四維皆用木板合縫砌完，以妨泥汙（造粗紙者不須為此）。"
    "The bottom and the four sides of this washing reservoir are lined with tightly joined wooden planks to prevent mud from soiling the pulp. (This is not required for making coarse paper.)"

    "洗淨，用柴灰漿過，再入釜中，其上按平，平鋪稻草灰寸許。"
    "Once washed, the pulp is mixed with wood-ash lye and put back into a cauldron. It is pressed flat, and a layer of rice-straw ash about an inch (cun) thick is spread evenly over it."

    "桶內水滾沸，即取出別桶之中，仍以灰汁淋下。倘水冷，燒滾再淋。如是十餘日，自然臭爛。"
    "When the liquid in the vessel boils, the pulp is taken out and placed into another vessel. The hot ash lye is then poured over it again. If the lye becomes cold, it is reboiled before being poured. Repeating this cycle for over ten days causes the fibers to completely decompose and rot."

    "取出入臼受舂（山國皆有水碓），舂至形同泥面，傾入槽內。"
    "The decomposed material is then taken out and beaten in a mortar (mountainous regions generally have water-powered trip-hammers for this). It is beaten until it has the consistency of mud, then poured into the pulp vat."

    "凡抄紙槽，上合方半，尺寸闊狹，槽視簾，簾視紙。"
    "The pulp vat is rectangular. Its dimensions are determined by the size of the paper mold (screen), and the mold's size is determined by the size of the paper desired."

    "竹麻已成，槽內清水浸浮其面三寸許，入紙藥水汁於其中（形同桃竹葉，方語無定名），則水幹自成潔白。"
    "The prepared bamboo pulp is suspended in clear water about three inches (cun) deep in the vat. A 'paper-forming drug' (a mucilaginous liquid made from a plant resembling peach/Actinidia leaves, known by various local names) is added to the suspension. This allows the water to drain away cleanly, leaving a white, formed sheet."

    "凡抄紙簾，用刮磨絕細竹絲編成。展捲張開時，下有縱橫架匡。兩手持簾入水，蕩起竹麻，入於簾內。"
    "The paper mold is woven from incredibly fine, polished bamboo strips. When opened and stretched, it rests on a cross-shaped supporting frame. [The vatman] holds the mold with both hands, dips it into the vat, and rocks it so that the bamboo fibers float up and disperse evenly across the screen."

    "厚薄由人手法，輕蕩則薄，重蕩則厚。"
    "The thickness of the sheet is governed by the vatman's technique: a gentle rocking motion produces thin sheets, while a vigorous motion produces thick ones."

    "竹料浮簾之頃，水從四際淋下槽內，然後覆簾，落紙於板上，疊積千萬張。"
    "As the bamboo fibers float on the screen, the water drains from the four sides back into the vat. The mold is then turned over, depositing the wet paper sheet onto a board. The sheets are stacked up, thousands upon thousands."

    "數滿，則上以板壓，俏繩入棍，如榨酒法，使水氣淨盡流幹。"
    "When the stack reaches the desired quantity, a board is placed on top. Pressure is applied by tightening ropes threaded through sticks (like the method used for pressing wine), forcing all the water to drain out completely."

    "然後，以輕細銅鑷逐張揭起、焙乾。"
    "After pressing, the sheets are carefully lifted one by one using fine, delicate copper tweezers and taken to be dried."

    "凡焙紙，先以土磚砌成夾巷，下以磚蓋巷地面，數塊以往，即空一磚。"
    "The paper drying (baking) room is built as a narrow alleyway of brick. The floor of this alley is covered with bricks, but every few bricks are left out, creating gaps."

    "火薪從頭穴燒發，火氣從磚隙透巷，外磚盡熱。濕紙逐張貼上焙乾，揭起成帙。"
    "A fire is lit in a fire pit at the head of the alley. The heat and flames pass through the gaps in the floor tiles to a secondary chamber and heat the main wall bricks. The damp paper sheets are pasted one by one onto the hot brick wall to dry. Once dry, they are peeled off and gathered into quires (bundles)."

    "近世闊幅者，名大四連，一時書文貴重。"
    "In recent times, a wide-format paper called 'Da Si Lian' (Big Four Sheet Connection) has become highly prized for calligraphy and writing."

    "其廢紙，洗去朱墨污穢，浸爛，入槽再造，全省從前煮浸之力，依然成紙，耗亦不多。"
    "Waste paper is washed to remove vermilion ink and stains, soaked until disintegrated, and returned to the vat to be remade. This process completely saves the previous steps of boiling and soaking, yet still produces paper with little material loss."

    "南方竹賤之國，不以為然。北方即寸條片角在地，隨手拾取再造，名曰還魂紙。"
    "In the southern regions where bamboo is abundant and cheap, this recycling is not practiced. In the North, however, even small scraps and torn corners of paper dropped on the ground are picked up and remade. This is called 'Huanhun Zhi' (Returned-Soul Paper)."

    "竹與皮，精與粗，皆同之也。"
    "The same principle applies whether the paper is made from bamboo or bark (leather paper), fine or coarse grade."

    "若火紙、糙紙，斬竹煮麻，灰漿水淋，皆同前法，唯脫簾之後，不用烘焙，壓水去濕，日曬成幹而已。"
    "Regarding the making of Fire Paper (Spirit Paper) and Rough Paper: the steps of cutting the bamboo, boiling the fibers, treating with ash lye and water washing are all the same as described. The only difference is that after couching, instead of being baked dry, the paper is simply pressed to remove water and then dried in the sun."

    "盛唐時，鬼神事繁，以紙錢代焚帛（北方用切條，名曰板錢），故造此者，名曰火紙。"
    "During the height of the Tang dynasty, due to the increased prevalence of spiritual rites, paper money replaced burnt silk as an offering to the dead (in the North, paper is cut into strips called 'Ban Qian' / Board Cash). Therefore, paper made for this purpose is called 'Fire Paper'."

    "荊楚近俗，有一焚侈至千斤者。此紙十七供冥燒，十三供日用。"
    "In the recent customs of the Jing-Chu area (modern Hubei/Hunan), a single burning ritual can be as extravagant as consuming a thousand catties (approx. 600 kg) of this paper. 70% of this paper goes to ghost burning, and 30% is used for daily purposes."

    "其最粗而厚者，名曰包裹紙，則竹麻和宿田晚稻稿所為也。"
    "The coarsest and thickest type of this paper is called Wrapping Paper. It is made by mixing bamboo pulp with the stalks of late-season rice from old fields."

    "若鉛山諸邑所造柬紙，則全用細竹料厚質蕩成，以射重價。"
    "As for the Fine Note Paper (Jianzhi) made in places like Yanshan county, it is formed thickly on the mold using entirely fine bamboo material, aiming for a high price."

    "最上者曰官柬。富貴之家，通刺用之，其紙敦厚而無筋膜；染紅為吉柬，則先以白礬水染過，後上紅花汁雲。"
    "The top-grade kind is called Official Card Paper (Guan Jian). Wealthy and noble families use it for calling cards. This paper is thick and sturdy, with no fiber lumps or coarse strands in it. To dye it into festive Red Cards (Ji Jian), it is first treated with an alum solution and then colored with a solution of safflower petals."

    "造皮紙"
    "Making Bark Paper (Zaopi Zhi)"

    Let's check if any explanations are needed. The user specifically asked to "必要时可用括号给出极短解释".

    For Chinese units, I converted roughly (e.g., 5-7 chi is ~1.6 to 2.3 meters). I should keep the original measurements as well? The user says to make it understandable. I can put the modern equivalent in parentheses.

    "截斷五、七尺長" -> "cut into lengths of five or seven chi (roughly 1.7 to 2.3 meters)".
    "中可裁水十餘石" -> "capable of holding over ten dan of water (approx. 1000 kg or 1000 liters)".
    "平鋪稻草灰寸許" -> "about an inch (cun) thick".
    "一焚侈至千斤" -> "consuming up to a thousand catties (jin, roughly 600 kg)".

    Let's refine the unit conversions to be accurate and consistent.
    - 1 尺 (chi) = 0.333 m. 5 chi = 1.67 m. 7 chi = 2.33 m.
    - 丈 (zhang) = 10 chi = 3.33 m. 丈五尺 = 15 chi = 5 m.
    - 寸 (cun) = 3.33 cm. "寸許" = about 3 cm.
    - 石 (dan) = volume unit. 1 石 = ~100 liters. 10 石 = ~1000 liters. Also ~60 kg but for water volume 100 liters is fine.
    - 斤 (jin) (catties) = 500g. 千斤 = 500 kg.

    Let's refine the "紙藥水汁" (paper drug) translation. "A mucilaginous plant extract, looking somewhat like Actinidia (kiwi) leaves, known by various local names, is added to the suspension. This regulates the drainage and allows the forming paper to become white and integrated."

    Is "形同桃竹葉" referring to *Actinidia chinensis* (Kiwi / Yang Tao) or *Phyllostachys* (peach bamboo)? 桃竹葉 usually refers to the kiwi vine (猕猴桃/羊桃藤) used as a papermaker's sizing agent. The English translation for this plant extract in papermaking contexts is usually "mucilage from the Actinidia vine" or "kiwi vine mucilage". "形同桃竹葉" translates closely to "resembling the leaves of the peach-bamboo/actinidia". I'll say "resembling Actinidia leaves, known by various local names".

    Let's check the phrase "則水幹自成潔白". "then the water drains away, and the sheet naturally forms into white paper."

    Let's ensure the cause and effect and timing are perfectly clear.

    "凡造竹紙，事出南方，而閩省獨專其盛。"
    "Bamboo papermaking originated in the south of China, but Fujian province is particularly famous for its thriving and specialized production."

    "當筍生之後，看視山窩深淺，其竹以將生枝葉者為上料。"
    "After the bamboo shoots appear, one inspects the groves in the mountain valleys. The best material comes from bamboo that is about to grow branches and leaves."

    "節界芒種，則登山砍伐，截斷五、七尺長，就於本山開塘一口，註水其中漂浸。"
    "Around the Mangzhong (Grain in Ear) solar term (early June), the bamboo is cut down on the mountain, trimmed to lengths of 5 to 7 chi (5 chi ≈ 1.7 m). A pond is dug right there on the mountain, and water is let in to soak the bamboo."

    "恐塘水有涸時，則用竹梘通引，不斷瀑流註入。"
    "To prevent the pond from drying up, a bamboo aqueduct is used to continuously channel a flow from a waterfall into it."

    "浸至百日之外，加功槌洗，洗去粗殼與青皮（是名殺青），其中竹穰形同苎麻樣。"
    "After soaking for over a hundred days, the bamboo is vigorously pounded and washed to remove the rough outer skin and green rind (this process is called 'Shāqīng', or 'killing the green'). The inner white fibrous pulp now looks like ramie fibers."

    "用上好石灰化汁塗漿，入楻桶下煮，火以八日八夜為率。"
    "A high-quality lime solution is made into a slurry and used to coat the fibers. This mixture is placed in a large wooden vat (the Huángtǒng) and boiled for eight days and eight nights as the standard duration."

    "凡煮竹，下鍋用徑四尺者，鍋上泥與石灰捏弦，高闊如廣中煮鹽牢盆樣，中可裁水十餘石。"
    "For boiling the bamboo, an iron cauldron with a diameter of 4 chi (approx. 1.3 m) is used. A rim of mud mixed with lime is built around its top, making it tall and capacious, similar to the salt-boiling pans of Guangdong. It can hold over ten dan (approx. 1000 liters) of water."

    "上蓋楻桶，其圍丈五尺，其徑四尺餘。蓋定受煮，八日已足。"
    "The Huángtǒng vat is placed over this as a lid. It has a circumference of 1 zhàng and 5 chi (approx. 5 m) and a diameter of over 4 chi (approx. 1.3 m). The lid is sealed, and the heating is applied. Eight days is sufficient."

    "歇火一日，揭楻取出竹麻，入清水漂塘之內洗淨。"
    "After allowing the fire to cool for a day, the vat is opened and the bamboo pulp (Zhúmá) is taken out. It is washed clean in a reservoir of fresh water."

    "其塘底面、四維皆用木板合縫砌完，以妨泥汙（造粗紙者不須為此）。"
    "The bottom and the four sides of this washing reservoir are all lined with tightly joined wooden planks to prevent mud from soiling the pulp. (This is not necessary when making coarse paper.)"

    "洗淨，用柴灰漿過，再入釜中，其上按平，平鋪稻草灰寸許。"
    "Once washed, the pulp is mixed with wood-ash lye, put back into a cauldron, pressed flat, and a uniform layer of rice-straw ash about an inch (cun) thick is spread over it."

    "桶內水滾沸，即取出別桶之中，仍以灰汁淋下。倘水冷，燒滾再淋。如是十餘日，自然臭爛。"
    "When the water in the cauldron boils, the pulp is taken out and placed in another bucket, and the hot ash lye is poured over it again. If the lye becomes cold, it is reheated to boiling before being poured. Repeating this cycle for over ten days causes the fibers to naturally decompose and rot thoroughly."

    "取出入臼受舂（山國皆有水碓），舂至形同泥面，傾入槽內。"
    "The decomposed material is then taken out and beaten in a mortar (mountainous regions have water-powered trip-hammers for this). It is beaten until it has the consistency of mud, then poured into the pulp vat."

    "凡抄紙槽，上合方半，尺寸闊狹，槽視簾，簾視紙。"
    "The pulp vat is rectangular in shape. Its width and length are determined by the size of the paper mold (the screen), and the size of the mold is determined by the size of the paper desired."

    "竹麻已成，槽內清水浸浮其面三寸許，入紙藥水汁於其中（形同桃竹葉，方語無定名），則水幹自成潔白。"
    "The prepared bamboo pulp is suspended in clear water about three inches (cun) deep in the vat. A paper-making sizing liquid is added to it (this is a mucilaginous plant extract resembling Actinidia leaves, known by various local names). This allows the water to drain away cleanly, leaving the sheet white and formed."

    "凡抄紙簾，用刮磨絕細竹絲編成。展捲張開時，下有縱橫架匡。兩手持簾入水，蕩起竹麻，入於簾內。"
    "The paper mold is woven from incredibly fine, polished bamboo strips. When stretched out for use, it rests on a supporting wooden frame with horizontal and vertical beams. The vatman holds the mold with both hands, dips it into the vat, and rocks it so that the bamboo fibers are suspended and settle evenly onto the screen."

    "厚薄由人手法，輕蕩則薄，重蕩則厚。"
    "The thickness of the sheet is governed by the vatman's technique: a gentle dipping motion produces thin sheets, while a vigorous dipping motion produces thick sheets."

    "竹料浮簾之頃，水從四際淋下槽內，然後覆簾，落紙於板上，疊積千萬張。"
    "In the moment the bamboo fibers float on the screen, the water drains from the four sides back into the vat. The mold is then turned over, depositing the wet sheet onto a board. Sheets are stacked up, accumulating thousands and tens of thousands."

    "數滿，則上以板壓，俏繩入棍，如榨酒法，使水氣淨盡流幹。"
    "Once the pile reaches the desired height, a board is placed on top. Pressure is applied by tightening ropes threaded through sticks (resembling a wine press technique), forcing all the water to drain out completely."

    "然後，以輕細銅鑷逐張揭起、焙乾。"
    "After this pressing, the sheets are carefully lifted one by one using fine, delicate copper tweezers and taken to be dried."

    "凡焙紙，先以土磚砌成夾巷，下以磚蓋巷地面，數塊以往，即空一磚。"
    "The paper drying (baking) room is built as a narrow alleyway of brick walls. The floor of this alley is paved with bricks, but every few bricks are left out, creating gaps."

    "火薪從頭穴燒發，火氣從磚隙透巷，外磚盡熱。濕紙逐張貼上焙乾，揭起成帙。"
    "A fire is lit in the fire pit at the head of the alley. Hot air and smoke pass through the gaps and thoroughly heat the main wall bricks. The damp paper sheets are pasted one by one onto this hot brick wall until dry. Once dry, they are peeled off and gathered into quires (bundles)."

    "近世闊幅者，名大四連，一時書文貴重。"
    "In recent times, a wide-format paper called 'Da Si Lian' (Big Four Sheet Connection) has become highly prized for calligraphy and important documents."

    "其廢紙，洗去朱墨污穢，浸爛，入槽再造，全省從前煮浸之力，依然成紙，耗亦不多。"
    "Waste paper is washed to remove vermilion ink and other stains, soaked until disintegrated, and put back into the vat to be remanufactured. This process completely saves the previous steps of boiling and soaking, yet still produces paper with little material loss."

    "南方竹賤之國，不以為然。北方即寸條片角在地，隨手拾取再造，名曰還魂紙。"
    "In the southern regions where bamboo is plentiful and cheap, this practice is not considered worthwhile. In the North, however, even small scraps and torn corners of paper dropped on the ground are picked up and remade. This is called 'Huánhún Zhǐ' (Returned-Soul Paper)."

    "竹與皮，精與粗，皆同之也。"
    "The same principle governs this recycling whether the paper is made from bamboo or bark (bast fibers), fine quality or coarse quality."

    "若火紙、糙紙，斬竹煮麻，灰漿水淋，皆同前法，唯脫簾之後，不用烘焙，壓水去濕，日曬成幹而已。"
    "Regarding the making of Fire Paper (Spirit Paper) and Rough Paper: the steps of cutting the bamboo, boiling the fibers, treating with ash lye and water washing are all identical to the methods described above. The only difference is that after the sheets are couched, instead of being baked dry, they are merely pressed to remove water and then dried in the sun."

    "盛唐時，鬼神事繁，以紙錢代焚帛（北方用切條，名曰板錢），故造此者，名曰火紙。"
    "During the height of the Tang dynasty, due to the frequency of rites for spirits and ancestors, paper money replaced the burning of silk cloth as an offering. (In the North, paper is cut into strips called 'Ban Qian' / Board Cash). Therefore, the paper made for this purpose is called 'Fire Paper'."

    "荊楚近俗，有一焚侈至千斤者。此紙十七供冥燒，十三供日用。"
    "In the modern customs of the Jing-Chu region (modern Hubei and Hunan), some burning ceremonies are so lavish they consume up to a thousand catties (500 kg) of this paper. 70% of this paper is used for spirit burning, and 30% is used for daily practical purposes."

    "其最粗而厚者，名曰包裹紙，則竹麻和宿田晚稻稿所為也。"
    "The coarsest and thickest of this kind is called Wrapping Paper. It is made by mixing bamboo pulp with the stalks of late-season rice grown in old fields."

    "若鉛山諸邑所造柬紙，則全用細竹料厚質蕩成，以射重價。"
    "As for the Fine Note Paper (Jianzhi) made in places like Yanshan county, it is formed thickly on the mold using entirely fine bamboo material, aiming for a high price."

    "最上者曰官柬。富貴之家，通刺用之，其紙敦厚而無筋膜；染紅為吉柬，則先以白礬水染過，後上紅花汁雲。"
    "The top-grade kind of this is called 'Official Card' (Guan Jian). Wealthy and noble families use it for visiting cards. This paper is thick and robust, without any fiber clumps or coarse strands in it. To dye it into festive 'Red Cards' (Ji Jian), it is first treated with a solution of alum water and then colored with a solution of safflower juice."

    "造皮紙"
    "Making Bark Paper (Zaopi Zhi)"

    This looks very solid. The language is clear, it respects the order, time, materials, and causality. It uses modern English without being anachronistic. Parentheticals are used minimally and only for clarification (units, local names, specific concepts like "Shiqing"). It does not expand into an encyclopedia article.

    Double check the specific word "造皮紙". This is just the header for the next section in the original text, the user provided it so I will translate it exactly.

    Let's check if "紙藥水汁 (形同桃竹葉，方語無定名)" needs a slightly different explanation. "Actinidia leaves" is a specific identification, but that's widely accepted (it is the mucilage from the kiwi vine / Actindia chinensis / Actinidia arguta or similar, which is indeed 桃竹/羊桃/猕猴桃).

    桃竹 is actually a specific name from the text, not a modern misidentification. 桃竹葉 is the modern Chinese name for the kiwi vine leaves used in papermaking. So "Actinidia" is correct and scientific, using parentheses to add the local context "known by various local names" is completely faithful.

    "凡抄紙簾，用刮磨絕細竹絲編成。展捲張開時，下有縱橫架匡。兩手持簾入水，蕩起竹麻，入於簾內。" -> I translated "paper mold" for 抄紙簾. This is the standard term in paper history.

    仔细检查所有的计量单位转换：
    - 五、七尺長: I wrote "5 to 7 chi (5 chi ≈ 1.7 m)" – the exact is 1.65m, but close enough. Oh, 7 chi is 2.31m. "5 to 7 chi (approx. 1.7 to 2.3 meters)" is better. I will add this.
    - 塘一口: pond.
    - 芒種: Grain in Ear.
    - 竹梘: bamboo aqueduct / flume.
    - 殺青: killing the green.
    - 楻桶: vat / huangtong. (I used Huángtǒng vat).
    - 徑四尺: diameter 4 chi (approx. 1.3 m).
    - 圍丈五尺: circumference 1 zhang 5 chi (approx. 5 m).
    - 十餘石: over ten dan (approx. 1000 liters).
    - 竹麻: bamboo pulp / Zhúmá.
    - 柴灰漿: wood ash slurry/lye.
    - 稻草灰: rice straw ash.
    - 水碓: water-powered trip-hammer.
    - 抄紙槽: pulp vat.
    - 紙藥水汁: paper-making sizing liquid / paper-drug.
    - 抄紙簾: paper mold / screen.
    - 覆簾: turn over the mold / couch the sheet.
    - 烘培 / 焙乾: bake dry / heat dry.
    - 火紙: Fire Paper / Spirit Paper.
    - 板錢: Board Cash.
    - 官柬: Official Card Paper (Guan Jian).
    - 吉柬: Red Card (Ji Jian).

    The logic and flow are perfectly maintained. The translation avoids archaic English while faithfully rendering the technical process.

    Final check on the instruction: "目标不是逐字古雅，而是让现代英语读者理解造纸流程。要求：忠实保留工序、材料、时间和因果关系；必要时可用括号给出极短解释；不要扩写为百科文章。"

    Perfect. I have adhered strictly to the source text without expansion. I have not written a summary or an information article, just a direct translation that places value on clarity for a modern reader.

    Ready to output.
```

## Assistant

```markdown
Here is the English translation of the provided text, focused on clarity for a modern reader while strictly preserving the process, materials, timing, and causality.

---

**Making Bamboo Paper**

Bamboo papermaking originated in the south of China, but Fujian province is particularly famous for its thriving and specialized production. After the bamboo shoots sprout, the groves in the mountain valleys are inspected. The best material is bamboo that is about to grow branches and leaves.

Around the Mangzhong (Grain in Ear) solar term (early June), the bamboo is cut down on the mountain, trimmed to lengths of 5 to 7 chi (approx. 1.7 to 2.3 meters). A pond is dug right there on the mountain, and the bamboo is steeped in the water. To prevent the pond from drying up, a bamboo aqueduct is used to continuously channel a flow from a stream or waterfall into it.

After soaking for over a hundred days, the bamboo is heavily pounded and washed to remove the rough outer rind and green skin (this step is called “Shāqīng” / “killing the green”). The inner white pulp that remains looks like ramie fibers. A high-quality lime solution is made into a slurry and used to coat the pulp. This mixture is then placed in a large wooden vat (a “Huángtǒng”) and boiled over a fire, with a standard duration of eight days and eight nights.

For this boiling, a cauldron with a diameter of 4 chi (approx. 1.3 m) is used. A rim of mud and lime is built up around its edge, making it tall and wide, similar to the salt-boiling pans of Guangdong. It can hold over ten *dan* (approx. 1000 liters) of water. The Huángtǒng vat sits over this like a lid. It has a circumference of 1 *zhang* and 5 *chi* (approx. 5 m) and a diameter of over 4 chi (approx. 1.3 m). The lid is sealed, and the cooking proceeds. Eight days is sufficient.

After letting the fire cool for a day, the vat is opened and the bamboo pulp (Zhúmá) is taken out. It is washed clean in a reservoir of fresh water. The bottom and the four sides of this washing reservoir are lined with tightly joined wooden planks to prevent mud from soiling the pulp. (This is not necessary when making coarse paper.) Once washed, the pulp is mixed with wood-ash lye, put back into a cauldron, pressed flat, and a uniform layer of rice-straw ash about an inch (a *cun*) thick is spread over it.

When the water in the cauldron boils, the pulp is taken out and placed into another container. The hot ash lye is then poured over it again. If the lye becomes cold, it is reboiled before being poured. Repeating this cycle for over ten days causes the fibers to completely decompose and rot. The decomposed material is then taken out and beaten in a mortar (mountainous regions generally have water-powered trip-hammers for this). It is beaten until it has the consistency of mud, then poured into the pulp vat.

The pulp vat is rectangular. Its dimensions are determined by the size of the paper mold (the screen), and the size of the mold is determined by the size of the paper desired. The prepared bamboo pulp is suspended in clear water about three inches (cun) deep in the vat. A paper-forming sizing liquid is added to this suspension (it is a mucilaginous plant extract resembling Actinidia leaves, known by various local names). This allows the water to drain away cleanly, leaving the sheet formed and white.

The paper mold is woven from incredibly fine, polished bamboo strips. When stretched out for use, it rests on a supporting wooden frame. [The vatman] holds the mold with both hands, dips it into the vat, and rocks it so that the bamboo fibers are suspended and settle evenly onto the screen. The thickness of the sheet depends on the vatman’s skill: a gentle dip produces thin sheets, while a vigorous dip produces thick ones. As the fibers float on the screen, the water drains from the four sides back into the vat. The mold is then turned over (couched), depositing the wet sheet onto a board. Sheets are stacked up, accumulating thousands upon thousands.

When the pile reaches the desired height, a board is placed on top. Pressure is applied by tightening ropes threaded through sticks (resembling a wine-press technique), forcing all the water out of the stack. After pressing, the sheets are carefully lifted one by one using fine, delicate copper tweezers and taken to be dried.

The drying (baking) room is built as a narrow alleyway of brick walls. The floor of this alley is paved with bricks, but every few bricks are left out, creating gaps. A fire is lit in a fire pit at the head of the alley. The hot air and flames pass through the gaps and thoroughly heat the main wall bricks. The damp sheets are pasted one by one onto this hot brick wall to dry. Once dry, they are peeled off and gathered into quires (bundles).

In recent times, a wide-format paper called “Dà Sì Lián” (Big Four Sheet Connection) has become highly prized for calligraphy and writing.

Waste paper is washed to remove vermilion ink and other stains, soaked until disintegrated, and put back into the vat to be remanufactured. This process completely saves the earlier steps of boiling and soaking, yet still produces paper with little material loss. In the southern regions where bamboo is abundant and cheap, this practice is not considered worthwhile. In the North, however, even small scraps and torn corners of paper dropped on the ground are picked up and remade. This is called “Huánhún Zhǐ” (Returned-Soul Paper). The same principle applies whether the paper is made from bamboo or bark, fine or coarse.

Regarding the making of Fire Paper (Spirit Paper) and Rough Paper: the steps of cutting the bamboo, boiling the fibers, and treating them with ash lye are all identical to the methods described above. The only difference is that after the sheets are couched, instead of being baked dry, they are simply pressed to remove water and then dried in the sun.

During the height of the Tang dynasty, due to the increased prevalence of rites for spirits, paper money replaced the burning of silk as an offering. (In the North, the paper is cut into strips called “Bǎn Qián” / Board Cash). Therefore, this paper is called “Fire Paper”. In the modern customs of the Jing-Chu region (modern Hubei/Hunan), some burning ceremonies are so lavish they consume up to a thousand catties (500 kg) of this paper. 70% of this paper is used for spirit burning, and 30% is used for daily purposes. The coarsest and thickest of this kind is called Wrapping Paper. It is made by mixing bamboo pulp with the stalks of late-season rice grown in old fields.

As for the Fine Note Paper (Jiǎnzhǐ) made in places like Yanshan county, it is formed thickly on the mold using entirely fine bamboo material, aiming for a high price. The top-grade kind is called Official Card Paper (Guān Jiǎn). Wealthy and noble families use it for visiting (name) cards. This paper is thick and sturdy, with no fiber clumps or coarse strands in it. To dye it into festive Red Cards (Jí Jiǎn), it is first treated with a solution of alum water and then colored with a solution of safflower juice.

**Making Bark Paper**
```
