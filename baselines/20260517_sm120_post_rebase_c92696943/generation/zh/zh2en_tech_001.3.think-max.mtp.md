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
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 57.425595
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 1112, "total_tokens": 11190, "completion_tokens": 10078, "prompt_tokens_details": null}`
- Prompt tokens: 1112
- Completion tokens: 10078
- Total tokens: 11190

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
    *   **Goal:** Translate traditional Chinese technical text (about bamboo papermaking from *Tiangong Kaiwu*) into English.
    *   **Style/Tone:** Not archaic word-for-word. Aim for clarity for modern readers regarding the papermaking process.
    *   **Requirements:** Faithful retention of steps, materials, time, and causality. Minor parenthetical explanations allowed if necessary. **No expansion into an encyclopedia article.**
    *   **Source:** *Tiangong Kaiwu* (Song Yingxing), "Zao zhu zhi" (Making Bamboo Paper). Public domain (Project Gutenberg).
    *   **Text:** The provided Chinese text starting from "凡造竹紙，事出南方..." (excluding the final paragraph about 造皮纸 which seems cut off, let's stick to the bamboo paper part as the prompt calls it "素材来源：《天開物》节选：造竹紙" and the text ends "...後上紅花汁雲。" which is still part of the bamboo paper section describing different paper types like 柬纸 and touching on 皮纸 but wait, the text actually ends with "造皮纸". Let's check the provided text: it ends with "造皮紙". No wait, the text given at the end is "...染紅為吉柬，則先以白礬水染過，後上紅花汁雲。\n\n造皮紙". Yes, it ends with "造皮紙", which is just the title of the next section. I will only translate the "造竹紙" part provided up to "染紅為吉柬，則先以白礬水染過，後上紅花汁雲。" which is clearly the end of the bamboo paper section. The "造皮紙" is just a dangling header. The prompt title is "素材来源：《天工開物》节选：**造竹紙**". So I will translate the full text provided, which covers bamboo paper, from the beginning to "後上紅花汁雲。".

    *   **Translation Strategy:**
        *   Modern, clear English.
        *   Respect the physical process.
        *   Add small clarifications if culturally specific terms are confusing.
        *   "殺青" -> "kill the green" (stop fermentation or remove green bark? Here it means removing the outer green skin).
        *   "竹梘" -> bamboo aqueduct.
        *   "火紙" -> fire paper / spirit money.
        *   "還魂紙" -> revived paper.
        *   "鬼事繁" -> abundant spiritual affairs / ghost festivals.
        *   "斬竹煮麻，灰漿水淋" -> standard process steps.

    *   **Structure of the text:**
        1.  Introduction & Raw materials (South, Fujian, bamboo selection, timing).
        2.  Soaking and initial processing (pond, bamboo pipes, 100+ days, beating, removing skin/blue).
        3.  Lime boiling (lime paste, vat, 8 days fire).
        4.  Washing and second soaking/fermenting (clean water tank, wood lining, ash lye, repeated boiling/soaking for ~10 days).
        5.  Beating (mortar, hydraulic pestle/water trip hammer).
        6.  Vat preparation (sizing liquid from specific plant).
        7.  Moulding/Scooping (bamboo screen, frame, dipping, thickness control).
        8.  Pressing (stack, board, leverage / winch).
        9.  Drying (copper tongs, drying walls / heated brick corridor).
        10. Paper types (Da Si Lian, Huo Zhi / spirit money, Chun paper, Bao Guo paper / wrapping paper, Jian paper / letter paper).
        11. Recycling (waste paper, revived paper / huan hun zhi, raw materials).
        12. Fire paper specific.
        13. Jian paper types (Guan Jian, red Grievance paper). -> wait, 吉柬 is auspicious letter paper, not grievance. "染紅為吉柬" -> dyed red for auspicious letters.
        14. "造皮紙" -> This is the title of the next chapter. The prompt says "素材来源：《天工開物》节选：造竹紙". I should probably just translate the provided text, which means the final "造皮紙" header, but it's incongruous. Should I just leave it as a heading? The user might have accidentally included it. Let's translate it as "Making Bark Paper" but since the user didn't ask for that section, it's best to either include it as a header or omit it. The request says "【待处理素材】..." which includes everything up to "造皮紙". I will translate the whole text provided, including that dangling last sentence, which looks like a section title.

        Wait, the text provided ends with:
        "...染紅為吉柬，則先以白礬水染過，後上紅花汁雲。

        造皮紙"

        This is the text of the bamboo paper chapter minus the final chapter header. The full Bamboo Paper chapter actually ends right there, and the next chapter is "造皮紙". I will translate "造皮紙" as the header for the next section, e.g., "Making Bark Paper". But the instruction is "素材来源...造竹紙", so I'll translate exactly what is given.

        Let's carefully translate sentence by sentence.

        "凡造竹紙，事出南方，而閩省獨專其盛。"
        -> "The making of bamboo paper is carried out in the south, but Fujian province is particularly famous for it."

        "當筍生之後，看視山窩深淺，其竹以將生枝葉者為上料。"
        -> "After the bamboo shoots have grown, one assesses the bamboo groves (literally the depths of the mountain hollows). The best material is bamboo that is about to grow its branches and leaves."

        "節界芒種，則登山砍伐，截斷五、七尺長，就於本山開塘一口，註水其中漂浸。"
        -> "Around the time of the Grain in Ear (Mangzhong) solar term, the bamboo is cut in the mountains. It is chopped into lengths of five to seven *chi* (approx. 1.7 - 2.3 meters), and a pond is dug right on the mountain to soak it. "

        "恐塘水有涸時，則用竹梘通引，不斷瀑流註入。"
        -> "To prevent the pond water from drying out, bamboo aqueducts are used to channel a constant stream of waterfall-fed water into it."

        "浸至百日之外，加功槌洗，洗去粗殼與青皮（是名殺青），其中竹穰形同苎麻樣。"
        -> "After soaking for over a hundred days, it is beaten and washed to remove the rough outer shell and green skin (this step is called *sha qing* / killing the green*). The inner pulp, or bamboo fiber, resembles ramie in texture."

        "用上好石灰化汁塗漿，入楻桶下煮，火以八日八夜為率。"
        -> "High-quality lime is dissolved into a liquid and mixed into a paste with the pulp. This is placed into a *huang* (large steamer vat) and boiled for eight days and eight nights."

        "凡煮竹，下鍋用徑四尺者，鍋上泥與石灰捏弦，高闊如廣中煮鹽牢盆樣，中可裁水十餘石。"
        -> "For boiling the bamboo, a cauldron about four *chi* in diameter is used. A rim made of mud and lime is built around the top of the cauldron, making it tall and wide like the salt pans used in Guangdong. It can hold over ten *dan* (approx. 1000 liters) of water."

        "上蓋楻桶，其圍丈五尺，其徑四尺餘。"
        -> "A large wooden *huang* barrel is placed over it, with a circumference of one *zhang* and five *chi* and a diameter of over four *chi*."

        "蓋定受煮，八日已足。"
        -> "Once covered and boiled, eight days is sufficient."

        "歇火一日，揭楻取出竹麻，入清水漂塘之內洗淨。"
        -> "The fire is allowed to go out for a day. The *huang* is uncovered, and the bamboo pulp (bamboo hemp) is taken out and washed clean in a fresh water pond."

        "其塘底面、四維皆用木板合縫砌完，以妨泥汙（造粗紙者不須為此）。"
        -> "The bottom and sides of this pond are lined with tightly fitted wooden boards to prevent mud contamination (this is not necessary for making coarse paper)."

        "洗淨，用柴灰漿過，再入釜中，其上按平，平鋪稻草灰寸許。"
        -> "After washing, the pulp is mixed with wood ash lye. It is then placed back into a cauldron, leveled, and covered with a one-*cun*-thick layer of rice straw ash."

        "桶內水滾沸，即取出別桶之中，仍以灰汁淋下。"
        -> "When the water in the vat boils, the pulp is taken out and placed into another vat. The ash lye is poured over it again."

        "倘水冷，燒滾再淋。如是十餘日，自然臭爛。"
        -> "If the liquid cools, it is reheated and poured over again. After about ten days of this, the bamboo fibers naturally become completely decomposed and rotten."

        "取出入臼受舂（山國皆有水碓），舂至形同泥面，傾入槽內。"
        -> "It is taken out and placed into a mortar for pounding (mountainous regions all use water-powered trip-hammers). It is pounded until it has the consistency of mud, and then poured into a vat."

        "凡抄紙槽，上合方半，尺寸闊狹，槽視簾，簾視紙。"
        -> "The papermaking vat has a rectangular or partially square upper opening. The width and dimensions of the vat are based on the mould screen, and the screen is based on the desired paper size."

        "竹麻已成，槽內清水浸浮其面三寸許，入紙藥水汁於其中（形同桃竹葉，方語無定名），則水幹自成潔白。"
        -> "Once the bamboo pulp is ready, it is suspended in clear water in the vat to a depth of about three *cun*. A 'paper drug' liquid is added to the vat (it looks like peach/bamboo leaves, names vary by region). This causes the fibers to separate cleanly and form white paper sheets when the water drains."

        "凡抄紙簾，用刮磨絕細竹絲編成。展捲張開時，下有縱橫架匡。"
        -> "The papermaking mould screen is woven from extremely fine, polished bamboo strips. When mounted for use, it is stretched over a rectangular frame with a lattice support beneath."

        "兩手持簾入水，蕩起竹麻，入於簾內。"
        -> "Holding the mould with both hands, the worker dips it into the vat, scooping up the pulp and spreading it evenly over the screen."

        "厚薄由人手法，輕蕩則薄，重蕩則厚。"
        -> "The thickness of the paper depends on the worker's skill: a light shake results in thin paper, while a vigorous shake produces thicker paper."

        "竹料浮簾之頃，水從四際淋下槽內，然後覆簾，落紙於板上，疊積千萬張。"
        -> "As the bamboo fibers settle on the screen, the water drains through it back into the vat. The mould is then inverted, depositing the wet sheet onto a board. Sheets are stacked up in the thousands."

        "數滿，則上以板壓，俏繩入棍，如榨酒法，使水氣淨盡流幹。"
        -> "When the stack reaches a certain height, it is covered with a board. A lever is inserted into ropes bound around the stack, and pressure is applied (like pressing wine lees) to squeeze out all the water completely."

        "然後，以輕細銅鑷逐張揭起、焙乾。"
        -> "Then, using light and fine copper tweezers, the paper sheets are lifted one by one and dried over a fire / on a heater."

        "凡焙紙，先以土磚砌成夾巷，下以磚蓋巷地面，數塊以往，即空一磚。"
        -> "For drying the paper, a narrow corridor is built with hollow brick walls. The floor of the corridor is paved with bricks, leaving every few bricks spaced apart to create gaps."

        "火薪從頭穴燒發，火氣從磚隙透巷，外磚盡熱。"
        -> "A fire is lit at one end of the channel. The heat and flames travel through the gaps under the floor, heating all the bricks in the corridor."

        "濕紙逐張貼上焙乾，揭起成帙。"
        -> "The wet sheets are pasted onto the hot brick wall to dry. Once dry, they are peeled off and gathered into quires."

        "近世闊幅者，名大四連，一時書文貴重。"
        -> "In recent times, a wide-sized paper called *Da Si Lian* (Big Four-Connection) was valued for writing and printing."

        "其廢紙，洗去朱墨污穢，浸爛，入槽再造，全省從前煮浸之力，依然成紙，耗亦不多。"
        -> "Waste paper is washed to remove red ink and dirt, soaked to a pulp, and returned to the vat to be re-made into paper. This process saves all the work of boiling and soaking the raw bamboo, and the loss of fiber is very small."

        "南方竹賤之國，不以為然。北方即寸條片角在地，隨手拾取再造，名曰還魂紙。"
        -> "In the south, where bamboo is cheap, this recycling is not considered worthwhile. In the north, however, even a scrap or corner of paper is picked up from the ground and re-pulped. This is called *Huan Hun Zhi* (Revived Soul Paper)."

        "竹與皮，精與粗，皆同之也。"
        -> "This principle applies equally to bamboo paper and bark paper, fine paper and coarse paper."

        "若火紙、糙紙，斬竹煮麻，灰漿水淋，皆同前法，唯脫簾之後，不用烘焙，壓水去濕，日曬成幹而已。"
        -> "As for *Huo Zhi* (Fire Paper / spirit money) and coarse paper, the processes of cutting bamboo, boiling the pulp, and treating with ash lye are all the same as described above. The only difference is that after being couched from the mould, these papers are not dried over a fire. They are simply pressed to remove water and then dried in the sun."

        "盛唐時，鬼神事繁，以紙錢代焚帛（北方用切條，名曰板錢），故造此者，名曰火紙。"
        -> "During the High Tang dynasty, spiritual affairs were abundant. Paper money began to be burned as a substitute for silk cloth (in the north, cut strips were used, called *Ban Qian*). Thus, paper made for this purpose was named *Huo Zhi*."

        "荊楚近俗，有一焚侈至千斤者。此紙十七供冥燒，十三供日用。"
        -> "In the modern custom of the Jing-Chu region, a single burning ceremony might consume as much as a thousand *jin* of paper. Roughly 70% of this paper is used for spiritual burning, and 30% for daily use."

        "其最粗而厚者，名曰包裹紙，則竹麻和宿田晚稻稿所為也。"
        -> "The coarsest and thickest type is called *Bao Guo Zhi* (Wrapping Paper). It is made by mixing bamboo pulp with straw from last year's late rice crop."

        "若鉛山諸邑所造柬紙，則全用細竹料厚質蕩成，以射重價。"
        -> "As for the *Jian Zhi* (Letter Paper) made in places like Yanshan, it is entirely made from fine bamboo material, formed into a thick sheet, and commands a high price."

        "最上者曰官柬。富貴之家，通刺用之，其紙敦厚而無筋膜；"
        -> "The highest quality is *Guan Jian* (Official Letter Paper). The wealthy and influential use it for their visiting cards and correspondence. This paper is thick and pure, without any fiber bundles or knots."

        "染紅為吉柬，則先以白礬水染過，後上紅花汁雲。"
        -> "To make red *Ji Jian* (Auspicious Letter Paper), the paper is first treated with an alum solution, and then dyed with the juice of safflower petals."

        "造皮紙"
        -> "Making Bark Paper"

        Let's refine the translation to make sure it reads well.
        "事出南方，而閩省獨專其盛" -> "The craft of making bamboo paper is found in the south, but the province of Fujian is particularly renowned for its prosperity in this industry."
        "看視山窩深淺" -> "one examines the mountain valleys (suggesting different varieties of bamboo grow at different depths/elevations)". Maybe just "examines the bamboo groves". The literal meaning "looks at the depth of the mountain hollows" might be a bit opaque. Actually, it might mean they vary the processing based on the location, or just go to the valleys. Let's keep it simple: "The location of the bamboo groves in the mountain valleys is inspected."

        "其竹以將生枝葉者為上料" -> "The best raw material is bamboo that is about to sprout branches and leaves."

        "節界芒種" -> "Around the time of the Mangzhong solar term (Grain in Ear, early June)". The parenthetical is good.

        "就於本山開塘一口，註水其中漂浸" -> "a pond is dug on the mountain itself, filled with water for soaking the bamboo."

        "用竹梘通引，不斷瀑流註入。" -> "bamboo pipes/flumes are used to channel a constant flow of water from a waterfall into it."

        "浸至百日之外" -> "After soaking for over a hundred days"

        "加功槌洗" -> "it is thoroughly beaten and washed"

        "洗去粗殼與青皮（是名殺青）" -> "to remove the rough outer rind and the green skin (this process is called "sha qing" – literally "killing the green")."

        "其中竹穰形同苎麻樣" -> "The remaining bamboo pulp (or fiber, "rang" meaning pith or inner material) resembles ramie (Boehmeria nivea) in texture and appearance."

        "用上好石灰化汁塗漿" -> "High-quality lime is dissolved into a milky liquid, which is then thoroughly mixed with the pulp."

        "入楻桶下煮" -> "The pulp is placed into a *huang* (a large circular steamer vat) and boiled. (The vat is placed on top of the cauldron)."

        "火以八日八夜為率" -> "The fire is maintained for eight full days and nights."

        "凡煮竹，下鍋用徑四尺者" -> "For boiling bamboo, the lower cauldron used has a diameter of about four *chi*."

        "鍋上泥與石灰捏弦，高闊如廣中煮鹽牢盆樣" -> "A rim made from a mixture of mud and lime is built up around the top of the cauldron. It is constructed tall and wide, resembling the salt-boiling pans used in Guangdong."

        "中可裁水十餘石" -> "It can hold over ten *dan* of water."

        "上蓋楻桶，其圍丈五尺，其徑四尺餘。" -> "A large wooden *huang* barrel is placed over this. It has a circumference of one *zhang* and five *chi* and a diameter of over four *chi*."

        "蓋定受煮，八日已足。" -> "Once the lid is secured and the boiling begins, eight days is sufficient."

        "歇火一日，揭楻取出竹麻，入清水漂塘之內洗淨。" -> "The fire is allowed to die down for a day. The *huang* is uncovered, and the bamboo pulp (bamboo hemp, *zhu ma*) is taken out and thoroughly washed in a clear water pond."

        "其塘底面、四維皆用木板合縫砌完，以妨泥汙（造粗紙者不須為此）。" -> "The bottom and all four sides of this pond are lined with tightly joined wooden boards to prevent mud from dirtying the pulp (this step is unnecessary for making coarse paper)."

        "洗淨，用柴灰漿過，再入釜中，其上按平，平鋪稻草灰寸許。" -> "After washing, the pulp is mixed with a wood ash lye (slurry). It is then returned to a cauldron (or vat), pressed flat, and covered with rice straw ash to a depth of about one *cun*."

        "桶內水滾沸，即取出別桶之中，仍以灰汁淋下。" -> "When the water in the vat boils, the pulp is quickly transferred to another vat. The alkaline ash liquid (lye) is still poured over it."

        "倘水冷，燒滾再淋。如是十餘日，自然臭爛。" -> "If the liquid cools down, it is heated to a boil and poured over again. After ten or so days of this process, the fibers naturally become thoroughly decomposed and soft (literally, 'rotten')."

        "取出入臼受舂（山國皆有水碓），舂至形同泥面，傾入槽內。" -> "The pulp is taken out and beaten in a mortar. (Mountainous regions commonly use water-powered trip-hammers, *shuidui*, for this). It is beaten until it has the consistency of wet mud, and then poured into the preparation vat."

        "凡抄紙槽，上合方半，尺寸闊狹，槽視簾，簾視紙。" -> "The papermaking vat is roughly square or rectangular in shape. The width of the vat determines the size of the mould screen, and the screen size determines the dimensions of the final paper."

        "竹麻已成，槽內清水浸浮其面三寸許，入紙藥水汁於其中（形同桃竹葉，方語無定名），則水幹自成潔白。" -> "Once the bamboo pulp is ready, it is suspended in clear water in the vat, floating in a layer about three *cun* deep. A 'paper drug' liquid is added to the vat (the plant looks like a peach/bamboo leaf, with local names varying). This ensures that when the water drains, the fibers bond into a clean, white sheet."

        "凡抄紙簾，用刮磨絕細竹絲編成。展捲張開時，下有縱橫架匡。" -> "The papermaking mould screen is woven from extremely fine, scraped and polished bamboo strips. When it is mounted and stretched for use, it is placed on a frame with a supporting lattice structure beneath."

        "兩手持簾入水，蕩起竹麻，入於簾內。" -> "Holding the mould with both hands, the worker dips it into the vat. The pulp is agitated and suspended in the water, and evenly distributed over the screen."

        "厚薄由人手法，輕蕩則薄，重蕩則厚。" -> "The thickness of the paper is controlled by the worker's technique: a light shaking motion produces thin paper, while vigorous shaking produces thick paper."

        "竹料浮簾之頃，水從四際淋下槽內，然後覆簾，落紙於板上，疊積千萬張。" -> "As the bamboo fibers settle on the screen, the water drains from all sides back into the vat. The mould is then overturned, depositing the wet sheet onto a wooden board. Sheets are stacked in this way, accumulating in the thousands."

        "數滿，則上以板壓，俏繩入棍，如榨酒法，使水氣淨盡流幹。" -> "When the stack reaches a suitable height, a board is placed over it. A lever is inserted into ropes bound around the stack, creating pressure similar to pressing wine lees. This squeezes the remaining water out completely."

        "然後，以輕細銅鑷逐張揭起、焙乾。" -> "After pressing, each sheet is carefully lifted from the stack using fine, light copper tweezers and taken to be dried over a fire."

        "凡焙紙，先以土磚砌成夾巷，下以磚蓋巷地面，數塊以往，即空一磚。" -> "For drying the paper, a double-walled corridor is built from earthen bricks. The floor of this corridor is paved with bricks, but every few bricks are left out, creating a gap."

        "火薪從頭穴燒發，火氣從磚隙透巷，外磚盡熱。" -> "A fire is lit in the combustion chamber at one end of the corridor. The heat and smoke are channeled through the gaps under the bricks, heating the floor of the corridor until all the outer bricks are hot."

        "濕紙逐張貼上焙乾，揭起成帙。" -> "The wet sheets are pasted one by one onto the hot brick wall or floor surface to dry. Once dry, they are peeled off and collected into quires (bundles)."

        "近世闊幅者，名大四連，一時書文貴重。" -> "In recent times, a wide-format paper called *Da Si Lian* (Big Four Connection) has become highly valued for printing and writing."

        "其廢紙，洗去朱墨污穢，浸爛，入槽再造，全省從前煮浸之力，依然成紙，耗亦不多。" -> "Waste paper has the vermilion ink and dirt washed off, is soaked until it falls apart, and is then mixed into a new vat for re-making paper. This process entirely saves the previous work of boiling and soaking raw bamboo, and very little fiber is lost."

        "南方竹賤之國，不以為然。北方即寸條片角在地，隨手拾取再造，名曰還魂紙。" -> "In the south, where bamboo is cheap, this recycling is not common. In the north, however, even a strip or scrap of paper on the ground is picked up and re-pulped. This is called *Huan Hun Zhi* (Revived Soul Paper)."

        "竹與皮，精與粗，皆同之也。" -> "The same principle applies whether the paper is made from bamboo or bark, fine material or coarse."

        "若火紙、糙紙，斬竹煮麻，灰漿水淋，皆同前法，唯脫簾之後，不用烘焙，壓水去濕，日曬成幹而已。" -> "As for *Huo Zhi* (Fire Paper / spirit money) and *Cao Zhi* (Rough Paper), the methods of cutting bamboo, boiling the pulp, and treating with ash lye are exactly the same. The only difference is that after the sheets are couched from the mould, they are not dried over a fire. The water is simply pressed out, and the paper is left to dry in the sun."

        "盛唐時，鬼神事繁，以紙錢代焚帛（北方用切條，名曰板錢），故造此者，名曰火紙。" -> "During the High Tang dynasty, customs regarding spirits and ancestors were widespread. Paper money came to be burned as a substitute for silk cloth (in the north, cut strips were used, called *Ban Qian*). Thus, paper made specifically for this purpose was named *Huo Zhi*."

        "荊楚近俗，有一焚侈至千斤者。此紙十七供冥燒，十三供日用。" -> "In the modern customs of the Jing-Chu region, a single burning might lavishly consume as much as a thousand *jin* of paper. Roughly 70% of this paper is used for spiritual offerings, and 30% for daily practical use."

        "其最粗而厚者，名曰包裹紙，則竹麻和宿田晚稻稿所為也。" -> "The coarsest and thickest type is called *Bao Guo Zhi* (Wrapping Paper). It is made by mixing bamboo pulp with the straw from last year's late rice crop."

        "若鉛山諸邑所造柬紙，則全用細竹料厚質蕩成，以射重價。" -> "As for the *Jian Zhi* (Stationery / Letter Paper) made in counties like Yanshan, it is entirely formed from fine bamboo material. It is made thick and sturdy to command a high price."

        "最上者曰官柬。富貴之家，通刺用之，其紙敦厚而無筋膜；" -> "The highest grade is called *Guan Jian* (Official Letter Paper). Wealthy and noble families use it for their name cards and correspondence. This paper is thick, rich in texture, and free from fiber clumps or specks."

        "染紅為吉柬，則先以白礬水染過，後上紅花汁雲。" -> "To make red *Ji Jian* (Auspicious Letter Paper), the paper is first treated with an alum solution, and is then dyed with the juice of safflower petals."

        "造皮紙" -> "([Next section:] Making Bark Paper)"

        Let's check if the user wants a translation of the whole thing including the header. The prompt says "素材来源：《天工開物》节选：造竹紙". The text in the prompt ends with "造皮紙". Translating the entire block exactly as given is the safest.

        Is there any cultural point that needs a very short parenthetical that is missing? "殺青" -> "killing the green". "紙藥" -> "paper drug". "形同桃竹葉" -> "looks like peach or bamboo leaves". "山國" -> "mountainous regions". "水碓" -> "water-powered trip hammer". "冉冉" not in text. "無定名" -> "no fixed name". "紙藥" -> "sizing liquid" (from *Tiangong Kaiwu* context, it acts as a dispersant / sizing agent).

        Let's review the final text to ensure it flows naturally in modern English while being completely faithful.

        "The making of bamboo paper is carried out in the south, but Fujian province is especially preeminent in this craft. When the bamboo shoots have grown, the mountain hollows are inspected. The best raw material is bamboo that is about to grow branches and leaves. Around the Grain in Ear (Mangzhong) solar term, the workers go into the mountains to cut the bamboo. It is chopped into lengths of five to seven *chi* (roughly 1.7–2.3 m). A pond is dug right there on the mountain, which is filled with water to soak the bamboo. To prevent the pond from drying out, bamboo flumes are used to channel a continuous flow of water from a stream into it. After soaking for over a hundred days, the bamboo is beaten and washed to remove the rough outer rind and the green skin (this step is called *sha qing*, 'killing the green'). The inner pulp now resembles ramie fiber. High-quality lime is dissolved into a milky liquid and mixed with the pulp. This is placed into a *huang* (a large steamer vat) and boiled over a fire for eight full days and nights.

        For boiling the bamboo, a lower cauldron with a diameter of four *chi* is used. A rim is built around its top using a paste of mud and lime, making it tall and wide, resembling the salt boiling pans of Guangdong. It can hold over ten *dan* of water. A large wooden *huang* barrel is placed over this. Its circumference is one *zhang* and five *chi*, and its diameter is over four *chi*. The lid is sealed, and the boiling proceeds; eight days is sufficient. After the fire is allowed to go out for one day, the *huang* is uncovered and the bamboo pulp (bamboo hemp) is taken out. It is washed clean in a clear water pond. The bottom and all sides of this pond are lined with tightly joined wooden boards to prevent contamination from mud (this is not necessary for making coarse paper). After washing, the pulp is mixed with a wood ash lye and returned to a cauldron. It is leveled and covered with an inch-thick layer of rice straw ash. When the water in the vat boils, the pulp is taken out and transferred to another vat, where the ash lye is poured over it again. If the liquid cools, it is heated to a boil and poured over again. After about ten days of this, the bamboo naturally becomes completely decomposed. The pulp is taken out and placed into a mortar for pounding. Mountainous regions all use water-powered trip hammers (*shuidui*) for this. The pulp is beaten until it has the consistency of mud, and then poured into the preparation vat.

        The papermaking vat has a roughly square or rectangular opening. Its width depends on the mould screen, and the screen depends on the size of the paper desired. The bamboo pulp is suspended in clear water in the vat to a depth of about three *cun*. A 'paper drug' liquid is added to the vat (the plant leaves resemble those of a peach or a specific bamboo, with local names varying). This makes the water drain cleanly, leaving bright white paper. The papermaking mould screen is woven from very finely scraped and polished bamboo strips. When it is mounted, it is stretched over a frame with a supporting lattice beneath. Holding the mould with both hands, the worker dips it into the water and agitates the pulp, allowing the fibers to settle onto the screen. Thickness depends entirely on the worker's skill: a gentle shake produces thin paper, a vigorous shake produces thick paper. As the bamboo fibers float on the screen, the water drains from all sides back into the vat. The mould is then overturned, depositing the wet sheet on a board. Sheets are stacked up in this way, accumulating in the thousands. When the stack is high enough, a board is placed on top. Ropes are bound around the stack and a lever is inserted, exactly like pressing wine lees, to squeeze out all the remaining water. Then, using fine, light copper tweezers, the sheets are lifted one by one and dried over a fire.

        For drying paper, a double-walled corridor is built from earthen bricks. The floor of the corridor is paved with bricks, but every few bricks are left out to create gaps. A fire is lit at one end of this channel. The heat and smoke travel through the gaps under the floor, heating all the bricks in the corridor. The wet sheets are pasted one by one onto the hot brick wall to dry. Once dry, they are peeled off and collected into quires.

        In recent times, a wide format paper called *Da Si Lian* (Big Four Connection) has become highly valued for writing and printing. Waste paper is washed to remove vermilion ink and dirt, soaked until rotten, and returned to the vat to be re-made into paper. This entirely saves the previous work of boiling and soaking the raw bamboo material, and very little is lost. In the south, where bamboo is cheap, this is not considered worthwhile. In the north, however, even a scrap of paper found on the ground is picked up and recycled. This is called *Huan Hun Zhi* (Revived Soul Paper). This applies to both bamboo paper and bark paper, fine paper and coarse paper.

        As for *Huo Zhi* (Fire Paper / spirit money) and coarse paper, the processes of cutting bamboo, boiling the pulp, and treating with ash lye are exactly the same. The only difference is that after being couched from the mould, they are not dried over a fire. They are simply pressed to remove the water and dried in the sun. During the High Tang dynasty, there were many religious and funerary ceremonies, and paper money came to be burned in place of silk cloth (in the north, cut strips were used, called *Ban Qian*). Hence, paper made for this purpose was called *Huo Zhi*. In the modern customs of the Jing-Chu region, a single burning might lavishly consume as much as a thousand *jin* of this paper. About 70% is used for spiritual burning, and 30% for daily use.

        The coarsest and thickest type is called *Bao Guo Zhi* (Wrapping Paper). It is made by mixing bamboo pulp with the straw from last year's late rice crop. The letter paper made in counties like Yanshan is entirely formed from fine bamboo material to produce a thick, sturdy sheet that commands a high price. The highest grade is called *Guan Jian* (Official Letter Paper). Wealthy and noble families use it for their visiting cards and correspondence. This paper is thick and rich, without any fiber specks or knots. To make red *Ji Jian* (Auspicious Letter Paper), the paper is first treated with an alum solution and then dyed with the juice of safflower petals.

        ([Next chapter:] Making Bark Paper)"

        Looks solid. Clean, modern, careful translation. Represents the original closely. No unwarranted expansions. Parentheticals are completely justified.

        I will format it nicely for the user. The user specified "忠实保留工序、材料、时间和因果关系；必要时可用括号给出极短解释；不要扩写为百科文章。"

        Check: "dry in the sun", "press to remove water", "70% for spiritual burning", "30% for daily use", "eight days and nights", "ten days", "solar term", "chi", "cun", "jin", "dan". The units are kept and explained if necessary. The parentheticals (sha qing, bamboos flumes, sizing liquid etc) are present only when necessary.

        Double check the "造皮紙" at the end. The user might find it extraneous, but since it's in the prompt text, I will translate it and bracket it to show it's the header of the next section. Ah, looking back at the original text: "染紅為吉柬，則先以白礬水染過，後上紅花汁雲。\n\n造皮紙". This is exactly the end of the Bamboo Paper chapter. Many editions have the next chapter header starting right after. I will include it but clearly demarcate it as the start of the next chapter.

        Everything looks good. Ready to generate the final translation.
```

## Assistant

```markdown
The making of bamboo paper is carried out in the south, but Fujian province is especially preeminent in this craft. When the bamboo shoots have grown, the mountain hollows are inspected. The best raw material is bamboo that is about to grow branches and leaves. Around the Grain in Ear (Mangzhong) solar term, the workers go into the mountains to cut the bamboo. It is chopped into lengths of five to seven *chi* (roughly 1.7–2.3 m). A pond is dug right there on the mountain, which is filled with water to soak the bamboo. To prevent the pond from drying out, bamboo flumes are used to channel a continuous flow of water from a stream into it. After soaking for over a hundred days, the bamboo is beaten and washed to remove the rough outer rind and the green skin (this step is called *sha qing*, "killing the green"). The inner pulp now resembles ramie fiber. High-quality lime is dissolved into a milky liquid and mixed with the pulp. This is placed into a *huang* (a large steamer vat) and boiled over a fire for eight full days and nights.

For boiling the bamboo, a lower cauldron with a diameter of four *chi* is used. A rim is built around its top using a paste of mud and lime, making it tall and wide, resembling the salt-boiling pans of Guangdong. It can hold over ten *dan* of water. A large wooden *huang* barrel is placed over this. Its circumference is one *zhang* and five *chi*, and its diameter is over four *chi*. The lid is sealed, and the boiling proceeds; eight days is sufficient. After the fire is allowed to go out for one day, the *huang* is uncovered and the bamboo pulp (bamboo hemp) is taken out. It is washed clean in a clear water pond. The bottom and all sides of this pond are lined with tightly joined wooden boards to prevent contamination from mud (this is not necessary for making coarse paper). After washing, the pulp is mixed with a wood ash lye and returned to a cauldron. It is leveled and covered with an inch-thick layer of rice straw ash. When the water in the vat boils, the pulp is taken out and transferred to another vat, where the ash lye is poured over it again. If the liquid cools, it is heated to a boil and poured over again. After about ten days of this, the bamboo naturally becomes completely decomposed. The pulp is taken out and placed into a mortar for pounding. Mountainous regions all use water-powered trip hammers (*shuidui*) for this. The pulp is beaten until it has the consistency of mud, and then poured into the preparation vat.

The papermaking vat has a roughly square or rectangular opening. Its width depends on the mould screen, and the screen depends on the size of the paper desired. The bamboo pulp is suspended in clear water in the vat to a depth of about three *cun*. A "paper drug" liquid is added to the vat (the plant leaves resemble those of a peach or a specific local bamboo, names vary by region). This makes the water drain cleanly, leaving bright white paper. The papermaking mould screen is woven from very finely scraped and polished bamboo strips. When it is mounted, it is stretched over a frame with a supporting lattice beneath. Holding the mould with both hands, the worker dips it into the water and agitates the pulp, allowing the fibers to settle onto the screen. Thickness depends entirely on the worker's skill: a gentle shake produces thin paper, a vigorous shake produces thick paper. As the bamboo fibers float on the screen, the water drains from all sides back into the vat. The mould is then overturned, depositing the wet sheet on a board. Sheets are stacked up in this way, accumulating in the thousands. When the stack is high enough, a board is placed on top. Ropes are bound around the stack and a lever is inserted, exactly like pressing wine lees, to squeeze out all the remaining water. Then, using fine, light copper tweezers, the sheets are lifted one by one and dried over a fire.

For drying paper, a double-walled corridor is built from earthen bricks. The floor of the corridor is paved with bricks, but every few bricks are left out to create gaps. A fire is lit at one end of this channel. The heat and smoke travel through the gaps under the floor, heating all the bricks in the corridor. The wet sheets are pasted one by one onto the hot brick wall to dry. Once dry, they are peeled off and collected into quires.

In recent times, a wide-format paper called *Da Si Lian* (Big Four Connection) has become highly valued for writing and printing. Waste paper is washed to remove vermilion ink and dirt, soaked until rotten, and returned to the vat to be re-made into paper. This entirely saves the previous work of boiling and soaking the raw bamboo material, and very little is lost. In the south, where bamboo is cheap, this is not considered worthwhile. In the north, however, even a scrap of paper found on the ground is picked up and recycled. This is called *Huan Hun Zhi* (Revived Soul Paper). This applies equally to bamboo paper and bark paper, fine paper and coarse paper.

As for *Huo Zhi* (Fire Paper / spirit money) and rough paper, the processes of cutting bamboo, boiling the pulp, and treating with ash lye are exactly the same. The only difference is that after being couched from the mould, they are not dried over a fire. They are simply pressed to remove the water and dried in the sun. During the High Tang dynasty, customs regarding spirits and ancestors were widespread, and paper money was burned as a substitute for silk cloth (in the north, cut strips were used, called *Ban Qian*). Hence, paper made for this purpose was called *Huo Zhi*. In the modern customs of the Jing-Chu region, a single burning might lavishly consume as much as a thousand *jin* of this paper. About 70% of this paper goes to spiritual offerings, and 30% for daily use.

The coarsest and thickest type is called *Bao Guo Zhi* (Wrapping Paper). It is made by mixing bamboo pulp with the straw from last year's late rice crop. The letter paper made in counties like Yanshan is entirely formed from fine bamboo material to produce a thick, sturdy sheet that commands a high price. The highest grade is called *Guan Jian* (Official Letter Paper). Wealthy and noble families use it for their visiting cards and correspondence. This paper is thick and rich in texture, without any fiber specks or knots. To make red *Ji Jian* (Auspicious Letter Paper), the paper is first treated with an alum solution and then dyed with the juice of safflower petals.

[Next section:] Making Bark Paper
```
