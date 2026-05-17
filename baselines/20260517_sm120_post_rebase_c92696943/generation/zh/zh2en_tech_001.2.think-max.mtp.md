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
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 73.055088
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 1112, "total_tokens": 13822, "completion_tokens": 12710, "prompt_tokens_details": null}`
- Prompt tokens: 1112
- Completion tokens: 12710
- Total tokens: 13822

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
    *   **Task:** Translate traditional Chinese technical text about ancient papermaking (from *Tiangong Kaiwu* section on bamboo paper) into English.
    *   **Style:** Not archaic/florid, but understandable for a modern English reader. Faithful to processes, materials, time, and causality. Extremely short explanatory parentheticals if necessary. No expansion into an encyclopedia article.
    *   **Source:** *Tiangong Kaiwu*, "Creating Bamboo Paper".
    *   **Permission:** Public domain in the USA (Project Gutenberg).

2.  **Structure the Translation:**
    *   The text is a dense procedural description of traditional bamboo papermaking.
    *   I need to break it down into logical English sentences and paragraphs while preserving the sequence.
    *   **Key terms:**
        *   造竹紙: Making bamboo paper. (Keep consistent: "making bamboo paper")
        *   事出南方，而閩省獨專其盛 (Originated in the south, but Fujian province particularly excels/thrives in it).
        *   筍生之後: After the bamboo shoots have grown.
        *   將生枝葉者: Bamboo about to grow branches/leaves.
        *   節界芒種: Around the time of *Mangzhong* (Grain in Ear, a solar term, roughly early June).
        *   砍伐: Cut down.
        *   截斷五、七尺長: Cut into lengths of 5 to 7 *chi* (approx. 1.7 to 2.3 meters).
        *   開塘一口: Dig a pit/pond.
        *   註水其中漂浸: Fill it with water to soak/steep the bamboo. (Steeping, retting).
        *   竹梘通引: Bamboo pipes/aqueducts to channel flowing water.
        *   百日之外: Over 100 days.
        *   加功槌洗: Work it, pound and wash.
        *   粗殼與青皮 (殺青): Rough outer layer and green skin (this is "killing the green" / *shāqīng*).
        *   竹穰形同苎麻樣: The inner pith/bast fibers resemble ramie/hemp.
        *   上好石灰化汁塗漿: Make a slurry from high-quality quicklime, apply/dip it.
        *   入楻桶下煮: Put in the steamer vat/bucket and cook below.
        *   火以八日八夜為率: Standard is to fire it for eight days and eight nights.
        *   煮竹: Boiling the bamboo.
        *   下鍋用徑四尺者: The pan/cauldron is four *chi* in diameter.
        *   鍋上泥與石灰捏弦: The rim is built up with mud and lime.
        *   高闊如廣中煮鹽牢盆樣: Like the salt-boiling pans in Guangdong/Guangxi.
        *   中可裁水十餘石: Holds over 10 *dan* (a unit of volume, ~100 liters) of water.
        *   上蓋楻桶: The bucket is placed on top as a lid/cover.
        *   其圍丈五尺: Circumference ~1.5 *zhang* (5 meters).
        *   其徑四尺餘: Diameter ~4 *chi* (~1.3 meters).
        *   歇火一日: Rest one day (cool down).
        *   揭楻取出竹麻: Lift the bucket, take out the bamboo pulp (竹麻, bamboo pulp/fiber).
        *   入清水漂塘之內洗淨: Wash in a clear water tank.
        *   塘底面、四維皆用木板合縫砌完: The tank's bottom and sides are made of tightly joined wooden planks.
        *   以妨泥汙: To prevent mud contamination.
        *   造粗紙者不須為此: Those making coarse paper don't need to do this.
        *   洗淨，用柴灰漿過: After washing, re-slurry with plant ash / wood ash lye.
        *   再入釜中: Put into a pot/cauldron again.
        *   其上按平，平鋪稻草灰寸許: Spread flat, lay a layer of rice straw ash on top.
        *   桶內水滾沸，即取出別桶之中...: When the water in the bucket boils, take the fibers out and put them in another bucket... pouring the lye over them.
        *   如是十餘日，自然臭爛: After 10+ days of this, it naturally rots and disintegrates.
        *   取出入臼受舂 (山國皆有水碓): Take it out to be pounded in a mortar (mountainous regions have water-powered trip-hammers).
        *   舂至形同泥面: Pound until it looks like mud/paste.
        *   傾入槽內: Pour into the vat.
        *   抄紙槽: Papermaking vat (stuff chest).
        *   上合方半: ...
        *   尺寸闊狹，槽視簾，簾視紙: The size of the vat depends on the mold (簾, screen/mould), and the mold depends on the paper size.
        *   入紙藥水汁於其中 (形同桃竹葉，方語無定名): Add the "paper medicine" (a streaming agent/surfactant, mucilage from a plant resembling peach/bamboo leaves, local names vary).
        *   則水幹自成潔白: The water drains away leaving pure white (paper/fibers).
        *   抄紙簾: Papermaking mold (woven bamboo screen).
        *   用刮磨絕細竹絲編成: Made of very finely scraped and polished bamboo strips.
        *   展捲張開時，下有縱橫架匡: Supported by a frame.
        *   兩手持簾入水，蕩起竹麻: Take the mold in both hands, dip it in the vat, and shake/swirl to lift and distribute the pulp.
        *   厚薄由人手法，輕蕩則薄，重蕩則厚: Thickness depends on the craftsman's skill; a lighter shake makes thin paper, a stronger shake makes thick paper.
        *   竹料浮簾之頃: When the bamboo fibers float on the mold.
        *   水從四際淋下槽內: Water drains from the four sides back into the vat.
        *   覆簾，落紙於板上: Flip the mold to deposit the wet sheet onto a board.
        *   疊積千萬張: Stack thousands of sheets.
        *   數滿: When the pile reaches a certain height.
        *   上以板壓，俏繩入棍，如榨酒法: Press with a board, tighten with ropes and sticks like a wine press.
        *   使水氣淨盡流幹: Squeeze out all excess water.
        *   以輕細銅鑷逐張揭起: Lift each sheet with fine copper tweezers/forceps.
        *   焙乾: Dry on a heated wall / drying stove.
        *   焙紙: Drying paper.
        *   先以土磚砌成夾巷: Build a double wall / flue of bricks.
        *   下以磚蓋巷地面，數塊以往，即空一磚: Brick floor of the flue, with gaps.
        *   火薪從頭穴燒發: Fire is lit at the mouth of the flue.
        *   火氣從磚隙透巷，外磚盡熱: Heat flows through the flue, heating the bricks on the outside.
        *   濕紙逐張貼上焙乾，揭起成帙: Wet paper is pasted on the hot wall to dry, then taken off as a finished quire.
        *   近世闊幅者，名大四連: Wide paper is called "Large Four-joint".
        *   一時書文貴重: Prized for writing and printing.
        *   其廢紙，洗去朱墨污穢，浸爛，入槽再造: Waste paper can be washed, soaked, pulped, and remade.
        *   全省從前煮浸之力: Saves the entire effort of the earlier cooking and soaking.
        *   耗亦不多: Little material is wasted/lost.
        *   南方竹賤之國，不以為然: In southern regions where bamboo is cheap, this isn't considered significant.
        *   北方即寸條片角在地，隨手拾取再造，名曰還魂紙: In the north, even tiny scraps are picked up to be remade; called "recycled paper" (spirit paper).
        *   竹與皮，精與粗，皆同之也: Bamboo and bast fibers, refined and coarse papers, all share the same principles.
        *   火紙、糙紙: Fire paper (for burning as offerings), coarse paper.
        *   斬竹煮麻，灰漿水淋，皆同前法: Cutting bamboo, boiling pulp, lye treatment all same.
        *   唯脫簾之後，不用烘焙，壓水去濕，日曬成幹而已: Only difference is that after being taken off the mold, they aren't dried on the hot wall. They are pressed and sun-dried.
        *   盛唐時，鬼神事繁，以紙錢代焚帛: In the High Tang, rituals for spirits were elaborate; paper money replaced burning silk.
        *   北方用切條，名曰板錢: In the north, cut strips called *banqian*.
        *   此紙十七供冥燒，十三供日用: 70% of this paper is used for burning to the dead, 30% for daily use.
        *   包裹紙: Wrapping paper.
        *   竹麻和宿田晚稻稿所為也: Made from bamboo pulp mixed with rice straw from late-harvest fields.
        *   鉛山諸邑所造柬紙: Note paper made by Yanshan county.
        *   全用細竹料厚質蕩成: Entirely from fine bamboo pulp, thick sheets.
        *   以射重價: To command a high price.
        *   最上者曰官柬: The highest grade is called Official Note (*guanjian*).
        *   富貴之家，通刺用之: Wealthy families use it for calling cards.
        *   其紙敦厚而無筋膜: The paper is thick and substantial, without fiber knots/streaks.
        *   染紅為吉柬: Dyed red for auspicious greetings.
        *   先以白礬水染過，後上紅花汁云: First treated with alum water, then dyed with a red safflower infusion.

3.  **Translating the Text (Step-by-Step):**

    *   *Opening lines:*
        凡造竹紙，事出南方，而閩省獨專其盛。
        -> Papermaking from bamboo originated in the south, and Fujian province is particularly famous for its abundance and quality.
        (Refine: The general making of bamboo paper is undertaken in the south, but Fujian province alone holds a monopoly on its prosperity / holds the most thriving industry.)

    *   *Bamboo selection & cutting:*
        當筍生之後，看視山窩深淺，其竹以將生枝葉者為上料。節界芒種，則登山砍伐，截斷五、七尺長，就於本山開塘一口，註水其中漂浸。恐塘水有涸時，則用竹梘通引，不斷瀑流註入。
        -> After the bamboo shoots have grown, the density/depth of the bamboo in the mountain valleys is assessed. Bamboo that is on the verge of sprouting branches and leaves is considered the best raw material. Around the *Mangzhong* (Grain in Ear, early June) solar term, the bamboo is felled on the mountain. It is cut into lengths of 5 to 7 *chi* (~1.6 to 2.3 meters). A pit is dug on the mountain itself, and water is channeled into it to steep the bamboo. To prevent the pit water from drying up, bamboo pipes are used to bring a continuous stream of flowing water.

    *   *First soaking & cleaning:*
        浸至百日之外，加功槌洗，洗去粗殼與青皮（是名殺青），其中竹穰形同苎麻樣。用上好石灰化汁塗漿，入楻桶下煮，火以八日八夜為率。
        -> After steeping for over a hundred days, the bamboo is pounded and washed to remove the rough outer shell and green skin (this process is called *shāqīng*, "killing the green"). The inner bamboo pith/bast effectively resembles ramie fibers. A slurry is made from high-quality quicklime, and the fibers are coated with it. This is placed into a steam vat (楻桶) and cooked below, with the standard fire time being eight days and eight nights.

    *   *Cooking apparatus & process:*
        凡煮竹，下鍋用徑四尺者，鍋上泥與石灰捏弦，高闊如廣中煮鹽牢盆樣，中可裁水十餘石。上蓋楻桶，其圍丈五尺，其徑四尺餘。蓋定受煮，八日已足。歇火一日，揭楻取出竹麻，入清水漂塘之內洗淨。其塘底面、四維皆用木板合縫砌完，以妨泥汙（造粗紙者不須為此）。洗淨，用柴灰漿過，再入釜中，其上按平，平鋪稻草灰寸許。桶內水滾沸，即取出別桶之中，仍以灰汁淋下。倘水冷，燒滾再淋。如是十餘日，自然臭爛。取出入臼受舂（山國皆有水碓），舂至形同泥面，傾入槽內。
        -> The cauldron for boiling the bamboo is four *chi* in diameter. Its rim is built up with mud and lime, making it tall and wide, just like the salt-boiling pans used in Guangdong. It can hold over ten *dan* of water. The vat is placed on top as a lid. The vat has a circumference of one *zhang* and five *chi* (~5 meters) and a diameter of over four *chi* (~1.3 m). Once sealed for boiling, eight days is sufficient. The fire is stopped for one day. The vat is opened, and the bamboo pulp (竹麻) is taken out and washed in a clear water tank. The tank's bottom and sides are constructed of tightly joined wooden planks to prevent mud contamination (those making coarse paper don't need this). After washing, the pulp is re-slurried in wood ash lye, and placed back into a cauldron. It is leveled flat, and a one-*cun* layer of rice straw ash is spread on top. When the water in the bucket boils, the fibers are dipped out into another bucket, and the ash lye is poured over them again. If the lye cools, it is boiled and poured over again. After ten or more days of this, the fibers naturally rot and disintegrate. They are then taken out and pounded in a mortar (mountainous regions universally have water-powered trip-hammers). It is pounded until it has the consistency of mud/plaster, and then poured into the vat (stuff chest).

    *   *The Vat & Formation aids:*
        凡抄紙槽，上合方半，尺寸闊狹，槽視簾，簾視紙。竹麻已成，槽內清水浸浮其面三寸許，入紙藥水汁於其中（形同桃竹葉，方語無定名），則水幹自成潔白。
        -> The papermaking vat is rectangular. Its dimensions are determined by the mold (screen), and the mold's size is determined by the desired paper size. Once the bamboo pulp is ready, the vat is filled with clear water to a depth of about three *cun* over the surface of the pulp. A "paper medicine" fluid is added to the vat (made from a plant resembling peach and bamboo leaves—local names vary). This ensures that as the water drains away, the fiber mat forms a pure white sheet.

    *   *The Mold & Forming (Vatman work):*
        凡抄紙簾，用刮磨絕細竹絲編成。展捲張開時，下有縱橫架匡。兩手持簾入水，蕩起竹麻，入於簾內。厚薄由人手法，輕蕩則薄，重蕩則厚。竹料浮簾之頃，水從四際淋下槽內，然後覆簾，落紙於板上，疊積千萬張。
        -> The papermaking mold is woven from very finely scraped and polished bamboo strips. When opened flat, the mold is supported by a horizontal and vertical frame. The vatman takes the mold in both hands, dips it into the vat, and shakes/swirls it to lift the bamboo fibers and settle them evenly on the mold's surface. The thickness of the sheet is determined by the vatman's technique: a light shake produces thin paper, a vigorous shake produces thick paper. As the bamboo fiber mat floats on the mold screen, the water drains from the four sides back into the vat. The mold is then flipped over, depositing the wet sheet onto a board. Thousands upon thousands of sheets are stacked in this way.

    *   *Pressing:*
        數滿，則上以板壓，俏繩入棍，如榨酒法，使水氣淨盡流幹。
        -> When the stack is sufficiently high, a board is placed on top and pressed down. Ropes are tightened around sticks (levers) to compress the stack, exactly like pressing wine, until nearly all the water is squeezed out.

    *   *Lifting & Drying:*
        然後，以輕細銅鑷逐張揭起、焙乾。凡焙紙，先以土磚砌成夾巷，下以磚蓋巷地面，數塊以往，即空一磚。火薪從頭穴燒發，火氣從磚隙透巷，外磚盡熱。濕紙逐張貼上焙乾，揭起成帙。
        -> Afterwards, the sheets are carefully separated and lifted one by one with fine copper tweezers and then dried on the heated wall (焙乾). To build a drying wall, bricks are first arranged to form a double-walled flue/channel. The floor of the flue is also covered with bricks, but with every few bricks, one is omitted to create a gap. Fire is lit at the opening of the flue. The heat and smoke travel through the flue, escaping through the brick gaps, heating the outer brick surface thoroughly. Each wet sheet is pasted onto this hot wall to dry. Once dry, they are taken off as a finished gathering (quire / *zhì*).

    *   *Fine Papers & Recycling:*
        近世闊幅者，名大四連，一時書文貴重。其廢紙，洗去朱墨污穢，浸爛，入槽再造，全省從前煮浸之力，耗亦不多。南方竹賤之國，不以為然。北方即寸條片角在地，隨手拾取再造，名曰還魂紙。竹與皮，精與粗，皆同之也。
        -> In recent times, the wide-sized paper known as the "Large Four-Joint" was highly valued for writing and printing. Waste paper can be washed free of red ink and other stains, soaked until rotten, returned to the vat, and remade into paper. This entirely saves the effort of the previous cooking and steeping stages, and consumption of material is minimal. In the south, where bamboo is plentiful and cheap, this practice is not highly regarded. In the north, even scraps the size of an inch or a corner lying on the ground are picked up and remade; this is called "spirit-returning paper" (recycled paper). Bamboo and bast fibers, fine paper and coarse paper, all share this same basic process.

    *   *Fire Paper & wrapping paper:*
        若火紙、糙紙，斬竹煮麻，灰漿水淋，皆同前法，唯脫簾之後，不用烘焙，壓水去濕，日曬成幹而已。
        -> As for "fire paper" and coarse paper, the cutting of bamboo, boiling of pulp, and treating with ash lye all follow the same methods described above. The only difference is that after being taken off the mold, they are not dried on the heated wall. They are simply pressed to remove water and dried in the sun.

        盛唐時，鬼神事繁，以紙錢代焚帛（北方用切條，名曰板錢），故造此者，名曰火紙。荊楚近俗，有一焚侈至千斤者。此紙十七供冥燒，十三供日用。其最粗而厚者，名曰包裹紙，則竹麻和宿田晚稻稿所為也。
        -> During the High Tang dynasty, religious and superstitious ceremonies were elaborate. Paper money was used to replace the burning of silk cloth (in the north, cut paper strips are used, called *banqian*). Thus this type of paper is called "fire paper" (or spirit paper). In the modern customs of the Chu region, some extravagantly burn up to a thousand catties at a time. 70% of this paper is used for offerings to the dead, and 30% for daily use. The coarsest and thickest type is called wrapping paper, which is made from bamboo pulp mixed with rice straw from late-harvest fields.

    *   *High quality note paper:*
        若鉛山諸邑所造柬紙，則全用細竹料厚質蕩成，以射重價。最上者曰官柬。富貴之家，通刺用之，其紙敦厚而無筋膜；染紅為吉柬，則先以白礬水染過，後上紅花汁云。
        -> The note paper made in places like Yanshan county is made entirely from fine bamboo pulp, formed into a thick, substantial sheet, and fetches a high price. The very highest grade is called Official Note Paper (*Guan Jian*). Wealthy and noble families use it for name cards. The paper is thick and solid, with no fiber streaks or knots. It is dyed red for festive greeting cards (*Ji Jian*). It is first treated with an alum solution, and then dyed with a red safflower pigment infusion.

4.  **Refining the Translation & Language:**
    *   Check for modern clarity.
    *   "事出南方，而閩省獨專其盛": "The manufacture of bamboo paper is practiced throughout the south, but Fujian province especially excels/thrives in it." -> "Papermaking from bamboo is undertaken in the southern regions, but Fujian Province holds a unique prominence in this industry."
    *   "節界芒種": "Around the solar term *Mangzhong* (Grain in Ear)". Adding a brief parenthetical for a modern reader is exactly what the prompt asks. "(芒種 *Mangzhong*, the period around early June when grains are planted)".
    *   "就於本山開塘一口": "A pit/pond is dug right on the mountain".
    *   "竹梘": Bamboo pipes/aqueducts.
    *   "殺青": (*shaqing*, "killing the green", the term used today for finishing a film or manuscript, but literally the process of removing the green skin from bamboo).
    *   "上料": Top-grade raw material.
    *   "入楻桶下煮": The setup seems to be a cauldron with a tall wooden bucket acting as a lid/vat. The *Tiangong Kaiwu* illustration shows this. "Placed into a tall wooden vat (楻桶) which sits on top of a cauldron to be boiled." Let's make this clear. "The material is placed into a large wooden vat set over a cauldron, and boiled from below."
    *   "火以八日八夜為率": "The heating/firing lasts for a standard period of eight days and eight nights."
    *   "鍋上泥與石灰捏弦，高闊如廣中煮鹽牢盆樣": "The rim of the cauldron is raised high with mud and lime, making it tall and wide like the salt-boiling pans of Guangdong" . "牢盆" refers to the official salt-boiling pans.
    *   "中可裁水十餘石": "It can hold over ten shi of water." (1 shi/dan = approx 100 litres, but maybe just say it can hold a vast amount, or "over 1000 litres" for clarity? The prompt says "必要时可用括号给出极短解释", so "ten *shi* (a shi is a unit of volume, roughly 100 litres)" is an option. Better phrasing: "Holding over ten *dan* of water (1 *dan* ~ 100 liters / a large barrel)." Or just say "over a thousand litres of water". But "十餘石" is pretty significant. "over ten shi of water (a shi being a large ancient unit of volume)".
    *   "形同泥面": "until its consistency resembles plaster/mud".
    *   "凡抄紙槽": The vat. "抄紙" is the sheet forming.
    *   "視簾，簾視紙": "depends on the mold, and the mold depends on the paper".
    *   "紙藥水汁": The suspension agent (mucilage) from an unknown plant (*Tiangong Kaiwu* suggests it is from a specific plant, later understood as the extract of *Abelmoschus manihot* or similar, but here just "paper medicine"). "a fluid extract of 'paper medicine' (made from a mucilaginous plant whose local name varies)"
    *   "水幹自成潔白": "this ensures the water drains away and the sheet forms pure white".
    *   "厚薄由人手法，輕蕩則薄，重蕩則厚": Look at the *Tiangong Kaiwu* description of the mould. "The thickness of the paper is controlled by the vatman's skill; a gentle shake produces thin paper, a vigorous shake produces thick paper."
    *   "俏繩入棍，如榨酒法": "threading ropes and inserting sticks to tighten them, exactly like a wine press".
    *   "輕細銅鑷": "fine copper tweezers/forceps".
    *   "焙乾": drying on the heated wall. "dried on a hot wall / drying stove".
    *   "夾巷": double wall / flue.
    *   "數塊以往，即空一磚": "leaving a gap one brick wide for every several bricks laid".
    *   "火氣從磚隙透巷": "the heat and smoke stream out through the brick gaps, heating the wall".
    *   "揭起成帙": "taken off and gathered into quires".
    *   "大四連": "Large Four-Joiner" or "Large Four-Sheet" paper. Standard sizes existed.
    *   "還魂紙": "Spirit-returning paper" / recycled paper.
    *   "宿田晚稻稿": rice straw from the fields of the previous late harvest.
    *   "鉛山諸邑所造柬紙": Note paper from Yanshan district.
    *   "通刺用之": Used for name cards / visiting cards.
    *   "染紅為吉柬": "Dyed red for festive greeting cards".

5.  **Formatting the Output:**
    The text is clearly delimited in the prompt. The target audience is modern English readers. The style must be clear and narrative, revealing the process step-by-step. I will translate the paragraphs as they appear, keeping the logical flow. The prompt says "要求：忠实保留工序、材料、时间和因果关系；必要时可用括号给出极短解释；不要扩写为百科文章".

    Let's translate carefully, sentence by sentence, respecting the ancient technical details.

    *Paragraph 1:*
    凡造竹紙，事出南方，而閩省獨專其盛。
    -> The manufacture of bamboo paper is practiced in the southern regions, but Fujian Province has a unique prominence in its production.

    當筍生之後，看視山窩深淺，其竹以將生枝葉者為上料。
    -> After the bamboo shoots have sprouted, the density of the bamboo forests in the mountain valleys is examined. Bamboo that is about to put forth branches and leaves is selected as the best raw material.

    節界芒種，則登山砍伐，截斷五、七尺長，就於本山開塘一口，註水其中漂浸。
    -> Around the time of the solar term *Mangzhong* (芒種, "Grain in Ear", early June), the bamboo is felled on the mountain, cut into lengths of five to seven *chi* (about 1.7 to 2.3 meters). A pond is dug right on the mountain and filled with water to steep the bamboo.

    恐塘水有涸時，則用竹梘通引，不斷瀑流註入。
    -> To prevent the pond water from drying up, bamboo pipes are used to channel a continuous stream of flowing water into it.

    浸至百日之外，加功槌洗，洗去粗殼與青皮（是名殺青），其中竹穰形同苎麻樣。
    -> After steeping for over a hundred days, the bamboo is worked by pounding and washing to remove the rough outer shell and the green skin (this process is called *shaqing*, "killing the green"). The inner pith/bast fiber now resembles ramie.

    用上好石灰化汁塗漿，入楻桶下煮，火以八日八夜為率。
    -> High-quality quicklime is slaked with water to form a slurry, and the fibers are coated with it. This is placed into a large wooden vat (楻桶) set over a cauldron and boiled, with a standard firing time of eight days and eight nights.

    *Paragraph 2:*
    凡煮竹，下鍋用徑四尺者，鍋上泥與石灰捏弦，高闊如廣中煮鹽牢盆樣，中可裁水十餘石。
    -> For boiling the bamboo, a cauldron four *chi* in diameter is used. Its rim is built up high with mud and lime, resembling the large salt-boiling pans (*laopen*) of Guangdong. It can hold over ten *shi* (石, a unit of volume) of water.

    上蓋楻桶，其圍丈五尺，其徑四尺餘。
    -> The vat placed on top has a circumference of one *zhang* and five *chi* (about 5 meters) and a diameter of over four *chi*.

    蓋定受煮，八日已足。歇火一日，揭楻取出竹麻，入清水漂塘之內洗淨。
    -> Once sealed for boiling, eight days is sufficient. The fire is stopped for one day, then the vat is opened and the bamboo pulp (竹麻, *zhuma*) is taken out and washed in a clear water tank.

    其塘底面、四維皆用木板合縫砌完，以妨泥汙（造粗紙者不須為此）。
    -> The bottom and sides of this tank are constructed of wooden planks joined tightly to prevent mud contamination (those making coarse paper do not need to do this).

    洗淨，用柴灰漿過，再入釜中，其上按平，平鋪稻草灰寸許。
    -> After washing, the fibers are re-slurried with wood ash lye and put back into the cauldron. The surface is leveled flat, and a layer of rice straw ash, about one *cun* thick, is spread on top.

    桶內水滾沸，即取出別桶之中，仍以灰汁淋下。
    -> When the water in the cauldron boils, the fibers are dipped out into another bucket, and the ash lye is poured over them.

    倘水冷，燒滾再淋。如是十餘日，自然臭爛。
    -> If the lye cools, it is boiled again and poured over. After a course of ten-plus days of this treatment, the fibers naturally decompose into a rotten mass.

    取出入臼受舂（山國皆有水碓），舂至形同泥面，傾入槽內。
    -> The pulp is then taken out and beaten in a mortar/mill (mountainous regions universally have water-powered trip-hammers for this), beaten until it has the consistency of wet plaster, and then poured into the forming vat (抄紙槽).

    *Paragraph 3:*
    凡抄紙槽，上合方半，尺寸闊狹，槽視簾，簾視紙。
    -> The papermaking vat is rectangular. The dimensions of the vat are determined by the paper mold (簾), and the size of the mold is determined by the desired paper size.

    竹麻已成，槽內清水浸浮其面三寸許，入紙藥水汁於其中（形同桃竹葉，方語無定名），則水幹自成潔白。
    -> When the bamboo pulp is ready, clear water is added to the vat so it stands about three *cun* above the surface of the pulp. A fluid extract of "paper medicine" (紙藥, an agent made from a plant resembling peach and bamboo leaves, known by various local names) is added to the water. This ensures that when the water drains away, the fibers bind together into a pure white sheet.

    凡抄紙簾，用刮磨絕細竹絲編成。
    -> The paper mold is woven from very finely scraped and polished bamboo strips.

    展捲張開時，下有縱橫架匡。
    -> When laid flat for use, it is supported by a rectangular frame with horizontal and vertical crossbars.

    兩手持簾入水，蕩起竹麻，入於簾內。
    -> The vatman takes the mold in both hands, dips it into the vat, and shakes it to lift and distribute the bamboo fibers evenly over the mold's surface.

    厚薄由人手法，輕蕩則薄，重蕩則厚。
    -> The thickness of the paper depends on the vatman's technique: a light shake produces thin paper, while a vigorous shake produces thick paper.

    竹料浮簾之頃，水從四際淋下槽內，然後覆簾，落紙於板上，疊積千萬張。
    -> As the bamboo fibers float into place on the mold screen, the water drains from the four sides back into the vat. The mold is then flipped over, depositing the wet sheet onto a board. This process is repeated, stacking thousands upon thousands of sheets.

    數滿，則上以板壓，俏繩入棍，如榨酒法，使水氣淨盡流幹。
    -> When the pile reaches a sufficient height, a pressing board is placed on top, and ropes are tightened around sticks inserted into the ropes, exactly like a winepress, to squeeze out all excess water.

    然後，以輕細銅鑷逐張揭起、焙乾。
    -> Afterwards, each sheet is carefully lifted from the stack using delicate fine copper tweezers, and then dried on a heated wall.

    凡焙紙，先以土磚砌成夾巷，下以磚蓋巷地面，數塊以往，即空一磚。
    -> To build the drying stove, a double-walled flue is first constructed from bricks. The floor of the flue is also bricked over, leaving a gap in every few bricks.

    火薪從頭穴燒發，火氣從磚隙透巷，外磚盡熱。
    -> A fire is lit at the opening of the flue. The heat and smoke travel along the flue and escape through the brick gaps, causing the surface of the outer wall to become thoroughly hot.

    濕紙逐張貼上焙乾，揭起成帙。
    -> The wet sheets are pasted one by one onto this hot wall to dry. When dry, they are peeled off and gathered into quires (*zhi*).

    *Paragraph 4:*
    近世闊幅者，名大四連，一時書文貴重。
    -> In modern times, the wide-sized paper known as "Large Four-Joined" (*Dasi Lian*) became highly esteemed for writing and printing.

    其廢紙，洗去朱墨污穢，浸爛，入槽再造，全省從前煮浸之力，耗亦不多。
    -> Waste paper can be washed clean of red ink and other stains, soaked until disintegrated, put into the vat, and remade into paper. This entirely saves the previous steps of cooking and steeping the raw material, and the waste of material is very slight.

    南方竹賤之國，不以為然。
    -> In the southern regions where bamboo is plentiful and cheap, this recycling is not considered necessary.

    北方即寸條片角在地，隨手拾取再造，名曰還魂紙。
    -> In the north, even scraps and fragments lying on the ground are immediately picked up and remade into paper, which is called "spirit-returning paper" (*Huanhun Zhi*, recycled paper).

    竹與皮，精與粗，皆同之也。
    -> This principle applies to paper made from bamboo and from bast fibers, to fine paper and coarse paper.

    *Paragraph 5:*
    若火紙、糙紙，斬竹煮麻，灰漿水淋，皆同前法，唯脫簾之後，不用烘焙，壓水去濕，日曬成幹而已。
    -> As for "fire paper" (spirit paper) and rough paper (糙紙), the cutting of bamboo, boiling of pulp, and treating with ash lye all follow the same methods described above. The only difference is that after the sheets are taken off the mould, they are not dried on the heated wall. They are simply pressed to remove the water and dried by exposure to the sun.

    盛唐時，鬼神事繁，以紙錢代焚帛（北方用切條，名曰板錢），故造此者，名曰火紙。
    -> During the High Tang dynasty, observances for spirits and gods were elaborate. Paper money was used to replace the burning of silk cloth (in the north, cut strips of paper called *Banqian* are used). Therefore, this type of paper is called "fire paper" (火紙).

    荊楚近俗，有一焚侈至千斤者。此紙十七供冥燒，十三供日用。
    -> In the modern customs of the Jing-Chu region, there are cases where as much as a thousand catties are extravagantly burned at a time. 70% of this paper is used for burning to the dead, and 30% for daily use.

    其最粗而厚者，名曰包裹紙，則竹麻和宿田晚稻稿所為也。
    -> The coarsest and thickest type is called wrapping paper (包裹紙), which is made from bamboo pulp mixed with the rice straw of late-harvest fields.

    若鉛山諸邑所造柬紙，則全用細竹料厚質蕩成，以射重價。
    -> The note paper (*Jian Zhi*) made in the districts of Yanshan and its environs is made entirely of fine bamboo pulp, formed into a thick, high-quality sheet, in order to fetch a high price.

    最上者曰官柬。富貴之家，通刺用之，其紙敦厚而無筋膜；染紅為吉柬，則先以白礬水染過，後上紅花汁云。
    -> The very highest grade is called Official Note Paper (官柬). Wealthy and noble families use it for their calling cards. This paper is thick and substantial, completely free from fiber streaks or knots. It is dyed red to make auspicious greeting cards (吉柬). For this, it is first treated with a solution of alum and then dyed with a red pigment derived from safflower.

    *Self-Correction / Refinement:*
    - The text says "事出南方，而閩省獨專其盛". "独专其盛" implies it holds a monopoly or is especially prosperous in Fujian. "Fujian province holds a unique prominence" sounds good.
    - "節界芒種" -> "At the border of the *Mangzhong* solar term" / roughly... "Around the time of the *Mangzhong* (Grain in Ear) solar term".
    - "加功槌洗" -> "subjected to pounding and washing".
    - "山國皆有水碓": "mountainous regions all have water-powered stamping mills / trip-hammers".
    - "方語無定名": "known under various local names".
    - "展捲張開時": "When it is unrolled/opened for use" -> "When opened flat for use".
    - "數滿": "When the stack of sheets is sufficiently high".
    - "俏繩入棍": "threading ropes and inserting sticks" -> "ropes are tightened around sticks".
    - "一時書文貴重": "Was highly valued for writing and printing in its time" -> "came to be highly valued for writing and printing".
    - "不以為然": "do not think so / do not consider it important" -> "this is not practiced or valued".
    - "盛唐時": High Tang.
    - "十七供冥燒，十三供日用": Seven parts for funerary burning, three parts for daily use. "Seventy percent for spiritual burning, thirty percent for daily use."
    - "通刺用之": Used for name cards / visiting cards *tong ci*.
    - "染紅為吉柬": Dyed red to make auspicious cards.
    - "白礬水": Alum water.
    - "紅花汁": Safflower juice.

    Is there anything that might be confusing to a modern reader?
    "尺 (Chi)", "丈 (Zhang)", "石 (Shi)", "斤 (Jin)". If I translate "五、七尺长", literally "five, seven feet". 1 chi = ~0.333m. So 5 chi = 1.65m. 7 chi = 2.31m. "Cut into lengths of five to seven chi (roughly 1.6 to 2.3 meters)".
    "十餘石": 1 shi = ~100 liters for dry, but for water: 1 shi = 100 L (roughly a hectoliter). "Over ten shi (more than 1000 liters)".
    "丈五尺": 1 zhang = 10 chi. "One zhang and five chi (about 5 meters)".
    "千斤": 1000 jin. 1 jin = 0.5kg. "500 kilograms".

    Let's review for flow and strict fidelity. The instruction says: "目标不是逐字古雅，而是让现代英语读者理解造纸流程。要求：忠实保留工序、材料、时间和因果关系；必要时可用括号给出极短解释；不要扩写为百科文章。"

    The tone should be technical but fluid. I have avoided poetical flourishes. The parentheticals are brief and serve to explain terms like *shaqing*, *Mangzhong*, *Huanhun Zhi*, etc.

    Are there any steps omitted? Let's track the process chain in the translation:
    1. Geographical origin & season.
    2. Growth state of bamboo.
    3. Cutting season (Mangzhong).
    4. Cutting length.
    5. Soaking pit.
    6. Water supply via pipes.
    7. Duration of soaking (100 days).
    8. Pounding and washing (removing green skin + outer shell).
    9. Inner fiber resembles ramie.
    10. Applying lime slurry.
    11. Steaming/boiling in vat (8 days/nights).
    12. Description of apparatus.
    13. Cooling (1 day).
    14. Extracting pulp.
    15. Washing in clean tank (wooden planks).
    16. Lye treatment (wood ash -> rice straw ash).
    17. Repeated boiling and lye pouring (10+ days).
    18. Beating in mortar / water trip-hammer.
    19. Forming vat, consistency.
    20. "Paper Medicine" added.
    21. Paper mould (woven bamboo frame).
    22. Vatman dipping and shaking (thickness control).
    23. Felt couch / layering on board.
    24. Pressing (wine-press style).
    25. Lifting with copper tweezers.
    26. Drying on heated brick wall (flue construction).
    27. Wide paper ("Large Four Joiner").
    28. Recycling (waste paper).
    29. "Spirit-returning paper".
    30. Fire paper & Coarse paper (no heated drying, sun-dry).
    31. Historical context (Tang Dynasty, spirit money).
    32. Regional customs (Jing-Chu).
    33. Wrapping paper (bamboo + rice straw).
    34. Official Note Paper (Yanshan, fine pulp, uniform).
    35. Dyeing red for festive cards (alum + safflower).

    The translation maps very well to the original text.
    I will compile the final version. Ensure the paragraphs align well.

    "當筍生之後，看視山窩深淺" -> After the bamboo shoots have grown, the density of the bamboo in the mountain valleys is surveyed. (看视 can mean looking at/surveying, 深浅 can mean depth/proximity of bamboo stalks).
    "其竹以將生枝葉者為上料" -> Bamboo that is about to grow branches and leaves is considered the best raw material.

    "火以八日八夜為率" -> "the fire is maintained for eight days and eight nights as the standard rule."

    "鍋上泥與石灰捏弦，高闊如廣中煮鹽牢盆樣，中可裁水十餘石" -> "The rim of the cauldron is built up high with mud and lime, making it tall and wide, resembling the salt-boiling pans of Guangdong. It can hold over ten *shi* of water."

    "其塘底面、四維皆用木板合縫砌完" -> "The bottom and the four sides (the tank) are constructed of tightly joined wooden planks."

    "用柴灰漿過" -> "slurried with wood ash lye".

    "自然臭爛" -> "naturally rots (ferments/disintegrates)".

    "山國皆有水碓" -> "mountainous regions universally have water-powered trip-hammers".

    "舂至形同泥面" -> "pounded until it has the consistency of wet mud".

    "凡抄紙槽，上合方半" -> "The forming vat is rectangular/open on top".

    "尺寸闊狹，槽視簾，簾視紙" -> The dimensions of the vat match the mold (mould), and the mold matches the paper.

    "厚薄由人手法，輕蕩則薄，重蕩則厚" -> "The thickness depends on the vatman's skill; a gentle shake makes it thin, a heavy shake makes it thick."

    "數滿，則上以板壓，俏繩入棍，如榨酒法，使水氣淨盡流幹" -> "When the pile is complete, a board is placed on top and pressed. Ropes are threaded and sticks inserted to tighten them, exactly like pressing wine, so that all the water is squeezed out."

    "近世闊幅者，名大四連，一時書文貴重" -> "In recent times, the wide sheet known as the 'Large Four-Joiner' was prized for writing and printing."

    "全省從前煮浸之力，耗亦不多" -> "this entirely saves the earlier effort of cooking and steeping, and the loss of material is slight."

    "南方竹賤之國，不以為然" -> "In the southern regions, where bamboo is cheap, this is not considered necessary."

    "竹與皮，精與粗，皆同之也" -> "This applies to paper made from bamboo and from bark/bast, fine and coarse."

    "凡造竹紙，事出南方，而閩省獨專其盛" is translated nicely.

    "唯脫簾之後，不用烘焙，壓水去濕，日曬成幹而已" -> "The only difference is that after being taken off the mold, they are not dried on a heated wall. They are simply pressed to remove moisture and dried in the sun."

    "荊楚近俗，有一焚侈至千斤者" -> "In the modern customs of the Jing-Chu area, there are extravagant burnings reaching a thousand catties at a time."

    "此紙十七供冥燒，十三供日用" -> "Seventy percent of this paper is supplied for funeral/spirit burning, and thirty percent for daily use."

    "若鉛山諸邑所造柬紙，則全用細竹料厚質蕩成，以射重價" -> "As for the note paper made in Yanshan and its surrounding districts, it is entirely made of fine bamboo fibers, formed into a thick sheet, in order to fetch a high price."

    "染紅為吉柬，則先以白礬水染過，後上紅花汁云" -> "To dye it red for auspicious cards, it is first treated with alum water, and then dyed with a safflower pigment infusion."

    Looks solid. Ready to finalize. No expansion, just faithful translation with brief needed clarifications in brackets. No circumlocution or added literary embellishment.

    Drafting the final text. I will keep the paragraph structure the same as the prompt. The prompt has the source text as a single block, but large. I will break it into logical paragraphs for readability, mirroring the original flow. No need to number them exactly. The prompt's structure has paragraphs naturally from the PDF.

    "素材来源：《天工開物》节选：造竹紙"
    "来源链接：... "
    "版权/授权说明：..."

    The user provided a block of text. I translate the block.

    Ready.
```

## Assistant

```markdown
The manufacture of bamboo paper is practiced throughout the southern regions, but Fujian Province holds a unique prominence in this industry. After the bamboo shoots have grown, the density of the stalks in the mountain valleys is examined. Bamboo that is just about to put forth branches and leaves is selected as the best raw material. Around the time of the solar term *Mangzhong* (芒種, "Grain in Ear", early June), the bamboo is felled on the mountain, cut into lengths of five to seven *chi* (roughly 1.6 to 2.3 meters). A pond is dug right on the mountain and filled with water to steep the bamboo. To prevent the pond water from drying up, bamboo pipes are used to channel a continuous stream of flowing water into it.

After steeping for over a hundred days, the bamboo is worked by pounding and washing to remove the rough outer shell and the green skin (this process is called *shāqīng*, “killing the green”). The inner bamboo pith now resembles ramie fibers. A slurry is made from high-quality quicklime, and the fibers are coated with it. This is placed into a large wooden vat (楻桶) set over a cauldron and boiled, with a standard firing time of eight days and eight nights.

For boiling the bamboo, a cauldron four *chi* in diameter is used. Its rim is built up high with mud and lime, making it tall and wide, resembling the large salt-boiling pans (*láopén*) of Guangdong. It can hold over ten *shi* (石, a unit of volume, roughly 100 liters each) of water. The vat placed on top has a circumference of one *zhang* and five *chi* (about 5 meters) and a diameter of over four *chi*. Once sealed for boiling, eight days is sufficient. The fire is stopped for one day, then the vat is opened and the bamboo pulp (竹麻, *zhúmá*) is taken out and washed in a clear water tank. The bottom and sides of this tank are constructed of wooden planks joined tightly to prevent mud contamination (those making coarse paper do not need to do this). After washing, the fibers are re-slurried with wood ash lye and put back into the cauldron. The surface is leveled flat, and a layer of rice straw ash, about one *cun* (roughly 3 cm) thick, is spread on top. When the water in the cauldron boils, the fibers are dipped out into another bucket, and the ash lye is poured over them. If the lye cools, it is boiled again and poured over. After a course of ten or more days of this treatment, the fibers naturally decompose into a rotten mass. The pulp is then taken out and beaten in a mortar (mountainous regions universally have water-powered trip-hammers for this), beaten until it has the consistency of wet plaster, and then poured into the forming vat (抄紙槽).

The papermaking vat is rectangular. The dimensions of the vat are determined by the paper mold (簾), and the size of the mold is determined by the desired paper size. When the bamboo pulp is ready, clear water is added to the vat so it stands about three *cun* above the surface of the pulp. A fluid extract of "paper medicine" (紙藥, an agent made from a mucilaginous plant resembling peach and bamboo leaves, known by various local names) is added to the water. This ensures that when the water drains away, the fibers bind together into a pure white sheet. The paper mold is woven from very finely scraped and polished bamboo strips. When laid flat for use, it is supported by a rectangular frame with crossbars. The vatman takes the mold in both hands, dips it into the vat, and shakes it to lift and distribute the bamboo fibers evenly over the mold's surface. The thickness of the paper depends on the vatman's technique: a light shake produces thin paper, while a vigorous shake produces thick paper. As the bamboo fibers float into place on the mold screen, the water drains from the four sides back into the vat. The mold is then flipped over, depositing the wet sheet onto a board. This process is repeated, stacking thousands upon thousands of sheets.

When the pile reaches a sufficient height, a pressing board is placed on top, and ropes are tightened around sticks inserted into the ropes, exactly like a winepress, to squeeze out all excess water. Afterwards, each sheet is carefully lifted from the stack using delicate fine copper tweezers, and then dried on a heated wall. To build the drying stove, a double-walled flue is first constructed from bricks. The floor of the flue is also bricked over, leaving a gap in every few bricks. A fire is lit at the opening of the flue. The heat and smoke travel along the flue and escape through the brick gaps, causing the outer surface of the wall to become thoroughly hot. The wet sheets are pasted one by one onto this hot wall to dry. When dry, they are peeled off and gathered into quires (*zhì*).

In modern times, the wide-sized paper known as the "Large Four-Joined" (大四連) became highly esteemed for writing and printing. Waste paper can be washed clean of red ink and other stains, soaked until disintegrated, put into the vat, and remade into paper. This entirely saves the previous steps of cooking and steeping the raw material, and the loss of material is very slight. In the southern regions where bamboo is plentiful and cheap, this recycling is not considered necessary. In the north, however, even scraps and fragments lying on the ground are immediately picked up and remade into paper, which is called "spirit-returning paper" (還魂紙, recycled paper). This principle applies to paper made from bamboo and from bast fibers, to fine paper and coarse paper alike.

As for "fire paper" (火紙, spirit paper for offerings) and rough paper (糙紙), the cutting of bamboo, boiling of pulp, and treating with ash lye all follow the same methods described above. The only difference is that after the sheets are taken off the mold, they are not dried on the heated wall. They are simply pressed to remove the water and dried by exposure to the sun. During the High Tang dynasty, observances for spirits and gods were elaborate. Paper money was used to replace the burning of silk cloth (in the north, cut strips of paper called *bǎnqián* are used). Therefore, this type of paper is called "fire paper". In the modern customs of the Jing-Chu region, some extravagantly burn as much as a thousand catties (500 kg) at a time. 70% of this paper is used for burning to the dead, and 30% for daily use. The coarsest and thickest type is called wrapping paper (包裹紙), which is made from bamboo pulp mixed with the rice straw of late-harvest fields.

As for the note paper (柬紙) made in the districts of Yanshan and its environs, it is made entirely of fine bamboo pulp, formed into a thick, high-quality sheet, in order to fetch a high price. The very highest grade is called Official Note Paper (官柬). Wealthy and noble families use it for their calling cards. This paper is thick and substantial, completely free from fiber streaks or knots. To dye it red for auspicious greeting cards (吉柬), it is first treated with a solution of alum, and then dyed with a red pigment derived from safflower.
```
