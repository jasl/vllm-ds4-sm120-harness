# Generation Transcript

- Case: `zh2en_tech_001`
- Language group: `zh`
- Workload: `translation`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 75.958188
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 1112, "total_tokens": 8582, "completion_tokens": 7470, "prompt_tokens_details": null}`
- Prompt tokens: 1112
- Completion tokens: 7470
- Total tokens: 8582

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
    *   **Task:** Translate the provided Classical Chinese text (specifically the "Zao Zhu Zhi" / Making Bamboo Paper section from *Tiangong Kaiwu*) into Modern English.
    *   **Target Audience:** A modern English speaker interested in understanding the papermaking process flow.
    *   **Objective:** Fidelity to the process, materials, time, and causality. NOT a word-for-word archaic translation. NOT an expanded encyclopedia article. Aim for clear technical clarity.
    *   **Stylistic Constraints:**
        *   Keep the process steps/logical flow intact.
        *   Use short parenthetical explanations where necessary (e.g., clarifying a technical term or a concept without breaking the narrative).
        *   Avoid modern technical jargon unless it directly translates (like "pulper", but the text uses specific historical terms like "楻桶", "抄紙簾" -> clarify without over-explaining).
    *   **Source Text:** Provided below (the excerpt).

    *   **Part 1: 造竹紙 (Making Bamboo Paper)**
        *   "凡造竹紙，事出南方，而閩省獨專其盛。" -> Papermaking from bamboo originates in the south, Fujian province is especially renowned/thriving.
        *   "當筍生之後，看視山窩深淺，其竹以將生枝葉者為上料。" -> When the bamboo shoots grow, inspect the mountain valleys. The best material is bamboo that is just about to grow its branches and leaves.
        *   "節界芒種，則登山砍伐，截斷五、七尺長，就於本山開塘一口，註水其中漂浸。" -> Around the Grain in Ear (Mangzhong) solar term, go up the mountain to cut it down. Cut it into pieces 5 to 7 *chi* long. Dig a pond on the mountain itself, fill it with water, and soak the bamboo in it.
        *   "恐塘水有涸時，則用竹梘通引，不斷瀑流註入。" -> Lest the pond water dries up, use bamboo aqueducts (竹梘) to channel a continuous water supply into it.
        *   "浸至百日之外，加功槌洗，洗去粗殼與青皮（是名殺青），其中竹穰形同苎麻樣。" -> Soak for over a hundred days. Then, work it by beating and washing to remove the outer shell and green skin (this step is called *sha qing* / killing the green). The inner pulp (竹穰) then looks like ramie fibers.
        *   "用上好石灰化汁塗漿，入楻桶下煮，火以八日八夜為率。" -> Apply a paste made from high-quality quicklime mixed with water. Put the mass into a *huang* bucket (steaming vat) and boil it for exactly eight days and eight nights.

        *   "凡煮竹，下鍋用徑四尺者，鍋上泥與石灰捏弦，高闊如廣中煮鹽牢盆樣，中可裁水十餘石。" -> The vat for boiling bamboo uses a cauldron with a diameter of 4 *chi*. The rim is built up with clay and lime, making it tall and wide like the salt-boiling pans used in Guangdong, holding over 10 piculs (石) of water.
        *   "上蓋楻桶，其圍丈五尺，其徑四尺餘。" -> The *huang* bucket (large wooden cask) is placed on top. It has a circumference of 15 *chi* and a diameter of over 4 *chi*.
        *   "蓋定受煮，八日已足。歇火一日，揭楻取出竹麻，入清水漂塘之內洗淨。" -> Cover it and boil. After the eight days are complete, let the fire die down for one day. Open the *huang* bucket and take out the bamboo pulp (竹麻). Wash it thoroughly in a pond filled with clean water.
        *   "其塘底面、四維皆用木板合縫砌完，以妨泥汙（造粗紙者不須為此）。" -> The bottom and sides of this pond are carefully lined with wooden boards fitted together to prevent mud contamination (makers of coarse paper do not need to do this).
        *   "洗淨，用柴灰漿過，再入釜中，其上按平，平鋪稻草灰寸許。" -> After washing, treat the pulp with wood ash lye. Put it back into a cauldron (or pot), press it level, and spread a layer of rice straw ash about an inch thick over it.
        *   "桶內水滾沸，即取出別桶之中，仍以灰汁淋下。倘水冷，燒滾再淋。如是十餘日，自然臭爛。" -> When the liquid in the pot boils, take the pulp out and put it in another container, continuing to pour the lye over it. If the liquid cools, reheat it and pour it again. After treating it like this for ten-plus days, the fibers naturally rot/break down.
        *   "取出入臼受舂（山國皆有水碓），舂至形同泥面，傾入槽內。" -> Take it out and beat it in a mortar (mountainous regions all use water-powered trip-hammers, 水碓). Beat it until it is like mud, then pour it into a vat (抄紙槽).

        *   "凡抄紙槽，上合方半，尺寸闊狹，槽視簾，簾視紙。" -> The papermaking vat (抄紙槽) has an open top, roughly square or rectangular. Its size depends on the mold frame, which in turn depends on the desired paper size.
        *   "竹麻已成，槽內清水浸浮其面三寸許，入紙藥水汁於其中（形同桃竹葉，方語無定名），則水幹自成潔白。" -> Once the bamboo pulp (竹麻) is ready, it is suspended in clear water about three inches deep in the vat. An herbal sizing liquid (紙藥水汁) is added (it comes from a plant resembling peach bamboo leaves, with no fixed local name). This causes the water to drain away and leaves a pure white sheet of paper.
        *   "凡抄紙簾，用刮磨絕細竹絲編成。展捲張開時，下有縱橫架匡。" -> The paper mold (抄紙簾) is made of very finely scraped and polished bamboo strips woven into a screen. It is mounted on a frame with vertical and horizontal supports.
        *   "兩手持簾入水，蕩起竹麻，入於簾內。厚薄由人手法，輕蕩則薄，重蕩則厚。" -> Holding the mold frame with both hands, dip it into the vat and shake it to lift the pulp fibers onto the screen. The thickness of the paper is controlled by the vatman's skill: a gentle shake gives a thin sheet, a vigorous shake gives a thicker sheet.
        *   "竹料浮簾之頃，水從四際淋下槽內，然後覆簾，落紙於板上，疊積千萬張。" -> As the bamboo fibers settle on the screen, water drains back into the vat from all sides. Then, the mold is inverted, depositing the wet sheet of paper onto a board. Thousands of sheets are accumulated in a stack this way.
        *   "數滿，則上以板壓，俏繩入棍，如榨酒法，使水氣淨盡流幹。" -> When the stack is high enough, a board is placed on top, and it is pressed with a lever mechanism tightened with ropes (like a wine press) to squeeze out as much water as possible.
        *   "然後，以輕細銅鑷逐張揭起、焙乾。" -> Afterwards, the sheets are lifted one by one with a fine copper tweezers (or spatula) and dried on a heated wall/kiln.
        *   "凡焙紙，先以土磚砌成夾巷，下以磚蓋巷地面，數塊以往，即空一磚。" -> The drying wall (焙紙) is built as a narrow passageway (夹巷) with hollow walls. The floor of the passage is paved with bricks, leaving an open brick gap at intervals.
        *   "火薪從頭穴燒發，火氣從磚隙透巷，外磚盡熱。" -> A fire is lit at the entrance of the passage. The heat from the fire travels through the gaps into the cavity, heating the entire outer brick surface.
        *   "濕紙逐張貼上焙乾，揭起成帙。" -> Wet sheets are pasted onto this hot brick wall, dried, and then peeled off to form quires (or bundles).

        *   "近世闊幅者，名大四連，一時書文貴重。" -> In recent times, wide-format paper called "Da Si Lian" has become highly valued for writing and documents.
        *   "其廢紙，洗去朱墨污穢，浸爛，入槽再造，全省從前煮浸之力，依然成紙，耗亦不多。" -> Waste paper of this type can be washed to remove red ink and dirt, soaked to soften it, and repulped in the vat. This saves the entire previous process of boiling and soaking, yet still makes paper, and the loss of fiber is minimal.
        *   "南方竹賤之國，不以為然。北方即寸條片角在地，隨手拾取再造，名曰還魂紙。" -> In the south, where bamboo (and thus paper) is cheap, this is not done. In the north, even a tiny scrap of paper on the floor is picked up and recycled. This paper is called *Huan Hun Zhi* (Returned Soul Paper).
        *   "竹與皮，精與粗，皆同之也。" -> Bamboo and bark papers, fine and coarse, are all treated the same way in this recycling process.
        *   "若火紙、糙紙，斬竹煮麻，灰漿水淋，皆同前法，唯脫簾之後，不用烘焙，壓水去濕，日曬成幹而已。" -> As for fire paper (火紙) and rough paper (糙紙), the initial steps of cutting bamboo, boiling, treating with ash, etc., are the same. The difference is that after de-molding, they are not dried on a hot wall. Instead, after pressing, they are simply dried in the sun.

        *   "盛唐時，鬼神事繁，以紙錢代焚帛（北方用切條，名曰板錢），故造此者，名曰火紙。" -> During the High Tang dynasty, matters of spirits and ghosts were numerous. Paper money replaced burned silk fabrics for offerings. (In the north, they cut it into strips called *Ban Qian*). Thus, this paper is called fire paper.
        *   "荊楚近俗，有一焚侈至千斤者。此紙十七供冥燒，十三供日用。" -> The recent custom in the Jing-Chu region is so extravagant that a thousand catties (*jin*) are burned in a single ceremony. About 70% of this paper is used for spirit offerings, and 30% for daily use.
        *   "其最粗而厚者，名曰包裹紙，則竹麻和宿田晚稻稿所為也。" -> The coarsest and thickest type is called wrapping paper (包裹紙). It is made by mixing bamboo pulp with straw from late-harvested rice from old fields.
        *   "若鉛山諸邑所造柬紙，則全用細竹料厚質蕩成，以射重價。" -> The fine note-paper (柬紙) made in counties like Yanshan, however, is made entirely from fine bamboo fiber, formed into a thick sheet to fetch a high price.
        *   "最上者曰官柬。富貴之家，通刺用之，其紙敦厚而無筋膜；染紅為吉柬，則先以白礬水染過，後上紅花汁雲。" -> The highest quality is called official note-paper (官柬). Wealthy and noble families use it for name cards (visiting cards). It is thick and solid, without fiber streaks. To dye it red for auspicious cards (吉柬), it is first treated with an alum solution, and then dyed with safflower juice.

        *   Wait, there is no text for 造皮紙 provided in the user prompt. The title of the section is "造皮紙" at the very end of the prompt, but no text follows it. I will strictly adhere to the text provided, which is "《天工開物》節選：造竹紙". The user prompt text ends with "染紅為吉柬，則先以白礬水染過，後上紅花汁雲。" and then a newline and "造皮紙". I should ignore "造皮紙" as it signals the *next* section of the original text which was cut off or just mentioned as a header. Oh, I see the source text provided ends with "染紅為吉柬，則先以白礬水染過，後上紅花汁雲。" and then "造皮紙". I will translate *only* the text under "造竹紙" because that's what is provided. I'll assume "造皮紙" is just a stray header from the original eBook that leaked into the copy-paste. I will not translate it.

    *   **Reviewing the Translation Strategy:**
        *   Keep the paragraph structure loosely corresponding to the original process steps, but as clear English prose.
        *   Ensure technical terms are explained minimally in parentheses.
        *   Use modern equivalents for measures? The text uses ancient Chinese measures (尺 chi, 石 shi/dan/picul, 斤 jin, 寸 cun, 丈 zhang). The instruction says "忠实保留工序、材料、时间和因果关系". Should I transform measures? "A picul" is a translation for 石. "A Chinese foot" for 尺. It might be better to just translate them directly or use approximations. "Around 5-7 feet long" for 五、七尺長, although 1 尺 is ~ 0.33m, 5-7尺 is ~1.6m to 2.3m. Giving the exact unit "chi" with a parenthetical metric conversion might be better for a modern reader: "5 to 7 *chi* (approx. 1.6–2.3 meters) long". The prompt says "必要时可用括号给出极短解释", so translating units is a valid need. No, keep it simple. If the exactness isn't strictly required for the *process flow*, historical units are fine. "five to seven feet long" is fine enough, though technically it was slightly shorter. "Ten-picul capacity". Let's translate 石 as piculs, 尺 as feet, 寸 as inches. This is standard for translating *Tiangong Kaiwu* into English (e.g. E-Tu Zen Sun & Shiou-Chuan Sun translation). Or I can just say "ten *dan* (picul) capacity".

        *   **Specific terminology:**
            *   芒種: Grain in Ear (the traditional solar term, reasonable translation).
            *   竹梘: bamboo aqueduct/pipe.
            *   殺青: *Shaging* / Killing the green. (Standard term in tech history).
            *   楻桶: *Huang* bucket. (Steaming vessel). Steam vat. Wooden cask.
            *   竹麻: Bamboo pulp.
            *   抄紙簾: Paper mold screen.
            *   紙藥水汁: Sizing liquid (e.g., plant mucilage / formation aid).
            *   水碓: Water-powered trip hammer / pestle.
            *   還魂紙: *Huanhun* paper / returned soul paper.
            *   火紙: Fire paper.
            *   官柬: Official note paper.

            Let's write a coherent, flowing translation.

    *   **Drafting the Translation:**

        **Making Bamboo Paper (造竹紙)**

        Bamboo papermaking originated in the south, but Fujian province is particularly known for its flourishing industry.
        After the bamboo shoots have grown, inspect the mountain valleys. The best material is bamboo that is just about to put forth branches and leaves.
        Around the Grain in Ear solar term (芒種, early June), go up the mountain to cut the bamboo down. Cut it into pieces five to seven *chi* long. Dig a pond on the mountain itself, fill it with water, and completely submerge the bamboo for soaking.
        To prevent the pond from drying out, bamboo aqueducts (竹梘) are used to channel a continuous stream of water into it.
        After soaking has continued for over a hundred days, the bamboo is pounded and washed vigorously to remove the coarse outer shell and green skin. (This step is called *sha qing* / killing the green.) What remains is a bamboo fiber mass (竹穰) that looks like ramie fibers.
        These fibers are then daubed with a mixture made from high-quality quicklime and water. This is placed in a *huang* bucket (large wooden steaming vat) set over a cauldron, and boiled over a fire for exactly eight days and eight nights.

        The cauldron used for this boiling is four *chi* in diameter. Its rim is built up with clay and lime, making it tall and wide like the salt-boiling pans in Guangdong, and it can hold over ten *shi* (piculs / stones) of water.
        The *huang* bucket placed on top has a circumference of fifteen *chi* and a diameter of over four *chi*.
        Once covered and boiling, the eight days are strictly observed. The fire is then allowed to die down for a full day. The bucket is opened, and the bamboo pulp (竹麻) is taken out and thoroughly washed in a pond of clean, clear water.
        The floor and four sides of this washing pond must be carefully lined with wooden boards joined tightly together to prevent contamination from mud. (This is not necessary when making coarse paper).
        After washing, the pulp is treated with a wood-ash lye (柴灰漿). It is then placed back into a cauldron, leveled flat, and covered with about an inch of rice-straw ash.
        When the liquid in the cauldron boils, the pulp is taken out and placed in another container, with the lye continuously poured back over it. If the liquid cools down, it is reheated and poured over again. After repeating this process for more than ten days, the fibers will naturally rot down into a fine pulp.
        The pulp is then removed and placed in a mortar to be beaten. (In mountainous regions, water-powered trip-hammers, 水碓, are used for this purpose.) It is beaten until it becomes a smooth, mud-like consistency, and then poured into a papermaking vat (抄紙槽).

        The papermaking vat has a square or rectangular opening. The size of the vat depends on the paper mold (簾), which in turn depends on the desired dimensions of the paper.
        With the bamboo pulp ready, it is suspended in clear water in the vat to a depth of about three inches. An herbal sizing liquid (紙藥水汁) is added. (It comes from a plant resembling a peach bamboo leaf; its local name varies.) This sizing agent makes the water drain freely and produces a pure white sheet.
        The paper mold (抄紙簾) is woven from very finely scraped and polished bamboo strips. When mounted for use, it is stretched on a frame with a network of vertical and horizontal supports.
        The vatman holds the mold with both hands, dips it into the vat, and shakes it to lift the bamboo pulp fibers onto the screen. The thickness of the sheet is controlled by the vatman's skill: a light, gentle shake produces a thin sheet; a heavy shake produces a thick sheet.
        As the fibers interlace on the screen, water drains back into the vat from all four edges. The mold is then inverted to deposit the wet sheet onto a board. Sheets are accumulated in a stack, thousands upon thousands.
        When the stack reaches a suitable thickness, a board is placed on top. Ropes and levers are used to press the stack firmly (like a wine press) to squeeze out as much water as possible.
        Afterwards, the sheets are lifted one by one with a slender copper spatula or tweezers (銅鑷) and taken to be dried.
        For drying, a narrow baking chamber (焙紙) is built with a double wall of clay bricks. The floor of the chamber is paved with bricks, leaving a gap forming a fire tunnel.
        A fire is lit at the opening. The hot air and smoke travel through the tunnel, heating the entire outer brick wall until it is very hot.
        The damp sheets of paper are pasted one by one onto this hot wall to dry, then peeled off and gathered into quires (or bundles).

        In recent times, a wide-format paper called *Da Si Lian* (大四連, roughly "Large Four-Link") has become highly valued for writing and documents.
        Waste paper of this kind can be washed to remove red ink and dirt, soaked, and repulped in the vat. This recycling saves the entire previous process of boiling, soaking, and reducing, yet it still produces perfectly usable paper with very little loss of fiber.
        In the south, where bamboo (and thus paper raw material) is cheap, people don't bother with this. In the north, even a tiny scrap of paper thrown on the floor is picked up immediately and recycled. This recycled product is called *Huan Hun Zhi* (還魂紙, "Returned Soul Paper").
        The same recycling principle applies to both bamboo paper and bark paper, and to both fine and coarse varieties.

        As for *Huo Zhi* (火紙, Fire Paper) and *Cao Zhi* (糙紙, Coarse Paper), the initial steps of cutting, boiling, treating with ash lye, and washing are all identical to the standard method. The only difference is that after de-molding and pressing, the sheets are not dried in the baking chamber. Instead, after pressing out the water, they are simply dried in the sun.

        During the High Tang dynasty (盛唐, 7th-8th cent.), rituals involving spirits and ghosts were widespread, and paper money was burned as a substitute for expensive silk cloth. (In the north, the paper is cut into strips and called *Ban Qian* / Board Money). Paper made for this purpose is called Fire Paper.
        The recent custom in the Jing-Chu region (荊楚, the middle Yangzi area) is so extravagant that a thousand *jin* (catties) of paper might be burned in a single ceremony. Of this paper, roughly 70% is made for sacrificial burning and 30% for daily practical use.
        The coarsest and thickest variety of paper is called *Bao Guo Zhi* (包裹紙, Wrapping Paper). It is made from a mixture of bamboo pulp and the straw of late-harvested rice from worn-out fields.
        In contrast, the fine letter-paper (*Jian Zhi*, 柬紙) produced in counties like Yanshan (鉛山, in Jiangxi) is made entirely from high-quality fine bamboo fiber, formed into thick, solid sheets to fetch a high price.
        The finest grade is called *Guan Jian* (官柬, Official Note-Paper). Wealthy and noble families use it for their visiting cards. The paper is thick and solid, without any coarse fiber streaks showing through.
        To make it into red paper for auspicious events (*Ji Jian*, 吉柬), it is first treated with an alum solution (白礬水) and then dyed with safflower juice (紅花汁).

    *   **Checking constraints:**
        *   "忠实保留工序、材料、时间和因果关系" - Yes, thoroughly translated.
        *   "必要时可用括号给出极短解释" - Yes, used for *sha qing*, *da si lian*, *huo zhi*, *huan hun zhi*, etc.
        *   "不要扩写为百科文章" - Yes, kept strictly to the text provided without adding modern context outside of the immediate text/technical process.
        *   "不是逐字古雅" - Yes, sentence structure is modern English, "The vat is this...", "The pulp is treated..."
        *   "让现代英语读者理解造纸流程" - Yes. The flow is clear: harvest -> soak -> boil -> wash -> treat with ash -> beat -> suspend in vat -> mold -> press -> dry.
        *   "来源链接" provided, but I just need to translate the given text. No specific format required from the website besides the existing text.

    *   **Double check specific technical translations:**
        *   楻桶: The text calls it a *huang* bucket. The function is a large wooden cask or vat used for boiling. "large wooden steaming cask (楻桶, huangtong)".
        *   竹麻: "bamboo pulp" or "fiber mass".
        *   抄紙簾: "paper mold" (the screen + frame). The *Tiangong Kaiwu* specifically describes a woven bamboo screen stretched on a frame. "screen mold" or "bamboo paper mold". Let's stick with "paper mold (抄紙簾)".
        *   水碓: "water-powered trip-hammer" or "water-powered pestle mortar".
        *   柴灰漿: "wood ash lye" (ashes mixed with water or used to make a liquor).
        *   紙藥水汁: "plant sizing mucilage" / "formation aid".
        *   盛唐時: "During the golden age of the Tang dynasty (High Tang)".
        *   荊楚: "Jing and Chu regions" (modern Hubei/Hunan). "Jing-Chu region" is standard.
        *   鉛山: "Yanshan". The English reading of the city.

        Let's review the translation of the measures.
        "煮竹，下鍋用徑四尺者" -> Cauldron 4 *chi* in diameter. (~1.3m).
        "中可裁水十餘石" -> holds over 10 *shi* (picul) of water.
        "圍丈五尺" -> circumference 15 *chi*.
        "截斷五、七尺長" -> cut into pieces 5 to 7 *chi* long.
        "平鋪稻草灰寸許" -> layer of ash 1 *cun* (inch) thick.
        "槽內清水浸浮其面三寸許" -> suspended 3 *cun* above the base / 3 inches deep.

        Everything looks solid.

        **Final structural review:**
        The text reads chronologically and logically.
        The parenthetical explanations are short: just giving the Chinese term or a very brief gloss.
        No extra commentary is added outside the scope of the original text.

        Ready to generate the final output.
```

## Assistant

```markdown
Here is the translation of the provided excerpt from *Tiangong Kaiwu*, focusing on clarity of the manufacturing process for a modern English reader while strictly preserving the sequence, materials, times, and causal logic.

---

**Making Bamboo Paper**

Bamboo papermaking is a practice of the south, and Fujian province is particularly flourishing in this craft.

After the bamboo shoots have grown, the mountain valleys are surveyed. The best raw material is bamboo that is just about to grow branches and leaves. Around the time of the Grain in Ear solar term (early June), people go up the mountain to cut the bamboo. It is trimmed into pieces five to seven *chi* long. A pond is dug right there on the mountain, filled with water, and the bamboo is soaked in it. In case the pond water dries up, bamboo aqueducts are built to channel a continuous stream of water into it.

After soaking for over a hundred days, the bamboo is vigorously pounded and washed to remove the coarse outer shell and green skin. (This step is called *sha qing*, “killing the green.”) What remains is a bamboo fiber mass resembling ramie. A liquid paste of high-quality quicklime is applied to this pulp, and it is placed in a *huang* bucket (a large wooden vat) set over a cauldron and boiled for a full eight days and eight nights.

The cauldron used for this boiling has a diameter of four *chi*. Its rim is built up with clay and lime to make it tall and wide, like the salt-boiling pans in Guangdong. It can hold over ten *shi* (picul) of water. The *huang* bucket placed on top has a circumference of fifteen *chi* and a diameter of over four *chi*. The lid is set, and the boiling proceeds. When the eight days are completed, the fire is allowed to die for one day. The bucket is then opened, the bamboo pulp is removed, and it is thoroughly washed in a pond of clean, clear water. The bottom and four sides of this washing pond are carefully lined with wooden boards fitted tightly together to prevent contamination from mud. (Makers of coarse paper do not need to do this.)

After washing, the pulp is treated with a lye made from wood ash. It is placed back into a cauldron, pressed flat, and covered with a layer of rice straw ash about an inch thick. When the liquid in the cauldron boils, the pulp is taken out and transferred to another container, with the lye continuously poured over it. If the liquid cools, it is reheated and poured over again. After repeating this process for more than ten days, the fibers naturally rot and break down into a fine pulp.

The pulp is then taken out and placed in a mortar to be beaten (mountainous regions all use water-powered trip-hammers for this). It is beaten until it has the consistency of mud, and then poured into a papermaking vat.

The papermaking vat has a square or rectangular opening. The size of the vat depends on the mold screen, and the size of the mold screen depends on the desired size of the paper. Once the bamboo pulp is ready, it is suspended in clear water to a depth of about three inches in the vat. A herbal sizing liquid is added to it. (This comes from a plant resembling a peach bamboo leaf; its local name varies.) This allows the water to drain away cleanly, leaving a pure white sheet.

The paper mold screen is woven from very finely scraped and polished bamboo strips. When it is stretched for use, it is supported by a frame with vertical and horizontal bars. The vatman holds the mold with both hands, dips it into the vat, and shakes it to lift the bamboo fibers onto the screen. The thickness of the sheet depends entirely on the vatman’s technique: a light, gentle shake produces a thin sheet; a heavy shake produces a thick sheet. As the bamboo fibers float and interlace on the screen, water drains from all four sides back into the vat. The mold is then inverted, depositing the wet sheet onto a board. The sheets are stacked up, thousands upon thousands.

When the stack is high enough, a board is placed on top, and it is pressed using ropes and a lever, in the same manner as a wine press, to force the water out completely. After pressing, the sheets are lifted one by one with a fine copper spatula and taken to be dried.

For drying, a narrow chamber is built from clay bricks. The floor of the chamber is paved with bricks, leaving a gap open at intervals to form a fire tunnel. The fire is lit at the opening. The heat and hot air travel through the gaps in the bricks, making the entire outer brick wall very hot. The wet sheets are pasted onto this hot wall one by one to dry. Once dry, they are peeled off and gathered into quires.

In recent times, a wide-format paper called *Da Si Lian* (“Large Four-Link”) has become highly valued for writing and documents. Waste paper of this kind can be washed to remove traces of red ink and dirt, soaked, and repulped in the vat. This entirely saves the previous effort of boiling and soaking, yet it still makes paper, and the fiber loss is very small. In the south, where bamboo is cheap, people do not bother with this. In the north, however, even an inch-wide scrap or a corner of paper found on the ground will be picked up and recycled. This is called *Huan Hun Zhi* (“Returned Soul Paper”). Both bamboo and bark fibers, fine and coarse grades, are recycled in the same way.

As for *Huo Zhi* (fire paper used for offerings) and *Cao Zhi* (rough paper), the steps of cutting the bamboo, boiling the pulp, treating with ash lye, and washing are all the same as the method above. The only difference is that after de-molding, the sheets are not dried in the baking chamber. Instead, after pressing out the water, they are simply dried in the sun.

During the High Tang dynasty, rituals involving spirits and ghosts were widespread. Paper money was burned to replace woven silk offerings. (In the north, the paper is cut into strips and called *Ban Qian* – Board Money.) Thus, paper made for this purpose is called Fire Paper. The recent custom in the Jing-Chu region is so extravagant that over a thousand *jin* of paper might be burned in a single ceremony. About 70% of this paper is used for sacrificial burning, and 30% for daily practical use.

The coarsest and thickest type is called Wrapping Paper. It is made from bamboo pulp mixed with the straw from late-harvested rice grown in old fields. The fine letter-paper (*Jian Zhi*) produced in counties like Yanshan, however, is made entirely from fine bamboo material, formed into thick sheets, and sold at a high price. The highest grade is called *Guan Jian* (Official Note-Paper). Wealthy and noble families use it for visiting cards. This paper is thick and solid, without any fiber streaks. To dye it red for auspicious cards (*Ji Jian*), it is first treated with an alum solution and then dyed with safflower juice.
```
