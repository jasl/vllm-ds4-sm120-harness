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
- Elapsed seconds: 10.946582
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 1033, "total_tokens": 2561, "completion_tokens": 1528, "prompt_tokens_details": null}`
- Prompt tokens: 1033
- Completion tokens: 1528
- Total tokens: 2561

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

## Assistant

```markdown
Here is an English translation of the traditional Chinese technical text on bamboo papermaking, aimed at modern understanding while preserving the processes, materials, timing, and cause-effect relationships.

---

**Making Bamboo Paper**

All bamboo papermaking occurs in the South, but Fujian province is especially renowned for it. After the bamboo shoots have grown, one inspects the depth of the mountain valleys. Bamboo that is about to grow branches and leaves is the best raw material. Around the Grain in Ear solar term (early June), workers go into the mountains to cut it down. They cut the bamboo into sections five to seven *chi* (approx. 1.7–2.3 meters) long. Right there on the mountain, they dig a pond, fill it with water, and soak the bamboo. To prevent the pond from drying out, bamboo pipes are used to channel a continuous stream of flowing water into it.

After soaking for over a hundred days, the bamboo is beaten and washed to remove the coarse outer shell and green bark (this step is called "killing the green"). The inner bamboo fiber (*zhu rang*) then looks like ramie fibers. A paste is made from high-quality lime dissolved in water, and this is applied to the fibers. They are placed in a vat (*hu tong*) and boiled. The standard boiling time is eight days and eight nights.

For boiling bamboo, a cauldron with a diameter of four *chi* (approx. 1.3 m) is used. The rim of the cauldron is built up with mud and lime, making it tall and wide, much like the salt-boiling pans used in Guangdong, capable of holding over ten *dan* (approx. 1000 liters) of water. A large wooden vat (the *hu tong*) is placed on top as a lid; this vat has a circumference of fifteen *chi* (approx. 5 m) and a diameter of over four *chi*. Once sealed, the boiling proceeds. After exactly eight days, the fire is stopped for one day. Then the vat lid is removed, and the bamboo pulp (*zhu ma*) is taken out and washed clean in a clean-water soaking pond. The bottom and all four sides of this pond are lined with tightly joined wooden planks to prevent mud contamination (this is not necessary for making coarse paper). After washing, the pulp is treated with a wood-ash slurry and then placed back into the cauldron. It is leveled, and a one-inch (approx. 3 cm) layer of rice straw ash is spread evenly on top. When the water in the cauldron boils, the liquid is ladled out into another vat, and then this ash-water liquid is poured back over the pulp. If it cools, it is re-boiled before being poured again. This is repeated for ten or more days, until the fibers naturally rot and become soft. Then the pulp is taken out and placed in a mortar for pounding (in mountainous regions, water-powered trip-hammers are used). It is pounded until it has the consistency of mud. Finally, it is poured into a vat (*cao*).

The papermaking vat has a square top half. Its width and length are sized according to the paper mold, just as the mold is sized according to the desired paper size. Once the bamboo pulp is ready, the vat is filled with clear water to about three inches (approx. 7.6 cm) above the surface of the pulp. A "paper medicine" liquid is added (made from leaves resembling peach or bamboo leaves; the local name varies). This causes the water to drain away, leaving clean, white fibers.

The papermaking mold (*lian*) is made from very finely scraped and polished bamboo strips woven into a mat. It can be rolled up and unrolled. When in use, it is stretched flat over a rectangular supporting frame. The worker holds the mold with both hands and dips it into the vat, scooping up the bamboo fibers onto the mold's surface. The thickness of the sheet is controlled by the worker's technique: a gentle lift makes thin paper; a vigorous lift makes thick paper. As the bamboo fibers float on the mold, water drains from all four sides back into the vat. The worker then overturns the mold onto a board, depositing the wet sheet of paper. Thousands of sheets are stacked this way. Once the stack reaches the desired height, a board is placed on top, and a lever is tightened with ropes (like pressing wine) to squeeze out all the remaining water. Then, each sheet is lifted one by one with fine, lightweight copper tweezers and dried.

For drying paper, a brick-lined passageway (a drying oven) is built. The floor of the passage is covered with bricks, leaving one brick missing every few bricks to create air holes. A fire is lit at one end; the heat flows through the gaps between the bricks, heating the outer surface of the passage. Wet sheets are pasted one by one onto the hot brick wall to dry. Once dry, they are removed and gathered into quires.

Recently, a wide-format paper called "Big Four-Link" has become valued for calligraphy and writing. Waste paper, after having its red ink and dirt washed away and being soaked until rotten, can be re-pulped in the vat. This saves all the previous steps of boiling and soaking, yet still produces paper with little loss of material. In the South, where bamboo is cheap, this is not considered important. But in the North, even an inch of paper waste is picked up and re-made into "Returned-Soul Paper." Bamboo and bark papers, fine and coarse, are all treated this way.

As for ritual paper (*huo zhi*) and rough paper (*cao zhi*), the process of cutting bamboo, boiling the pulp, and treating it with ash water is the same. The only difference is that after being removed from the mold, these papers are not dried on the heated wall. Instead, they are simply pressed to remove water and then dried in the sun.

During the High Tang dynasty (c. 8th century), religious and funerary practices became widespread. Paper money replaced burned silk cloth (in the North, cut strips were used, called "board money"). The paper made for this was called "Fire Paper." In the modern customs of the Jing-Chu region (Hubei/Hunan), it is not uncommon to burn up to a thousand *jin* (approx. 600 kg) in a single ritual. About 70% of this paper is used for burial offerings, and 30% for daily purposes. The coarsest and thickest type, called wrapping paper, is made from bamboo pulp mixed with old rice straw from the late-season crop.

As for the high-quality note paper (*jian zhi*) made in Yanshan and other counties, it is made entirely from fine bamboo material, formed into a thick sheet, and commands a high price. The finest grade is called "Official Note" (*guan jian*). Wealthy families use it for their visiting cards. This paper is thick and strong, with no fibrous strands. To make red auspicious note paper, the sheets are first treated with an alum solution and then dyed with safflower juice.

---
**Making Bark Paper** (皮纸)
```
