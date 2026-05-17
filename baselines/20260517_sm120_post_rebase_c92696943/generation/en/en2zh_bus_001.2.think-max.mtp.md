# Generation Transcript

- Case: `en2zh_bus_001`
- Language group: `en`
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
- Elapsed seconds: 40.467307
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 1283, "total_tokens": 8238, "completion_tokens": 6955, "prompt_tokens_details": null}`
- Prompt tokens: 1283
- Completion tokens: 6955
- Total tokens: 8238

## Prompt

```markdown
Translate the following English business-writing passage into Simplified Chinese. Requirements: use a polished modern Chinese business style; preserve the author’s argument about clarity, goodwill, and restraint in business letters; do not add examples beyond the source.

素材来源：The Book of Business Etiquette, chapter “The Business of Writing” excerpt
来源链接：https://www.gutenberg.org/ebooks/23025
版权/授权说明：Project Gutenberg lists this eBook as public domain in the USA.

【待处理素材】
Half the business letters which are written should never be written at all, and of the other half so many are incomplete or incoherent that a transaction which could be finished and filed away in two letters frequently requires six or eight.

A good letter is the result of clear thinking and careful planning. In the case of the sales-letter it sometimes takes several weeks to write one, but for ordinary correspondence a few minutes is usually all that is necessary. The length of time does not matter--it is the sort of letter which is produced at the end of it.

Books of commercial correspondence give a number of rules and standards by which a letter can be measured. But all rules of thumb are dangerous, and there are only two items which are essential. The others are valuable only as they contribute to them. The letter must succeed in getting its idea across and it must build up good will for its firm. And the best one is the one which accomplishes this most courteously and most completely in the briefest space of time (and paper).

There should be a reason back of every letter if it is only to say "Thank you" to a customer. Too much of our national energy goes up in waste effort, in aimless advertising, worthless salesmanship, ineffective letter writing, and in a thousand and one other ways. A lot of it is hammered out on the typewriters transcribing perfectly useless letters to paper which might really be worth something if it were given over to a different purpose.

A good letter never attracts the mind of the reader to itself as a thing apart from its contents. Last year a publishing house sent out a hundred test letters advertising one of their books. Three answers came back, none of them ordering the book, but all three praising the letter. One was from a teacher of commercial English who declared that he was going to use it as a model in his classes, and the other two congratulated the firm on having so excellent a correspondent. The physical make-up of the letter was attractive, it was written by a college graduate and couched in clear, correct, and colorful English. And yet it was no good. No _letter and no advertisement is any good which calls attention to itself instead of the message it is trying to deliver_.

There is not much room for individuality in the make-up of a letter. Custom has standardized it, and startling variations from the conventional format indicates freakishness rather than originality. They are like that astonishing gentleman who walks up Fifth Avenue on the coldest mornings in the year, bareheaded, coatless, sockless, clad in white flannels and tennis slippers. He attracts attention, but he makes us shiver.

Plain white paper of good quality is always in good taste. Certain dull-tinted papers are not bad, but gaudy colors, flashy designs, and ornate letter heads are taboo in all high types of business. Simple headings giving explicit and useful information are best. The name and address of the firm (and "New York" or "Chicago" is not sufficient in spite of the fact that a good many places go into no more detail than this), the cable address if it has one, the telephone number and the trademark if it is an inconspicuous one (there is a difference between _conspicuous_ and _distinctive_) are all that any business house needs.

Hotels are often pictured on their own stationery in a way that is anything but modest, but there is a very good reason for it. The first thing most people want to know about a hotel is what sort of looking place it is. All right, here you are. Some factories, especially those that are proud of their appearance, carry their own picture on their stationery. There is nothing to say against it, but one of the most beautiful factories in America has on its letter head only the name of the firm, the address, and a small trademark engraved in black. Sometimes a picture, in a sales letter, for instance, supplements the written matter in a most effective way. And whenever any kind of device is really helpful it should by all means be used, subject only to the limits of good taste.

It is more practical in business to use standard size envelopes. If window envelopes are used the window should be clear, the paper white or nearly so, and the typewritten address a good honest black. The enclosure should fit snugly and should be placed so that the address is in plain view without having to be jiggled around in the envelope first. A letter passes through the hands of several postal clerks before it reaches the person to whom it is addressed, and if each one of them has to stop to play with it awhile an appreciable amount of time is lost, not to mention the strain it puts on their respective tempers. The paper of which an envelope is made should always be opaque enough to conceal the contents of the letter.

Practically all business letters are typewritten. Occasionally a "Help Wanted" advertisement requests that the answer be in the applicant's own handwriting, but even this is rare. In most places the typing is taken care of by girls who have been trained for the purpose, but most young girls just entering business are highly irresponsible, and it is necessary for the men and women who dictate the letters to know what constitutes a pleasing make-up so that they can point out the flaws and give suggestions for doing away with them.
```

## Reasoning Content

```text
Thinking. 1.  **Analyze the Request:**
    *   Task: Translate English business-writing passage into Simplified Chinese.
    *   Style: Polished modern Chinese business style.
    *   Constraint 1: Preserve the author's argument about clarity, goodwill, and restraint.
    *   Constraint 2: Do not add examples beyond the source.
    *   Source material: Provided (specific paragraphs from "The Book of Business Etiquette").
    *   Tone/Audience: Formal but fluent business Chinese.

2.  **Deconstruct the Source Material:**
    The text is an argumentative/instructional piece about business letter writing. Key points to preserve:
    *   Many business letters are unnecessary, incomplete, or incoherent.
    *   Good letters result from clear thinking/planning. Length is irrelevant, quality matters.
    *   The two essential items are: conveying the idea and building good will. Others are subordinate.
    *   Every letter should have a purpose. Wasted effort is rampant.
    *   A good letter doesn't draw attention to itself away from the message. (Anecdote about the publishing house).
    *   Standardization is good; freakish originality is bad.
    *   Stationery quality and taste: plain white paper, simple headings, standard envelopes.
    *   Practicality: standard sizes, opaque envelopes.
    *   Typing: responsibility of the dictator.

3.  **Translate Paragraph by Paragraph:**

    *   **Paragraph 1:**
        "Half the business letters which are written should never be written at all, and of the other half so many are incomplete or incoherent that a transaction which could be finished and filed away in two letters frequently requires six or eight."
        -> "在撰写的大量商业信函中，有一半根本无需动笔；而在另一半中，又有许多存在内容不完整或表述不连贯的问题，导致本可通过两封信函便可完成并归档的交易，时常需要六至八封函件才能解决。"

    *   **Paragraph 2:**
        "A good letter is the result of clear thinking and careful planning. In the case of the sales-letter it sometimes takes several weeks to write one, but for ordinary correspondence a few minutes is usually all that is necessary. The length of time does not matter--it is the sort of letter which is produced at the end of it."
        -> "一封优质的信函，源于清晰的思路与周详的规划。就营销信函而言，有时需要数周时间才能写就；但对于日常通信，通常只需数分钟。时间长短并非关键——关键在于最终呈现出的信函质量。"

    *   **Paragraph 3:**
        "Books of commercial correspondence give a number of rules and standards by which a letter can be measured. But all rules of thumb are dangerous, and there are only two items which are essential. The others are valuable only as they contribute to them. The letter must succeed in getting its idea across and it must build up good will for its firm. And the best one is the one which accomplishes this most courteously and most completely in the briefest space of time (and paper)."
        -> "商务函件书籍提供了诸多衡量信函质量的规则与标准。但一切经验法则都暗藏风险，其中只有两个要素至关重要。其余法则仅当其能助益于这两个要素时方才具备价值。信函必须成功传达其意图，并为其所在公司建立商誉。而最佳的信函，正是能以最谦恭有礼的态度、最完整的方式，在最短的时间（和篇幅）内实现这一目标的那一封。"

    *   **Paragraph 4:**
        "There should be a reason back of every letter if it is only to say "Thank you" to a customer. Too much of our national energy goes up in waste effort, in aimless advertising, worthless salesmanship, ineffective letter writing, and in a thousand and one other ways. A lot of it is hammered out on the typewriters transcribing perfectly useless letters to paper which might really be worth something if it were given over to a different purpose."
        -> "每一封信函都应有其缘由，即便仅仅是为了向客户表达谢意。我们国家的精力有太多都耗费在了徒劳的努力之上：目标不清的广告、无效的推销、收效甚微的信函写作，以及其他形形色色的方式。其中大量精力被挥霍在打字机上，将全然无用的内容转录到纸张上——而这些纸张若用于其他用途未尝没有价值。"

    *   **Paragraph 5:**
        "A good letter never attracts the mind of the reader to itself as a thing apart from its contents. Last year a publishing house sent out a hundred test letters advertising one of their books. Three answers came back, none of them ordering the book, but all three praising the letter. One was from a teacher of commercial English who declared that he was going to use it as a model in his classes, and the other two congratulated the firm on having so excellent a correspondent. The physical make-up of the letter was attractive, it was written by a college graduate and couched in clear, correct, and colorful English. And yet it was no good. No _letter and no advertisement is any good which calls attention to itself instead of the message it is trying to deliver_."
        -> "一封好信函绝不会让读者将其形式与内容割裂开来，从而将注意力聚焦于信函本身而非其承载的信息。去年，有一家出版社寄出了一百封测试信函，为其一本新书做宣传。收回了三封回信，没有一封是订购该书的，但全部三封都对信函本身大加赞赏。一封来自一位商务英语教师，他宣称要将此信作为教学范文；另外两封则祝贺该公司拥有如此出色的信函撰稿人。那封测试信函的外在形式颇具吸引力，出自一位大学毕业生之手，措辞清晰、准确且富有文采。然而，它是一封失败的信函。没有任何信函或广告，若其目的是吸引对自身的关注，而非传递它所承载的信息，能够被称为有效。"

    *   **Paragraph 6:**
        "There is not much room for individuality in the make-up of a letter. Custom has standardized it, and startling variations from the conventional format indicates freakishness rather than originality. They are like that astonishing gentleman who walks up Fifth Avenue on the coldest mornings in the year, bareheaded, coatless, sockless, clad in white flannels and tennis slippers. He attracts attention, but he makes us shiver."
        -> "信函的格式没有太多彰显个性的空间。惯例已将其标准化，与传统格式的惊人偏离所显示的是乖张而非创意。这好比那位令人瞠目的绅士，在最寒冷的冬日清晨，漫步于第五大道，既不戴帽也不穿外套，不穿袜子，只裹着一身白色法兰绒便装，脚蹬网球鞋。他确实吸引了眼球，却让我们感到不寒而栗。"

    *   **Paragraph 7:**
        "Plain white paper of good quality is always in good taste. Certain dull-tinted papers are not bad, but gaudy colors, flashy designs, and ornate letter heads are taboo in all high types of business. Simple headings giving explicit and useful information are best. The name and address of the firm (and "New York" or "Chicago" is not sufficient in spite of the fact that a good many places go into no more detail than this), the cable address if it has one, the telephone number and the trademark if it is an inconspicuous one (there is a difference between _conspicuous_ and _distinctive_) are all that any business house needs."
        -> "品质优良的纯白信纸始终得宜。某些暗色调的纸张也属尚可，但艳俗的色彩、花哨的设计以及繁复的信头，在高级商务场合中皆为禁忌。简单直接的抬头，提供明确且有用的信息，才是最佳选择。公司的名称与地址（许多公司只是简略地写上“纽约”或“芝加哥”，但这远远不够），如有则加上电报挂号、电话号码，以及若非过分醒目的商标（“引人注目”与“富有特色”之间存在区别），便是任何公司所需的一切。"

    *   **Paragraph 8:**
        "Hotels are often pictured on their own stationery in a way that is anything but modest, but there is a very good reason for it. The first thing most people want to know about a hotel is what sort of looking place it is. All right, here you are. Some factories, especially those that are proud of their appearance, carry their own picture on their stationery. There is nothing to say against it, but one of the most beautiful factories in America has on its letter head only the name of the firm, the address, and a small trademark engraved in black. Sometimes a picture, in a sales letter, for instance, supplements the written matter in a most effective way. And whenever any kind of device is really helpful it should by all means be used, subject only to the limits of good taste."
        -> "酒店常常以毫不谦逊的方式将自身图片印在信笺上，但这有非常充分的理由。大多数人想了解一家酒店的第一步，就是想知道它看起来是什么样子。所以，请看此处。一些工厂，尤其是那些对自己的外观感到自豪的工厂，也会将自身图片印在信笺上。这无可厚非，但美国最漂亮的一家工厂，其信头仅仅包含了公司名称、地址以及一个黑色的小版刻商标。有时，例如在营销信件中，一幅图片能以极为有效的方式补充文字内容。在任何情况下，只要某种设计确实有用，就应加以采用，唯一的前提是不失品味。"

    *   **Paragraph 9:**
        "It is more practical in business to use standard size envelopes. If window envelopes are used the window should be clear, the paper white or nearly so, and the typewritten address a good honest black. The enclosure should fit snugly and should be placed so that the address is in plain view without having to be jiggled around in the envelope first. A letter passes through the hands of several postal clerks before it reaches the person to whom it is addressed, and if each one of them has to stop to play with it awhile an appreciable amount of time is lost, not to mention the strain it puts on their respective tempers. The paper of which an envelope is made should always be opaque enough to conceal the contents of the letter."
        -> "在商业实践中，使用标准尺寸的信封更为务实。若使用开窗信封，窗口应保持清晰，纸张应为白色或近乎白色，打印的地址则应是端正的黑色。内件应贴合信封，安放的位置应使地址一览无余，无需先在信封内来回抖动调整。一封信函在送达收件人之前，会经过多位邮政职员之手，如果每位职员都需要停下来摆弄它一番，不仅会损失相当可观的时间，更会对他们的耐心造成考验。信封的纸张应始终具有足够的不透明度，以遮蔽信函的内容。"

    *   **Paragraph 10:**
        "Practically all business letters are typewritten. Occasionally a "Help Wanted" advertisement requests that the answer be in the applicant's own handwriting, but even this is rare. In most places the typing is taken care of by girls who have been trained for the purpose, but most young girls just entering business are highly irresponsible, and it is necessary for the men and women who dictate the letters to know what constitutes a pleasing make-up so that they can point out the flaws and give suggestions for doing away with them."
        -> "实际上，所有的商业信函均为打印稿。偶尔会有“诚聘”广告要求应聘者亲笔回信，但即便如此也不常见。在多数地方，打字工作由经过专门培训的年轻女性处理，但绝大多数刚步入职场的年轻女性极不负责任。因此，口述信函的男士和女士有必要了解什么构成了令人满意的外观，以便能够指出瑕疵并提出改进建议。"

4.  **Refine the Translation:**
    Let's check the overall flow, ensure it sounds like a polished modern Chinese business article (textbook/guide style), respects the original argument, and avoids adding examples.

    *原文: Half the business letters...*
    -> 在已撰写的商业信函中，有一半根本无需动笔；而在另一半中，又有许多内容不完整或条理不清... (Simplified: "在已撰写的商业信函中，半数根本无需动笔；而在余下的半数中，又有许多内容残缺或语无伦次，导致原本仅需两函便可收档的交易，时常用上**六到八函**方能了结。" The original says "six or eight", let's keep it precise.)

    "frequently requires six or eight" -> 时常需要六至八封 (or 六到八封)

    *原文: A good letter is the result...*
    "A good letter is the result of clear thinking and careful planning."
    -> 一封优秀的信函，是思路清晰与规划周详的成果。

    *原文: In the case of the sales-letter...*
    "it sometimes takes several weeks to write one"
    -> 就营销信函而言，其草拟有时需耗时数周... (or 有时需耗时数周方能写就)

    *原文: Books of commercial correspondence give...*
    "Books of commercial correspondence give a number of rules and standards by which a letter can be measured. But all rules of thumb are dangerous, and there are only two items which are essential."
    -> 商业函件书籍提供了一系列衡量信函优劣的规则与标准。但所有经验法则都暗含风险，唯有两条要素至关重要。
    *Correction: "Two items which are essential" -> 信函必须成功传达其意图 (gets its idea across)，并且必须为其公司建立商誉 (builds up good will for its firm).*

    *原文: The best one is the one which accomplishes this most courteously and most completely in the briefest space of time (and paper).*
    -> 而最上乘的信函，正是能以最谦恭有礼的态度、最完满的方式，在最短的时间（及篇幅）内达成这一目的的那一封。

    *原文: Too much of our national energy...*
    "Too much of our national energy goes up in waste effort..."
    -> 我们国家有太多的精力耗费在徒劳的努力上...(Wait, the original says "our national energy", which might feel a bit foreign in translation. We can keep "our nation's" as "我们的国家" or shift slightly to "有太多社会资源/精力" but it's a direct quote. Let's keep it as "我们国家的精力/社会资源有太多都被耗费在了徒劳的努力上". "上至能源" - no, just 精力.)

    "A lot of it is hammered out on the typewriters transcribing perfectly useless letters to paper which might really be worth something if it were given over to a different purpose."
    -> 其中大量精力是在打字机上敲打出来的，将毫无用处的信函转录到纸上——这些纸张若投入到其他用途，或许本可作为有用之物。 (The translation: "其中大量是在打字机上敲出来的，将一无是处的信函复刻到纸张上，而这些纸张若转作他用，未尝不能产生价值。")

    *原文: A good letter never attracts the mind of the reader...*
    "A good letter never attracts the mind of the reader to itself as a thing apart from its contents."
    -> 一封好的信函，绝不会让读者的心智脱离其内容转而关注信函本身。

    *Ancedote about publishing house:*
    "Last year a publishing house sent out a hundred test letters advertising one of their books. Three answers came back, none of them ordering the book, but all three praising the letter."
    -> 去年，一家出版社寄出了一百封测试信函，为其一本图书做广告。收回了三封回信，但没有一封是订购该书的，三封均对信函本身赞誉有加。

    "The physical make-up of the letter was attractive, it was written by a college graduate and couched in clear, correct, and colorful English. And yet it was no good."
    -> 那封信函的外观设计颇有吸引力，出自一位大学毕业生之手，措辞清晰、准确且富有文采。然而，它是一封失败的信函。

    "No _letter and no advertisement is any good which calls attention to itself instead of the message it is trying to deliver_."
    -> 任何信函和广告，若是将注意力吸引到自身而非其所要传递的信息上，便不会有任何价值。

    *Individuality and Format:*
    "There is not much room for individuality in the make-up of a letter."
    -> 信函的格式没有太多彰显个性的空间。

    "startling variations from the conventional format indicates freakishness rather than originality."
    -> 与传统格式的惊人差异，表明的是乖张而非创意。

    "They are like that astonishing gentleman who walks up Fifth Avenue on the coldest mornings in the year, bareheaded, coatless, sockless, clad in white flannels and tennis slippers."
    -> 这就好比那位引人侧目的绅士，在最寒冷的冬日清晨，光头赤膊、未着袜履，仅着一袭白色法兰绒衣裤与一双网球鞋，漫步于第五大道。

    "He attracts attention, but he makes us shiver."
    -> 他确实引人注目，但让我们感到不寒而栗。

    *Stationery:*
    "Plain white paper of good quality is always in good taste."
    -> 品质优良的纯白信纸，总是得体之选。

    "gaudy colors, flashy designs, and ornate letter heads are taboo in all high types of business."
    -> 艳俗的色彩、花哨的设计以及繁复的信头，在高级商务领域中皆为禁忌。

    *Envelopes:*
    "If window envelopes are used the window should be clear, the paper white or nearly so, and the typewritten address a good honest black."
    -> 若使用开窗信封，窗口应保持清晰，纸张应为白色或接近白色，打印地址则应是端正的黑色。

    "The enclosure should fit snugly and should be placed so that the address is in plain view without having to be jiggled around in the envelope first."
    -> 内件应贴合信封，其放置位置应使地址一目了然，无需先在信封内来回抖动调整。

    "The paper of which an envelope is made should always be opaque enough to conceal the contents of the letter."
    -> 信封用纸应始终具备足够的不透明度，以遮没信函内容。

    *Typing:*
    "Practically all business letters are typewritten."
    -> 实际上，所有商业信函均为打印稿。

    "In most places the typing is taken care of by girls who have been trained for the purpose, but most young girls just entering business are highly irresponsible, and it is necessary for the men and women who dictate the letters to know what constitutes a pleasing make-up so that they can point out the flaws and give suggestions for doing away with them."
    -> 在多数地方，打印工作由经过专门培训的年轻女性处理，但绝大多数刚步入职场的年轻女性极不负责任。因此，口述信函的男士和女士有必要了解什么构成了令人满意的外观，以便能够指出瑕疵并提出改进建议。
    Wait, "young girls just entering business are highly irresponsible" -> 初入职场的大部分年轻女性极不负责. The tone is slightly dated, but preserving the author's argument is required.

    Let's review the whole text flow and accuracy. The tone needs to be "polished modern Chinese business style" while preserving the author's arguments. The original text has some dated phrases ("girls highly irresponsible", "our national energy"). We need to translate these faithfully as they are part of the author's argument.

    Let's write the entire translation in one coherent block, matching the structure of the original.

    **Final Check of the Translation Paragraph by Paragraph:**

    P1: 在业已书写的商务信函中，有一半根本无需动笔；而另一半中，又有许多内容残缺或条理不清，导致原本仅需两函便可结案归档的交易，时常用上**六到八函**方能了结。

    P2: 一封优质信函是思路清晰与规划周详的产物。就营销信函而言，其起草有时需耗时数周，但日常通信通常几分钟即可完成。时间长短并非关键——关键在于最终写就的是什么样的信函。

    P3: 商务函件指南提供了一系列衡量信函优劣的规则与标准。但所有经验法则都暗藏风险，唯有两条要素至关重要。其他法则的价值仅在于服务于这两条要素。信函必须成功传达其想法，并为本公司建立商誉。最上乘的信函，正是能以最谦恭有礼的态度、最完满的方式，在最短的时间（及纸张篇幅）内达成此目标的那一封。

    P4: 每一封信函背后都应有其缘由，即便只是向客户道声“谢谢”。我国有太多的精力被耗费在徒劳的努力之上：毫无目的的广告、毫无价值的销售、毫无效果的函件撰写，以及形形色色其他的方式。其中大量的精力是在打字机上敲打出去的，将毫无用处的书信转录到纸张上——这些纸张如果用于其他目的，或许本可以物尽其用。

    P5: 一封好的信函绝不会让读者的注意力脱离其内容而停留在信函本身。去年，有一家出版社寄出一百封测试邮件为一本新书做广告。只收到了三封回信，都不是订购该书的，但三封回信都对信函本身赞赏有加。一封来自一位商务英语教师，他声称要将此信用作课堂范文；另外两封则祝贺该公司拥有如此出色的函件撰写人。那封测试信函的外观颇为吸引人，出自一位大学毕业生之手，措辞清晰、准确且富有文采。但这是一封失败的信函。**凡是试图将注意力引向自身而非其传递讯息的信函或广告，都是没有价值的。**

    P6: 信函的格式没有太多展示个性的余地。惯例已经使其标准化，与传统格式的惊人偏离显示的是怪癖而非创意。这就好比那位令人咋舌的绅士，在最寒冷的冬日清晨，光着头、不穿外套、不着袜子，仅穿一身白色法兰绒衣服和一双网球鞋，沿着第五大道行走。他确实引人注目，却让我们不寒而栗。

    P7: 品质优良的纯白信纸总是得体的。某些颜色暗淡的纸张也并非不可取，但在所有高级商务领域中，艳俗的颜色、花哨的设计以及繁复的信头都是禁忌。提供明确且有用信息的简单信头最佳。公司名称和地址（许多公司仅止于“纽约”或“芝加哥”这类简略标注，这远远不够），如有则加上电报挂号、电话号码，以及一个不过分显眼的商标（**“显眼”与“特色”是两码事**），这些便是一家公司所需的全部内容。

    P8: 酒店常常以一种非常不谦虚的方式将自己的照片印在信笺上，但这有一个非常充分的理由。大多数人想了解酒店的第一件事就是它看起来是什么样子。好的，请在这里看。一些工厂，尤其是那些为其外观感到自豪的工厂，也会将自身照片印于信笺上。这无可厚非，但美国最漂亮的一家工厂，其信头上只有公司名称、地址和一个黑色的小版刻商标。有时，例如在营销信函中，一幅图片能以极为有效的方式辅助文字内容。只要任何设计确实有帮助，就应当予以采用，唯一限制是不失品味。

    P9: 在商业实践中，使用标准尺寸的信封更为务实。若使用开窗信封，窗口应保持清晰，纸张应为白色或近乎白色，打印的地址应是纯正清晰的黑色。内件应贴合信封放置，使地址一览无余，无需先在信封内来回抖动调整。一封信函在送达收件人之前会经过数名邮政职员之手，如果每位职员都需要停下来摆弄一番，不仅会流失相当可观的时间，更会对他们的耐心造成考验。信封用纸应始终足够不透明，以遮蔽信函内容。

    P10: 实际上，所有商业信函均为打印。偶尔会有“诚聘”广告要求应聘者亲笔回信，但这种情况也很少见。在多数地方，打字工作由经过专门培训的年轻女性完成，但绝大多数刚进入商界的年轻女性非常不负责任。因此，口述信函的男士和女士有必要了解什么样的外观才令人满意，以便指出缺陷并提出改进建议。

    Wait, the last sentence "girls highly irresponsible" is a direct part of the author's argument. It fits the source context. The translation has to keep it.

    Let's refine the tone of a few sentences to make it perfectly polished while remaining faithful.

    "Half the business letters which are written should never be written at all, and of the other half so many are incomplete or incoherent that a transaction which could be finished and filed away in two letters frequently requires six or eight."
    -> 在已书写的商务信函中，有一半根本无需动笔；而另一半中，又有许多内容残缺或语无伦次，导致本可通过两函便可结案归档的交易，时常需要六到八函方能了结。

    "A good letter is the result of clear thinking and careful planning."
    -> 一封上乘信函，是思路清晰与规划周详的产物。

    "The letter must succeed in getting its idea across and it must build up good will for its firm."
    -> 信函必须成功传达其意图，并为其公司建立商誉。

    "There should be a reason back of every letter if it is only to say "Thank you" to a customer."
    -> 每一封信背后都应有一个理由，即便仅仅是对客户说声“谢谢”。

    "A good letter never attracts the mind of the reader to itself as a thing apart from its contents."
    -> 一封好信函，绝不会让读者的心智脱离其内容，转而关注信函本身这个形式。

    "No _letter and no advertisement is any good which calls attention to itself instead of the message it is trying to deliver_."
    -> 凡是试图吸引对自己本身的关注，而非聚焦于其试图传递的信息的**信函或广告，都毫无价值**。

    "Plain white paper of good quality is always in good taste."
    -> 品质上乘的纯白信纸始终不失为雅致之选。

    "He attracts attention, but he makes us shiver."
    -> 他确实引人注目，却令我们不禁不寒而栗。

    "A letter passes through the hands of several postal clerks before it reaches the person to whom it is addressed, and if each one of them has to stop to play with it awhile an appreciable amount of time is lost, not to mention the strain it puts on their respective tempers."
    -> 一封信函在送达收件人之前会经过数名邮务人员之手，如果每一位都需要停下摆弄一番，不仅会损失相当可观的时间，更会对他们的耐心造成不小的考验。

    "but most young girls just entering business are highly irresponsible"
    -> 但大多数初入商界的年轻女性极不负责任。
    (Alternative: 但大多数刚进入商界的年轻女性极不可靠 / 非常不靠谱。 "Irresponsible" is better translated directly as 不负责任, it's a stronger, direct critique matching the author's tone.)

    Let's do a final sweep, ensuring no examples are added and the argument is precisely the same.

    No extra examples. The translation conveys the author's argument about clarity, goodwill, and restraint perfectly.

    Drafting the final output. The instructions say "do not add examples beyond the source". The source has the publishing house example, the Fifth Avenue gentleman example, the hotel/factory stationery examples. All these are in the source, so they must be included.

    The structure of the output should be a continuous translation as requested. No preface, no notes, just the translation.

    "Translate the following English business-writing passage into Simplified Chinese."

    Outputting.
```

## Assistant

```markdown
在已书写的商务信函中，有一半根本无需动笔；而在另一半中，又有许多内容残缺或条理不清，导致本可通过两函便可结案归档的交易，时常需要六到八函方能了结。

一封上乘信函，是思路清晰与规划周详的产物。就营销信函而言，其起草有时需耗时数周，但日常通信通常数分钟即可完成。时间长短并非关键——关键在于最终写就的是何等信函。

商务函件指南提供了一系列衡量信函优劣的规则与标准。但所有经验法则都暗藏风险，唯有两条要素至关重要；其余法则仅在其能助益于这两条要素时方才具备价值。信函必须成功传达其意图，并为其公司建立商誉。最上乘的信函，正是能以最谦恭有礼的态度、最完满的方式，在最短的时间（及纸张篇幅）内达成此目标的那一封。

每一封信背后都应有一个理由，即便仅仅是对客户道声“谢谢”。我国有太多的精力被耗费在徒劳的努力之上：毫无目的的广告、毫无价值的推销、毫无效果的函件撰写，以及其他形形色色的方式。其中大量的精力是在打字机上敲打出去的，将毫无用处的信函转录到纸上——这些纸张若用于其他用途，或许本可以物尽其用。

一封好信函，绝不会让读者的心智脱离其内容，转而关注信函本身这个形式。去年，有一家出版社寄出一百封测试邮件为一本新书做广告。只收回了三封回信，没有一封是订购该书的，但三封回信都对信函本身赞赏有加。一封来自一位商务英语教师，他声称要将此信用作课堂范文；另外两封则祝贺该公司拥有如此出色的信函撰稿人。那封测试信函的外观颇为吸引人，出自一位大学毕业生之手，措辞清晰、准确且富有文采。但这是一封失败的信函。凡是试图将注意力引向自身而非其试图传递信息的信函或广告，都毫无价值。

信函的格式没有太多展示个性的余地。惯例已将其标准化，与传统格式的惊人偏离，表明的是乖张而非创意。这就好比那位令人咋舌的绅士，在最寒冷的冬日清晨，光着头、未穿外套、不着袜子，仅着一身白色法兰绒衣裤和一双网球鞋，漫步于第五大道。他确实引人注目，却让我们不寒而栗。

品质优良的纯白信纸始终不失雅致。某些颜色暗淡的纸张也并非不可取，但在所有高级商务领域中，艳俗的颜色、花哨的设计以及繁复的信头都是禁忌。提供明确且有用信息的简单信头才是最佳选择。公司名称和地址（许多公司仅止于“纽约”或“芝加哥”这类简略标注，但这远远不够），如有则加上电报挂号、电话号码，以及一个不过分显眼的商标（**“显眼”与“富有特色”是两码事**），这些便是一家公司所需的全部信息。

酒店常常以一种非常不谦虚的方式将自身照片印在信笺上，但这有非常充分的理由。大多数人想了解一家酒店的第一件事，就是它看起来是什么样子。所以，请看这里。一些工厂，尤其是那些为自身外观感到自豪的工厂，也会将自身图片印于信笺上。这无可厚非，但美国最漂亮的一家工厂，其信头上只有公司名称、地址和一个小小的黑色版刻商标。有时，例如在营销信函中，一幅图片能以极为有效的方式辅助文字内容。只要任何设计确实有帮助，就应当予以采用，唯一限制是不失品味。

在商业实践中，使用标准尺寸的信封更为务实。若使用开窗信封，窗口应保持清晰，纸张应为白色或近乎白色，打印的地址则应是纯正清晰的黑色。内件应贴合信封放置，使地址一览无余，无需先在信封内来回抖动调整。一封信函在送达收件人之前会经过数名邮务人员之手，如果每一位都需要停下来摆弄一番，不仅会损失相当可观的时间，更会对他们的耐心造成不小的考验。信封用纸应始终足够不透明，以遮蔽信函内容。

实际上，所有商业信函均为打印件。偶尔会有“诚聘”广告要求应聘者亲笔回信，但这种情况也很罕见。在多数地方，打字工作由经过专门培训的年轻女性完成，但绝大多数初入商界的年轻女性极不负责任。因此，口述信函的男士和女士有必要了解什么样的外观才算令人满意，以便指出缺陷并提出改进建议。
```
