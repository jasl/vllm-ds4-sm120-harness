# Generation Transcript

- Case: `zh2en_tech_001`
- Language group: `zh`
- Workload: `translation`
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
- Elapsed seconds: 125.816872
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 1112, "total_tokens": 13459, "completion_tokens": 12347, "prompt_tokens_details": null}`
- Prompt tokens: 1112
- Completion tokens: 12347
- Total tokens: 13459

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
    *   **Task:** Translate traditional Chinese technical text on papermaking (from *Tiangong Kaiwu*, "Making Bamboo Paper") into English.
    *   **Goal:** Not archaic, but understandable for a modern English reader.
    *   **Requirements:** Faithfully retain procedures, materials, timing, and causal relationships. Short explanations in parentheses if necessary. Do not expand into encyclopedia articles.
    *   **Source:** Public domain text from Project Gutenberg (specifically the section on bamboo papermaking).

2.  **Analyze the Source Material:**
    *   The text is a step-by-step description of bamboo papermaking in ancient China.
    *   **Key Stages:**
        1.  Raw material selection (bamboo shoots about to branch).
        2.  Cutting and soaking (in mountain ponds, with water diverted via bamboo pipes).
        3.  Beating/washing (removing outer green skin, "killing the green").
        4.  First boiling (with lime in a large pot/huang barrel for 8 days).
        5.  Washing.
        6.  Second treatment (ash water soaking, repeated boiling/showering for 10+ days until rotten).
        7.  Beating (pestle, usually water-powered, until mud-like).
        8.  Pulp vat preparation (adding water and "paper drug").
        9.  Sheet forming (bamboo screen, dipping, shaking, thickness control).
        10. Pressing (stack, plank, lever/winch to remove water).
        11. Drying (heating wall/brick tunnel).
        12. Varieties (Da Si Lian, recycled paper, fire paper, coarse paper, official note paper, leather paper).
    *   **Technical terms to handle carefully:**
        *   殺青 (Killing the green)
        *   楻桶 (Huang barrel / cooking vat)
        *   紙藥水汁 (Paper drug / sizing agent)
        *   抄紙簾 (Paper mold / screen)
        *   焙乾 (Drying over heat)
        *   還魂紙 (Recycled paper / revived soul paper)
        *   火紙 (Fire paper / joss paper)
        *   皮紙 (Leather paper / bark paper)

3.  **Determine Translation Strategy:**
    *   **Tone:** Explanatory, technical, clear. Avoid flowery language. Superstitions/background can be kept (e.g., joss paper for ghosts), but vast historical extrapolations should not be added.
    *   **Structure:** Follow the original text paragraph by paragraph, grouping the steps.
    *   **Parentheses:** Use for clarifying local terms, measurements in modern units, or explaining concepts like "殺青".
    *   **Specific challenges:**
        *   "凡造竹紙..." -> Translation must clearly state the location and material properties.
        *   Measurements (五七尺, 十餘石, 八日八夜, 径四尺, 围丈五尺). Can keep the original and optionally give a rough modern equivalent in parentheses, e.g., "five to seven chi (approx. 1.5–2 m) long", "a pond facing south".
        *   "竹梘" -> Bamboo pipes / aqueducts.
        *   "入楻桶下煮" -> Vat/cooking barrel.
        *   "紙藥水汁" -> "Paper drug" is the literal translation. It is a mucilage/sizing agent (e.g., from the leaves of *Broussonetia papyrifera* or specific local plants like the "peach bamboo leaf" mentioned, often identified as *Hibiscus manihot* or similar mucilaginous plants). "Sizing agent" or "mucilage" is more scientifically accurate, but the text says "形同桃竹葉，方語無定名" (shaped like peach bamboo leaves, local names vary). "Paper drug" or "mucilage" can be used, with a slight nod to the original. "Papermaking glue" or "suspension agent". Let's use "paper drug / mucilage".
        *   "山國皆有水碓" -> Mountain regions all have water-powered trip-hammers.

4.  **Drafting the Translation:**

    **Paragraph 1: Harvesting and Initial Soaking**
    "Bamboo paper is always made in the south of China, but Fujian province is particularly famous for it. After the shoots have grown, the valleys are examined for their depth. The best bamboo is that which is about to put forth branches and leaves. Just before the Mangzhong period (around early June, Grain in Ear), the bamboo is cut down. It is cut into lengths of five to seven *chi* (roughly 1.5 to 2.1 meters). A pond is dug right there on the mountain, and the bamboo is soaked in it. To prevent the pond water from drying up, bamboo pipes are used to channel a continuous flow of water into it. After more than a hundred days of soaking, the bamboo is taken out and beaten to wash off the coarse shell and green skin (this process is called 'killing the green'). The inner fiber layer, which looks like ramie, is left."

    **Paragraph 2: First Cooking**
    "The bamboo fiber is then coated with a paste made from high-quality lime dissolved in water. It is placed in a *huang* (a large cooking vat) and boiled. The fire is maintained for eight days and eight nights."

    **Paragraph 3: Details of the Cooking Vat and Washing**
    "The cooking pot used has a diameter of four *chi* (approx. 1.2 m). Its rim is built up with a mixture of mud and lime, making it high and wide like the salt boiling pans in Guangdong, holding over ten *shi* (approx. 600 kg / liters) of water. The vat (*huang* barrel) covering the pot has a circumference of fifteen *chi* (approx. 4.5 m) and a diameter of four *chi* (approx. 1.2 m). After the vat is sealed, the boiling proceeds. After eight days, the fire is stopped for one day. The vat is then opened, and the bamboo pulp (*zhuma*) is taken out and washed clean in a clear-water pond. The bottom and four sides of this pond are carefully lined with boards tightly joined together to prevent mud from contaminating the pulp (this is not necessary for making coarse paper). After washing, the material is treated with ash water (the ashes of firewood have been used). It is then placed back into a pot. The material is leveled, and a layer of rice straw ash about an inch thick is spread evenly on top. When the water in the pot boils, the liquid is scooped out and poured over the bamboo material in another vat. If the liquid cools, it is reheated and poured again. This process is repeated for ten days or so, until the material naturally rots and disintegrates."

    **Paragraph 4: Beating and Pulp Preparation**
    "The rotten material is then taken out and placed in a mortar to be beaten. (In mountainous regions, water-powered trip-hammers are used.) It is beaten until it becomes a mud-like paste. This paste is then poured into a vat."

    **Paragraph 5: The Vat and Paper Drug**
    "The papermaking vat is square at the top. Its dimensions vary: the vat is sized according to the screen, and the screen is sized according to the desired paper. The bamboo pulp is placed in the vat, and clean water is added until the water stands about three inches above the pulp. Then a 'paper drug' (*zhiyao* / mucilage) is added to the water (the plant used looks like peach bamboo leaves, and its name varies by locality). This ensures the paper will naturally be white and firm when the water drains."

    **Paragraph 6: Sheet Forming**
    "The papermaking screen (*zhi lian*) is made from extremely fine, scraped and polished bamboo strips woven together. It is stretched on a frame with horizontal and vertical supports. The craftsman holds the screen with both hands and dips it into the vat, lifting up the bamboo pulp so that it spreads evenly on the screen. The thickness of the sheet is controlled by the skill of the hand: a gentle shake produces thin paper, a heavier shake produces thick paper. As the bamboo fibers float on the screen, the water drains back into the vat from the four sides. The screen is then turned over, depositing the wet sheet onto a board. Thousands of sheets are stacked up like this."

    **Paragraph 7: Pressing and Drying**
    "When the stack reaches the desired height, a board is placed on top. A rope is tightened around it with a lever (like in wine pressing) to squeeze out all the water. After the water is completely removed, the sheets are separated one by one using fine copper tweezers and dried over heat."

    **Paragraph 8: The Drying Wall (Firing)**
    "For drying the paper, a narrow corridor is built with earth bricks. The floor of the corridor is paved with bricks, with a gap left after every few bricks. A fire is lit in the fireplace at one end of the corridor. The heat and smoke pass through the gaps between the bricks, heating the outer wall bricks. The wet sheets are pasted onto this hot wall one by one to dry. When dry, they are peeled off and gathered into quires."

    **Paragraph 9: Varieties (Da Si Lian and Recycled Paper)**
    "In modern times, a wide format called 'Da Si Lian' is valued for writing and documents. Waste paper, after washing off the red and black inks, is soaked until it rots and then re-processed in the vat. This saves the entire previous process of boiling and soaking. The resulting paper is not very different, and the material loss is small. In the south, where bamboo is cheap, this recycling is not highly regarded. In the north, every scrap of paper, even an inch or a strip, is picked up from the ground and recycled. This is called 'revived soul paper' (*huanhun zhi*). Whether made from bamboo or bark, fine or coarse, the principle is the same."

    **Paragraph 10: Fire Paper and Coarse Paper**
    "As for fire paper (*huo zhi*) and rough paper (*cao zhi*), the processes of cutting bamboo, cooking the fiber, treating with ash and water are all the same. The only difference is that after being taken off the screen, they are not dried by baking. They are simply pressed to remove water and dried in the sun."

    **Paragraph 11: Use of Fire Paper**
    "During the height of the Tang Dynasty, religious activities (spirit worship) were common. Paper money was burned to replace silk cloth (in the north, cut strips are used, called 'board money'). Therefore, this type of paper is called 'fire paper'. In the modern custom of the Hubei/Hunan region (Jing-Chu), it is not uncommon to burn up to a thousand catties of this paper in a single offering. 70% of this fire paper is used for spirit offerings, and 30% for daily use. The coarsest, thickest type is called 'wrapping paper' (*baoguo zhi*), which is made from bamboo pulp mixed with late-season rice stalks from old fields."

    **Paragraph 12: Fine Note Paper**
    "As for the letter paper (*jian zhi*) made in places like Yanshan, it is entirely made from fine bamboo material, formed with a thick texture, and commands a high price. The best quality is called 'official note paper' (*guan jian*). Wealthy and noble families use it for their visiting cards. The paper is thick and firm, with no coarse fibers. To make red auspicious note paper (*ji jian*), the paper is first stained with an alum solution and then with a juice made from safflower petals."

    **Final Paragraph Snippet:**
    "Making bark paper..." (The instruction says "造皮紙" but the text provided under this heading isn't fully elaborated in the user's prompt beyond the title. Wait, the user only provided the text for 造竹紙. The system prompt includes "造皮纸" only as a trailing unfinished thought. The user said they are providing the material for 造竹紙. I should only translate what was provided. The "造皮纸" is just the end of the section header. The actual content follows... wait, the prompt ends exactly at "造皮纸". Is there more text? The user input ends at: "富貴之家，通刺用之，其紙敦厚而無筋膜；染紅為吉柬，則先以白礬水染過，後上紅花汁雲。\n\n造皮紙".
    Oh, the user provided the *entire* text snippet for Bamboo paper, ending with the header for Bark paper. I will translate the text provided. The text is a continuous excerpt. I'm good.

    Let's review the translation for accuracy and clarity.
    *   "凡造竹紙，事出南方，而閩省獨專其盛。" -> Always made in the south, Fujian province is especially renowned.
    *   "當筍生之後，看視山窩深淺，其竹以將生枝葉者為上料。" -> After bamboo shoots grow, examine the valleys. Best material is bamboo about to sprout branches.
    *   "節界芒種" -> Around the Mangzhong period (Grain in Ear).
    *   "就於本山開塘一口，註水其中漂浸。" -> Dig a pond on the mountain, fill it with water, soak.
    *   "用竹梘通引，不斷瀑流註入。" -> Bamboo pipes channel a continuous waterfall/torrent into it.
    *   "浸至百日之外，加功槌洗，洗去粗殼與青皮（是名殺青），其中竹穰形同苎麻樣。" -> After 100 days, beat and wash to remove outer shell and green skin (killing the green). Inner part looks like ramie.
    *   "用上好石灰化汁塗漿，入楻桶下煮，火以八日八夜為率。" -> Coat with high quality lime solution, boil in a huang vat, 8 days.
    *   "凡煮竹，下鍋用徑四尺者，鍋上泥與石灰捏弦，高闊如廣中煮鹽牢盆樣，中可裁水十餘石。" -> Pot diameter 4 chi (1.2m), rim made of mud/lime, high and wide like salt pans in Guangdong, holds 10+ shi.
    *   "上蓋楻桶，其圍丈五尺，其徑四尺餘。蓋定受煮，八日已足。歇火一日，揭楻取出竹麻，入清水漂塘之內洗淨。其塘底面、四維皆用木板合縫砌完，以妨泥汙（造粗紙者不須為此）" -> Cover with huang vat (circ. 15 chi, di. 4 chi). Boil 8 days. Rest 1 day. Open vat, take out bamboo pulp, wash in clean pond (lined with boards).
    *   "洗淨，用柴灰漿過，再入釜中，其上按平，平鋪稻草灰寸許。桶內水滾沸，即取出別桶之中，仍以灰汁淋下。倘水冷，燒滾再淋。如是十餘日，自然臭爛。取出入臼受舂（山國皆有水碓），舂至形同泥面，傾入槽內。" -> Wash, slurry with wood ashes, put in pot again, level, spread inch of straw ash. When water boils, remove liquid and pour over bamboo in another vat. Reheat and pour if cold. 10+ days, naturally rots. Take out, beat in mortar (water-powered trip hammer), until mud-like. Pour into vat.
    *   Pay attention to the timeline! Soaking (100+ days), First Boil (8 days), Rest (1 day), Washing, Ash Treatment (10+ days). This is explicitly laid out.
    *   "凡抄紙槽，上合方半，尺寸闊狹，槽視簾，簾視紙。竹麻已成，槽內清水浸浮其面三寸許，入紙藥水汁於其中（形同桃竹葉，方語無定名），則水幹自成潔白。" -> The vat is square at the top. Dimensions vary. Pulp ready, clear water 3 inches above. Add 'paper drug' (looks like peach bamboo leaves, local names vary). Water drains white.
    *   "凡抄紙簾，用刮磨絕細竹絲編成。展捲張開時，下有縱橫架匡。兩手持簾入水，蕩起竹麻，入於簾內。厚薄由人手法，輕蕩則薄，重蕩則厚。竹料浮簾之頃，水從四際淋下槽內，然後覆簾，落紙於板上，疊積千萬張。" -> Screen made of very fine polished bamboo strips. Frame support. Dip into vat, shake pulp onto screen. Thickness controlled by shaking technique. Water drains, turn screen over onto board. Stack thousands...
    *   "數滿，則上以板壓，俏繩入棍，如榨酒法，使水氣淨盡流幹。然後，以輕細銅鑷逐張揭起、焙乾。凡焙紙，先以土磚砌成夾巷，下以磚蓋巷地面，數塊以往，即空一磚。火薪從頭穴燒發，火氣從磚隙透巷，外磚盡熱。濕紙逐張貼上焙乾，揭起成帙。" -> Stack pressed with board and lever (like wine press). Water squeezed out. Copper tweezers to lift sheets, dry on heated wall. Brick corridor, fire at one end, heat passes through gaps, outer bricks heat. Paste on, peel off.
    *   "近世闊幅者，名大四連，一時書文貴重。其廢紙，洗去朱墨污穢，浸爛，入槽再造，全省從前煮浸之力，依然成紙，耗亦不多。南方竹賤之國，不以為然。北方即寸條片角在地，隨手拾取再造，名曰還魂紙。竹與皮，精與粗，皆同之也。" -> Modern wide size is Da Si Lian. Waste paper cleaned, soaked, repulped. Saves previous cooking. Southern bamboo cheap areas don't care. North picks up every scrap, called Huanhun Zhi (revived soul paper). Bark and bamboo same.
    *   "若火紙、糙紙，斬竹煮麻，灰漿水淋，皆同前法，唯脫簾之後，不用烘焙，壓水去濕，日曬成幹而已。" -> Fire paper and coarse paper: same process, but no baking, just sun-dried after pressing.
    *   "盛唐時，鬼神事繁，以紙錢代焚帛（北方用切條，名曰板錢），故造此者，名曰火紙。荊楚近俗，有一焚侈至千斤者。此紙十七供冥燒，十三供日用。其最粗而厚者，名曰包裹紙，則竹麻和宿田晚稻稿所為也。" -> High Tang, paper money replaces silk for ghosts. Fire paper. Jing-Chu area burns 1000 catties. 70% spirit burning, 30% daily use. Coarsest thickest is wrapping paper, made of bamboo pulp and old field late rice stalks.
    *   "若鉛山諸邑所造柬紙，則全用細竹料厚質蕩成，以射重價。最上者曰官柬。富貴之家，通刺用之，其紙敦厚而無筋膜；染紅為吉柬，則先以白礬水染過，後上紅花汁雲。" -> Yanshan letter paper, fine bamboo, thick texture, high price. Best is Guan Jian (official note paper). Rich use for visiting cards, thick no coarse fibers. Red auspicious paper -> alum solution first, then safflower juice.
    *   "造皮紙" -> "Making Bark Paper..." (The text ends here. I will just put the title as a heading or final line, as the passage ends. Actually, the prompt says: "素材来源：《天工開物》节选：造竹紙" and the text is the *complete* provided text. The translation should just reflect the text given. The single line "造皮紙" at the end seems like the start of the next section title. Should I translate it? Yes, "Making bark paper." It's perfectly fine to just state it as the logical conclusion of the passage, or simply a standalone line. The user wants the translation of the material.)

5.  **Refining the Language:**
    *   "事出南方" -> "Paper is always made in the south."
    *   "獨專其盛" -> "is particularly famous/skilled in this."
    *   "竹將生枝葉者為上料" -> "Bamboo which is about to put forth branches is considered the best material."
    *   "節界芒種" -> "At the time of the Mangzhong solar term (around June 5-7, 'Grain in Ear')."
    *   "用竹梘通引，不斷瀑流註入" -> "using bamboo pipes to continuously channel a fresh stream into it." (瀑流 suggests a strong flow/waterfall).
    *   "加功槌洗" -> "intensively beat and wash".
    *   "（是名殺青）" -> "(this is called *shaqing*, 'killing the green')". Short explanation.
    *   "楻桶" -> "Huang cooking barrel / vat"
    *   "廣中煮鹽牢盆" -> "the large salt-boiling pans in Guangdong".
    *   "中可裁水十餘石" -> "can hold over ten *shi* of water (approx. 1000 liters)." (1 石 ≈ 100 liters, but Song/Ming *shi* is a unit of weight/capacity. I'll keep the original and give a rough modern equivalent).
    *   "歇火一日" -> "Rest the fire for one day."
    *   "竹麻" -> "Zhu ma" can be literally translated as "bamboo pulp" / "bamboo fiber".
    *   "柴灰" -> "Wood ashes / plant ashes"
    *   "入臼受舂（山國皆有水碓）" -> "In mountainous regions, water-powered trip-hammers (*shuidui*) are used." -> "put in a mortar and beaten (mountain regions all have water-powered trip hammers)."
    *   "舂至形同泥面" -> "pounded until it resembles mud/clay".
    *   "槽內清水浸浮其面三寸許" -> "clear water stands about three *cun* above its surface".
    *   "紙藥水汁" -> "Paper drug liquid / mucilage".
    *   "形同桃竹葉，方語無定名" -> "The plant used looks like peach bamboo leaves, its name varies by locality."
    *   "厚薄由人手法，輕蕩則薄，重蕩則厚。" -> "Thickness depends on the skill of the hand: a gentle shake makes thin paper, a vigorous shake makes thick paper."
    *   "覆簾，落紙於板上" -> "The screen is turned over, depositing the sheet onto a board."
    *   "俏繩入棍，如榨酒法" -> "A lever is inserted into the ropes (a windlass/tightening stick) to press it, like pressing wine."
    *   "以輕細銅鑷逐張揭起" -> "using fine copper tweezers, lift the sheets one by one."
    *   "烘乾" -> "Dried over heat / baked dry".
    *   "凡焙紙，先以土磚砌成夾巷，下以磚蓋巷地面，數塊以往，即空一磚。火薪從頭穴燒發，火氣從磚隙透巷，外磚盡熱。" -> "For drying paper, a narrow corridor is built with earthen bricks. The floor of the corridor is paved with bricks, with a gap left after every few bricks. The fire is kindled at an opening at one end. The heat and flames pass through the brick gaps into the corridor, heating the outer walls thoroughly."
    *   "濕紙逐張貼上焙乾，揭起成帙。" -> "Wet sheets are pasted one by one on the hot wall to dry. When dry, they are lifted off and gathered into a book/quire."
    *   "大四連" -> "Da Si Lian" (large four-fold, probably a name). I will keep the pinyin.
    *   "書文貴重" -> "Valued for writing and documents."
    *   "全省從前煮浸之力" -> "saves entirely the previous labor of cooking and soaking."
    *   "還魂紙" -> "Revived soul paper". This is a good technical/cultural term.
    *   "十七供冥燒，十三供日用" -> "seventy percent for spirit burning, thirty percent for daily use."
    *   "宿田晚稻稿" -> "stalks of late rice from old fields".
    *   "鉛山諸邑" -> "the counties around Yanshan (in Jiangxi province, a famous papermaking area)."
    *   "厚質蕩成" -> "formed with a thick texture."
    *   "以射重價" -> "to seek/command a high price."
    *   "官柬" -> "Official note paper" / *Guan Jian*.
    *   "通刺用之" -> "Used for visiting cards / name cards."
    *   "先以白礬水染過，後上紅花汁" -> "First stained with an alum solution, then with juice of safflower (*Carthamus tinctorius*)."

6.  **Reviewing the entire translation against the requirements:**
    *   "目标不是逐字古雅，而是让现代英语读者理解造纸流程。" -> YES. Explanation over archaic adherence. Keep *pinyin* for specific native terms but explain them.
    *   "要求：忠实保留工序、材料、时间和因果关系" -> YES. The entire logic of the sequence is preserved.
    *   "必要时可用括号给出极短解释" -> YES. Done for 殺青, 芒種, 紙藥, 楻桶, 大四連, 還魂紙.
    *   "不要扩写为百科文章" -> YES. Avoided adding historical context beyond what is in the text. The text itself has context (Tang Dynasty burning money, etc.) which is faithfully translated.
    *   "版权/授权说明：Project Gutenberg lists this eBook as public domain in the USA." -> Noted. Not needed in the output unless requested, but it shows the user is aware. Wait, the prompt says "请将下面的繁体中文古代技术文本翻译成英文... 目标不是...". I don't need to reproduce the copyright info in the output unless it is part of the translation. The user provided it as context.

    Let's refine some phrasing further.
    *   "而閩省獨專其盛" -> "Fujian province is especially renowned for it."
    *   "看視山窩深淺" -> "The depth of the mountain valleys is examined." (This might be related to ensuring enough water for the ponds? Or just selecting the right bamboo groves. I'll keep it literally but contextualized). "Examine the depths of the mountain hollows/valleys."
    *   "其竹以將生枝葉者為上料" -> "The best material is bamboo that is about to grow branches and leaves."
    *   "節界芒種" -> "At the boundary of the Mangzhong solar term (around June 5–6)."
    *   "山窩深淺" could be "the conditions of the mountain valleys".
    *   "砍伐" -> "cut down / harvested"
    *   "截斷五、七尺長" -> "Cut into lengths of 5 to 7 *chi*"
    *   "就於本山開塘一口，註水其中漂浸。" -> "Dig a pond right on the mountain, fill it with water, and soak the bamboo."
    *   "恐塘水有涸時，則用竹梘通引，不斷瀑流註入。" -> "Fearing the pond water might dry up, they channel a continuous stream of water into it using bamboo pipes/aqueducts."
    *   "侵至百日之外" -> "Soaked for over a hundred days."
    *   "加功槌洗" -> "Then it is thoroughly beaten and washed."
    *   "洗去粗殼與青皮（是名殺青），其中竹穰形同苎麻樣。" -> "The coarse outer husk and the green skin are washed off (this is called *shaqing* - killing the green). The inner bamboo fiber left behind looks like ramie."
    *   "用上好石灰化汁塗漿" -> "It is then coated with a solution of high-quality lime."
    *   "入楻桶下煮" -> "Placed in a *huang* barrel and boiled."
    *   "火以八日八夜為率。" -> "The fire is maintained for eight days and eight nights."
    *   *Check the measurements.*
        "鍋上泥與石灰捏弦，高闊如廣中煮鹽牢盆樣" -> "The rim of the pot is built up with mud and lime, making it high and wide, similar to the salt-boiling pans in Guangdong."
        "中可裁水十餘石" -> "It can hold over ten *shi* of water." (approx. 1000 liters).
        "上蓋楻桶，其圍丈五尺，其徑四尺餘。" -> "The *huang* barrel covering it has a circumference of 15 *chi* and a diameter of over 4 *chi*."
    *   "蓋定受煮，八日已足。" -> "It is covered and boiled. After eight days, it is done."
    *   "歇火一日，揭楻取出竹麻，入清水漂塘之內洗淨。" -> "The fire is stopped for one day. The vat is opened, the bamboo pulp (*zhuma*) is taken out and washed clean in a clear-water pond."
    *   "其塘底面、四維皆用木板合縫砌完，以妨泥汙（造粗紙者不須為此）。" -> "The bottom and four sides of the pond are tightly lined with boards, joined at the seams, to prevent mud from contaminating the pulp. (This is not necessary for making coarse paper.)"
    *   "洗淨，用柴灰漿過" -> "After washing, the pulp is treated/coated with wood ash (or plant ash)."
    *   "再入釜中，其上按平，平鋪稻草灰寸許。" -> "It is placed back in the pot. The surface is leveled, and a flat layer of rice-straw ash, about an inch thick, is spread over it."
    *   "桶內水滾沸，即取出別桶之中，仍以灰汁淋下。" -> "When the water in the pot comes to a rolling boil, it is ladled out and poured over the pulp in another vat, allowing the ash-laden liquid to drain through."
    *   "倘水冷，燒滾再淋。" -> "If the liquid cools, it is reheated and poured again."
    *   "如是十餘日，自然臭爛。" -> "This process is repeated for over ten days, until the bamboo naturally rots and becomes soft."
    *   "取出入臼受舂（山國皆有水碓），舂至形同泥面，傾入槽內。" -> "It is then taken out and put into a mortar for pounding. (Mountainous regions use water-powered trip-hammers.) It is pounded until it becomes a mud-like paste. This paste is then poured into the vat."
    *   "凡抄紙槽，上合方半，尺寸闊狹，槽視簾，簾視紙。" -> "The papermaking vat is square at the top. Its dimensions vary depending on the screen, and the screen's size depends on the desired paper format."
    *   "竹麻已成，槽內清水浸浮其面三寸許，入紙藥水汁於其中（形同桃竹葉，方語無定名），則水幹自成潔白。" -> "The pulp is ready. Clean water is added to the vat until it stands about three *cun* (approx. 10 cm) above the surface. Then a 'paper drug' (*zhiyao*) liquid is added. The plant used looks like peach bamboo leaves, and its name varies by locality. This makes the pulp form white sheets naturally when the water drains."
    *   "凡抄紙簾，用刮磨絕細竹絲編成。" -> "The papermaking screen is woven from extremely fine, polished bamboo strips."
    *   "展捲張開時，下有縱橫架匡。" -> "It is stretched on a frame with horizontal and vertical supports when spread open."
    *   "兩手持簾入水，蕩起竹麻，入於簾內。" -> "The worker holds the screen with both hands, dips it into the water, and shakes it so that the bamboo pulp spreads evenly across the screen."
    *   "厚薄由人手法，輕蕩則薄，重蕩則厚。" -> "The thickness of the paper depends on the worker's technique: a gentle shake yields thin paper, a heavy shake yields thick paper."
    *   "竹料浮簾之頃，水從四際淋下槽內" -> "As the bamboo fibers float on the screen, the water drains back into the vat from the four sides."
    *   "然後覆簾，落紙於板上，疊積千萬張。" -> "Then the screen is turned over, depositing the wet sheet onto a board. The sheets are stacked up, thousands of them."
    *   "數滿，則上以板壓，俏繩入棍，如榨酒法，使水氣淨盡流幹。" -> "When the stack is high enough, a board is placed on top. A rope is tightened around it with a lever (like pressing wine) to squeeze out all the water completely."
    *   "然後，以輕細銅鑷逐張揭起、焙乾。" -> "Afterwards, the sheets are lifted one by one with fine copper tweezers and dried over heat (baked)."
    *   "凡焙紙，先以土磚砌成夾巷，下以磚蓋巷地面，數塊以往，即空一磚。火薪從頭穴燒發，火氣從磚隙透巷，外磚盡熱。" -> "For drying the paper, a narrow corridor is built with earth bricks. The floor of the corridor is paved with bricks, with a gap left after every few bricks. A fire is kindled at an opening at the head of the corridor. The heat and smoke pass through the brick gaps into the corridor, heating the outer bricks thoroughly."
    *   "濕紙逐張貼上焙乾，揭起成帙。" -> "The wet sheets are pasted one by one onto this hot wall to dry. When dry, they are peeled off and gathered into a book (*zhi* - quire/volume)."
    *   "近世闊幅者，名大四連，一時書文貴重。" -> "In recent times, a wide-format paper called 'Da Si Lian' has become highly valued for writing and documents."
    *   "其廢紙，洗去朱墨污穢，浸爛，入槽再造，全省從前煮浸之力，依然成紙，耗亦不多。" -> "Waste paper, after washing off the red (cinnabar) and black ink stains, is soaked until it rots and then repulped in the vat. This saves the entire effort of the previous boiling and soaking. It is still made into paper, and the material loss is small."
    *   "南方竹賤之國，不以為然。北方即寸條片角在地，隨手拾取再造，名曰還魂紙。" -> "In the south, where bamboo is cheap, this recycling is not widely practiced. In the north, every bit of paper on the ground, even an inch or a strip, is picked up and recycled. This is called 'Revived Soul Paper' (*Huanhun Zhi*)."
    *   "竹與皮，精與粗，皆同之也。" -> "The principle is the same whether it is bamboo or bark paper, fine or coarse."
    *   "若火紙、糙紙，斬竹煮麻，灰漿水淋，皆同前法，唯脫簾之後，不用烘焙，壓水去濕，日曬成幹而已。" -> "As for fire paper (*Huo Zhi*) and rough paper (*Cao Zhi*), the processes of cutting bamboo, cooking the fiber, and treating with ash-water are all the same. The only difference is that after being lifted from the screen, they are not baked. They are simply pressed to remove the water and dried in the sun."
    *   "盛唐時，鬼神事繁，以紙錢代焚帛（北方用切條，名曰板錢），故造此者，名曰火紙。荊楚近俗，有一焚侈至千斤者。此紙十七供冥燒，十三供日用。" -> "During the height of the Tang Dynasty, there were many customs concerning gods and spirits. Paper money was burned to replace woven silk (in the north, cut strips are used, known as 'Board Money'), hence paper made for this purpose is called 'Fire Paper'. In the modern customs of the Jing-Chu region (Hunan/Hubei), it is wasteful extravagance to burn as much as a thousand *jin* (approx. 600 kg) of this paper in a single ceremony. Seven-tenths of this paper is used for spirit burning, and three-tenths for daily purposes."
    *   "其最粗而厚者，名曰包裹紙，則竹麻和宿田晚稻稿所為也。" -> "The coarsest and thickest type is called 'Wrapping Paper' (*Baoguo Zhi*). It is made from bamboo pulp mixed with the stalks of late rice from old fields."
    *   "若鉛山諸邑所造柬紙，則全用細竹料厚質蕩成，以射重價。" -> "As for the letter paper (*Jian Zhi*) made in the counties around Yanshan, it is entirely made from fine bamboo material, formed with a thick texture, to command a high price."
    *   "最上者曰官柬。富貴之家，通刺用之，其紙敦厚而無筋膜；染紅為吉柬，則先以白礬水染過，後上紅花汁雲。" -> "The best quality is called 'Official Note Paper' (*Guan Jian*). Wealthy and noble families use it for their visiting cards. The paper is thick and solid, with no coarse fibers. To dye it red for auspicious note paper (*Ji Jian*), it is first stained with an alum solution, and then with a juice made from safflower petals."
    *   "造皮紙" -> "Making bark paper..." (Heading for the next section, which is not in the text provided. I will just translate it as a standalone line or heading, as the prompt only gives the text for bamboo paper).

7.  **Final formatting and checks:**
    *   Is it clear?
    *   Is it faithful?
    *   Parentheses used properly?
    *   Are measurements handled well? (Yes, original term + modern approximation in parentheses).
    *   "事出南方" (made in the south) -> "Paper is always made in the south" / "Papermaking is done in the south". The original says "凡造竹紙，事出南方，而閩省獨專其盛。" -> "Wherever bamboo paper is made, it is always in the south, but Fujian province is particularly skilled/noted for this."
    *   "當筍生之後" -> After the shoots have grown.
    *   "節界芒種" -> "Around the Mangzhong solar term" (I'll keep the solar term name in pinyin with a seasonal explanation, e.g., "around the time of *Mangzhong* (Grain in Ear, early June)"). This is standard for technical translations of this material (e.g., Tiangong Kaiwu translations).
    *   "紙藥水汁" -> "Paper drug liquid". Let's use "papermaking sizing agent / paper drug". The parentheses: "(a mucilage made from a plant resembling peach bamboo leaves; local names vary)".
    *   "形同桃竹葉" -> "shaped like peach bamboo leaves".
    *   "俏繩入棍" -> "a rope is tightened around it with a lever stick (like a windlass)". The original describes a classic screw/lever press. "A rope is passed around it, and a stick/lever is inserted to twist it tight, like pressing wine."
    *   "揭起成帙" -> "peeled off and gathered into quires / booklets".
    *   "全省從前煮浸之力" -> "completely saves the previous work of boiling and soaking".
    *   "竹與皮，精與粗，皆同之也。" -> "Bamboo paper and bark paper, fine and coarse, all follow similar principles / the principle is the same."
    *   "造皮紙" just "Making bark paper."

8.  **Constructing the translation text:**
    "Wherever bamboo paper is made, it is always in the south, but Fujian province is especially renowned for it. After the shoots have grown, the mountain valleys are examined for their depth. The best material is bamboo that is about to grow branches and leaves. Around the time of the Mangzhong solar term (Grain in Ear, early June), the bamboo is cut down. It is cut into lengths of five to seven *chi* (roughly 1.5 to 2.1 meters). A pond is dug right there on the mountain, filled with water, and the bamboo is soaked in it. Fearing that the pond water might dry up, bamboo pipes are used to channel a continuous stream of fresh water into it. Soaked for over a hundred days, it is then thoroughly beaten and washed to remove the coarse outer shell and green skin (this process is called *shaqing*, 'killing the green'). The inner bamboo fiber left behind looks like ramie.

    This fiber is coated with a solution of high-quality lime and placed in a *huang* barrel (a large cooking vat) to be boiled. The fire is maintained for eight days and eight nights.

    The cooking pot used has a diameter of four *chi* (approx. 1.2 meters). Its rim is built up with a mixture of mud and lime, making it high and wide, similar to the salt-boiling pans in Guangdong, holding over ten *shi* (approx. 600-1000 liters) of water. The *huang* barrel covering the pot has a circumference of fifteen *chi* (approx. 4.5 meters) and a diameter of over four *chi* (approx. 1.2 meters). Once covered, the boiling proceeds. After eight days, it is finished. The fire is stopped for one day. The vat is then opened, and the bamboo pulp (*zhuma*) is taken out and washed clean in a pond of clear water. The bottom and four sides of this pond are tightly lined with boards joined at the seams to prevent mud from contaminating the pulp (this is not necessary for making coarse paper).

    After washing, the fiber is treated with a slurry of plant ashes (or wood ashes). It is then placed back in the pot, leveled, and a flat layer of rice-straw ash about an inch thick is spread over the top. When the water in the pot comes to a rolling boil, it is immediately ladled out and poured over the fiber in another vat, allowing the ash-laden liquid to drain through. If the liquid cools, it is reheated and poured again. This process is repeated for over ten days, until the fiber naturally rots and disintegrates. It is then taken out and placed in a mortar for pounding (mountainous regions use water-powered trip-hammers for this). It is pounded until it becomes a mud-like paste, which is then poured into the vat for sheet formation.

    The papermaking vat is square at the top. Its dimensions vary: the vat is sized according to the mold, and the mold according to the desired paper. The pulp is placed in the vat, and clean water is added until it stands about three *cun* (approx. 10 cm) above the surface. A 'paper drug' (*zhiyao*) liquid is added to the water. The plant used resembles peach bamboo leaves, and its name varies by locality. This ensures the water drains cleanly, leaving the fibers to form a white sheet.

    The papermaking screen is woven from extremely fine, scraped and polished bamboo strips. It is stretched on a frame with a network of supporting crossbars. The worker holds the screen with both hands, dips it into the vat, and shakes it so that the bamboo pulp is lifted and evenly distributed across the screen. The thickness of the sheet depends on the worker's skill: a gentle shake produces thin paper, a vigorous shake produces thick paper. As the fibers float on the screen, the water drains back into the vat from the four sides. The screen is then turned over, depositing the wet sheet onto a board. The sheets are stacked up, thousands of them.

    When the stack is high enough, a board is placed on top. A rope is tightened around it with a lever stick (like pressing wine in a traditional wine press) to squeeze out all the water completely. Afterwards, the sheets are carefully lifted one by one with fine copper tweezers and baked dry. For drying, a narrow corridor is built with earth bricks. The floor of the corridor is paved with bricks, with a gap left after every few bricks. A fire is kindled at an opening at one end. The heat and flames pass through the gaps in the bricks, heating the outer walls thoroughly. The wet sheets are pasted one by one onto this hot wall to dry. When dry, they are peeled off and gathered into quires.

    In recent times, a wide format called 'Da Si Lian' (Large Four-Fold) has been valued for writing and documents. Waste paper is recycled: after washing off the red cinnabar and black ink stains, it is soaked until it rots and then repulped in the vat. This entirely saves the previous labor of cooking and soaking. It is still made into paper, and the material loss is small. In the south, where bamboo is cheap, this recycling is not widely practiced. In the north, every scrap of paper on the ground, even an inch or a strip, is picked up and recycled. This is called 'Revived Soul Paper' (*Huanhun Zhi*). The principle is the same whether it is bamboo or bark paper, fine or coarse.

    As for fire paper (*huo zhi*) and rough paper (*cao zhi*), the processes of cutting bamboo, cooking the fiber, and treating with ash water are all the same as described above. The only difference is that after being lifted from the screen, they are not baked. They are simply pressed to remove the water and dried in the sun.

    During the height of the Tang Dynasty, customs concerning gods and spirits were numerous. Paper money was burned to replace woven silk (in the north, cut strips are used, called 'Board Money'). Hence, paper made for this purpose is called 'Fire Paper'. In the modern customs of the Jing-Chu region (Hunan and Hubei), it is not uncommon to burn as much as a thousand *jin* (approx. 600 kg) in a single extravagant offering. Seven-tenths of this fire paper is used for spirit offerings, and three-tenths for daily purposes. The coarsest and thickest paper is called 'Wrapping Paper' (*baoguo zhi*), which is made from bamboo pulp mixed with the stalks of late rice from old fields.

    As for the letter paper (*jian zhi*) made in the counties around Yanshan, it is entirely made from fine bamboo material, formed with a thick texture, to command a high price. The best quality is called 'Official Note Paper' (*guan jian*). Wealthy and noble families use it for their visiting cards (name cards). The paper is thick and firm, with no coarse fibers. To dye it red for auspicious note paper (*ji jian*), the paper is first stained with an alum solution and then with a juice made from safflower petals.

    Making bark paper."
```

## Assistant

```markdown
**Making Bamboo Paper** (from *Tiangong Kaiwu*)

Bamboo paper is always made in the south of China, but Fujian province is especially renowned for it. After the shoots have grown, the mountain valleys are examined for their depth. The best material is bamboo that is about to grow branches and leaves. Around the Mangzhong solar term (Grain in Ear, early June), the bamboo is cut down. It is cut into lengths of five to seven *chi* (roughly 1.5–2.1 m). A pond is dug right there on the mountain, filled with water, and the bamboo is soaked in it. Fearing that the pond water might dry up, bamboo pipes are used to channel a continuous stream of fresh water into it. After soaking for over a hundred days, it is thoroughly beaten and washed to remove the coarse outer shell and green skin (this process is called *shaqing*, "killing the green"). The inner bamboo fiber left behind looks like ramie.

The fiber is then coated with a solution of high-quality lime and placed in a *huang* barrel (a large cooking vat) to be boiled. The fire is maintained for eight days and eight nights.

The cooking pot used has a diameter of four *chi* (approx. 1.2 m). Its rim is built up with a mixture of mud and lime, making it high and wide, similar to the salt-boiling pans in Guangdong, holding over ten *shi* (roughly 600–1000 liters) of water. The *huang* barrel covering the pot has a circumference of fifteen *chi* (approx. 4.5 m) and a diameter of over four *chi* (approx. 1.2 m). Once covered, the boiling proceeds. After eight days, it is finished. The fire is stopped for one day. The vat is then opened, and the bamboo pulp (*zhuma*) is taken out and washed clean in a pond of clear water. The bottom and four sides of this pond are tightly lined with boards joined at the seams to prevent mud from contaminating the pulp (this is not necessary for making coarse paper).

After washing, the fiber is treated with a slurry of plant ashes. It is then placed back in the pot, leveled, and a flat layer of rice-straw ash about an inch thick is spread over the top. When the water in the pot comes to a rolling boil, it is immediately ladled out and poured over the fiber in another vat, allowing the ash-laden liquid to drain through. If the liquid cools, it is reheated and poured again. This process is repeated for over ten days, until the fiber naturally rots and disintegrates. It is then taken out and placed in a mortar for pounding (mountainous regions use water-powered trip-hammers for this). It is pounded until it becomes a mud-like paste, which is then poured into the vat for sheet formation.

The papermaking vat is square at the top. Its dimensions vary: the vat is sized according to the screen mold, and the mold according to the desired paper. The pulp is placed in the vat, and clean water is added until it stands about three *cun* (approx. 9 cm) above the surface. A "paper drug" (*zhiyao*, a natural mucilage) is added to the water. The plant used resembles peach bamboo leaves, and its name varies by locality. This ensures the water drains cleanly, leaving the fibers to form a white sheet.

The papermaking screen is woven from extremely fine, scraped and polished bamboo strips. It is stretched on a frame with a network of supporting crossbars. The worker holds the screen with both hands, dips it into the vat, and shakes it so that the bamboo pulp is lifted and evenly distributed across the screen. The thickness of the sheet depends on the worker's skill: a gentle shake produces thin paper, a vigorous shake produces thick paper. As the fibers float on the screen, the water drains back into the vat from the four sides. The screen is then turned over, depositing the wet sheet onto a board. The sheets are stacked up, thousands of them.

When the stack is high enough, a board is placed on top. A rope is tightened around it with a lever stick (like pressing wine in a traditional wine press) to squeeze out all the water completely. Afterwards, the sheets are carefully lifted one by one with fine copper tweezers and baked dry. For drying, a narrow corridor is built with earth bricks. The floor of the corridor is paved with bricks, with a gap left after every few bricks. A fire is kindled at an opening at one end. The heat and flames pass through the gaps in the bricks, heating the outer walls thoroughly. The wet sheets are pasted one by one onto this hot wall to dry. When dry, they are peeled off and gathered into quires.

In recent times, a wide format called *Da Si Lian* (Large Four-Fold) has been valued for writing and documents. Waste paper is recycled: after washing off the red cinnabar and black ink stains, it is soaked until it rots and then repulped in the vat. This entirely saves the previous labor of cooking and soaking. It is still made into paper, and the material loss is small. In the south, where bamboo is cheap, this recycling is not widely practiced. In the north, every scrap of paper on the ground, even an inch or a strip, is picked up and recycled. This is called "Revived Soul Paper" (*Huanhun Zhi*). The principle is the same whether it is bamboo or bark paper, fine or coarse.

As for fire paper (*huo zhi*) and rough paper (*cao zhi*), the processes of cutting bamboo, cooking the fiber, and treating with ash water are all the same as described above. The only difference is that after being lifted from the screen, they are not baked. They are simply pressed to remove the water and dried in the sun.

During the height of the Tang Dynasty, customs concerning gods and spirits were numerous. Paper money was burned to replace woven silk (in the north, cut strips are used, called "Board Money"). Hence, paper made for this purpose is called "Fire Paper." In the modern customs of the Jing-Chu region (Hunan and Hubei), it is not uncommon to burn as much as a thousand *jin* (approx. 600 kg) in a single extravagant offering. Seven-tenths of this fire paper is used for spirit offerings, and three-tenths for daily purposes. The coarsest and thickest paper is called "Wrapping Paper" (*baoguo zhi*), which is made from bamboo pulp mixed with the stalks of late rice from old fields.

As for the letter paper (*jian zhi*) made in the counties around Yanshan, it is entirely made from fine bamboo material, formed with a thick texture, to command a high price. The best quality is called "Official Note Paper" (*guan jian*). Wealthy and noble families use it for their visiting cards (name cards). The paper is thick and firm, with no coarse fibers. To dye it red for auspicious note paper (*ji jian*), the paper is first stained with an alum solution and then with a juice made from safflower petals.

**Making bark paper...**
```
