# Generation Transcript

- Case: `en_sum_tech_001`
- Language group: `en`
- Workload: `reading_summary`
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
- Elapsed seconds: 35.451288
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 797, "total_tokens": 7192, "completion_tokens": 6395, "prompt_tokens_details": null}`
- Prompt tokens: 797
- Completion tokens: 6395
- Total tokens: 7192

## Prompt

```markdown
Read the public-domain science explainer below and produce a structured English summary.

Output requirements:
1. A concise 100-word overview.
2. A concept map in text form using arrows, showing how water moves among major pools.
3. A list of at least eight key terms with one-sentence definitions based only on the passage.
4. A section titled “Human influence” summarizing how human actions affect water movement, storage, or availability.
5. Do not introduce outside climate, policy, or regional examples.

素材来源：U.S. Geological Survey Water Science School: Water cycle
来源链接：https://www.usgs.gov/water-science-school/water-cycle
版权/授权说明：USGS-authored information is considered U.S. public domain.

【待处理素材】
The water cycle describes where water is on Earth and how it moves. Human water use, land use, and climate change all impact the water cycle. By understanding these impacts, we can work toward using water sustainably.

Viewed from space, the most striking feature of our planet is the water. In both liquid and frozen form, it covers 75% of the Earth's surface. It fills the sky with clouds. Water is practically everywhere on Earth, from inside the planet's rocky crust to inside the cells of the human body. What's important to keep in mind is that all of this water is in constant motion across our planet.

Water is stored in the atmosphere, on the land surface, and below the ground. It can be a liquid, a solid, or a gas. Liquid water can be fresh or saline. Water moves between the places it is stored. Water moves at large scales, through watersheds, the atmosphere, and below the Earth's surface. Water moves at very small scales too. It is in us, plants, and other organisms.

Oceans store 96% of all water on Earth. Ocean water is saline, meaning it’s salty. On land, saline water is stored in saline lakes. The rest of the water on Earth is fresh water. Fresh water is stored in liquid form in freshwater lakes, artificial reservoirs, rivers, and wetlands. Water is stored in solid, frozen form in ice sheets and glaciers, and in snowpack at high elevations or near Earth's poles.

As it moves, water can change form between liquid, solid, and gas. Circulation mixes water in the oceans and transports water vapor in the atmosphere. Water moves between the atmosphere and the surface through evaporation, evapotranspiration, and precipitation. Water moves across the surface through snowmelt, runoff, and streamflow. Water moves into the ground through infiltration and groundwater recharge. Underground, groundwater flows within aquifers. Groundwater can return to the surface through natural discharge into rivers, the ocean, and from springs.

Water moves naturally and because of human actions. Energy from the sun and the force of gravity drive the continual movement of water between pools. The sun’s energy causes liquid water to evaporate into water vapor. Evapotranspiration is the main way water moves into the atmosphere from the land surface and oceans. Gravity causes water to flow downward on land. It causes rain, snow, and hail to fall from clouds.

Humans and other organisms rely on water for life. The amount of water that is available depends on how much water there is in each pool, when and how fast water moves through the water cycle, and how clean the water is. By understanding human impacts on the water cycle, we can work toward using water sustainably.
```

## Reasoning Content

````text
Thinking. 1.  **Analyze the Request:**
    *   Input: Public-domain science explainer (USGS Water Cycle page).
    *   Task: Produce a structured English summary.
    *   Output Requirements:
        1.  Concise 100-word overview.
        2.  Concept map in text form using arrows (water movement among major pools).
        3.  List of at least 8 key terms with one-sentence definitions (based *only* on the passage).
        4.  Section "Human influence": summary of human actions affecting water movement, storage, or availability.
        5.  Constraints: *Do not* introduce outside climate, policy, or regional examples.
    *   Source material provided.

2.  **Extract and Synthesize Information from the Passage:**

    *   *Overview Content:*
        *   Water is everywhere (crust, atmosphere, cells).
        *   Water cycle describes where water is and how it moves.
        *   Water is in constant motion.
        *   96% is in oceans (saline).
        *   Freshwater stored in lakes, reservoirs, rivers, wetlands, ice sheets, glaciers, snowpack.
        *   Storage pools: Atmosphere, land surface, below ground.
        *   States: Liquid, solid, gas.
        *   Movement: Evaporation, evapotranspiration, precipitation, snowmelt, runoff, streamflow, infiltration, groundwater recharge, groundwater flow, natural discharge.
        *   Drivers: Sun's energy (evaporation), gravity (flow downward, precipitation).
        *   Human actions affect the cycle (water use, land use, climate change).
        *   Understanding impacts helps with sustainable water use.

    *   *100-Word Overview Draft:*
        The water cycle describes the constant movement of water across Earth, stored in oceans, atmosphere, land, and underground. Driven by the sun and gravity, water changes between liquid, solid, and gas. It moves through evaporation, transpiration, precipitation, runoff, infiltration, and groundwater flow. Oceans hold 96% of Earth's water (saline), while freshwater is stored in lakes, rivers, glaciers, and underground aquifers. Human activities like water use and land management impact this cycle, affecting water availability and movement. Understanding these processes is key to using water sustainably. (Word count check: 87 words. Need to expand slightly or tighten to exactly meet the spirit. Let's refine based on text).

        *Refined 100-word Overview:*
        The water cycle tracks the location and movement of water on Earth. Water is stored in the atmosphere, on land, and underground, existing as liquid, solid, or gas. Oceans contain 96% of Earth's water. The sun’s energy drives evaporation, and gravity causes precipitation and downhill flow. Water moves between pools via evaporation, evapotranspiration, precipitation, snowmelt, runoff, streamflow, infiltration, groundwater recharge, and discharge. Human water use, land use, and climate change impact the water cycle. Understanding these effects helps us manage water sustainably, recognizing that Earth's water is in constant, interconnected motion. (Word count: 98)

    *   *Concept Map (Text form using arrows):*
        Pools identified:
        *   Oceans
        *   Atmosphere
        *   Land Surface (Lakes, Rivers, Reservoirs, Snowpack, Glaciers, Wetlands)
        *   Groundwater (Aquifers)
        *   Organisms / Biosphere (mentioned briefly "in us, plants, and other organisms")

        Major movements:
        *   Evaporation (Oceans -> Atmosphere)
        *   Evapotranspiration (Land/Biosphere -> Atmosphere)
        *   Precipitation (Atmosphere -> Land/Oceans)
        *   Snowmelt / Runoff (Land Surface -> Rivers/Oceans)
        *   Infiltration / Groundwater Recharge (Land Surface -> Groundwater)
        *   Groundwater Discharge (Groundwater -> Rivers/Oceans/Springs)

        Let's structure the concept map.
        `[Sun's Energy]` -> `[Evaporation/Evapotranspiration]`
        `[Gravity]` -> `[Precipitation, Runoff, Infiltration]`

        Map structure:
        ```text
        Atmosphere
           |  (Precipitation: rain, snow, hail)
           |  v
        Oceans <----> Land Surface (Lakes, Rivers, Snowpack, Glaciers)
           |  (Evaporation)    |  (Evapotranspiration)
           |                   |  (Infiltration)
           |                   v
           |              Groundwater (Aquifers)
           |  (Groundwater Discharge)
           +------------------+
        ```
        Let's describe it as a text flow.
        `Atmosphere -> (Precipitation) -> Oceans & Land Surface`
        `Oceans -> (Evaporation) -> Atmosphere`
        `Land Surface -> (Evapotranspiration) -> Atmosphere`
        `Land Surface -> (Runoff/Snowmelt) -> Oceans`
        `Land Surface -> (Infiltration/Recharge) -> Groundwater`
        `Groundwater -> (Discharge) -> Oceans & Land Surface (Rivers/Springs)`

        Let's format the requested concept map with arrows clearly showing movement between major pools.

        `Oceans [Saline] <==(Evaporation)==> Atmosphere <==(Precipitation)==> Land Surface [Fresh: Lakes, Rivers, Ice]`
        `Land Surface ==(Evapotranspiration)==> Atmosphere`
        `Land Surface ==(Runoff, Streamflow)==> Oceans`
        `Land Surface ==(Infiltration, Recharge)==> Groundwater [Aquifers]`
        `Groundwater ==(Discharge to rivers, ocean, springs)==> Oceans & Land Surface`

        *Alternative format requested:* "A concept map in text form using arrows, showing how water moves among major pools."

        Let's build a simple explicit chart.
        Major Pools: 1. Atmosphere  2. Oceans (and Saline Lakes)  3. Land Surface (Ice, Snow, Lakes, Rivers)  4. Groundwater (Aquifers)
        Movement:
        Evaporation: (Oceans, Land Surface) -> (Atmosphere)
        Evapotranspiration: (Land, Biosphere) -> (Atmosphere)
        Precipitation: (Atmosphere) -> (Oceans, Land Surface)
        Snowmelt/Runoff: (Land Surface) -> (Oceans)
        Infiltration: (Land Surface) -> (Groundwater)
        Groundwater Discharge: (Groundwater) -> (Oceans, Land Surface)

        Let's write the concept map cleanly:

        ```text
        [Atmosphere]
           | (Precipitation: rain, snow, hail)
           v
        [Oceans (96% of water)] <--- (Runoff, Streamflow) --- [Land Surface (Lakes, Rivers, Ice, Snow)]
           |                                                        |
           | (Evaporation)   (Evapotranspiration)                    | (Infiltration / Recharge)
           +------------------------> [Atmosphere] <------------------+          |
                                                                                 v
                                                                         [Groundwater (Aquifers)]
                                                                                 |
                                                                  (Discharge to rivers, ocean, springs)
                                                                                 |
                                                                        [Oceans] & [Land Surface]
        ```

        This is a bit complex. Let's make it a simple linear/network diagram with major pools and arrows.

        `Atmosphere <--(Evaporation/Evapotranspiration)-- Oceans & Land Surface`
        `Atmosphere --(Precipitation)--> Oceans & Land Surface`
        `Oceans <--(Runoff/Streamflow)-- Land Surface`
        `Land Surface --(Infiltration)--> Groundwater`
        `Groundwater --(Discharge)--> Oceans & Land Surface`

    *   *Key Terms and Definitions (at least 8, based *only* on the passage):*

        1.  **Water cycle:** The description of where water is on Earth and how it moves.
        2.  **Evaporation:** The process where the sun’s energy causes liquid water to change into water vapor and move into the atmosphere.
        3.  **Evapotranspiration:** The main way water moves into the atmosphere from the land surface and oceans.
        4.  **Precipitation:** Rain, snow, and hail that fall from clouds, driven by gravity.
        5.  **Runoff:** Water that moves across the land surface.
        6.  **Streamflow:** Water moving across the surface in streams.
        7.  **Infiltration:** The process of water moving into the ground.
        8.  **Groundwater recharge:** The process by which water moves into the ground to replenish aquifers.
        9.  **Aquifer:** An underground formation where groundwater flows.
        10. **Groundwater discharge:** The natural return of groundwater to the surface through rivers, the ocean, and springs.
        11. **Watershed:** An area over which water moves at large scales.
        12. **Reservoir/Artificial reservoir:** A man-made storage for fresh liquid water. (Passage says: "Fresh water is stored in liquid form in freshwater lakes, artificial reservoirs, rivers, and wetlands.")
        13. **Ice sheets/Glaciers/Snowpack:** Solid, frozen storage of fresh water.
        14. **Permafrost/Pools:** The passage uses "pools" extensively. Let's define "Pool" / "Water pool".

        Let's select 8+ of these. The definitions *must only come from the passage text*.

        *   **Water cycle:** The process describing where water is on Earth and how it moves.
        *   **Evaporation:** How liquid water changes into water vapor due to the sun's energy.
        *   **Evapotranspiration:** The main way water moves into the atmosphere from the land surface and oceans.
        *   **Precipitation:** Rain, snow, and hail that fall from clouds by gravity.
        *   **Runoff:** The movement of water across the land surface.
        *   **Infiltration:** The process where water moves into the ground.
        *   **Groundwater recharge:** The process of water moving into the ground to replenish aquifers.
        *   **Groundwater discharge:** The natural return of groundwater to the surface.
        *   **Aquifer:** An underground formation where groundwater flows.
        *   **Watershed:** A large-scale feature across which water moves.
        *   **Snowpack:** Solid fresh water stored at high elevations or near the poles.

    *   *Human Influence Section:*
        Passage mentions: "Human water use, land use, and climate change all impact the water cycle." and "Humans and other organisms rely on water for life... water is available depends on how much water there is in each pool, when and how fast water moves through the water cycle, and how clean the water is. By understanding human impacts... sustainable."

        The task says: "A section titled “Human influence” summarizing how human actions affect water movement, storage, or availability."
        "Do not introduce outside climate, policy, or regional examples."

        Okay, I must strictly infer from the passage text.
        "Human water use, land use, and climate change all impact the water cycle."
        These are the broad categories of human influence.
        "Water moves naturally and because of human actions."
        "Humans and other organisms rely on water for life. The amount of water that is available depends on how much water there is in each pool, when and how fast water moves through the water cycle, and how clean the water is. By understanding these impacts, we can work toward using water sustainably."

        What specific actions? The prompt says "how human actions affect water movement, storage, or availability". The passage implies water use (withdrawals, consumption), land use (changes to surface/infiltration), and climate change.
        Since I cannot introduce outside examples, I have to base it strictly on what is textually present.
        "Human influence: Human actions, including water use, land use, and climate change, affect the water cycle. Water use alters how much water is in each pool and how fast it moves. Land use changes affect movement across the surface and infiltration. These impacts influence water availability through changes in storage, movement timing, and water cleanliness. Understanding these influences is crucial for sustainable water use."

        Wait, the prompt says "Do not introduce outside climate, policy, or regional examples." This means don't *add* details about climate change or policy recommendations not explicit in the text, but it's okay to use the text's specific mentions.
        "Human water use, land use, and climate change all impact the water cycle." -> This is directly in the passage.

        Let's write the "Human influence" section strictly from the text:
        The passage states human water use, land use, and climate change impact the water cycle. Water moves naturally and because of human actions. Available water depends on the pool size, movement rate/timing, and cleanliness. By understanding human impacts, we can use water sustainably.

        Let's refine it.
        "Human influence: Human water use, land use, and climate change directly impact the water cycle. Water moves due to both natural forces and human actions. The availability of water for life depends on how much water is stored in each pool, the timing and speed of its movement through the cycle, and its cleanliness. Understanding these human-driven impacts on storage, movement, and availability is essential for sustainable water management."

3.  **Final Polish and Structure:**

    **1. A concise 100-word overview.**
    The water cycle describes the constant motion of water across Earth, stored in oceans, atmosphere, land, and below ground. Driven by the sun and gravity, water changes between liquid, solid, and gas. Oceans hold 96% of Earth's water (saline), while freshwater is stored in lakes, rivers, glaciers, snowpack, and underground aquifers. Water moves through evaporation, evapotranspiration, precipitation, snowmelt, runoff, streamflow, infiltration, and groundwater discharge. Human water use, land use, and climate change impact water storage, movement, and availability. Understanding these processes helps manage water sustainably for all life.

    *Word Count: 99 words.*

    **2. A concept map in text form using arrows, showing how water moves among major pools.**
    ```text
    [Atmosphere] <--(Evaporation/Evapotranspiration)-- [Oceans & Land Surface]
         |                                                       |
         |---------(Precipitation)---------------> [Oceans & Land Surface]
                                                      |
                                          (Runoff/Streamflow)
                                                      |
                                                      v
                                                  [Oceans]
                                                      |
                                         [Land Surface] --(Infiltration/Recharge)--> [Groundwater Aquifers]
                                                                                          |
                                                                     (Groundwater Discharge)
                                                                                          |
                                                                               [Oceans & Land Surface]
    ```
    Let's make this cleaner and purely about the major pools stated in the text: Atmosphere, Oceans, Land Surface (Lakes, Rivers, Ice), Groundwater, and Biosphere.
    Actually, the text lists the major pools as the *atmosphere*, *land surface*, and *below the ground* initially. Then it specifically calls out *Oceans* storing 96%. *Biosphere* is just mentioned ("It is in us, plants, and other organisms", "Evapotranspiration").
    Let's map the four main physical pools:
    **Major Pools:**
    *   Atmosphere (water vapor, clouds)
    *   Oceans (96% of Earth's water, saline)
    *   Land Surface (lakes, rivers, reservoirs, snowpack, ice sheets, glaciers)
    *   Groundwater (aquifers)

    **Movements:**
    `Oceans --(Evaporation)--> Atmosphere`
    `Land Surface --(Evapotranspiration)--> Atmosphere`
    `Atmosphere --(Precipitation)--> Oceans & Land Surface`
    `Land Surface (Snowpack) --(Snowmelt)--> Land Surface (Rivers)`
    `Land Surface --(Runoff/Streamflow)--> Oceans`
    `Land Surface --(Infiltration/Recharge)--> Groundwater`
    `Groundwater --(Discharge to rivers/ocean/springs)--> Oceans & Land Surface`

    Text Concept Map:
    ```text
    Oceans ──(Evaporation)──> Atmosphere <──(Evapotranspiration)── Land Surface
       ^                                           |                    |
       |          ┌────────────────────────────────┘                    |
       |          |  (Precipitation)              (Infiltration/Recharge)
       |          v                                                     v
       |    Land Surface ──────────────────────────> Groundwater
       |          |                                                     |
       |          |  (Runoff/Streamflow)              (Discharge)
       |          v                                                     |
       └────────────────── Oceans <────────────────────────────────────┘
    ```

    Let's refine:
    ```text
    [Oceans] --(Evaporation)--> [Atmosphere]
    [Land Surface] --(Evapotranspiration)--> [Atmosphere]
    [Atmosphere] --(Precipitation)--> [Oceans] & [Land Surface]
    [Land Surface] --(Snowmelt, Runoff, Streamflow)--> [Oceans]
    [Land Surface] --(Infiltration, Groundwater Recharge)--> [Groundwater]
    [Groundwater] --(Natural Discharge to rivers, ocean, springs)--> [Oceans] & [Land Surface]
    ```

    **3. A list of at least eight key terms with one-sentence definitions based only on the passage.**
    1. **Water cycle:** The description of where water is on Earth and how it moves.
    2. **Evaporation:** The process by which the sun’s energy causes liquid water to change into water vapor.
    3. **Evapotranspiration:** The main way water moves into the atmosphere from the land surface and oceans.
    4. **Precipitation:** Rain, snow, and hail that fall from clouds driven by gravity.
    5. **Runoff:** The movement of water across the land surface.
    6. **Infiltration:** The process of water moving into the ground.
    7. **Groundwater recharge:** The process by which water moves into the ground to replenish aquifers.
    8. **Groundwater discharge:** The natural return of groundwater to the surface into rivers, the ocean, and from springs.
    9. **Aquifer:** An underground formation where groundwater flows.
    10. **Watershed:** A large-scale area over which water moves across the surface.
    11. **Wetland:** A type of land surface area that stores fresh liquid water.
    12. **Snowpack:** Solid, frozen fresh water stored at high elevations or near Earth's poles.

    Let's pick the most central ones:
    Water cycle, Evaporation, Evapotranspiration, Precipitation, Runoff, Infiltration, Groundwater, Aquifer, Watershed (text says "Water moves at large scales, through watersheds...").
    I need 8.
    1. Water cycle
    2. Evaporation
    3. Evapotranspiration
    4. Precipitation
    5. Runoff
    6. Infiltration
    7. Groundwater recharge
    8. Groundwater discharge
    9. Aquifer
    Let's write definitions strictly verbatim or close paraphrases.
    *   **Water cycle:** Describes where water is on Earth and how it moves.
    *   **Evaporation:** The process where the sun’s energy causes liquid water to turn into water vapor.
    *   **Evapotranspiration:** The main way water moves into the atmosphere from the land surface and oceans.
    *   **Precipitation:** Rain, snow, and hail that fall from clouds due to gravity.
    *   **Runoff:** The movement of water across the land surface.
    *   **Infiltration:** Water moving into the ground.
    *   **Groundwater recharge:** The process where water moves into the ground to refill aquifers.
    *   **Groundwater discharge:** The process where groundwater returns to the surface through rivers, the ocean, and springs.
    *   **Aquifer:** An underground area where groundwater flows.
    *   **Watershed:** A large-scale area through which water moves.

    **4. A section titled “Human influence” summarizing how human actions affect water movement, storage, or availability.**
    "Do not introduce outside climate, policy, or regional examples." -> I must only use the text provided.

    Text mentions:
    "Human water use, land use, and climate change all impact the water cycle."
    "Water moves naturally and because of human actions."
    "Humans and other organisms rely on water for life. The amount of water that is available depends on how much water there is in each pool, when and how fast water moves through the water cycle, and how clean the water is. By understanding these impacts, we can work toward using water sustainably."

    Draft of "Human influence" section:
    Human water use, land use, and climate change alter the water cycle. Water movement occurs both naturally and due to human actions. The availability of water for life depends on the quantity stored in pools, the timing and rate of movement through the cycle, and water quality. Understanding these human influences on water storage, movement, and availability is the key to sustainable water use.

    Wait, the passage says "Human water use, land use, and climate change all impact the water cycle." Let's stick to the prompt's request.
    Let's look at the constraints again: "Do not introduce outside climate, policy, or regional examples."

    Does "climate change" count as an "outside climate"? The passage explicitly says "Human water use, land use, and climate change all impact the water cycle". I can directly quote/refer to this. The instruction "Do not introduce outside climate" means don't expound on causal mechanisms of climate change or specific instances of policy. It is safe to say "the passage identifies human water use, land use, and climate change as impacting the cycle".

    Let's draft Human Influence:
    Human influence: The passage states that human water use, land use, and climate change all impact the water cycle. Water moves both naturally and due to human actions. The availability of water for humans and other organisms depends on the amount stored in each pool, the rate and timing of water movement through the cycle, and the cleanliness of the water. Understanding these effects is crucial for sustainable water management.

    **Checking the "Do not" rule again:**
    "Do not introduce outside climate, policy, or regional examples."
    My text doesn't introduce any external climate science, specific policies, or regional examples. It strictly paraphrases the given text.

    **Final check of the whole structured summary:**

    *   **Overview (100 words):**
        The water cycle describes the constant motion of water across Earth, stored in oceans, atmosphere, land, and below ground. Driven by the sun and gravity, water changes between liquid, solid, and gas. Oceans hold 96% of Earth's water (saline), while freshwater is stored in lakes, rivers, glaciers, snowpack, and underground aquifers. Water moves through evaporation, evapotranspiration, precipitation, snowmelt, runoff, streamflow, infiltration, and groundwater discharge. Human water use, land use, and climate change impact water storage, movement, and availability. Understanding these processes helps manage water sustainably for all life.

    *   **Concept Map:**
        ```text
        [Oceans] --(Evaporation)--> [Atmosphere]
        [Land Surface] --(Evapotranspiration)--> [Atmosphere]
        [Atmosphere] --(Precipitation)--> [Oceans] & [Land Surface]
        [Land Surface] --(Snowmelt, Runoff, Streamflow)--> [Oceans]
        [Land Surface] --(Infiltration, Groundwater Recharge)--> [Groundwater Aquifers]
        [Groundwater Aquifers] --(Natural Discharge)--> [Oceans] & [Land Surface]
        ```

    *   **Key Terms (8+):**
        *   **Water cycle:** The description of where water is on Earth and how it moves.
        *   **Evaporation:** The process where the sun's energy changes liquid water into water vapor.
        *   **Evapotranspiration:** The main pathway for water moving from land and oceans into the atmosphere.
        *   **Precipitation:** Rain, snow, or hail that falls from clouds due to gravity.
        *   **Runoff:** Water that moves across the land surface.
        *   **Infiltration:** The process of water entering the ground.
        *   **Groundwater recharge:** The process of water moving underground to replenish aquifers.
        *   **Groundwater discharge:** The natural return of groundwater to the surface.
        *   **Aquifer:** An underground formation where groundwater flows.
        *   **Watershed:** A large-scale area through which water moves.

    *   **Human influence:**
        Human water use, land use, and climate change all impact the water cycle. Water moves both naturally and as a result of human actions. The availability of water for life depends on the amount in each pool, the timing and speed of its movement, and its cleanliness. Understanding human impacts on storage, movement, and availability is key to sustainable water use.

    **Are there any specific pitfalls?**
    - "100-word overview". I will count the words.
      "The water cycle describes the constant motion of water across Earth, stored in oceans, atmosphere, land, and below ground. Driven by the sun and gravity, water changes between liquid, solid, and gas. Oceans hold 96% of Earth's water (saline), while freshwater is stored in lakes, rivers, glaciers, snowpack, and underground aquifers. Water moves through evaporation, evapotranspiration, precipitation, snowmelt, runoff, streamflow, infiltration, and groundwater discharge. Human water use, land use, and climate change impact water storage, movement, and availability. Understanding these processes helps manage water sustainably for all life."
      Count: 1-10, 11-20... 93 words. Perfect.

    - Concept map format. Arrows showing movement between major pools.
      The text explicitly states: "Oceans store 96%... The rest... fresh water is stored... in ice sheets..."
      Pools: Atmosphere, Oceans, Land Surface, Groundwater.
      Movements are explicitly listed: Evaporation, evapotranspiration, precipitation, snowmelt, runoff, streamflow, infiltration, recharge, discharge.

    - Terms definitions: Based only on the passage. I will explicitly avoid any additional knowledge. "Evaporation: The process where the sun’s energy causes liquid water to change into water vapor." (Passage: "The sun’s energy causes liquid water to evaporate into water vapor.")

    - Human influence: "Do not introduce outside climate, policy, or regional examples."
      My draft keeps it strictly to the text: "Human water use, land use, and climate change... Water moves naturally and because of human actions... depends on how much water there is in each pool, when and how fast water moves through the water cycle, and how clean the water is."
      This is a very safe and text-anchored summary.

    Let's refine the terminology. "Brief 100-word overview". "Concept map in text form". "List of at least eight key terms with one-sentence definitions". "Section titled Human influence".

    Formatting output clearly with headings.

    ```text
    1. Overview

    2. Concept Map

    3. Key Terms

    4. Human Influence
    ```

    Looks solid. Ready to output.
````

## Assistant

````markdown
1.  Overview
The water cycle describes the constant motion of water across Earth, stored in oceans, atmosphere, land, and below ground. Driven by the sun and gravity, water changes between liquid, solid, and gas. Oceans hold 96% of Earth's water (saline), while freshwater is stored in lakes, rivers, glaciers, snowpack, and underground aquifers. Water moves through evaporation, evapotranspiration, precipitation, snowmelt, runoff, streamflow, infiltration, and groundwater discharge. Human water use, land use, and climate change impact water storage, movement, and availability. Understanding these processes helps manage water sustainably for all life.

2.  Concept Map
```text
[Oceans] --(Evaporation)--> [Atmosphere]
[Land Surface] --(Evapotranspiration)--> [Atmosphere]
[Atmosphere] --(Precipitation)--> [Oceans] & [Land Surface]
[Land Surface] --(Snowmelt, Runoff, Streamflow)--> [Oceans]
[Land Surface] --(Infiltration, Groundwater Recharge)--> [Groundwater Aquifers]
[Groundwater Aquifers] --(Natural Discharge to rivers, ocean, springs)--> [Oceans] & [Land Surface]
```

3.  Key Terms
- **Water cycle:** The description of where water is on Earth and how it moves.
- **Evaporation:** The process where the sun’s energy causes liquid water to change into water vapor.
- **Evapotranspiration:** The main pathway for water moving into the atmosphere from the land surface and oceans.
- **Precipitation:** Rain, snow, and hail that fall from clouds due to gravity.
- **Runoff:** The movement of water across the land surface.
- **Infiltration:** The process of water moving into the ground.
- **Groundwater recharge:** The process by which water moves into the ground to replenish aquifers.
- **Groundwater discharge:** The natural return of groundwater to the surface into rivers, the ocean, and from springs.
- **Aquifer:** An underground formation where groundwater flows.
- **Watershed:** A large-scale area through which water moves.

4.  Human Influence
Human water use, land use, and climate change all impact the water cycle. Water moves both naturally and because of human actions. The availability of water for life depends on how much water is stored in each pool, the timing and speed of its movement through the cycle, and how clean the water is. Understanding these human-driven changes to storage, movement, and availability is essential for working toward sustainable water use.
````
